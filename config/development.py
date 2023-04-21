from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

DATABASE_URI = 'sqlite:////tmp/data.db'

TIME_ZONE = 'UTC'
