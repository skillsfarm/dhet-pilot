"""
Drop and recreate the database.

DANGER: This command will DELETE ALL DATA in the database.

Usage:
    uv run python manage.py drop_db
    uv run python manage.py drop_db --no-recreate  # Drop only, don't recreate
"""

import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Drop and recreate the database (DANGER: DELETES ALL DATA)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-recreate",
            action="store_true",
            help="Drop database without recreating it",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args, **options):
        db_settings = settings.DATABASES["default"]
        db_engine = db_settings["ENGINE"]

        # Safety check: prevent running in production
        mode = getattr(settings, "MODE", "development").lower()
        if mode == "production":
            logger.error("BLOCKED: Cannot drop database in PRODUCTION mode for safety.")
            logger.info("  Change MODE to 'development' or 'testing' to proceed.")
            sys.exit(1)

        # Only support PostgreSQL and SQLite
        if "postgresql" not in db_engine and "sqlite" not in db_engine:
            logger.error(
                f"Unsupported database engine: {db_engine}. Only PostgreSQL and SQLite are supported."
            )
            sys.exit(1)

        db_name = db_settings.get("NAME", "")

        # Confirmation prompt
        if not options["yes"]:
            logger.warning(
                f"\n{'=' * 60}\nDANGER: This will DELETE ALL DATA in the database!\n{'=' * 60}"
            )
            logger.info(f"  Database: {db_name}")
            logger.info(f"  Engine:   {db_engine}")
            logger.info(f"  Mode:     {mode.upper()}")
            logger.info("")

            confirm = input("Type 'DELETE ALL DATA' to confirm: ")
            if confirm != "DELETE ALL DATA":
                logger.error("Aborted.")
                sys.exit(0)

        # Handle SQLite
        if "sqlite" in db_engine:
            import os

            if os.path.exists(db_name):
                os.remove(db_name)
                logger.info(f"Deleted SQLite database: {db_name}")
            else:
                logger.warning(f"SQLite database not found: {db_name}")

            if not options["no_recreate"]:
                # Run migrations to recreate
                logger.info("\nRecreating database...")
                from django.core.management import call_command

                call_command("migrate", "--noinput")
                logger.info("Database recreated successfully.")

        # Handle PostgreSQL
        elif "postgresql" in db_engine:
            db_user = db_settings.get("USER", "postgres")
            db_host = db_settings.get("HOST", "localhost")
            db_port = db_settings.get("PORT", "5432")
            db_password = db_settings.get("PASSWORD", "")

            # Close all connections first
            try:
                connection.close()
            except Exception:
                pass

            # Drop database using psycopg directly
            try:
                import psycopg

                # Connect to postgres database (not the target database)
                conn_params = {
                    "dbname": "postgres",
                    "user": db_user,
                    "host": db_host,
                    "port": db_port,
                }
                if db_password:
                    conn_params["password"] = db_password

                with psycopg.connect(**conn_params, autocommit=True) as conn:
                    with conn.cursor() as cur:
                        # Terminate all connections to the database
                        cur.execute(
                            """
                            SELECT pg_terminate_backend(pg_stat_activity.pid)
                            FROM pg_stat_activity
                            WHERE pg_stat_activity.datname = %s
                              AND pid <> pg_backend_pid();
                            """,
                            (db_name,),
                        )

                        # Drop the database
                        cur.execute(f'DROP DATABASE IF EXISTS "{db_name}";')
                        logger.info(f"Dropped PostgreSQL database: {db_name}")

                        # Recreate if requested
                        if not options["no_recreate"]:
                            cur.execute(f'CREATE DATABASE "{db_name}";')
                            logger.info(f"Created PostgreSQL database: {db_name}")

                if not options["no_recreate"]:
                    # Run migrations
                    logger.info("\nRunning migrations...")
                    from django.core.management import call_command

                    call_command("migrate", "--noinput")
                    logger.info("Migrations completed successfully.")

            except Exception as e:
                logger.error(f"Failed to drop PostgreSQL database: {e}")
                sys.exit(1)

        logger.info("")
        if not options["no_recreate"]:
            logger.info("Done! Database has been reset.")
        else:
            logger.info("Done! Database has been dropped.")

        logger.info("")
        logger.info("Next steps:")
        if not options["no_recreate"]:
            logger.info("  uv run python manage.py seed_roles")
            logger.info("  uv run python manage.py seed_users")
            logger.info("  uv run python manage.py seed_cookie_groups")
            logger.info("  uv run python manage.py update_site")
