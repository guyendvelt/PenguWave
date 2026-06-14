from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_plaintext_and_verifies():
    hashed = hash_password("s3cret-pw")
    assert hashed != "s3cret-pw"
    assert verify_password("s3cret-pw", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_verify_handles_malformed_hash():
    assert verify_password("anything", "not-a-real-hash") is False


def test_jwt_roundtrip_carries_subject():
    token = create_access_token("usr-123")
    payload = decode_access_token(token)
    assert payload["sub"] == "usr-123"
    assert "exp" in payload
