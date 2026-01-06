<!-- Context: workflows/review | Priority: high | Version: 2.0 | Updated: 2025-01-21 -->

# Code Review Guidelines

## Quick Reference

**Golden Rule**: Review code as you'd want yours reviewed - thoroughly but kindly

**Checklist**: Functionality, Code Quality, Security, Testing, Performance, Maintainability

**Report Format**: Summary, Assessment, Issues (🔴🟡🔵), Positive Observations, Recommendations

**Principles**: Constructive, Thorough, Timely

---

## Principles

**Constructive**: Focus on code not person, explain WHY, suggest improvements, acknowledge good practices
**Thorough**: Check functionality not just style, consider edge cases, think maintainability, look for security
**Timely**: Review promptly, don't block unnecessarily, prioritize critical issues

## Review Checklist

### Functionality
- [ ] Does what it's supposed to do
- [ ] Edge cases handled
- [ ] Error cases handled
- [ ] No obvious bugs

### Code Quality
- [ ] Clear, descriptive Rails naming conventions
- [ ] Methods small and focused (< 20 lines)
- [ ] Concern composition over inheritance
- [ ] Follows Rails conventions and 37signals patterns
- [ ] DRY - no duplication, reusable concerns

### Security
- [ ] Strong parameters validation present
- [ ] No SQL injection vulnerabilities (Active Record safe)
- [ ] No XSS vulnerabilities (Rails view helpers safe)
- [ ] No hardcoded secrets (environment variables used)
- [ ] Sensitive data handled properly
- [ ] Auth/authorization appropriate (Pundit/CanCanCan)

### Testing
- [ ] Rails tests present (model, controller, system)
- [ ] Rails fixtures used over factories
- [ ] Event tracking and side effects tested
- [ ] Real database state tested
- [ ] Hotwire interactions tested in system tests

### Performance
- [ ] No N+1 queries (Active Record associations optimized)
- [ ] Efficient database queries and indexing
- [ ] Background jobs used for expensive operations
- [ ] Rails caching implemented where appropriate

### Maintainability
- [ ] Rails conventions followed (easy to understand)
- [ ] Complex business logic in models with concerns
- [ ] Follows Rails and 37signals conventions
- [ ] Easy to modify/extend with Rails patterns

## Review Report Format

```markdown
## Code Review: {Feature/PR Name}

**Summary:** {Brief overview}
**Assessment:** Approve / Needs Work / Requires Changes

---

### Issues Found

#### 🔴 Critical (Must Fix)
- **File:** `src/auth.js:42`
  **Issue:** Password stored in plain text
  **Fix:** Hash password before storing

#### 🟡 Warnings (Should Fix)
- **File:** `src/user.js:15`
  **Issue:** No input validation
  **Fix:** Validate email format

#### 🔵 Suggestions (Nice to Have)
- **File:** `src/utils.js:28`
  **Issue:** Could be more concise
  **Fix:** Use array methods instead of loop

---

### Positive Observations
- ✅ Good test coverage (95%)
- ✅ Clear function names
- ✅ Proper error handling

---

### Recommendations
{Next steps, improvements, follow-up items}
```

## Common Issues

### Security
🔴 Hardcoded credentials or secrets
🔴 SQL injection vulnerabilities (use Active Record)
🔴 Missing strong parameters validation
🔴 Exposed sensitive data in logs

### Code Quality
🟡 Large methods (>20 lines)
🟡 Deep inheritance hierarchies
🟡 Missing concern composition
🟡 Non-standard Rails naming

### Testing
🟡 Missing Rails tests (model/controller/system)
🟡 Using factories instead of Rails fixtures
🟡 Transaction rollback testing (not real database)
🟡 Tests not verifying events and side effects

## Best Practices

✅ Review within 24 hours
✅ Provide specific, actionable feedback
✅ Explain WHY, not just WHAT
✅ Suggest alternatives
✅ Acknowledge good work
✅ Use severity levels (Critical/Warning/Suggestion)
✅ Test the code if possible
✅ Check for security issues first

**Golden Rule**: Review code as you'd want yours reviewed - thoroughly but kindly.
