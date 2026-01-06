# Essential Patterns - Rails Development Guidelines

## Quick Reference

**Core Philosophy**: Rails-First, Composition over Inheritance, Rich Domain Models

**Critical Patterns**: Concern Composition, Transaction Safety, Event Tracking, Strong Parameters

**ALWAYS**: Use concerns for composition, wrap critical operations in transactions, track significant actions, validate input strictly

**NEVER**: Deep inheritance, fat controllers, missing transactions, permissive parameters

**Rails-Optimized**: Following 37signals/Basecamp patterns and conventions

---

## Overview

This file provides essential Rails development patterns following 37signals/Basecamp conventions. For detailed standards, see:
- `standards/code.md` - Rails code patterns and conventions
- `standards/patterns.md` - Rails-specific patterns and anti-patterns
- `standards/tests.md` - Rails testing with fixtures and real database
- `standards/docs.md` - Documentation standards
- `standards/analysis.md` - Code analysis framework

---

## Core Philosophy

**Rails-First**: Prefer Rails conventions and native features over external gems
**Composition**: Build complex behavior through concern composition
**Domain-Driven**: Models are the heart of the application, rich with business logic
**Transactional**: Wrap critical operations in database transactions
**Event-Driven**: Track significant actions for audit trails and notifications

---

## Critical Patterns

### 1. Concern Composition

**ALWAYS** use concerns for behavior composition:
- Single responsibility per concern
- Composable through ActiveSupport::Concern
- Feature-based organization (not layer-based)
- Prefer over deep inheritance hierarchies

### 2. Rich Domain Models

**ALWAYS** keep business logic in models:
- Models are the heart of the application
- Transaction safety for critical operations
- Event tracking for audit trails
- Push logic from controllers to models

### 3. Transaction Safety

**ALWAYS** wrap critical operations in transactions:
- Use `transaction` blocks for multi-step operations
- Ensure data consistency and atomicity
- Automatic rollback on any failure
- Test transaction boundaries

### 4. Event Tracking

**ALWAYS** track significant actions:
- Create audit trails for user actions
- Enable activity feeds and notifications
- Use for debugging and analytics
- Store in dedicated events table

### 5. Strong Parameters

**ALWAYS** use strict input validation:
- Use `params.expect()` for required parameters
- Strict typing and structure validation
- Reject unexpected parameters
- Clear error messages for invalid input

### 6. Current Attributes

**ALWAYS** use request-scoped context:
- Thread-safe request context with Current
- No global variables or thread locals
- Automatic cleanup per request
- Access via Current.user, Current.account

---

## Code Structure Patterns

### Rails Directory Structure
```
app/
├── models/
│   ├── application_record.rb
│   ├── concerns/              # Cross-cutting concerns
│   │   ├── searchable.rb
│   │   └── eventable.rb
│   ├── card.rb
│   └── card/                   # Card-specific concerns
│       ├── assignable.rb
│       └── closeable.rb
├── controllers/
│   ├── application_controller.rb
│   ├── concerns/              # Controller concerns
│   │   ├── board_scoped.rb
│   │   └── card_scoped.rb
│   ├── cards_controller.rb
│   └── cards/
│       └── comments_controller.rb
└── jobs/
    └── notify_recipients_job.rb
```

### Concern Organization
- **Cross-cutting concerns**: Shared behavior across models/controllers
- **Feature-specific concerns**: Domain-specific behavior
- **Single responsibility**: Each concern has one clear purpose
- **Composable**: Mix and match concerns to build complex behavior

---

## Anti-Patterns to Avoid

**Rails Code Smells**:
- ❌ Fat controllers with business logic
- ❌ Deep inheritance hierarchies
- ❌ Complex callback chains
- ❌ Synchronous external API calls
- ❌ Missing transaction safety
- ❌ Permissive parameter validation
- ❌ God models with too many responsibilities

**Security Issues**:
- ❌ Hardcoded credentials or secrets
- ❌ Exposed sensitive data in logs
- ❌ Permissive parameter handling
- ❌ Missing CSRF protection
- ❌ XSS vulnerabilities in views

---

## Testing Patterns

**ALWAYS** write Rails tests:
- Model tests for business logic and behavior
- Controller tests for request/response handling
- System tests for critical user flows
- Use Rails fixtures over factories
- Test with real database state
- Verify events and side effects

**Test Structure**:
```ruby
class CardTest < ActiveSupport::TestCase
  test "closing a card creates closure record" do
    card = cards(:open_card)

    card.close(user: users(:alice))

    assert card.closed?
    assert_equal users(:alice), card.closure.user
  end

  test "cannot close already closed card" do
    card = cards(:closed_card)

    assert_no_changes -> { card.closure } do
      card.close(user: users(:alice))
    end
  end
end
```

---

## Documentation Patterns

**ALWAYS** document:
- Public APIs and interfaces
- Complex logic and algorithms
- Non-obvious decisions
- Usage examples

**Use clear, concise language**:
- Explain WHY, not just WHAT
- Include examples
- Keep it up to date
- Use consistent formatting

---

## Rails-Specific Implementations

These patterns are Rails-optimized. For Rails-specific implementations:

**Models**: See Rails Basecamp Engineer skill - `references/models.md`
**Controllers**: See Rails Basecamp Engineer skill - `references/controllers.md`
**Testing**: See Rails Basecamp Engineer skill - `references/testing.md`
**Hotwire/Turbo**: See Rails Basecamp Engineer skill - `references/hotwire.md`
**Authentication**: See Rails Basecamp Engineer skill - `authentication/*.md`

---

## Quick Checklist

Before committing Rails code, verify:
- ✅ Concern composition over inheritance
- ✅ Business logic in models, not controllers
- ✅ Transaction safety for critical operations
- ✅ Event tracking for significant actions
- ✅ Strong parameters for input validation
- ✅ Current attributes for request context
- ✅ Rails fixtures used for test data
- ✅ Tests written and passing
- ✅ No synchronous external API calls

---

## Additional Resources

For more detailed Rails guidelines, see:
- `standards/code.md` - Rails code patterns and conventions
- `standards/patterns.md` - Rails-specific patterns and anti-patterns
- `standards/tests.md` - Rails testing with fixtures and real database
- `standards/docs.md` - Documentation standards
- `standards/analysis.md` - Code analysis framework
- `workflows/review.md` - Code review process
- Rails Basecamp Engineer skill - Complete Rails development patterns
