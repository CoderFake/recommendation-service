import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

# Tạo thư mục logs nếu chưa tồn tại
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Tên file log với timestamp
log_filename = logs_dir / f"recommendation_service_{datetime.now().strftime('%Y%m%d')}.log"

# Cấu hình logging
logger = logging.getLogger("recommendation_service")
logger.setLevel(logging.INFO)

# Định dạng log
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Handler cho console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# Handler cho file với xoay vòng mỗi ngày
file_handler = TimedRotatingFileHandler(
    filename=log_filename,
    when="midnight",
    interval=1,
    backupCount=30,  # Giữ log 30 ngày
    encoding="utf-8"
)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)


# Hàm ghi log với context bổ sung
def log_with_context(level, message, context=None):
    """
    Ghi log với context bổ sung để dễ dàng debug.

    Args:
        level: Mức độ log (INFO, ERROR, etc.)
        message: Thông điệp log
        context: Dict chứa thông tin bổ sung
    """
    if context:
        context_str = " - " + " - ".join([f"{k}={v}" for k, v in context.items()])
        message = message + context_str

    if level == "INFO":
        logger.info(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "DEBUG":
        logger.debug(message)
    else:
        logger.info(message)