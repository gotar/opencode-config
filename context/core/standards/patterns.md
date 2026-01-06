<!-- Context: standards/patterns | Priority: high | Version: 2.0 | Updated: 2025-01-21 -->

# Essential Patterns - Core Knowledge Base

## Quick Reference

**Critical Patterns**: Rails-First, Composition over Inheritance, Domain-Driven Design

**ALWAYS**: Use concerns for composition, rich domain models, transaction safety, event tracking

**NEVER**: Deep inheritance, fat controllers, missing transactions, synchronous external calls

**Rails-Optimized**: Following 37signals/Basecamp patterns and conventions

---

These patterns are optimized for Ruby on Rails development following 37signals patterns. General language-agnostic patterns are included where they apply to Rails development.

## Rails-Specific Patterns

### Concern Composition Pattern
**ALWAYS** use concerns for behavior composition:

- Single responsibility per concern
- Composable through ActiveSupport::Concern
- Feature-based organization (not layer-based)
- Mix and match to build complex behavior
- Prefer over deep inheritance hierarchies

### Rich Domain Models Pattern
**ALWAYS** keep business logic in models:

- Models are the heart of the application
- Transaction safety for critical operations
- Event tracking for audit trails
- Push logic from controllers to models
- Use concerns to organize model behavior

### Transaction Safety Pattern
**ALWAYS** wrap critical operations in transactions:

- Use `transaction` blocks for multi-step operations
- Ensure data consistency
- Automatic rollback on failures
- Test transaction boundaries

### Event Tracking Pattern
**ALWAYS** track significant actions:

- Create audit trails for user actions
- Enable activity feeds and notifications
- Use for debugging and analytics
- Store in dedicated events table

### Current Attributes Pattern
**ALWAYS** use request-scoped context:

- Thread-safe request context with Current
- No global variables or thread locals
- Automatic cleanup per request
- Access via Current.user, Current.account

## Error Handling Pattern

**ALWAYS** handle errors gracefully:

- Catch specific errors, not generic ones
- Log errors with context
- Return meaningful error messages
- Don't expose internal implementation details
- Use Rails error handling (rescue_from, ActiveRecord validations)

## Strong Parameters Pattern

**ALWAYS** use strict input validation:

- Use `params.expect()` for required parameters
- Strict typing and structure validation
- Reject unexpected parameters
- Clear error messages for invalid input
- Controller-level validation with strong parameters

## Validation Pattern

**ALWAYS** validate input data:

- Check for null/nil/None values
- Validate data types and ranges
- Use ActiveRecord validations in models
- Controller-level validation with strong parameters
- Return clear validation error messages

## Logging Pattern

**USE** consistent logging levels:

- **Debug**: Detailed information for debugging (development only)
- **Info**: Important events and milestones
- **Warning**: Potential issues that don't stop execution
- **Error**: Failures and exceptions

## Security Pattern

**NEVER** expose sensitive information:

- Don't log passwords, tokens, or API keys
- Don't expose internal error details to users
- Use strong parameters for input validation
- Environment variables for all secrets
- Follow principle of least privilege
- Use Rails security features (CSRF protection, XSS prevention)

## File System Safety Pattern

**ALWAYS** validate file paths:

- Prevent path traversal attacks
- Check file permissions before operations
- Use absolute paths when possible
- Handle file not found errors gracefully
- Close file handles properly

## Configuration Pattern

**ALWAYS** use environment variables for configuration:

- Never hardcode secrets or credentials
- Provide sensible defaults
- Validate required configuration on startup
- Document all configuration options
- Use different configs for dev/staging/production

## Testing Pattern

**ALWAYS** write testable Rails code:

- Use Rails fixtures over factories
- Test with real database state
- Focus on behavior, not implementation
- Test events and side effects
- Use system tests for critical user flows
- Model tests for business logic, controller tests for request/response

## Documentation Pattern

**DOCUMENT** complex logic and public APIs:

- Explain the "why", not just the "what"
- Document function parameters and return values
- Include usage examples
- Keep documentation up to date with code
- Use language-specific documentation tools

## Performance Pattern

**AVOID** unnecessary operations:

- Don't repeat expensive calculations
- Cache results when appropriate
- Use efficient data structures
- Profile before optimizing
- Consider time and space complexity

## Code Organization Pattern

**KEEP** Rails code modular and focused:

- Single Responsibility Principle per class/concern
- Feature-based organization (not MVC layers)
- Concerns for cross-cutting behavior
- Rich domain models with business logic
- Minimal controllers pushing logic to models
- Keep methods small and focused (< 20 lines ideally)

## Dependency Management

**MANAGE** dependencies carefully:

- Pin dependency versions for reproducibility
- Regularly update dependencies for security
- Minimize number of dependencies
- Audit dependencies for security vulnerabilities
- Document why each dependency is needed

## Version Control

**FOLLOW** git best practices:

- Write clear, descriptive commit messages
- Make atomic commits (one logical change per commit)
- Use feature branches for development
- Review code before merging
- Keep main/master branch stable

## Code Review Checklist

**REVIEW** for Rails-specific issues:

- Concern composition over inheritance used
- Business logic in models, not controllers
- Transaction safety for critical operations
- Event tracking for significant actions
- Strong parameters for input validation
- Current attributes for request context
- Rails fixtures used for test data
- Turbo Stream responses for real-time UI
- No synchronous external API calls
- Proper error handling with Rails patterns
