---
name: plan
description: Plan implementation of a Rails feature with multi-tenant architecture and DaisyUI
---

You are planning a new feature for a Rails application with multi-tenant architecture.

ARCHITECTURE CONTEXT:
- This project uses TWO databases:
  * Primary database: Non-tenanted, for global/shared data
  * Account database: Tenant-based, for customer-specific data
- Always verify which database a model should use before planning
- Models in the account database must be properly scoped to the current tenant

ARCHITECTURE PATTERNS:
- **Rails-First**: Prefer Rails conventions over external gems
- **Concern Composition**: Build behavior through ActiveSupport::Concern mixins
- **Rich Domain Models**: Business logic in models with event tracking
- **Transaction Safety**: Wrap critical operations in database transactions
- **Current Attributes**: Request-scoped context with Current.user/account
- **Strong Parameters**: Strict input validation in controllers
- **Hotwire Integration**: Real-time UI with Turbo Frames/Streams

TEST-DRIVEN DEVELOPMENT (TDD):
- **MANDATORY**: All implementation must follow TDD approach
- Write unit tests BEFORE implementation:
  * Model tests: validations, associations, scopes, instance methods, class methods
  * Controller tests: request specs for each action
- Plan should include test specifications for:
  * Each model with expected behavior
  * Each controller action with success/failure cases
  * Edge cases and error handling
- Use RSpec or Minitest based on project conventions

STYLING & COMPONENTS:
- **CRITICAL**: Use DaisyUI components throughout the implementation
- Keep all styles aligned with existing DaisyUI patterns
- Before planning, CHECK DOCUMENTATION:
  * Use context7 for DaisyUI component reference
  * Use context7 for Rails documentation
  * Use tidwave MCPs for additional technical documentation
- Prefer DaisyUI's semantic component classes over custom Tailwind

PLANNING PROCESS:
1. First, analyze the current project structure:
   - Examine relevant controllers, models, and views
   - Check existing patterns for similar features
   - Review the database schema (both primary and account)
   - **Identify DaisyUI components already in use**
   - Review existing Stimulus controllers and patterns
   - Check existing concerns and model patterns
   - Identify testing framework (RSpec/Minitest)

2. Consult documentation BEFORE asking questions:
   - Check context7 for DaisyUI components relevant to the feature
   - Check context7 for Rails best practices
   - Check tidwave MCPs for technical references

3. Ask up to 10 clarifying questions in groups of 2-3:
   - Database & Models: Which database? Associations? Validations? Business logic?
   - UI/UX: Which DaisyUI components? User interactions? View structure?
   - Integration: Where does this fit? Lazy loading? Turbo frames?
   - Technical: Stimulus controllers? Background jobs? Permissions?
   - Testing: Edge cases? Authorization scenarios?
   - Wait for answers between question groups

4. Provide a comprehensive implementation plan including:
   - **TDD Test Plan**: Specify tests to write for each model and controller
   - Database choice justification (primary vs account)
   - Model structure with correct database configuration
   - Business logic placement (models, concerns, POROs)
   - Controller actions and routing (thin controllers)
   - **DaisyUI component specifications for each UI element**
   - View structure (Turbo frames, Stimulus controllers)
   - Styling approach using DaisyUI (matching existing patterns)
   - Testing strategy with specific test cases
   - Migration steps
   - Integration points with existing code

IMPLEMENTATION ORDER:
1. Write failing tests (Red)
2. Implement minimal code to pass tests (Green)
3. Refactor (extract concerns, improve design)
4. Repeat for each feature increment

RAILS SPECIFICS TO CONSIDER:
- Hotwire/Turbo for dynamic updates
- Stimulus controllers for JavaScript behavior
- Proper tenant scoping for account database models
- DRY principles and Rails conventions
- Database connection configuration for multi-tenancy
- ActiveModel for POROs when needed

Feature to plan: {FEATURE_DESCRIPTION}
