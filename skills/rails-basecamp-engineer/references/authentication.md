# Authentication Patterns

This document covers the shared authentication architecture. For specific authentication methods, see:

- `authentication/magic-link.md` - Passwordless magic link (recommended)
- `authentication/password.md` - Traditional password authentication

## Detecting Existing Authentication Method

Before implementing authentication features, check what the project already uses:

**Indicators of Magic Link auth:**
- `MagicLink` model exists in `app/models/`
- `magic_link` or `magic_links` routes in `routes.rb`
- `MagicLinkMailer` exists in `app/mailers/`
- `send_magic_link` method on Identity model
- Email-based login without password fields

**Indicators of Password auth:**
- `has_secure_password` in Identity or User model
- `password_digest` column in `identities` or `users` migration
- Password reset routes/controllers (`password_resets`, `passwords`)
- Password fields in login forms
- `bcrypt` gem in Gemfile

**If both present:** The app supports multiple authentication methods. Load both reference files.

**If unknown:** Use Explore agent to search for `MagicLink`, `has_secure_password`, or session controllers.

---

## Architecture Overview

The authentication system separates global identity from account-specific users:

- **Identity**: Global user record (email-based), can belong to multiple accounts
- **User**: Account-specific membership with roles
- **Session**: Active login session tied to Identity

```
Identity (email: david@example.com)
  ├── User (Account: Basecamp, role: owner)
  ├── User (Account: Hey, role: admin)
  └── Session (device: Chrome on Mac)
```

## Core Models

### Identity Model

```ruby
# app/models/identity.rb
class Identity < ApplicationRecord
  has_many :sessions, dependent: :destroy
  has_many :users, dependent: :nullify
  has_many :accounts, through: :users

  normalizes :email_address, with: ->(value) { value.strip.downcase.presence }
end
```

### Session Model

```ruby
# app/models/session.rb
class Session < ApplicationRecord
  belongs_to :identity

  # Stores user_agent and ip_address for device tracking
end
```

### User Model

```ruby
# app/models/user.rb
class User < ApplicationRecord
  belongs_to :account
  belongs_to :identity, optional: true

  enum :role, %i[owner admin member system].index_by(&:itself)

  def admin?
    super || owner?  # Owner implicitly has admin permissions
  end
end
```

## Authentication Controller Concern

```ruby
# app/controllers/concerns/authentication.rb
module Authentication
  extend ActiveSupport::Concern

  included do
    before_action :require_account
    before_action :require_authentication
    helper_method :authenticated?
  end

  class_methods do
    def require_unauthenticated_access(**options)
      allow_unauthenticated_access(**options)
      before_action :redirect_authenticated_user, **options
    end

    def allow_unauthenticated_access(**options)
      skip_before_action :require_authentication, **options
      before_action :resume_session, **options
    end

    def disallow_account_scope(**options)
      skip_before_action :require_account, **options
    end
  end

  private
    def authenticated?
      Current.session.present?
    end

    def require_account
      redirect_to session_menu_url(script_name: nil) unless Current.account.present?
    end

    def require_authentication
      resume_session || request_authentication
    end

    def resume_session
      if session = find_session_by_cookie
        set_current_session(session)
      end
    end

    def find_session_by_cookie
      Session.find_signed(cookies.signed[:session_token])
    end

    def start_new_session_for(identity)
      identity.sessions.create!(
        user_agent: request.user_agent,
        ip_address: request.remote_ip
      ).tap { |session| set_current_session(session) }
    end

    def set_current_session(session)
      Current.session = session
      cookies.signed.permanent[:session_token] = {
        value: session.signed_id,
        httponly: true,
        same_site: :lax
      }
    end

    def terminate_session
      Current.session.destroy
      cookies.delete(:session_token)
    end

    def request_authentication
      session[:return_to_after_authenticating] = request.url if Current.account.present?
      redirect_to new_session_path(script_name: nil)
    end

    def after_authentication_url
      session.delete(:return_to_after_authenticating) || landing_url
    end
end
```

## Account Menu (Multi-Account Selection)

When a user belongs to multiple accounts, show a menu:

```ruby
# app/controllers/sessions/menus_controller.rb
class Sessions::MenusController < ApplicationController
  disallow_account_scope

  def show
    @accounts = Current.identity.accounts

    # Auto-redirect if only one account
    if @accounts.one?
      redirect_to root_url(script_name: @accounts.first.slug)
    end
  end
end
```

## Session Security Features

1. **Signed Cookies**: Rails cryptographic signing prevents tampering
2. **HTTPOnly**: JavaScript cannot access session tokens
3. **SameSite=Lax**: CSRF protection
4. **Device Tracking**: User agent and IP stored per session

## Testing Authentication

```ruby
# test/test_helper.rb
def sign_in_as(identity)
  identity = identities(identity) unless identity.is_a?(Identity)

  identity.send_magic_link
  magic_link = identity.magic_links.last

  untenanted do
    post session_magic_link_url, params: { code: magic_link.code }
  end

  assert_response :redirect
  assert cookies[:session_token].present?
end

def with_current_user(user)
  old_session = Current.session
  Current.session = Session.new(identity: user.identity)
  yield
ensure
  Current.session = old_session
end
```

## Choosing an Authentication Method

| Factor | Magic Link | Password |
|--------|------------|----------|
| User friction | Lower (no password to remember) | Higher (must remember password) |
| Email dependency | Required | Not required for login |
| Password storage | None | Requires bcrypt/secure storage |
| Reset flows | None needed | Password reset required |
| Enterprise requirements | May not meet compliance | Often required |
| Offline access | Not possible | Possible |

**Recommendation:** Start with magic links. Add password auth only if required by enterprise customers or specific use cases.
