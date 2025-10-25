# JWT Authentication Guide

## Overview

The application now uses **JWT (JSON Web Tokens)** for secure, stateless authentication. This provides better security, scalability, and flexibility compared to traditional session-based authentication.

## Table of Contents

- [What is JWT?](#what-is-jwt)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Security Features](#security-features)
- [Usage Examples](#usage-examples)
- [API Endpoints](#api-endpoints)
- [Token Management](#token-management)
- [Troubleshooting](#troubleshooting)

---

## What is JWT?

JWT (JSON Web Token) is an industry-standard method for securely transmitting information between parties as a JSON object. It consists of three parts:

1. **Header**: Contains token type and signing algorithm
2. **Payload**: Contains user data (claims)
3. **Signature**: Ensures token hasn't been tampered with

### Why JWT?

**Advantages over sessions:**
- **Stateless**: No server-side session storage needed
- **Scalable**: Works across multiple servers
- **Secure**: Cryptographically signed, HttpOnly cookies
- **Flexible**: Can include custom claims (user data)
- **Mobile-friendly**: Easy to use in mobile apps

---

## How It Works

### 1. Login Flow

```
User → Login with credentials → Server validates → Server generates JWT →
Server sets HttpOnly cookies → User redirected to dashboard
```

1. User submits Amazon API credentials
2. Server validates credentials with Amazon API
3. Server generates **two** tokens:
   - **Access Token** (expires in 1 hour)
   - **Refresh Token** (expires in 30 days)
4. Tokens stored in **HttpOnly cookies** (secure, cannot be accessed by JavaScript)
5. User redirected to dashboard

### 2. Authentication Flow

```
User requests protected page → Browser sends cookie → Server verifies JWT →
Server grants access → User sees page
```

1. Browser automatically sends JWT cookie with each request
2. Server validates JWT signature and expiration
3. Server extracts user data from token
4. Request proceeds if valid, otherwise redirects to login

### 3. Logout Flow

```
User clicks logout → Server blacklists token → Server clears cookies →
User redirected to login
```

1. Server adds token to blacklist (prevents reuse)
2. Server clears JWT cookies
3. Server terminates background processes
4. User redirected to login page

---

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# JWT Secret Key (CHANGE THIS IN PRODUCTION!)
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-me

# Optional: Override token expiration times
# JWT_ACCESS_TOKEN_HOURS=1
# JWT_REFRESH_TOKEN_DAYS=30
```

### Config Settings ([config.py](../config.py))

```python
# JWT configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
JWT_ALGORITHM = 'HS256'  # HMAC with SHA-256
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
```

**Production Security:**
- Generate a strong random secret: `python -c "import secrets; print(secrets.token_hex(32))"`
- Store in environment variables, NEVER commit to git
- Use different secrets for dev/staging/production

---

## Security Features

### 1. HttpOnly Cookies

Tokens stored in **HttpOnly cookies** cannot be accessed by JavaScript, preventing XSS attacks:

```python
response.set_cookie(
    'access_token',
    token,
    httponly=True,    # Prevents JavaScript access
    secure=True,      # HTTPS only (production)
    samesite='Lax'    # CSRF protection
)
```

### 2. Token Blacklisting

Logout invalidates tokens by adding them to a blacklist:

```python
jwt_service.blacklist_token(token)  # Token cannot be reused
```

**Note**: In production, use Redis or database for blacklist storage.

### 3. Token Expiration

- **Access Token**: 1 hour (short-lived for security)
- **Refresh Token**: 30 days (longer-lived for convenience)

### 4. Secure Cookie Settings

- **Secure**: HTTPS only in production
- **SameSite**: Prevents CSRF attacks
- **HttpOnly**: Prevents XSS attacks

---

## Usage Examples

### Protecting Routes with JWT

**Method 1: JWT Required (default)**

```python
from app.utils import jwt_required
from flask import g

@app.route('/dashboard')
@jwt_required
def dashboard():
    # Access user data from g.current_user
    user_data = g.current_user
    api_key = user_data['api_key']
    return f"Welcome, user {user_data['user_id']}"
```

**Method 2: JWT Optional**

```python
from app.utils import jwt_optional
from flask import g

@app.route('/home')
@jwt_optional
def home():
    if g.current_user:
        return f"Welcome back, {g.current_user['user_id']}"
    return "Welcome, guest"
```

**Method 3: Legacy Session Auth (backward compatible)**

```python
from app.utils import login_required

@app.route('/old-route')
@login_required
def old_route():
    # Uses session-based auth
    return "Protected by sessions"
```

### Accessing User Data in Routes

```python
@app.route('/profile')
@jwt_required
def profile():
    # User data available in g.current_user
    user_data = g.current_user

    # Available fields:
    api_key = user_data['api_key']
    secret_key = user_data['secret_key']
    associate_tag = user_data['associate_tag']
    user_id = user_data['user_id']
    product_fetch_pid = user_data['product_fetch_pid']

    return render_template('profile.html', user=user_data)
```

---

## API Endpoints

### Login

**POST** `/submit`

```http
POST /submit HTTP/1.1
Content-Type: multipart/form-data

api_key=AKIAIOSFODNN7EXAMPLE
secret_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
associate_tag=yourtag-20
api_file=<uploaded file>
```

**Response:**
- **Success**: Redirects to `/dash` with JWT cookies set
- **Error**: Returns to login with error message

**Cookies Set:**
```
access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
refresh_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Logout

**POST** `/logout` or **GET** `/logout`

```http
POST /logout HTTP/1.1
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
- Blacklists token
- Clears cookies
- Redirects to `/login`

---

## Token Management

### Token Structure

**Access Token Payload:**
```json
{
  "type": "access",
  "user_id": "AKIAIOSF",
  "api_key": "AKIAIOSFODNN7EXAMPLE",
  "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "associate_tag": "yourtag-20",
  "product_fetch_pid": 12345,
  "exp": 1678901234,
  "iat": 1678897634
}
```

**Refresh Token Payload:**
```json
{
  "type": "refresh",
  "user_id": "AKIAIOSF",
  "exp": 1681493634,
  "iat": 1678897634
}
```

### Token Verification

The `jwt_required` decorator automatically:
1. Extracts token from cookie/header/query param
2. Verifies signature
3. Checks expiration
4. Checks blacklist
5. Stores user data in `g.current_user`

### Token Sources (Priority Order)

1. **Authorization Header**: `Authorization: Bearer <token>`
2. **Cookie**: `access_token` cookie
3. **Query Parameter**: `?token=<token>`

**Example with cURL:**
```bash
# Using Authorization header
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:5000/dash

# Using cookie (browser automatically sends this)
curl --cookie "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:5000/dash

# Using query parameter
curl "http://localhost:5000/dash?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Troubleshooting

### Issue: "Your session has expired"

**Cause**: Access token expired (after 1 hour)

**Solution**:
- Re-login (will generate new tokens)
- Future: Implement token refresh endpoint

### Issue: "Invalid or expired token"

**Causes**:
- Token signature invalid (secret key changed)
- Token expired
- Token blacklisted (logged out)
- Token tampered with

**Solution**:
- Clear browser cookies
- Re-login

### Issue: "Missing authentication token"

**Causes**:
- Not logged in
- Cookies disabled
- Third-party cookie blocking

**Solution**:
- Enable cookies in browser
- Login again
- Check browser privacy settings

### Clearing Token Blacklist (Development)

```python
from app.services import JWTService

# In Python shell or route
JWTService.clear_blacklist()
```

**Note**: Blacklist is in-memory. Restarting the server clears it.

---

## Production Recommendations

### 1. Secure Secret Keys

```bash
# Generate strong secret
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env
JWT_SECRET_KEY=a1b2c3d4e5f6... (64 chars)
```

### 2. Use Redis for Token Blacklist

```python
# Install redis
pip install redis

# Update jwt_service.py
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def blacklist_token(self, token):
    # Store in Redis with TTL
    redis_client.setex(
        f"blacklist:{token}",
        self.config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds(),
        "1"
    )
```

### 3. Enable HTTPS

```python
# config.py - Production
SESSION_COOKIE_SECURE = True  # Cookies only sent over HTTPS
```

### 4. Implement Token Refresh

```python
@app.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')
    jwt_service = JWTService(current_app.config)
    new_access_token = jwt_service.refresh_access_token(
        refresh_token,
        user_data
    )
    if new_access_token:
        response = make_response(jsonify({'success': True}))
        response.set_cookie('access_token', new_access_token, ...)
        return response
    return jsonify({'error': 'Invalid refresh token'}), 401
```

### 5. Monitor Token Usage

```python
# Add logging in jwt_service.py
logger.info(f"Token generated for user: {user_id}")
logger.warning(f"Invalid token attempt from IP: {request.remote_addr}")
```

---

## Migration from Session-Based Auth

Both JWT and session-based auth work side-by-side for backward compatibility:

1. **New code**: Use `@jwt_required`
2. **Legacy code**: Keep `@login_required` (still works)
3. **Login**: Now generates both session AND JWT
4. **Logout**: Clears both session AND JWT

**Gradual Migration:**
1. Update one route at a time from `@login_required` to `@jwt_required`
2. Test thoroughly
3. Eventually remove session support when all routes migrated

---

## Further Reading

- [JWT.io](https://jwt.io/) - JWT introduction and debugger
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JWT standard
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review server logs
3. Open GitHub issue with details
