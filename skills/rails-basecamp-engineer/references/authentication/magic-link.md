# Passwordless Magic Link Authentication

This is the primary 37signals authentication pattern - no passwords, just email-based magic links.

**Used by:** Fizzy, Basecamp, HEY

## When to Use

- Consumer-facing products (reduce friction)
- Apps where users forget passwords often
- When you want to avoid password storage liability
- Cross-device authentication (email is the transfer mechanism)

## Trade-offs

**Pros:**
- No password reset flows needed
- No password storage liability
- Works across devices naturally
- Simpler user experience

**Cons:**
- Depends on email availability
- Slightly slower than password entry
- Users must have email access

## Implementation

### Magic Link Model

```ruby
# app/models/magic_link.rb
class MagicLink < ApplicationRecord
  CODE_LENGTH = 6
  EXPIRATION_TIME = 15.minutes

  belongs_to :identity
  enum :purpose, %w[sign_in sign_up], prefix: :for, default: :sign_in

  scope :active, -> { where(expires_at: Time.current...) }
  scope :stale, -> { where(expires_at: ..Time.current) }

  before_create do
    self.code = Code.generate(CODE_LENGTH)
    self.expires_at = EXPIRATION_TIME.from_now
  end

  def self.consume(code)
    active.find_by(code: Code.sanitize(code))&.consume
  end

  def consume
    destroy  # One-time use
    self
  end
end
```

### Code Generation

Human-friendly codes that avoid ambiguous characters:

```ruby
# app/models/magic_link/code.rb
module MagicLink::Code
  # Exclude O, I, L to avoid confusion with 0, 1
  CODE_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ".chars.freeze
  CODE_SUBSTITUTIONS = { "O" => "0", "I" => "1", "L" => "1" }.freeze

  def self.generate(length = 6)
    length.times.map { CODE_ALPHABET.sample }.join
  end

  def self.sanitize(code)
    code.to_s
        .upcase
        .gsub(/[#{CODE_SUBSTITUTIONS.keys.join}]/, CODE_SUBSTITUTIONS)
        .gsub(/[^#{CODE_ALPHABET.join}]/, "")
  end
end
```

### Identity Model (Send Magic Link)

```ruby
# app/models/identity.rb
class Identity < ApplicationRecord
  has_many :magic_links, dependent: :destroy
  has_many :sessions, dependent: :destroy
  has_many :users, dependent: :nullify

  normalizes :email_address, with: ->(value) { value.strip.downcase.presence }

  def send_magic_link(purpose: :sign_in)
    magic_links.create!(purpose: purpose).tap do |link|
      MagicLinkMailer.send("#{purpose}_instructions", link).deliver_later
    end
  end
end
```

### Sessions Controller

```ruby
# app/controllers/sessions_controller.rb
class SessionsController < ApplicationController
  disallow_account_scope
  require_unauthenticated_access except: :destroy
  rate_limit to: 10, within: 3.minutes, only: :create

  layout "public"

  def new
    # Show email entry form
  end

  def create
    if identity = Identity.find_by_email_address(params[:email_address])
      identity.send_magic_link
    end
    # Always redirect to prevent email enumeration
    redirect_to session_magic_link_path
  end

  def destroy
    terminate_session
    redirect_to new_session_path
  end
end
```

### Magic Link Redemption Controller

```ruby
# app/controllers/sessions/magic_links_controller.rb
class Sessions::MagicLinksController < ApplicationController
  disallow_account_scope
  require_unauthenticated_access
  rate_limit to: 10, within: 15.minutes, only: :create

  def show
    # Display code entry form
  end

  def create
    if magic_link = MagicLink.consume(params[:code])
      start_new_session_for(magic_link.identity)
      redirect_to after_sign_in_url(magic_link)
    else
      redirect_to session_magic_link_path, alert: "Try another code."
    end
  end

  private
    def after_sign_in_url(magic_link)
      magic_link.for_sign_up? ? new_signup_completion_path : after_authentication_url
    end
end
```

### Mailer

```ruby
# app/mailers/magic_link_mailer.rb
class MagicLinkMailer < ApplicationMailer
  def sign_in_instructions(magic_link)
    @magic_link = magic_link
    @identity = magic_link.identity

    mail to: @identity.email_address,
         subject: "Your sign-in code is #{@magic_link.code}"
  end

  def sign_up_instructions(magic_link)
    @magic_link = magic_link
    @identity = magic_link.identity

    mail to: @identity.email_address,
         subject: "Your sign-up code is #{@magic_link.code}"
  end
end
```

### Routes

```ruby
# config/routes.rb
resource :session, only: %i[new create destroy] do
  resource :magic_link, only: %i[show create], module: :sessions
end
```

## Request Flow

```
1. User visits /session/new
2. User enters email → POST /session
3. MagicLink created, email sent
4. Redirect to /session/magic_link (code entry form)
5. User enters code → POST /session/magic_link
6. MagicLink.consume(code) finds and destroys link
7. start_new_session_for(identity) creates Session
8. Signed cookie set with session.signed_id
9. Redirect to account menu or dashboard
10. Future requests: resume_session reads cookie
```

## Security Features

1. **One-Time Use**: Magic links consumed on use (destroyed)
2. **Short Expiration**: 15-minute window
3. **Rate Limiting**: Prevents brute force
4. **No Email Enumeration**: Always redirect regardless of email existence
5. **Human-Friendly Codes**: 6 characters, no ambiguous chars
6. **Code Sanitization**: Handles common typos (O→0, I→1, L→1)

## Cleanup Job

```ruby
# Recurring job to clean up expired magic links
# config/recurring.yml
cleanup_magic_links:
  command: "MagicLink.stale.delete_all"
  schedule: every 4 hours
```
