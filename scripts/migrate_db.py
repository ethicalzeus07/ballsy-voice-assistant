#!/usr/bin/env python3
"""
Database migration script for Ballsy Voice Assistant.
Run this script to apply Alembic migrations to the database.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command
from src.backend.config import config as app_config


def main():
    """Run database migrations."""
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    
    # Set database URL
    alembic_cfg.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)
    
    print(f"Running migrations against: {app_config.DATABASE_URL.split('@')[-1] if '@' in app_config.DATABASE_URL else 'local'}")
    print("Upgrading to head...")
    
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

