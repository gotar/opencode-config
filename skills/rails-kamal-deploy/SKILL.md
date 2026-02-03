# Rails Kamal Deployment Skill

Specialized knowledge for deploying Rails applications using Kamal (Rails 8's built-in deployment tool), with focus on SQLite databases and production deployments.

## When to Use This Skill

Use this skill when:
- Deploying Rails applications with Kamal
- Managing SQLite databases in production with Kamal
- Configuring Kamal for Rails 8 apps
- Troubleshooting deployment issues
- Setting up volumes for persistent data
- Running database migrations during deployment

## Core Concepts

### Kamal Overview

Kamal is Rails 8's official deployment tool that uses Docker and SSH to deploy apps to servers. It replaces traditional tools like Capistrano.

**Key Benefits:**
- Zero-downtime deployments via Traefik
- Built-in asset bridging
- Automatic container management
- Multi-server support
- Rails-native configuration

### Rails 8 + SQLite in Production

Rails 8 supports SQLite as production database with proper configuration:

```ruby
# config/database.yml
production:
  primary:
    database: storage/production.sqlite3
    adapter: sqlite3
    pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
```

**Requirements for SQLite in Production:**
- Single server (no replication)
- Persistent volume for `storage/` directory
- Proper file permissions
- WAL mode enabled by default in Rails 8

## Kamal Commands

### Essential Commands

```bash
# Setup server for first deployment
kamal setup

# Deploy application
kamal deploy

# Deploy without running migrations
kamal deploy --skip-migrations

# Rollback to previous version
kamal rollback

# View current version
kamal current

# Check deployment status
kamal details

# View logs
kamal logs
kamal logs -f  # tail logs

# Run Rails commands on server
kamal app exec -r web --interactive --reuse "bin/rails db:migrate"
kamal app exec -r web --interactive --reuse "bin/rails console"

# Access server shell
kamal app exec -r web --interactive --reuse "bash"

# Database console
kamal dbconsole

# Backup database
kamal db_backup  # requires alias configured

# Remove old releases
kamal prune --releases --keep 5
```

### Alias Commands (add to deploy.yml)

```yaml
aliases:
  console: app exec --interactive --reuse "bin/rails console"
  shell: app exec --interactive --reuse "bash"
  logs: app logs -f
  dbc: app exec --interactive --reuse "bin/rails dbconsole"
  db_backup: server exec "bash /home/user/backup_trug_db.sh"
```

### Boot Command Options

```bash
# Deploy with custom boot timeout
kamal deploy -t 120

# Deploy from specific branch
kamal deploy -c deploy.staging.yml

# Skip asset compilation
kamal deploy --skip-assets
```

## Configuration

### Basic deploy.yml

```yaml
# config/deploy.yml
service: myapp

image: myapp

servers:
  web:
    - 192.168.1.100

proxy:
  ssl: false
  host: myapp.example.com

registry:
  server: ghcr.io
  username: myuser
  password:
    - GITHUB_TOKEN

env:
  secret:
    - RAILS_MASTER_KEY
    - GITHUB_CLIENT_ID
    - GITHUB_CLIENT_SECRET

volumes:
  - "/mnt/storage:/rails/storage"
  - "/mnt/db:/rails/db"

builder:
  arch: arm64  # or amd64
```

### Environment-Specific Configs

```bash
# Use staging config
kamal deploy -c config/deploy.staging.yml
```

## Database Migrations

### Running Migrations

```bash
# Standard migration deploy
kamal deploy

# Skip migrations (if already ran manually)
kamal deploy --skip-migrations

# Run migrations standalone
kamal app exec -r web --interactive --reuse "bin/rails db:migrate"

# Migrate with specific version
kamal app exec -r web --interactive --reuse "bin/rails db:migrate VERSION=20240201"
```

### Migration Best Practices

1. **Always test migrations locally first**
   ```bash
   RAILS_ENV=production bin/rails db:migrate
   ```

2. **Use reversible migrations**
   ```ruby
   class AddColumnToUsers < ActiveRecord::Migration[8.0]
     def change
       add_column :users, :premium, :boolean, default: false
     end
   end
   ```

3. **Avoid long-running migrations**
   - Break large schema changes into multiple migrations
   - Consider using `add_reference` with `foreign_key: false` for large tables

4. **Zero-downtime migration pattern**
   ```ruby
   # Add column as nullable first
   add_column :users, :new_status, :string
   # Backfill data
   User.update_all(new_status: 'pending')
   # Add constraint
   change_column_null :users, :new_status, false
   # Rename
   rename_column :users, :status, :old_status
   rename_column :users, :new_status, :status
   ```

### SQLite-Specific Considerations

```ruby
# Enable WAL mode for better concurrency
class EnableWalMode < ActiveRecord::Migration[8.0]
  def change
    execute "PRAGMA journal_mode=WAL"
  end
end
```

**SQLite Limitations:**
- No concurrent writes (single connection)
- File locking can cause timeouts under load
- Use `pool: 1` for very high-traffic apps
- Regular VACUUM recommended:
  ```ruby
  class VacuumDatabase < ActiveRecord::Migration[8.0]
    def change
      execute "VACUUM"
    end
  end
  ```

## Volumes Management

### Required Volumes

```yaml
volumes:
  # Active Storage files
  - "/mnt/storage:/rails/storage"
  # SQLite database
  - "/mnt/db:/rails/db"
  # Temp files
  - "/mnt/tmp:/rails/tmp"
```

### Backup Strategy

```bash
#!/bin/bash
# backup_trug_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/user/backups"
mkdir -p $BACKUP_DIR

# Copy database
cp /mnt/db/production.sqlite3 $BACKUP_DIR/production_$DATE.sqlite3

# Optional: Upload to cloud storage
# aws s3 cp $BACKUP_DIR/production_$DATE.sqlite3 s3://my-bucket/backups/

# Keep last 30 days
find $BACKUP_DIR -name "*.sqlite3" -mtime +30 -delete
```

## Docker Configuration

### Dockerfile for Rails

```dockerfile
# Dockerfile
FROM ghcr.io/rails/builder:ruby3.3 AS builder

WORKDIR /rails

# Copy Gemfiles first for better caching
COPY Gemfile* ./
RUN bundle install

COPY . .

# Precompile assets
RUN bin/rails assets:precompile

# Final stage
FROM ghcr.io/rails/runtime:ruby3.3

WORKDIR /rails

# Copy built artifacts from builder
COPY --from=builder /rails /rails

# Entrypoint handles migrations
COPY bin/docker-entrypoint /usr/local/bin/

ENTRYPOINT ["docker-entrypoint"]

EXPOSE 3000
CMD ["rails", "server", "-b", "0.0.0.0", "-p", "3000"]
```

### Docker Entrypoint

```bash
#!/bin/bash
# bin/docker-entrypoint
set -e

# Run database migrations
if [ "${RAILS_ENV}" == "production" ]; then
  bin/rails db:migrate || true
fi

# Start server
exec "${@}"
```

**Important:** Use `|| true` to prevent container crash if migrations fail.

## Server Setup

### Prerequisites

```bash
# On server (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl enable --now docker

# Add user to docker group
sudo usermod -aG docker $USER

# Install Kamal
gem install kamal

# Configure SSH access
ssh-copy-id user@server.com
```

### Server Requirements

- Docker 20.10+
- 2GB RAM minimum
- 10GB storage minimum
- SSH access with key authentication

## Troubleshooting

### Common Issues

**1. Deployment fails on migration**
```bash
# Check migration errors
kamal logs
kamal app exec -r web --interactive --reuse "bin/rails log:tail"

# Run migration manually to see error
kamal app exec -r web --interactive --reuse "bin/rails db:migrate"
```

**2. Database not persisting**
```yaml
# Verify volumes in deploy.yml
volumes:
  - "/mnt/db:/rails/db"

# Check volume mounting on server
docker inspect $(docker ps -q --filter ancestor=myapp) | grep -A2 Volumes
```

**3. Asset 404 errors**
```yaml
# Configure asset path in deploy.yml
asset_path: /rails/public/assets

# Precompile assets locally before deploy
RAILS_ENV=production bin/rails assets:precompile
```

**4. Container won't start**
```bash
# Check container logs
kamal logs

# Check Docker status
ssh user@server "docker ps -a"

# Restart container
kamal app restart
```

**5. Out of memory**
```yaml
# Reduce worker count in deploy.yml
servers:
  web:
    - host: 192.168.1.100
      options:
        memory: 2g
        cpus: 1
```

### Useful Debug Commands

```bash
# Check server resources
ssh user@server "docker stats"

# View container configuration
ssh user@server "docker inspect myapp-web-1"

# Check disk space
ssh user@server "df -h"

# Monitor deployment
kamal details --verbose
```

## Multi-Environment Deployment

### Staging and Production

```yaml
# config/deploy.staging.yml
include:
  - config/deploy.yml

servers:
  web:
    - staging.example.com

env:
  secret:
    - RAILS_MASTER_KEY_STAGING
```

### Environment Variables

```bash
# Set secrets for environment
kamal secrets set RAILS_MASTER_KEY_STAGING "$(cat config/master_staging.key)"
```

## Rolling Back

### Quick Rollback

```bash
# Rollback to previous version
kamal rollback

# Rollback specific number of releases
kamal rollback --to v1.2.3
```

### Database Rollback

```bash
# Rollback last migration
kamal app exec -r web --interactive --reuse "bin/rails db:rollback"

# Rollback specific migration
kamal app exec -r web --interactive --reuse "bin/rails db:migrate:down VERSION=20240201"
```

**Warning:** Rolling back migrations can cause data loss. Always backup first.

## Performance Optimization

### Asset Precompilation

```bash
# Precompile locally for faster deploy
RAILS_ENV=production bin/rails assets:precompile
```

### Image Building

```yaml
# Use remote builder for faster builds
builder:
  remote: ssh://docker@docker-builder-server
```

### Container Resource Limits

```yaml
servers:
  web:
    - host: 192.168.1.100
      options:
        memory: "2g"
        cpus: "2"
        swap: "1g"
```

## Security Best Practices

1. **Use encrypted credentials**
   ```bash
   EDITOR="vim" bin/rails credentials:edit --environment production
   ```

2. **Never commit secrets**
   - Use `kamal secrets` for sensitive data
   - Rotate regularly

3. **Use access tokens for registries**
   - GitHub: Personal Access Token
   - Docker Hub: Access Token

4. **Enable SSL**
   ```yaml
   proxy:
     ssl: true
     host: app.example.com
   ```

5. **Firewall configuration**
   - Block non-SSH ports
   - Use fail2ban

## Monitoring

### Health Checks

```bash
# Check app health
curl https://app.example.com/rails/health
```

### Log Management

```bash
# Tail logs
kamal logs -f

# View specific container logs
ssh user@server "docker logs myapp-web-1"
```

## Common Patterns

### Accessing Rails Console in Production

```bash
kamal console
```

### Running Rake Tasks

```bash
kamal app exec -r web --interactive --reuse "bin/rails my_namespace:my_task"
```

### Database Operations

```bash
# Console access
kamal dbconsole

# Run migrations
kamal app exec -r web --interactive --reuse "bin/rails db:migrate"

# Seed data
kamal app exec -r web --interactive --reuse "bin/rails db:seed"
```

### One-Off Commands

```bash
# Send email (example)
kamal app exec -r web --interactive --reuse "bin/rails users:send_welcome_emails"
```

## References

- [Kamal Official Documentation](https://kamal-deploy.org/)
- [Rails 8 Deployment Guide](https://rails.devdeploy.io/)
- [Docker for Rails Developers](https://dockerrails.com/)
- [SQLite in Production](https://www.sqlite.org/productionmode.html)
