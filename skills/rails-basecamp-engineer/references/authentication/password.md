# Traditional Password Authentication

Add password authentication alongside (or instead of) magic links.

## When to Use

- Enterprise requirements for password-based auth
- Offline scenarios where email access is limited
- When users prefer traditional password entry
- As a fallback alongside magic links

## Trade-offs

**Pros:**
- Familiar to all users
- No email dependency for login
- Instant authentication

**Cons:**
- Password storage liability
- Password reset flows needed
- Users forget passwords

## Implementation

### Migration

```ruby
class AddPasswordToIdentities < ActiveRecord::Migration[8.0]
  def change
    add_column :identities, :password_digest, :string
  end
end
```

### Identity Model Addition

```ruby
# app/models/identity.rb
class Identity < ApplicationRecord
  has_secure_password validations: false

  # Custom authentication that handles nil password_digest
  def authenticate_password(password)
    password_digest.present? && authenticate(password)
  end
end
```

**Note:** `validations: false` allows identities without passwords (for magic-link-only users).

### Password Sessions Controller

```ruby
# app/controllers/sessions/passwords_controller.rb
class Sessions::PasswordsController < ApplicationController
  disallow_account_scope
  require_unauthenticated_access
  rate_limit to: 10, within: 3.minutes, only: :create

  layout "public"

  def new
    # Show email + password form
  end

  def create
    if identity = Identity.find_by_email_address(params[:email_address])
      if identity.authenticate_password(params[:password])
        start_new_session_for(identity)
        redirect_to after_authentication_url
        return
      end
    end

    redirect_to new_session_password_path, alert: "Invalid email or password"
  end
end
```

### Routes

```ruby
# config/routes.rb
resource :session, only: %i[new create destroy] do
  resource :magic_link, only: %i[show create], module: :sessions
  resource :password, only: %i[new create], module: :sessions
end
```

### Password Reset Flow

If you need password reset:

```ruby
# app/models/password_reset.rb
class PasswordReset < ApplicationRecord
  TOKEN_EXPIRATION = 2.hours

  belongs_to :identity

  has_secure_token :token

  scope :active, -> { where(expires_at: Time.current...) }

  before_create do
    self.expires_at = TOKEN_EXPIRATION.from_now
  end

  def self.consume(token)
    active.find_by(token: token)&.tap(&:destroy)
  end
end
```

```ruby
# app/controllers/password_resets_controller.rb
class PasswordResetsController < ApplicationController
  disallow_account_scope
  require_unauthenticated_access

  def new
    # Email entry form
  end

  def create
    if identity = Identity.find_by_email_address(params[:email_address])
      reset = identity.password_resets.create!
      PasswordResetMailer.instructions(reset).deliver_later
    end
    redirect_to new_session_path, notice: "Check your email for reset instructions"
  end

  def edit
    @password_reset = PasswordReset.find_by!(token: params[:token])
  end

  def update
    if reset = PasswordReset.consume(params[:token])
      reset.identity.update!(password: params[:password])
      start_new_session_for(reset.identity)
      redirect_to after_authentication_url, notice: "Password updated"
    else
      redirect_to new_password_reset_path, alert: "Reset link expired"
    end
  end
end
```

## Combining with Magic Links

You can offer both authentication methods:

```erb
<%# app/views/sessions/new.html.erb %>
<h1>Sign In</h1>

<%= form_with url: session_path do |f| %>
  <%= f.email_field :email_address, placeholder: "Email" %>
  <%= f.submit "Send magic link" %>
<% end %>

<p>Or <a href="<%= new_session_password_path %>">sign in with password</a></p>
```

## Security Considerations

1. **Rate Limiting**: Always rate limit login attempts
2. **Generic Errors**: Don't reveal if email exists
3. **has_secure_password**: Uses bcrypt with proper cost factor
4. **Session on Success**: Always create new session after password change
5. **Token Expiration**: Password reset tokens should expire quickly (2 hours)
