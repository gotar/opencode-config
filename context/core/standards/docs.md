<!-- Context: standards/docs | Priority: critical | Version: 2.0 | Updated: 2025-01-21 -->

# Documentation Standards

## Quick Reference

**Golden Rule**: If users ask the same question twice, document it

**Document** (✅ DO):
- WHY decisions were made
- Complex algorithms/logic
- Public APIs, setup, common use cases

**Don't Document** (❌ DON'T):
- Obvious code (i++ doesn't need comment)
- What code does (should be self-explanatory)

**Principles**: Audience-focused, Show don't tell, Keep current

---

## Principles

**Audience-focused**: Write for users (what/how), developers (why/when), contributors (setup/conventions)
**Show, don't tell**: Code examples, real use cases, expected output
**Keep current**: Update with code changes, remove outdated info, mark deprecations

## README Structure

```markdown
# Project Name
Brief description (1-2 sentences)

## Features
- Key feature 1
- Key feature 2

## Installation
```bash
npm install package-name
```

## Quick Start
```javascript
const result = doSomething();
```

## Usage
[Detailed examples]

## API Reference
[If applicable]

## Contributing
[Link to CONTRIBUTING.md]

## License
[License type]
```

## Rails Method Documentation

```ruby
# Calculate total price including tax
#
# @param price [Float] Base price
# @param tax_rate [Float] Tax rate (0-1)
# @return [Float] Total with tax
#
# @example
#   calculate_total(100.0, 0.1) # => 110.0
def calculate_total(price, tax_rate)
  price * (1 + tax_rate)
end
```

## What to Document

### ✅ DO
- **WHY** decisions were made
- Complex algorithms/logic
- Non-obvious behavior
- Public APIs
- Setup/installation
- Common use cases
- Known limitations
- Workarounds (with explanation)

### ❌ DON'T
- Obvious code (i++ doesn't need comment)
- What code does (should be self-explanatory)
- Redundant information
- Outdated/incorrect info

## Comments

### Good
```ruby
# Calculate discount by tier (Bronze: 5%, Silver: 10%, Gold: 15%)
discount = calculate_discount_by_tier(customer.tier)

# HACK: API returns nil instead of [], normalize it
items = response.items || []

# TODO: Use Rails 8 features when minimum version allows
```

### Bad
```ruby
# Increment i
i += 1

# Get user
user = get_user
```

## Rails API Documentation

```markdown
### POST /api/users
Create a new user

**Request:**
```json
{ "user": { "name": "John", "email": "john@example.com" } }
```

**Response:**
```json
{ "id": "123", "name": "John", "email": "john@example.com" }
```

**Errors:**
- 422 - Validation failed (Rails standard)
- 409 - Email exists
```

## Best Practices

✅ Explain WHY Rails patterns are used
✅ Include working Rails code examples
✅ Show expected Rails behavior/output
✅ Cover Rails validation and error handling
✅ Use consistent Rails terminology
✅ Keep Rails documentation structure predictable
✅ Update when Rails code or patterns change

**Golden Rule**: If users ask the same question twice, document it.
