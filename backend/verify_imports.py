"""Verify all new modules import correctly."""
import sys
sys.path.insert(0, ".")

# Config
from app.config import settings
print(f"✓ config: SECRET_KEY={'***' if settings.SECRET_KEY else 'MISSING'}")

# Security
from app.security.passwords import hash_password, verify_password
h = hash_password("test123")
assert verify_password("test123", h), "password verify failed"
print("✓ passwords: hash + verify OK")

from app.security.jwt import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
token, payload = create_access_token("dummy-uuid")
decoded = decode_access_token(token)
assert decoded.user_id == "dummy-uuid"
print("✓ jwt: create + decode access token OK")

rtoken, rpayload = create_refresh_token("dummy-uuid")
rdecoded = decode_refresh_token(rtoken)
assert rdecoded.user_id == "dummy-uuid"
print("✓ jwt: create + decode refresh token OK")

# Models
from app.models.auth import User, RevokedToken, AuditLog
print("✓ models: auth models OK")

# Schemas
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse, UserResponse
print("✓ schemas: auth schemas OK")

# Envelope
from app.envelope import success_response, error_response
print(f"✓ envelope: success={success_response({'x':1})}")
print(f"✓ envelope: error={error_response('AUTH_REQUIRED', 'test')}")

# Dependencies
from app.deps import get_current_user, get_optional_user, require_admin, get_current_user_id
print("✓ deps: all dependencies OK")

print("\n=== ALL IMPORTS VERIFIED ===")