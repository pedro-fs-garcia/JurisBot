from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER", "default_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "default_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "default_db")
DB_PORT = os.getenv("DB_PORT", "3306")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")