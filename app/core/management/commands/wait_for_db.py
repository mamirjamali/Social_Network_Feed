"""
Django command to wait for the postgres database to be available.
"""
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError
import time


class Command(BaseCommand):
    """Command for wating for database"""

    def handle(self, *args, **options):
        """Entrypoint for commands"""
        self.stdout.write("Wating for db...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable wating 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
