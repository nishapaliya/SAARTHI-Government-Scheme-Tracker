import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # MySQL Database Config
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'saarthi_db')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

    # Upload Settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

    # Fallback SQLite DB path if MySQL is offline during local dev evaluation
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'database', 'saarthi.db')

    # ===========================
    # Brevo Email Configuration
    # ===========================
    BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
    BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL")
    BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "Saarthi")