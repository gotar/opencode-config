# Testing Patterns

## Philosophy

1. **Test behavior, not implementation** - Focus on what the code does, not how
2. **Fixtures over factories** - Pre-built data is faster and more deterministic
3. **Real database, minimal mocks** - Integration over isolation
4. **Domain-driven organization** - Tests mirror business model structure
5. **Event verification** - Check that events were created, not just state changed

## Directory Structure

```
test/
├── test_helper.rb
├── test_helpers/
│   ├── session_test_helper.rb
│   ├── action_text_test_helper.rb
│   └── search_test_helper.rb
├── fixtures/
│   ├── accounts.yml
│   ├── users.yml
│   ├── identities.yml
│   └── cards.yml
├── models/
│   ├── card_test.rb
│   └── card/
│       ├── assignable_test.rb
│       └── closeable_test.rb
├── controllers/
│   ├── boards_controller_test.rb
│   └── cards/
│       └── comments_controller_test.rb
├── system/
│   └── smoke_test.rb
└── jobs/
    └── delete_unused_tags_job_test.rb
```

## Test Helper Setup

```ruby
# test/test_helper.rb
ENV["RAILS_ENV"] ||= "test"
require_relative "../config/environment"
require "rails/test_help"

class ActiveSupport::TestCase
  parallelize(workers: :number_of_processors)
  fixtures :all

  # Custom test helpers
  include SessionTestHelper
  include ActionTextTestHelper
end

class ActionDispatch::IntegrationTest
  setup do
    # Set default account context for multi-tenancy
    integration_session.default_url_options[:script_name] =
      "/#{ActiveRecord::FixtureSet.identify("37signals")}"
  end
end

class ActionDispatch::SystemTestCase
  driven_by(ENV["SYSTEM_TESTS_BROWSER"] ? :chrome : :chrome_headless)

  setup do
    self.default_url_options[:script_name] =
      "/#{ActiveRecord::FixtureSet.identify("37signals")}"
  end
end
```

## Fixtures

### Deterministic UUIDs

```ruby
# Generate fixture UUIDs that sort before runtime records
def generate_fixture_uuid(label)
  fixture_int = Zlib.crc32("fixtures/#{label}") % (2**30 - 1)
  base_time = Time.utc(2024, 1, 1)
  timestamp = base_time + (fixture_int / 1000.0)
  uuid_v7_with_timestamp(timestamp, label)
end
```

### Fixture Files

```yaml
# test/fixtures/accounts.yml
37s:
  id: <%= ActiveRecord::FixtureSet.identify("37s", :uuid) %>
  name: 37signals
  external_account_id: <%= ActiveRecord::FixtureSet.identify("37signals") %>

initech:
  id: <%= ActiveRecord::FixtureSet.identify("initech", :uuid) %>
  name: Initech
  external_account_id: <%= ActiveRecord::FixtureSet.identify("initech") %>

# test/fixtures/users.yml
david:
  id: <%= ActiveRecord::FixtureSet.identify("david", :uuid) %>
  name: David
  role: member
  active: true
  identity: david
  account: 37s

kevin:
  id: <%= ActiveRecord::FixtureSet.identify("kevin", :uuid) %>
  name: Kevin
  role: admin
  active: true
  identity: kevin
  account: 37s

# test/fixtures/boards.yml
writebook:
  id: <%= ActiveRecord::FixtureSet.identify("writebook", :uuid) %>
  name: Writebook
  all_access: true
  creator: david
  account: 37s
```

## Session Test Helper

```ruby
module SessionTestHelper
  def sign_in_as(identity)
    identity = identities(identity) unless identity.is_a?(Identity)

    identity.send_magic_link
    magic_link = identity.magic_links.last

    untenanted do
      post session_magic_link_url, params: { code: magic_link.code }
    end

    assert_response :redirect
    assert cookies[:session_token].present?
  end

  def sign_out
    untenanted do
      delete session_path
    end
    assert_not cookies[:session_token].present?
  end

  def with_current_user(user)
    user = users(user) unless user.is_a?(User)
    old_session = Current.session
    Current.session = Session.new(identity: user.identity)
    yield
  ensure
    Current.session = old_session
  end

  def untenanted(&block)
    original = integration_session.default_url_options[:script_name]
    integration_session.default_url_options[:script_name] = ""
    yield
  ensure
    integration_session.default_url_options[:script_name] = original
  end
end
```

## Model Tests

### Testing Scopes

```ruby
class CardTest < ActiveSupport::TestCase
  test "closed scope returns only closed cards" do
    assert_equal [cards(:shipping)], Card.closed
    assert_not_includes Card.open, cards(:shipping)
  end

  test "assigned_to scope" do
    assert_includes Card.assigned_to(users(:kevin)), cards(:logo)
    assert_not_includes Card.assigned_to(users(:david)), cards(:logo)
  end
end
```

### Testing State Transitions

```ruby
class Card::CloseableTest < ActiveSupport::TestCase
  setup do
    Current.session = sessions(:david)
  end

  test "close creates closure and tracks event" do
    assert_not cards(:logo).closed?

    assert_difference -> { Event.count }, +1 do
      cards(:logo).close(user: users(:kevin))
    end

    assert cards(:logo).closed?
    assert_equal "card_closed", Event.last.action
    assert_equal users(:kevin), cards(:logo).closed_by
  end

  test "reopen destroys closure and tracks event" do
    assert cards(:shipping).closed?

    assert_difference -> { Event.count }, +1 do
      cards(:shipping).reopen
    end

    assert cards(:shipping).reload.open?
  end
end
```

### Testing Toggle Operations

```ruby
test "assignment toggling" do
  assert cards(:logo).assigned_to?(users(:kevin))

  assert_difference({ -> { cards(:logo).assignees.count } => -1, -> { Event.count } => +1 }) do
    cards(:logo).toggle_assignment(users(:kevin))
  end

  assert_not cards(:logo).reload.assigned_to?(users(:kevin))

  assert_difference ["cards(:logo).assignees.count", "Event.count"], +1 do
    cards(:logo).toggle_assignment(users(:kevin))
  end

  assert cards(:logo).assigned_to?(users(:kevin))
end
```

### Testing with Time Travel

```ruby
test "auto_postpone_at calculation" do
  freeze_time

  entropies(:writebook_board).update!(auto_postpone_period: 123.days)
  cards(:layout).update!(last_active_at: 2.days.ago)

  assert_equal (123 - 2).days.from_now, cards(:layout).entropy.auto_clean_at
end

test "new cards get current time as last activity" do
  freeze_time

  card = boards(:writebook).cards.create!(title: "New card", creator: users(:david))
  assert_equal Time.current, card.last_active_at
end
```

## Controller Tests

### Basic CRUD

```ruby
class BoardsControllerTest < ActionDispatch::IntegrationTest
  setup do
    sign_in_as :kevin
  end

  test "create" do
    assert_difference -> { Board.count }, +1 do
      post boards_path, params: { board: { name: "New Board" } }
    end

    board = Board.last
    assert_redirected_to board_path(board)
    assert_equal "New Board", board.name
  end

  test "update" do
    patch board_path(boards(:writebook)), params: {
      board: { name: "Updated" }
    }

    assert_redirected_to edit_board_path(boards(:writebook))
    assert_equal "Updated", boards(:writebook).reload.name
  end

  test "destroy" do
    assert_difference -> { Board.count }, -1 do
      delete board_path(boards(:writebook))
    end

    assert_redirected_to root_path
  end
end
```

### Turbo Stream Tests

```ruby
test "create comment with turbo stream" do
  sign_in_as :kevin

  assert_difference -> { cards(:logo).comments.count }, +1 do
    post card_comments_path(cards(:logo)),
         params: { comment: { body: "Great!" } },
         as: :turbo_stream
  end

  assert_response :success
end
```

### Access Control Tests

```ruby
test "users can only see cards in accessible boards" do
  sign_in_as :kevin

  get card_path(cards(:logo))
  assert_response :success

  # Revoke access
  boards(:writebook).update!(all_access: false)
  boards(:writebook).accesses.revoke_from(users(:kevin))

  get card_path(cards(:logo))
  assert_response :not_found
end

test "only admins can update board settings" do
  sign_in_as :member_user  # Non-admin

  patch board_path(boards(:writebook)), params: { board: { name: "Hacked" } }
  assert_response :forbidden
end
```

## System Tests

```ruby
class SmokeTest < ApplicationSystemTestCase
  test "create a card" do
    sign_in_as(users(:david))

    visit board_url(boards(:writebook))
    click_on "Add a card"
    fill_in "card_title", with: "Hello, world!"
    click_on "Create card"

    assert_selector "h3", text: "Hello, world!"
  end

  test "drag card to column" do
    sign_in_as(users(:david))

    card = cards(:logo)
    assert_nil card.column

    visit board_url(boards(:writebook))

    card_el = find("#article_card_#{card.id}")
    column_el = find("#column_#{columns(:triage).id}")

    card_el.drag_to(column_el)

    assert_equal "Triage", card.reload.column.name
  end
end
```

## Job Tests

```ruby
class DeleteUnusedTagsJobTest < ActiveJob::TestCase
  test "deletes unused tags" do
    unused = Tag.create!(title: "unused", account: accounts(:37s))

    assert_changes -> { Tag.count }, -1 do
      DeleteUnusedTagsJob.perform_now
    end

    assert_not Tag.exists?(unused.id)
  end
end

# Inline job execution
test "notification created after comment" do
  perform_enqueued_jobs only: NotifyRecipientsJob do
    cards(:logo).comments.create!(body: "Hello", creator: users(:kevin))
  end

  assert Notification.exists?
end
```

## Assertions

### Count/Difference

```ruby
assert_difference -> { Post.count }, +1
assert_difference "Post.count", +1
assert_no_difference -> { Post.count }

# Multiple assertions
assert_difference({ -> { Card.count } => +1, -> { Event.count } => +1 })
```

### Changes

```ruby
assert_changes -> { card.reload.status }, from: "draft", to: "published"
assert_no_changes -> { card.reload.title }
```

### Job Assertions

```ruby
assert_enqueued_with(job: NotifyRecipientsJob, args: [comment])
perform_enqueued_jobs only: SpecificJob { ... }
```

### Email Assertions

```ruby
assert_emails 1 do
  identity.send_magic_link
end
```

## CI Configuration

```ruby
# bin/ci
CI.run do
  step "Setup", "bin/setup --skip-server"

  # Style
  step "Style: Ruby", "bin/rubocop"

  # Security
  step "Security: Gem audit", "bin/bundler-audit check --update"
  step "Security: Brakeman", "bin/brakeman --quiet --exit-on-warn"

  # Tests
  step "Tests: Unit", "bin/rails test"
  step "Tests: System", "PARALLEL_WORKERS=1 bin/rails test:system"
end
```

## What to Test

**Always test:**
- State transitions (open -> closed, draft -> published)
- Permission checks (who can do what)
- Event creation (audit trail)
- Scope behavior (filtering, ordering)
- Edge cases (empty, nil, boundary values)

**Skip testing:**
- Ruby/Rails standard library behavior
- Simple associations without custom logic
- Exact HTML rendering (test presence, not markup)
- Third-party gem internals
