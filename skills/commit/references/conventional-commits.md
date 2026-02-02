# Conventional Commits Guide

Complete guide to writing conventional commit messages that are readable, searchable, and enable automation.

---

## Format

```
<type>[(optional scope)]: <description>

[optional body]

[optional footer(s)]
```

### With Emoji (Recommended)

```
<emoji> <type>[(scope)]: <description>
```

---

## Types

| Type | Emoji | Description | Example |
|------|-------|-------------|---------|
| **feat** | ✨ | New feature | `✨ feat: Add user authentication system` |
| **fix** | 🐛 | Bug fix | `🐛 fix: Resolve memory leak in data processing` |
| **docs** | 📚 | Documentation | `📚 docs: Update API reference for v2` |
| **style** | 💎 | Code style (formatting, semicolons, etc.) | `💎 style: Format code with black` |
| **refactor** | ♻️ | Code refactoring | `♻️ refactor: Extract auth logic to service` |
| **perf** | 🚀 | Performance improvements | `🚀 perf: Optimize database queries` |
| **test** | 🧪 | Adding or fixing tests | `🧪 test: Add unit tests for User model` |
| **build** | 🛠️ | Build system or dependencies | `🛠️ build: Update webpack to v5` |
| **ci** | ⚙️ | CI/CD changes | `⚙️ ci: Add GitHub Actions workflow` |
| **chore** | 🔧 | Maintenance tasks | `🔧 chore: Update dependencies` |
| **revert** | ⏪️ | Revert previous commit | `⏪️ revert: Revert "feat: Add dark mode"` |
| **wip** | 🚧 | Work in progress | `🚧 wip: Implementing payment gateway` |
| **debug** | 🔍 | Debugging/diagnostics | `🔍 debug: Add logging to auth flow` |

---

## Scope (Optional)

Scope indicates the part of codebase affected:

```
✨ feat(auth): Add OAuth2 integration
🐛 fix(api): Handle null response from server
📚 docs(readme): Update installation instructions
```

**Common Scopes:**
- `api` - API endpoints
- `ui` - User interface
- `auth` - Authentication
- `db` - Database
- `config` - Configuration
- `deps` - Dependencies
- `tests` - Test suite

---

## Description Guidelines

### Imperative Mood
Write as if giving a command:
- ✅ "Add feature"
- ✅ "Fix bug"  
- ✅ "Update docs"
- ❌ "Added feature"
- ❌ "Fixing bug"
- ❌ "Updated docs"

### Concise but Descriptive
- ✅ "feat: Add password reset functionality"
- ✅ "fix: Handle nil pointer in user service"
- ❌ "feat: Changes" (too vague)
- ❌ "fix: Fixed stuff" (too vague)

### No Period at End
- ✅ "feat: Add new button"
- ❌ "feat: Add new button."

---

## Body (Optional)

Use body for additional context:

```
✨ feat: Add user authentication system

- Implement JWT token validation
- Add login/logout endpoints  
- Create auth middleware for protected routes
- Add rate limiting to prevent brute force
```

**When to use body:**
- Complex changes need explanation
- Breaking changes need migration notes
- Multiple distinct changes in one commit
- Context helps future developers

---

## Footer (Optional)

### Referencing Issues
```
🐛 fix: Resolve memory leak in data processing

The batch processor wasn't closing database connections
properly, causing connections to accumulate over time.

Fixes #456
Closes #123
Relates to #789
```

### Breaking Changes
```
⚠️ feat(api)!: Change authentication response format

BREAKING CHANGE: Auth endpoints now return JSON instead of
plain text. Update client code accordingly.

Migration guide: docs/migrations/v2-auth.md
```

### Co-authors
```
✨ feat: Add collaborative editing

Co-authored-by: Alice <alice@example.com>
Co-authored-by: Bob <bob@example.com>
```

---

## Real-World Examples

### Feature Commit
```
✨ feat(auth): Implement GitHub OAuth login

- Add OAuth controller with callback handler
- Create User model with GitHub ID field
- Add login/logout routes
- Store sessions securely

Closes #42
```

### Fix Commit
```
🐛 fix(api): Handle missing Authorization header

Previously returned 500 error, now returns 401 Unauthorized
with helpful error message.

Fixes #156
```

### Refactor Commit
```
♻️ refactor(db): Extract database connection pool

Consolidate connection logic that was duplicated across
3 different models. Now managed by DatabasePool singleton.

No functional changes, just code organization.
```

### Documentation Commit
```
📚 docs: Add deployment guide

- Document Kamal deployment process
- Add environment variable reference
- Include troubleshooting section

Relates to #200
```

---

## Commit Templates by Scenario

### Adding a Feature
```
✨ feat(scope): Brief description

- Implementation detail 1
- Implementation detail 2

Closes #issue-number
```

### Fixing a Bug
```
🐛 fix(scope): Brief description

Root cause: explain what caused the bug
Solution: explain how it was fixed

Fixes #issue-number
```

### Code Review Changes
```
💎 style(scope): Address code review feedback

- Rename variable for clarity
- Extract method for readability
- Add missing type annotations
```

### Emergency Fix
```
🐛 fix(scope): Critical hotfix for production issue

Problem: Brief description of production issue
Impact: Who/what was affected
Solution: Quick fix applied

Note: Proper fix will follow in #issue-number
```

---

## Common Mistakes to Avoid

### ❌ Vague Messages
```
❌ fix: Fix bug
❌ feat: Add stuff
❌ docs: Update docs

✅ fix: Fix null pointer in user authentication
✅ feat: Add dark mode toggle to settings
✅ docs: Document new API rate limiting
```

### ❌ Wrong Type
```
❌ feat: Fix typo in README  (should be docs:)
❌ fix: Add new feature      (should be feat:)
❌ docs: Refactor auth code  (should be refactor:)
```

### ❌ Mixed Concerns
```
❌ feat(auth): Add OAuth and fix CSS bug

✨ feat(auth): Add OAuth integration
🐛 fix(css): Resolve layout issue on mobile
```

### ❌ Past Tense
```
❌ feat: Added new feature
❌ fix: Fixed memory leak

✅ feat: Add new feature
✅ fix: Fix memory leak
```

---

## Quick Reference Card

```
TYPE     EMOJI   USE FOR
─────────────────────────────────────
feat     ✨      New features
test     🧪      Tests only
fix      🐛      Bug fixes
perf     🚀      Performance
docs     📚      Documentation
build    🛠️      Build/deps
style    💎      Code style
ci       ⚙️      CI/CD changes
refactor ♻️      Refactoring
chore    🔧      Maintenance
revert   ⏪️      Reverting
wip      🚧      Work in progress
debug    🔍      Debugging

FORMAT: <emoji> <type>[(scope)]: <description>

NOTES:
• Use imperative mood
• No period at end
• Keep it concise
• Add body for complex changes
• Reference issues in footer
```

---

## Git Aliases (Optional)

Add to `~/.gitconfig`:

```ini
[alias]
    feat = "!f() { git commit -m \"✨ feat: $1\"; }; f"
    fix = "!f() { git commit -m \"🐛 fix: $1\"; }; f"
    docs = "!f() { git commit -m \"📚 docs: $1\"; }; f"
    style = "!f() { git commit -m \"💎 style: $1\"; }; f"
    test = "!f() { git commit -m \"🧪 test: $1\"; }; f"
    refactor = "!f() { git commit -m \"♻️ refactor: $1\"; }; f"
```

Usage:
```bash
git feat "Add user profile page"
git fix "Handle edge case in validator"
git docs "Update README"
```

---

## Further Reading

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Git Commit Message Best Practices](https://chris.beams.io/posts/git-commit/)
- [Semantic Versioning](https://semver.org/)
