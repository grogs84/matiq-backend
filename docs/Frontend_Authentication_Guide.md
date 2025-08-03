# Frontend Authentication Guide
## MatIQ Backend API Integration

This document provides a comprehensive guide for frontend developers to integrate with the MatIQ backend authentication system. Use this as your starting point for building authentication pages and user login flows.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication Endpoint](#authentication-endpoint)
- [Request/Response Schemas](#requestresponse-schemas)
- [Frontend Integration Examples](#frontend-integration-examples)
- [Error Handling](#error-handling)
- [Testing & Development](#testing--development)
- [Security Considerations](#security-considerations)
- [Next Steps & Production Ready Features](#next-steps--production-ready-features)

## 🎯 Overview

The MatIQ backend provides a simple, secure authentication system built with FastAPI and designed for Supabase integration. The current implementation includes:

- **Single Login Endpoint**: POST `/api/v1/auth/login`
- **JSON-based Communication**: Clean request/response format
- **Mock Authentication**: Demo credentials for development
- **Production Ready**: Supabase integration points ready
- **Comprehensive Error Handling**: Clear error messages
- **Security Logging**: Authentication events tracked

## 🔐 Authentication Endpoint

### Login User

**Endpoint:** `POST /api/v1/auth/login`

**Purpose:** Authenticate a user with email and password credentials

**Content-Type:** `application/json`

### Request Schema

```json
{
  "email": "string",
  "password": "string"
}
```

### Response Schema

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "user_id": "string",
  "access_token": "string"
}
```

**Failure Response (200):**
```json
{
  "success": false,
  "message": "Invalid email or password",
  "user_id": null,
  "access_token": null
}
```

**Server Error Response (500):**
```json
{
  "detail": "Internal server error during authentication"
}
```

## 📝 Request/Response Schemas

### LoginRequest
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | User's email address |
| `password` | string | ✅ | User's password |

### LoginResponse  
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if authentication was successful |
| `message` | string | Human-readable status message |
| `user_id` | string\|null | User identifier (null on failure) |
| `access_token` | string\|null | JWT access token (null on failure) |

## 💻 Frontend Integration Examples

### JavaScript/TypeScript (Fetch API)

```javascript
// Define the types
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  message: string;
  user_id?: string;
  access_token?: string;
}

// Login function
async function loginUser(email: string, password: string): Promise<LoginResponse> {
  try {
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: LoginResponse = await response.json();
    
    if (data.success) {
      // Store token securely
      localStorage.setItem('access_token', data.access_token!);
      localStorage.setItem('user_id', data.user_id!);
      
      console.log('Login successful:', data.message);
      return data;
    } else {
      console.log('Login failed:', data.message);
      return data;
    }
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// Usage example
const handleLogin = async (email: string, password: string) => {
  try {
    const result = await loginUser(email, password);
    
    if (result.success) {
      // Redirect to dashboard or main app
      window.location.href = '/dashboard';
    } else {
      // Show error message to user
      showErrorMessage(result.message);
    }
  } catch (error) {
    showErrorMessage('Network error. Please try again.');
  }
};
```

### React Hook Example

```typescript
import { useState } from 'react';

interface AuthState {
  isAuthenticated: boolean;
  user_id: string | null;
  access_token: string | null;
  loading: boolean;
  error: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user_id: null,
    access_token: null,
    loading: false,
    error: null
  });

  const login = async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (data.success) {
        setAuthState({
          isAuthenticated: true,
          user_id: data.user_id,
          access_token: data.access_token,
          loading: false,
          error: null
        });
        
        // Store in localStorage
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user_id', data.user_id);
      } else {
        setAuthState({
          isAuthenticated: false,
          user_id: null,
          access_token: null,
          loading: false,
          error: data.message
        });
      }
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        user_id: null,
        access_token: null,
        loading: false,
        error: 'Network error. Please try again.'
      });
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    setAuthState({
      isAuthenticated: false,
      user_id: null,
      access_token: null,
      loading: false,
      error: null
    });
  };

  return { authState, login, logout };
};
```

### Login Form Component (React)

```typescript
import React, { useState } from 'react';
import { useAuth } from './useAuth';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { authState, login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <div className="login-form">
      <h2>Login to MatIQ</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={authState.loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={authState.loading}
          />
        </div>
        
        {authState.error && (
          <div className="error-message">
            {authState.error}
          </div>
        )}
        
        <button 
          type="submit" 
          disabled={authState.loading}
        >
          {authState.loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};
```

### cURL Example (for testing)

```bash
# Successful login with demo credentials
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpassword"
     }'

# Response:
# {
#   "success": true,
#   "message": "Login successful",
#   "user_id": "mock-user-id-123",
#   "access_token": "mock-access-token-abc"
# }
```

## ⚠️ Error Handling

### Response Status Codes

- **200 OK**: Request processed (check `success` field for auth result)
- **422 Unprocessable Entity**: Invalid request format/validation errors
- **500 Internal Server Error**: Server-side authentication error

### Error Types and Handling

```typescript
const handleLoginResponse = (response: LoginResponse) => {
  if (response.success) {
    // Success case
    console.log('User authenticated successfully');
    return { authenticated: true, token: response.access_token };
  } else {
    // Authentication failed
    switch (response.message) {
      case 'Invalid email or password':
        return { authenticated: false, error: 'Please check your credentials' };
      case 'Authentication service error':
        return { authenticated: false, error: 'Server error. Please try again later' };
      default:
        return { authenticated: false, error: response.message };
    }
  }
};
```

### Network Error Handling

```typescript
const loginWithErrorHandling = async (email: string, password: string) => {
  try {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      if (response.status === 422) {
        const errorData = await response.json();
        throw new Error(`Validation error: ${errorData.detail}`);
      } else if (response.status === 500) {
        throw new Error('Server error. Please try again later.');
      } else {
        throw new Error(`Unexpected error: ${response.status}`);
      }
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      // Network error
      throw new Error('Network error. Please check your connection.');
    }
    throw error;
  }
};
```

## 🧪 Testing & Development

### Demo Credentials

For development and testing, use these credentials:

```json
{
  "email": "test@example.com",
  "password": "testpassword"
}
```

### Backend Server Setup

1. **Start the backend server:**
   ```bash
   cd matiq-backend
   python main.py
   ```

2. **Verify the server is running:**
   - API Root: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Testing Authentication Flow

1. **Test successful login:**
   ```javascript
   const result = await loginUser('test@example.com', 'testpassword');
   console.log(result);
   // Expected: { success: true, message: "Login successful", ... }
   ```

2. **Test failed login:**
   ```javascript
   const result = await loginUser('wrong@email.com', 'wrongpass');
   console.log(result);
   // Expected: { success: false, message: "Invalid email or password", ... }
   ```

3. **Test API availability:**
   ```javascript
   const response = await fetch('http://localhost:8000/health');
   const health = await response.json();
   console.log(health);
   // Expected: { status: "healthy" }
   ```

## 🔒 Security Considerations

### Token Storage

**Recommended approach:**
- Store access tokens in memory or secure storage
- Use httpOnly cookies for production (when backend supports it)
- Avoid localStorage for sensitive tokens in production

```typescript
// Development approach (localStorage)
localStorage.setItem('access_token', token);

// Production consideration
// Use secure, httpOnly cookies or memory storage
// Implement token refresh mechanism
```

### CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:8000` (Backend itself)

### Request Headers

Always include proper content type:
```javascript
headers: {
  'Content-Type': 'application/json'
}
```

### Password Handling

- Never log passwords
- Clear password fields after submission
- Use HTTPS in production
- Implement proper form validation

```typescript
// Clear sensitive data after use
const handleLogin = async (email: string, password: string) => {
  try {
    const result = await loginUser(email, password);
    
    // Clear password from memory
    password = '';
    
    return result;
  } catch (error) {
    // Clear password on error too
    password = '';
    throw error;
  }
};
```

## 🚀 Next Steps & Production Ready Features

### Current Implementation Status

✅ **Completed:**
- Basic login endpoint
- Request/response validation
- Error handling and logging
- Mock authentication for development
- Comprehensive test coverage
- Clean architecture (router/service/schema layers)

### Immediate Next Steps

📋 **For Frontend Development:**

1. **Build Login Page**
   - Create login form with email/password fields
   - Implement client-side validation
   - Add loading states and error display
   - Test with demo credentials

2. **Implement State Management**
   - Store authentication state (logged in/out)
   - Store user data and tokens
   - Handle session persistence

3. **Add Route Protection**
   - Create protected route components
   - Redirect unauthenticated users to login
   - Handle token expiration

### Future Backend Features (Planned)

🔄 **In Development Pipeline:**

- **User Registration**: `POST /api/v1/auth/register`
- **Password Reset**: `POST /api/v1/auth/reset-password`
- **Token Refresh**: `POST /api/v1/auth/refresh`
- **User Profile**: `GET /api/v1/auth/profile`
- **Logout**: `POST /api/v1/auth/logout`

### Production Configuration

🔧 **For Production Deployment:**

1. **Environment Setup:**
   ```bash
   # Set these environment variables:
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   ENVIRONMENT=production
   ```

2. **Supabase Integration:**
   - The service layer is ready for Supabase
   - Simply set environment variables
   - Remove mock credentials

3. **Security Enhancements:**
   - JWT token validation middleware
   - Rate limiting on auth endpoints
   - HTTPS enforcement
   - Secure cookie implementation

### Integration with MatIQ Features

🏆 **Wrestling Analytics Integration:**

Once authenticated, users will have access to:
- Wrestler profile management
- Tournament data and analytics
- School/team management
- Advanced search and filtering
- Performance tracking and insights

### API Evolution

The authentication system is designed to support:
- Role-based access control (admin, coach, athlete)
- Multi-tenant organization support
- OAuth integration (Google, Apple, etc.)
- SSO for school/organization integration

---

## 📞 Support & Feedback

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Test Endpoint**: Use demo credentials for development

This guide provides everything needed to build your first authentication page. Start with the basic login form using the demo credentials, then expand with proper state management and error handling as shown in the examples above.