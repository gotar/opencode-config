<!-- Context: workflows/task-breakdown | Priority: high | Version: 2.0 | Updated: 2025-01-21 -->

# Task Breakdown Guidelines

## Quick Reference

**When to Use**: 4+ files, >60 min effort, complex dependencies, multi-step coordination

**Process**: Scope → Phases → Small Tasks (1-2h) → Dependencies → Estimates

**Template Sections**: Overview, Prerequisites, Tasks (by Phase), Testing Strategy, Total Estimate, Notes

**Best Practices**: Keep tasks small (1-2h), make dependencies clear, include verification, be realistic with estimates

---

## Purpose
Framework for breaking down complex tasks into manageable, sequential subtasks.

## When to Use
Reference this when:
- Task involves 4+ files
- Estimated effort >60 minutes
- Complex dependencies exist
- Multi-step coordination needed
- User requests task breakdown

## Breakdown Process

### 1. Understand the Full Scope
- What's the complete requirement?
- What are all the components needed?
- What's the end goal?
- What are the constraints?

### 2. Identify Major Phases
- What are the logical groupings?
- What must happen first?
- What can happen in parallel?
- What depends on what?

### 3. Break Into Small Tasks
- Each task should be 1-2 hours max
- Clear, actionable items
- Independently completable
- Easy to verify completion

### 4. Define Dependencies
- What must be done first?
- What can be done in parallel?
- What blocks what?
- What's the critical path?

### 5. Estimate Effort
- Realistic time estimates
- Include testing time
- Account for unknowns
- Add buffer for complexity

## Breakdown Template

```markdown
# Task Breakdown: {Task Name}

## Overview
{1-2 sentence description of what we're building}

## Prerequisites
- [ ] {Prerequisite 1}
- [ ] {Prerequisite 2}

## Tasks

### Phase 1: {Phase Name}
**Goal:** {What this phase accomplishes}

- [ ] **Task 1.1:** {Description}
  - **Files:** {files to create/modify}
  - **Estimate:** {time estimate}
  - **Dependencies:** {none / task X}
  - **Verification:** {how to verify it's done}

- [ ] **Task 1.2:** {Description}
  - **Files:** {files to create/modify}
  - **Estimate:** {time estimate}
  - **Dependencies:** {task 1.1}
  - **Verification:** {how to verify it's done}

### Phase 2: {Phase Name}
**Goal:** {What this phase accomplishes}

- [ ] **Task 2.1:** {Description}
  - **Files:** {files to create/modify}
  - **Estimate:** {time estimate}
  - **Dependencies:** {phase 1 complete}
  - **Verification:** {how to verify it's done}

## Testing Strategy
- [ ] Unit tests for {component}
- [ ] Integration tests for {flow}
- [ ] Manual testing: {scenarios}

## Total Estimate
**Time:** {X} hours
**Complexity:** {Low / Medium / High}

## Notes
{Any important context, decisions, or considerations}
```

## Example Breakdown

### Rails Example: Card Management Feature

```markdown
# Rails Task Breakdown: Implement Card Management with Hotwire

## Overview
Build card creation, editing, and real-time updates using Rails and Hotwire.

## Prerequisites
- [ ] Rails application set up with PostgreSQL
- [ ] Board model exists for card relationships
- [ ] Hotwire (Turbo/Stimulus) configured
- [ ] Authentication system in place

## Tasks

### Phase 1: Database & Models
**Goal:** Create card data structure and rich domain model

- [ ] **Task 1.1:** Design card schema and relationships
  - **Rails Command:** `rails generate migration CreateCards`
  - **Files:** `db/migrate/20241215_create_cards.rb`
  - **Estimate:** 45 min
  - **Dependencies:** none
  - **Verification:** Migration creates cards table with proper indexes

- [ ] **Task 1.2:** Generate Card model with concerns
  - **Rails Command:** `rails generate model Card`
  - **Files:** `app/models/card.rb`, `app/models/concerns/`
  - **Estimate:** 1 hour
  - **Dependencies:** Task 1.1
  - **Verification:** Card model validates and has basic associations

- [ ] **Task 1.3:** Implement Assignable and Closeable concerns
  - **Files:** `app/models/concerns/assignable.rb`, `app/models/concerns/closeable.rb`
  - **Estimate:** 1.5 hours
  - **Dependencies:** Task 1.2
  - **Verification:** Cards can be assigned and closed with event tracking

### Phase 2: Controllers & Routes
**Goal:** RESTful card controller with strong parameters and Turbo

- [ ] **Task 2.1:** Generate cards controller with CRUD actions
  - **Rails Command:** `rails generate controller Cards`
  - **Files:** `app/controllers/cards_controller.rb`, `config/routes.rb`
  - **Estimate:** 1 hour
  - **Dependencies:** Phase 1 complete
  - **Verification:** Basic CRUD routes work with proper responses

- [ ] **Task 2.2:** Add strong parameters and scoping concerns
  - **Files:** `app/controllers/concerns/card_scoped.rb`
  - **Estimate:** 45 min
  - **Dependencies:** Task 2.1
  - **Verification:** Controller uses strong params and proper scoping

- [ ] **Task 2.3:** Implement Turbo Stream responses
  - **Files:** `app/controllers/cards_controller.rb`, `app/views/cards/`
  - **Estimate:** 1 hour
  - **Dependencies:** Task 2.2
  - **Verification:** Actions return Turbo Stream responses for real-time updates

### Phase 3: Views & Hotwire
**Goal:** Responsive UI with real-time updates

- [ ] **Task 3.1:** Create card form with Hotwire
  - **Files:** `app/views/cards/_form.html.erb`, `app/views/cards/new.html.erb`
  - **Estimate:** 1 hour
  - **Dependencies:** Phase 2 complete
  - **Verification:** Form submits via Turbo and updates UI

- [ ] **Task 3.2:** Implement card show and edit views
  - **Files:** `app/views/cards/show.html.erb`, `app/views/cards/edit.html.erb`
  - **Estimate:** 45 min
  - **Dependencies:** Task 3.1
  - **Verification:** Cards display and can be edited in real-time

- [ ] **Task 3.3:** Add Stimulus controllers for interactivity
  - **Files:** `app/javascript/controllers/card_controller.js`
  - **Estimate:** 1 hour
  - **Dependencies:** Task 3.2
  - **Verification:** Enhanced UI interactions work (drag-drop, inline editing)

### Phase 4: Testing & Validation
**Goal:** Comprehensive test coverage following Rails patterns

- [ ] **Task 4.1:** Write model tests for business logic
  - **Rails Command:** `rails generate test_unit:model Card`
  - **Files:** `test/models/card_test.rb`
  - **Estimate:** 1.5 hours
  - **Dependencies:** Phase 1 complete
  - **Verification:** Model tests pass, edge cases covered

- [ ] **Task 4.2:** Write controller tests for request/response
  - **Rails Command:** `rails generate test_unit:controller Cards`
  - **Files:** `test/controllers/cards_controller_test.rb`
  - **Estimate:** 1 hour
  - **Dependencies:** Phase 2 complete
  - **Verification:** Controller tests pass for all actions

- [ ] **Task 4.3:** Write system tests for end-to-end flows
  - **Rails Command:** `rails generate test_unit:system Cards`
  - **Files:** `test/system/cards_test.rb`
  - **Estimate:** 1.5 hours
  - **Dependencies:** Phase 3 complete
  - **Verification:** System tests pass, real-time updates work

## Testing Strategy
- [ ] Model tests: Business logic, validations, event tracking
- [ ] Controller tests: Request/response, authentication, strong params
- [ ] System tests: End-to-end card management flows
- [ ] Manual testing: Real-time updates, form interactions

## Total Estimate
**Time:** 12 hours
**Complexity:** Medium-High

## Notes
- Use Rails fixtures over factories for test data
- Implement event tracking for all card actions
- Ensure transaction safety for critical operations
- Follow 37signals patterns: composition over inheritance
- Test with real database state, not mocks
```

### General Example: User Authentication System

```markdown
# Task Breakdown: User Authentication System

## Overview
Build authentication system with login, registration, and password reset.

## Prerequisites
- [ ] Database schema designed
- [ ] Email service configured

## Tasks

### Phase 1: Core Authentication
**Goal:** Basic login/logout functionality

- [ ] **Task 1.1:** Create user model and database schema
  - **Files:** `models/user.js`, `migrations/001_users.sql`
  - **Estimate:** 1 hour
  - **Dependencies:** none
  - **Verification:** Can create user in database

- [ ] **Task 1.2:** Implement password hashing
  - **Files:** `utils/password.js`
  - **Estimate:** 30 min
  - **Dependencies:** Task 1.1
  - **Verification:** Passwords are hashed, not plain text

- [ ] **Task 1.3:** Create login endpoint
  - **Files:** `routes/auth.js`, `controllers/auth.js`
  - **Estimate:** 1.5 hours
  - **Dependencies:** Task 1.1, 1.2
  - **Verification:** Can login with valid credentials

### Phase 2: Registration
**Goal:** New user registration

- [ ] **Task 2.1:** Create registration endpoint
  - **Files:** `routes/auth.js`, `controllers/auth.js`
  - **Estimate:** 1 hour
  - **Dependencies:** Phase 1 complete
  - **Verification:** Can create new user account

- [ ] **Task 2.2:** Add email validation
  - **Files:** `utils/validation.js`
  - **Estimate:** 30 min
  - **Dependencies:** Task 2.1
  - **Verification:** Invalid emails rejected

### Phase 3: Password Reset
**Goal:** Users can reset forgotten passwords

- [ ] **Task 3.1:** Generate reset tokens
  - **Files:** `utils/tokens.js`
  - **Estimate:** 1 hour
  - **Dependencies:** Phase 1 complete
  - **Verification:** Tokens generated and validated

- [ ] **Task 3.2:** Create reset endpoints
  - **Files:** `routes/auth.js`, `controllers/auth.js`
  - **Estimate:** 1.5 hours
  - **Dependencies:** Task 3.1
  - **Verification:** Can request and complete password reset

- [ ] **Task 3.3:** Send reset emails
  - **Files:** `services/email.js`
  - **Estimate:** 1 hour
  - **Dependencies:** Task 3.2
  - **Verification:** Reset emails sent successfully

## Testing Strategy
- [ ] Unit tests for password hashing
- [ ] Unit tests for token generation
- [ ] Integration tests for login flow
- [ ] Integration tests for registration flow
- [ ] Integration tests for password reset flow
- [ ] Manual testing: Complete user journey

## Total Estimate
**Time:** 8.5 hours
**Complexity:** Medium

## Notes
- Use bcrypt for password hashing (industry standard)
- Reset tokens expire after 1 hour
- Rate limit password reset requests
- Email service must be configured before Phase 3
```

## Best Practices

### Keep Tasks Small
- 1-2 hours maximum per task
- If larger, break it down further
- Each task should be completable in one sitting

### Make Dependencies Clear
- Explicitly state what must be done first
- Identify parallel work opportunities
- Note blocking dependencies

### Include Verification
- How do you know the task is done?
- What should work when complete?
- How can it be tested?

### Be Realistic with Estimates
- Include time for testing
- Account for unknowns
- Add buffer for complexity
- Better to overestimate than underestimate

### Group Related Work
- Organize by feature or component
- Keep related tasks together
- Make phases logical and cohesive

## Common Patterns

### Rails Database-First Pattern
1. Design schema following Rails conventions
2. Create migrations with proper indexes
3. Generate models with associations
4. Implement concerns for business logic
5. Add event tracking and validations
6. Write comprehensive Rails tests (model, controller, system)

### Rails Feature-First Pattern
1. Define requirements and user stories
2. Design Hotwire UI and interactions
3. Implement rich domain models with concerns
4. Create controllers with strong parameters
5. Add Turbo Stream responses for real-time updates
6. Write Rails tests and verify end-to-end flows

### Rails Refactoring Pattern
1. Add Rails tests for existing behavior
2. Extract concerns for reusable logic
3. Implement event tracking for significant actions
4. Add transaction safety where needed
5. Update to follow Rails Basecamp Engineer patterns
6. Verify tests pass and update documentation

### Hotwire Implementation Pattern
1. Design UI with Turbo Frames for isolation
2. Implement server-side controller actions
3. Add Turbo Stream responses for updates
4. Create Stimulus controllers for client-side logic
5. Test real-time interactions with system tests
6. Optimize for performance and user experience

## Quick Reference

**Good breakdown:**
- Small, focused tasks (1-2 hours)
- Clear dependencies
- Realistic estimates
- Verification criteria
- Logical phases

**Rails Breakdown checklist:**
- [ ] Rails components identified (models, controllers, views, tests)
- [ ] Database design follows Rails conventions
- [ ] Concerns planned for reusable behavior
- [ ] Hotwire/Turbo integration considered
- [ ] Event tracking included for significant actions
- [ ] Transaction safety planned for critical operations
- [ ] Strong parameters for input validation
- [ ] Rails testing strategy (fixtures, real database)
- [ ] Verification includes real-time UI updates

**General Breakdown checklist:**
- [ ] All requirements captured
- [ ] Tasks are small and focused
- [ ] Dependencies identified
- [ ] Estimates are realistic
- [ ] Testing included
- [ ] Verification criteria clear
