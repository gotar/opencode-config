# OpenCode Agent System Project Context

## Technology Stack

**Primary Language:** Ruby (Rails development focus)
**Runtime:** Ruby 3.2+ with Rails 7+
**Package Manager:** Bundler (RubyGems)
**Build Tools:** Rails generators, Rake tasks
**Testing:** Rails testing framework with fixtures
**Linting:** RuboCop (Ruby style guide)
**Database:** PostgreSQL with Active Record

## Project Structure

```
.opencode/
├── agent/           # AI agents for specific tasks
│   ├── subagents/   # Specialized subagents
│   └── *.md         # Primary agents
├── command/         # Slash commands
├── context/         # Knowledge base for agents (Rails-optimized)
│   ├── core/standards/  # Rails development standards
│   ├── core/workflows/  # Rails development workflows
│   └── project/         # Rails project context
└── plugin/          # Extensions and integrations

tasks/               # Task management files
```

## Rails Development Focus

**Core Philosophy**: Rails-First, Composition over Inheritance, Rich Domain Models
**Primary Patterns**: Concern composition, transaction safety, event tracking
**Testing Approach**: Rails fixtures over factories, real database testing
**Architecture**: Hotwire/Turbo for real-time updates, Solid Queue for background jobs

## Core Patterns

### Rails Development Patterns
- **Concern Composition**: Build behavior through ActiveSupport::Concern mixins
- **Rich Domain Models**: Business logic in models, not controllers
- **Transaction Safety**: Wrap critical operations in database transactions
- **Event Tracking**: Audit trails for significant user actions
- **Strong Parameters**: Strict input validation with `params.expect()`
- **Current Attributes**: Request-scoped context with Current.user/account

### Agent Structure Pattern
```markdown
---
description: "What this agent does"
mode: primary|subagent
tools: [read, edit, bash, etc.]
permissions: [security restrictions]
rails_focus: true  # Rails-optimized agent
---

# Agent Name

[Direct instructions for Rails development behavior]

**EXECUTE** this [process type] for every [Rails task type]:

**1. [ACTION]** the [Rails subject]:
- [Rails-specific instruction 1]
- [Rails-specific instruction 2]

**RULES:**
- **ALWAYS** follow Rails conventions and 37signals patterns
- **NEVER** use external gems when Rails features suffice
```

### Command Structure Pattern
```markdown
---
name: command-name
agent: target-agent
rails_optimized: true
---

You are [doing specific Rails development task].

**Request:** $ARGUMENTS

**Context Loaded:**
@/home/gotar/.config/opencode/context/core/essential-patterns.md
@/home/gotar/.config/opencode/skills/rails-basecamp-engineer/SKILL.md
@[additional Rails context files]

Execute [Rails task] now.
```

### Context Loading Rules
- Commands load Rails context immediately using @ references
- Include Rails Basecamp Engineer skill references for Rails tasks
- Agents detect Rails patterns and load appropriate references
- Maximum 4 context files per command (250-450 lines total)
- Keep context files focused (50-150 lines each)
- Prioritize Rails-specific patterns over generic patterns

## Security Guidelines

- Agents have restricted permissions by default
- Sensitive operations require explicit approval
- Rails security: Strong parameters, CSRF protection, XSS prevention
- No direct database modifications without transaction safety
- Build commands limited to safe Rails operations
- Environment variables for all secrets and configuration

## Rails Development Workflow

1. **Planning:** Create detailed task plans for Rails features
2. **Implementation:** Follow Rails conventions, use generators, concerns
3. **Review:** Code review against Rails patterns and Basecamp conventions
4. **Testing:** Rails testing with fixtures, verify event tracking
5. **Documentation:** Update Rails-specific docs and context files

## Quality Gates

- Rails conventions followed (RuboCop passes)
- Code review completed against Rails patterns
- Rails tests pass (models, controllers, system tests)
- Database migrations safe and tested
- Rails Basecamp Engineer patterns applied
- Documentation updated with Rails examples