import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'coke-bake-premium-secret-key-2026-change-in-production'
    _db_dir = BASE_DIR / 'database'
    _db_dir.mkdir(parents=True, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or ('sqlite:///' + str(_db_dir / 'coke_bake.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    PRODUCTS_PER_PAGE = 12
    DELIVERY_FEE = 49
    FREE_DELIVERY_THRESHOLD = 999