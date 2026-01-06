---
description: Run the complete Rails testing pipeline with fixtures and real database
---

# Rails Testing Pipeline

This command runs the complete Rails testing pipeline following Rails conventions and 37signals patterns.

## Usage

To run the complete Rails testing pipeline:

```bash
# Full pipeline (recommended)
rails test:all

# Individual components
rails test:models        # Model unit tests
rails test:controllers   # Controller integration tests
rails test:system        # End-to-end system tests
rails test:jobs          # Background job tests

# With linting
bundle exec rubocop -a && rails test:all
```

## Rails Testing Strategy

### Test Pyramid (Rails-Optimized)
- **Model Tests** (60%): Business logic, validations, associations, event tracking
- **Controller Tests** (30%): Request/response, authentication, strong parameters
- **System Tests** (10%): Critical user flows, Hotwire interactions

### Rails Testing Patterns

#### Model Tests
```ruby
# ✅ Rails model testing with fixtures
class CardTest < ActiveSupport::TestCase
  test "closing card creates closure and tracks event" do
    card = cards(:open_card)

    card.close(user: users(:alice))

    assert card.closed?
    assert_equal users(:alice), card.closure.user
    assert_equal 1, card.events.where(action: "card_closed").count
  end
end
```

#### Controller Tests
```ruby
# ✅ Rails controller testing with real requests
class CardsControllerTest < ActionDispatch::IntegrationTest
  test "creates card with valid params and Turbo response" do
    sign_in users(:alice)

    assert_difference -> { Card.count } do
      post cards_path, params: { card: { title: "New Card" } }
    end

    assert_response :success
    assert_select "turbo-stream[action='append']"
  end
end
```

#### System Tests
```ruby
# ✅ Rails system testing for Hotwire flows
class CardManagementTest < ApplicationSystemTestCase
  test "user creates and closes card with real-time updates" do
    sign_in users(:alice)
    visit board_path(boards(:main_board))

    click_on "Add Card"
    fill_in "Title", with: "New Feature"
    click_on "Create Card"

    assert_text "Card created"
    click_on "Close Card"
    assert_text "Card closed"
  end
end
```

## What This Command Does

### 1. Rails Code Quality Checks
- **RuboCop**: Enforces Rails style guide and conventions
- **Rails Best Practices**: Checks for Rails-specific anti-patterns
- **Brakeman**: Security vulnerability scanning

### 2. Rails Test Execution
- **Model Tests**: Business logic, validations, associations
- **Controller Tests**: Request/response cycles, authentication
- **System Tests**: End-to-end user flows with Hotwire
- **Job Tests**: Background processing verification

### 3. Database Testing
- **Fixtures**: YAML fixtures over factories for reliable data
- **Real Database**: Tests run against actual database state
- **Transaction Rollback**: Each test isolated with proper cleanup

### 4. Coverage Reporting
- **SimpleCov**: Test coverage analysis
- **Rails-Specific Metrics**: Model coverage, controller coverage
- **Event Coverage**: Verifies significant actions are tracked

## Rails Testing Best Practices

### ✅ DO Use
- **Rails Fixtures**: `test/fixtures/*.yml` for test data
- **Real Database State**: No transaction rollback isolation
- **Event Verification**: Test side effects through events
- **Strong Parameters Testing**: Verify input validation
- **Hotwire Testing**: System tests for real-time features

### ❌ DON'T Use
- **Factory Objects**: Prefer Rails fixtures
- **Mock-heavy Testing**: Test real behavior, not mocks
- **Transaction Rollback**: Use real database state
- **Implementation Testing**: Test behavior, not internal methods

## Pipeline Steps

1. **Lint Code**: `bundle exec rubocop -a`
2. **Security Scan**: `bundle exec brakeman`
3. **Run Model Tests**: `rails test:models`
4. **Run Controller Tests**: `rails test:controllers`
5. **Run System Tests**: `rails test:system`
6. **Run Job Tests**: `rails test:jobs`
7. **Generate Coverage**: `open coverage/index.html`
8. **Report Results**: Success/failure with detailed breakdown

## Common Rails Testing Issues

### N+1 Query Problems
```ruby
# ❌ N+1 queries in tests
test "lists cards with assignees" do
  cards = Card.all.includes(:assignee) # Missing includes
  cards.each { |card| card.assignee.name } # N+1 queries
end

# ✅ Proper eager loading
test "lists cards with assignees" do
  cards = Card.all.includes(:assignee)
  cards.each { |card| card.assignee.name } # No N+1
end
```

### Event Testing
```ruby
# ✅ Test events are tracked
test "closing card tracks event" do
  card = cards(:open_card)

  assert_difference -> { Event.count } do
    card.close(user: users(:alice))
  end

  event = Event.last
  assert_equal "card_closed", event.action
  assert_equal card, event.eventable
end
```

### Hotwire Testing
```ruby
# ✅ Test Turbo Stream responses
test "card creation returns turbo stream" do
  sign_in users(:alice)

  post cards_path, params: { card: { title: "Test" } }, as: :turbo_stream

  assert_response :success
  assert_select "turbo-stream[action='append'][target='cards']"
end
```

## Troubleshooting

### Test Database Issues
- **Reset DB**: `rails db:test:prepare`
- **Load Fixtures**: `rails db:fixtures:load`
- **Check Schema**: `rails db:schema:dump`

### Coverage Problems
- **Missing Coverage**: Add tests for uncovered code
- **Fixture Issues**: Ensure fixtures provide realistic data
- **Event Gaps**: Verify all significant actions are tested

### Performance Issues
- **Slow Tests**: Use fixtures over factories
- **Database Contention**: Run tests in parallel when possible
- **N+1 Queries**: Use `includes` and check with bullet gem
