from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import hmac
import hashlib
import time
from app.core.config import settings

# API Key authentication header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_otp(user_id: str, timestamp: int) -> str:
    """
    Tạo OTP 8 số dựa trên user_id, timestamp và API_SECRET_KEY.
    Sử dụng HMAC-SHA256 để bảo mật.
    """
    message = f"{user_id}:{timestamp}"
    h = hmac.new(
        settings.API_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    )
    # Lấy 8 ký tự đầu tiên của hexdigest
    return h.hexdigest()[:8]


def create_access_token(user_id: str) -> str:
    """
    Tạo token truy cập với OTP cho người dùng.
    Format: user_id:timestamp:otp
    """
    timestamp = int(time.time())
    otp = generate_otp(user_id, timestamp)
    return f"{user_id}:{timestamp}:{otp}"


def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Kiểm tra tính hợp lệ của API key.
    Đây là một dependency sẽ được sử dụng trong các endpoint.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Format dự kiến: user_id:timestamp:otp
        parts = api_key.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid API key format")

        user_id, timestamp_str, provided_otp = parts
        timestamp = int(timestamp_str)

        # Kiểm tra token hết hạn chưa
        current_time = int(time.time())
        expiry_seconds = settings.OTP_EXPIRE_MINUTES * 60
        if current_time - timestamp > expiry_seconds:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Xác minh OTP
        expected_otp = generate_otp(user_id, timestamp)
        if not hmac.compare_digest(provided_otp, expected_otp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except (ValueError, IndexError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API key format: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )