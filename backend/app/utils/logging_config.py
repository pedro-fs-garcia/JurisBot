import logging
import os
from logging.handlers import RotatingFileHandler

# Cria a pasta logs se ela não existir
if not os.path.exists("logs"):
    os.makedirs("logs")

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
max_file_size = 10 * 1024 * 1024  # 10MB
backup_count = 5  # Número de arquivos de backup a serem mantidos

app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)

error_logger = logging.getLogger("error")
error_logger.setLevel(logging.ERROR)

app_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=max_file_size,
    backupCount=backup_count,
    encoding="utf-8",
)
app_handler.setFormatter(logging.Formatter(log_format))
app_logger.addHandler(app_handler)

error_handler = RotatingFileHandler(
    "logs/error.log",
    maxBytes=max_file_size,
    backupCount=backup_count,
    encoding="utf-8",
    mode="a",
)
error_handler.setFormatter(logging.Formatter(log_format))
error_logger.addHandler(error_handler)

# Handler para saída no terminal
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(log_format))
app_logger.addHandler(stream_handler)
error_logger.addHandler(stream_handler)

# Exemplo de uso
# app_logger.info("Este é um log de informação.")
# error_logger.error("Este é um log de erro.")