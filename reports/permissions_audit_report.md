# Permissions & Access Control Audit Report
**Generated:** 2026-02-05  
**Application:** Codebasics Practice Room  
**Auditor:** Security Analysis

---

## Executive Summary

This audit identified **CRITICAL** security vulnerabilities in the access control and permissions implementation. The application has severe authorization flaws that allow privilege escalation and bypass of business logic.

---

## 🚨 CRITICAL FINDINGS

### 1. User Signup Allows Role Assignment (Privilege Escalation)
**Risk Level:** 🔴 CRITICAL  
**Location:** `auth.py:68-76`, `auth_service.py:46-58`, `models.py:67-71`

**Attack Scenario:**
```bash
# Attacker creates admin account via public signup endpoint
curl -X POST "/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","email":"a@b.com","password":"x","role":"admin"}'
```

**Impact:** Any unauthenticated user can self-register as `admin`, gaining full administrative access to:
- Create/Delete/Modify questions
- Delete other users' data
- Access admin-only endpoints

**Solution:**
```python
# models.py - Remove role from UserCreate or force "learner"
class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    # REMOVE: role: str = "learner"  
    
# auth_service.py - Hardcode role
def create_user(user_create: UserCreate):
    db_user = User(
        ...
        role="learner"  # HARDCODE, never trust input
    )
```

---

### 2. Password Reset Without Verification
**Risk Level:** 🔴 CRITICAL  
**Location:** `auth.py:78-86`, `auth_service.py:60-71`

**Attack Scenario:**
```bash
# Attacker resets any user's password if they know username + email
# (often discoverable via user enumeration or social engineering)
curl -X POST "/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@admin.com","new_password":"hacked123"}'
```

**Impact:** Account takeover of any user (including admin) by anyone who knows or guesses the username/email combination.

**Vulnerabilities:**
- No email verification link
- No current password required
- No rate limiting
- No CAPTCHA

**Solution:**
```python
# Proper password reset flow:
# 1. Send reset token to user's email
# 2. User clicks link with token
# 3. Token verified before password change
# 4. Rate limit endpoint to 3 attempts per hour
```

---

### 3. User Enumeration via Signup/Login
**Risk Level:** 🟠 HIGH  
**Location:** `auth.py:70-75`

**Attack Scenario:**
```bash
# Enumerate existing usernames
curl -X POST "/api/v1/auth/signup" -d '{"username":"admin",...}'
# Response: "The user with this username already exists"
```

**Solution:** Return generic error: "If this account exists, a verification email has been sent."

---

## 🟠 HIGH RISK FINDINGS

### 4. No IDOR Protection on Progress Data
**Risk Level:** 🟠 HIGH  
**Location:** `questions.py:17-23`

**Issue:** Progress is filtered by `current_user.username`, which is correct. However, there's no audit log for access patterns that could indicate enumeration attempts.

---

### 5. File Upload Path Traversal (Admin-only)
**Risk Level:** 🟡 MEDIUM (requires admin)  
**Location:** `admin.py:73-77`

**Attack Scenario:**
```python
# Malicious admin uploads file with path-traversal name
data_file_name = "../../../../../../etc/passwd"
```

**Impact:** Write arbitrary files to server filesystem.

**Solution:**
```python
import os
safe_filename = os.path.basename(data_file_name)  # Strips directory components
```

---

### 6. Default Hardcoded Credentials
**Risk Level:** 🟡 MEDIUM  
**Location:** `database.py:60-66, 73-87`

**Issue:** Default admin/learner accounts with predictable passwords seeded on every startup.

**Solution:**
- Generate random admin password on first run
- Print password to console ONCE
- Require password change on first login

---

## Access Control Matrix

| Endpoint | Expected | Actual | Status |
|----------|----------|--------|--------|
| `POST /signup` | Public, learner-only | Public, **any role** | ❌ VULN |
| `POST /reset-password` | Verified user | **Anyone** | ❌ VULN |
| `POST /admin/questions` | Admin only | Admin only | ✅ OK |
| `DELETE /admin/questions/:id` | Admin only | Admin only | ✅ OK |
| `GET /questions/` | Authenticated | Authenticated | ✅ OK |
| `POST /execute/run` | Authenticated | Authenticated | ✅ OK |
| `POST /execute/validate` | Authenticated | Authenticated | ✅ OK |

---

## Remediation Priority

| Priority | Finding | Effort |
|----------|---------|--------|
| 1 | Role assignment in signup | 5 min |
| 2 | Password reset verification | 2-4 hours |
| 3 | User enumeration | 30 min |
| 4 | File path traversal | 10 min |
| 5 | Default credentials | 1 hour |
