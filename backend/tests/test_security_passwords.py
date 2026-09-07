"""Unit tests for password hashing and verification."""

from __future__ import annotations

import pytest
from app.security.passwords import hash_password, verify_password


class TestHashPassword:
    """Tests for hash_password()."""

    def test_returns_string(self) -> None:
        result = hash_password("test123")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_produces_bcrypt_prefix(self) -> None:
        result = hash_password("test123")
        assert result.startswith("$2b$") or result.startswith("$2a$")

    def test_different_salts_produce_different_hashes(self) -> None:
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2  # Different salts

    def test_handles_empty_password(self) -> None:
        result = hash_password("")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_handles_unicode_password(self) -> None:
        result = hash_password("密码测试🔐")
        assert isinstance(result, str)
        assert result.startswith("$2b$") or result.startswith("$2a$")

    def test_handles_long_password(self) -> None:
        long_pw = "a" * 1000
        result = hash_password(long_pw)
        assert isinstance(result, str)
        # bcrypt truncates at 72 bytes, but should still work
        assert len(result) > 0


class TestVerifyPassword:
    """Tests for verify_password()."""

    def test_correct_password_returns_true(self) -> None:
        plain = "correct-horse-battery-staple"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_wrong_password_returns_false(self) -> None:
        hashed = hash_password("right-password")
        assert verify_password("wrong-password", hashed) is False

    def test_empty_password(self) -> None:
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("not-empty", hashed) is False

    def test_unicode_roundtrip(self) -> None:
        plain = "パスワード测试"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True
        assert verify_password("different", hashed) is False

    def test_case_sensitive(self) -> None:
        hashed = hash_password("Password123")
        assert verify_password("Password123", hashed) is True
        assert verify_password("password123", hashed) is False
        assert verify_password("PASSWORD123", hashed) is False

    def test_whitespace_significant(self) -> None:
        hashed = hash_password("  spaced  ")
        assert verify_password("  spaced  ", hashed) is True
        assert verify_password("spaced", hashed) is False

    def test_verify_against_known_bcrypt_hash(self) -> None:
        # Known bcrypt hash for "hello"
        known_hash = (
            "$2b$12$LJ3m4ys3GZfnYzPTTGsZvOyVxHCPhG7HEiYB4J3vQ5Xz5yHv3x4qW"
        )
        # This is a dummy hash; we just verify the function doesn't crash
        result = verify_password("anything", known_hash)
        assert isinstance(result, bool)


class TestPasswordEdgeCases:
    """Edge case and security tests."""

    def test_hash_is_not_reversible(self) -> None:
        """Hashes should not contain the plaintext password."""
        plain = "secret-password-123"
        hashed = hash_password(plain)
        assert plain not in hashed
        assert plain.encode("utf-8") not in hashed.encode("utf-8")

    def test_timing_attack_resistance_constant_error(self) -> None:
        """verify_password should not raise on invalid hash format.
        (Timing-attack resistance is handled at the auth router level.)"""
        # Garbage hash should return False, not crash
        assert verify_password("test", "not-a-valid-hash") is False

    def test_near_72_byte_boundary(self) -> None:
        """bcrypt truncates input at 72 bytes. Verify this doesn't break."""
        # 71 bytes
        pw_71 = "a" * 71
        # 72 bytes
        pw_72 = "a" * 72
        # 73 bytes (truncated to 72)
        pw_73 = "a" * 73
        pw_73_first_72 = "a" * 72

        h71 = hash_password(pw_71)
        h72 = hash_password(pw_72)
        h73 = hash_password(pw_73)

        # All should verify correctly for their own passwords
        assert verify_password(pw_71, h71) is True
        assert verify_password(pw_72, h72) is True
        # pw_73 gets truncated to 72 bytes by bcrypt
        assert verify_password(pw_73_first_72, h73) is True