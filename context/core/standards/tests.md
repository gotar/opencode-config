<!-- Context: standards/tests | Priority: critical | Version: 2.0 | Updated: 2025-01-21 -->
# Testing Standards

## Quick Reference

**Core Philosophy**: Test behavior, not implementation; fixtures over factories
**Golden Rule**: Tests should be fast, reliable, and use real database state

**Critical Patterns** (use these):
- ✅ Behavior-driven tests (what, not how)
- ✅ Rails fixtures for test data (not factories)
- ✅ Real database testing (not mocks/transactions)
- ✅ Event verification (test side effects)
- ✅ System tests for critical user flows
- ✅ Model unit tests for business logic

**Anti-Patterns** (avoid these):
- ❌ Factory objects, excessive mocking
- ❌ Transaction rollback, isolated tests
- ❌ Implementation testing, slow test suites

---

## Core Philosophy

**Behavior-Driven**: Test what the code does, not how it does it
**Real Database**: Use fixtures and real database state for reliable tests
**Event-Focused**: Verify side effects through events and database changes
**Fast & Reliable**: Tests run quickly and consistently
**Rails-Native**: Prefer Rails testing tools over external gems

## Principles

### Test Pyramid
- **Model Tests**: Business logic, validations, associations
- **Controller Tests**: Request/response, authentication, authorization
- **System Tests**: Critical user flows, end-to-end scenarios
- **Job Tests**: Background processing, side effects

### Test Structure
```
test/
├── fixtures/           # YAML fixtures (preferred over factories)
├── models/            # Model unit tests
├── controllers/       # Controller integration tests
├── system/            # End-to-end system tests
├── jobs/             # Background job tests
├── helpers/          # Test helper methods
└── test_helper.rb    # Shared test setup
```

## Patterns

### Model Tests
```ruby
# ✅ Test business logic and behavior
class CardTest < ActiveSupport::TestCase
  test "closing a card creates closure record" do
    card = cards(:open_card)

    card.close(user: users(:alice))

    assert card.closed?
    assert_equal users(:alice), card.closure.user
  end

  test "reopening a closed card removes closure" do
    card = cards(:closed_card)

    card.reopen(user: users(:alice))

    assert_not card.closed?
    assert_nil card.closure
  end

  test "cannot close already closed card" do
    card = cards(:closed_card)

    assert_no_changes -> { card.closure } do
      card.close(user: users(:alice))
    end
  end
end

# ❌ Testing implementation details
test "close method calls create_closure!" do
  card = cards(:open_card)
  card.expects(:create_closure!).once

  card.close(user: users(:alice))
end
```

### Controller Tests
```ruby
# ✅ Test request/response behavior
class CardsControllerTest < ActionDispatch::IntegrationTest
  test "creates card with valid params" do
    sign_in users(:alice)

    assert_difference -> { Card.count } do
      post cards_path, params: { card: { title: "New Card", description: "Description" } }
    end

    assert_redirected_to card_path(Card.last)
    assert_equal "Card created successfully", flash[:notice]
  end

  test "rejects invalid card params" do
    sign_in users(:alice)

    assert_no_difference -> { Card.count } do
      post cards_path, params: { card: { title: "", description: "" } }
    end

    assert_response :unprocessable_entity
    assert_select "li", "Title can't be blank"
  end
end
```

### System Tests
```ruby
# ✅ Test critical user flows end-to-end
class CardManagementTest < ApplicationSystemTestCase
  test "user can create and close card" do
    sign_in users(:alice)
    visit board_path(boards(:main_board))

    click_on "Add Card"
    fill_in "Title", with: "New Feature"
    fill_in "Description", with: "Implement new feature"
    click_on "Create Card"

    assert_text "Card created successfully"
    assert_text "New Feature"

    click_on "Close Card"
    assert_text "Card closed"

    # Verify event was tracked
    assert_equal 1, Card.last.events.where(action: "card_closed").count
  end
end
```

### Event Verification
```ruby
# ✅ Test side effects through events
class CardTest < ActiveSupport::TestCase
  test "closing card tracks event" do
    card = cards(:open_card)

    assert_difference -> { Event.count } do
      card.close(user: users(:alice))
    end

    event = Event.last
    assert_equal "card_closed", event.action
    assert_equal users(:alice), event.creator
    assert_equal card, event.eventable
  end
end
```

### Fixtures Over Factories
```yaml
# ✅ Use YAML fixtures for reliable test data
# test/fixtures/cards.yml
open_card:
  title: "Open Card"
  description: "This card is open"
  board: main_board
  creator: alice

closed_card:
  title: "Closed Card"
  description: "This card is closed"
  board: main_board
  creator: alice
  closure: closed_card_closure

# ❌ Avoid factory objects
# FactoryBot.define do
#   factory :card do
#     title { "Card Title" }
#     description { "Card Description" }
#     association :board
#     association :creator
#   end
# end
```

## Naming Conventions

- **Test files**: `*_test.rb`
- **Test classes**: `ModelTest`, `ControllerTest`, `SystemTest`
- **Test methods**: `test "should do something when condition"`
- **Fixture files**: `*.yml` (plural table names)
- **Helper files**: `*_helper.rb`

## Best Practices

✅ **Test behavior, not implementation**
✅ **Use Rails fixtures for test data**
✅ **Test with real database state**
✅ **Verify events and side effects**
✅ **Keep tests fast and focused**
✅ **Test error cases and edge conditions**
✅ **Use descriptive test names**
✅ **Run tests frequently (pre-commit hooks)**

**Golden Rule**: Tests should be fast, reliable, and use real database state.
