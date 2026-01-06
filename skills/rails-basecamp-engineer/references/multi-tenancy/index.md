# Multi-Tenancy Approaches

## Detecting Existing Multi-Tenancy Approach

Before choosing an approach, check what the project already uses:

**Indicators of Shared Database (tenant_id filtering):**
- `Current.account` usage in controllers/models
- `account_id` or `tenant_id` columns in migrations
- `default_scope { where(account: Current.account) }` in models
- URL routing like `/:account_slug/...` in routes.rb
- Account/Tenant model with `has_many` associations to domain models

**Indicators of Database Per Tenant:**
- `activerecord-tenanted` gem in Gemfile
- `Tenanted` module included in models
- Subdomain routing (`constraints subdomain: /.+/`)
- Multiple database configurations in `database.yml`
- `establish_connection` calls based on tenant context

**If unknown:** Use Explore agent to search for `Current.account`, `tenant_id`, or `activerecord-tenanted`.

---

Choose based on isolation requirements and operational complexity:

| Approach | Isolation | Complexity | Use Case |
|----------|-----------|------------|----------|
| **Shared Database** | Row-level (tenant_id) | Lower | Most SaaS apps |
| **Database Per Tenant** | Complete DB isolation | Higher | Enterprise, compliance |

## Decision Guide

**Choose `shared-database.md` when:**
- Building a typical SaaS application
- Tenants don't need complete data isolation
- Want simpler operations (single schema to maintain)
- Cost efficiency is important (shared resources)
- Following 37signals/Basecamp patterns

**Choose `database-per-tenant.md` when:**
- Enterprise customers require data isolation
- Compliance requirements (HIPAA, SOC2) mandate separation
- Need ability to restore/remove individual tenant data easily
- Tenants have vastly different data volumes
- Want per-tenant database customization

## Reference Files

- `shared-database.md` - Shared Database, Shared Schema pattern (Fizzy/Basecamp approach)
  - URL path-based routing (`/account-slug/...`)
  - `tenant_id` column filtering via `default_scope`
  - CurrentAttributes for tenant context
  - Middleware for slug extraction

- `database-per-tenant.md` - Database Per Tenant pattern
  - Subdomain-based routing (`tenant.app.com`)
  - `activerecord-tenanted` gem integration
  - Separate database connections per tenant
  - Schema migration considerations

## Quick Comparison

| Aspect | Shared Database | Database Per Tenant |
|--------|-----------------|---------------------|
| Data isolation | Row-level | Complete |
| Schema changes | Single migration | Per-tenant migrations |
| Tenant restore | Complex | Simple (restore DB) |
| Noisy neighbor risk | Possible | None |
| Cost | Lower | Higher |
| Ops complexity | Lower | Higher |
| Data leak risk | Higher (if WHERE missed) | Lower |
