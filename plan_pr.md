# Enforce Authorization, Prepare for User Roles, Manage Env Variables, and Improve Tests for Access Control (issue #4 items 3-6)

**Objective:**  
Strengthen and extend backend authentication and authorization, building on Supabase JWT validation. Ensure only authenticated users can POST/PUT/PATCH restricted resources, prepare for future user roles, manage Supabase environment variables, and provide thorough tests for access control.

**Scope:**

### Enforce Authorization
- Require valid, authenticated Supabase JWTs for all POST, PUT, and PATCH requests to restricted endpoints (e.g., coaches, participants, affiliations).
- Reject unauthenticated or unauthorized requests with an appropriate error (e.g., 401 Unauthorized or 403 Forbidden).
- Ensure GET requests to public resources remain unaffected.

### (Optional) User Roles Preparation
- Refactor endpoints, request context, and (if applicable) user-related database tables to include a “role” field (e.g., admin, editor, user).
- Do not enforce role checks yet; just structure data and code to support roles in the future.

### Environment Variables
- Store all Supabase project details, secrets, and public keys required for JWT validation and future role support in environment variables.
- Update documentation (e.g., .env.example) with any new required variables.

### Testing
- Add tests to confirm:
  - Unauthenticated users cannot access protected POST/PUT/PATCH endpoints.
  - Authenticated users with valid JWTs can access and update restricted resources.
  - Public GET routes remain accessible as appropriate.

**Exclusions:**
- Do not implement actual role-based permissions (e.g., restricting actions based on role).
- Do not change unrelated endpoints or public route behaviors.
