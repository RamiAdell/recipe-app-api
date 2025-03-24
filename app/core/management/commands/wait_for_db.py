""" Django wait for DB """
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error
import time


class Command(BaseCommand):
    """ wait for db """
    def handle(self, *args, **options):
        """ Entry for comaand """
        self.stdout.write(' Waiting for db... ')

        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write(' DB unavaliable sleeping 1 second ')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database avaliable'))
