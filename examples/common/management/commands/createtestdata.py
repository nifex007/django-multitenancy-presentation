import importlib

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import router
from django.db import transaction
from factory.fuzzy import FuzzyInteger
from factory.random import reseed_random

from ...factories import AccountFactory
from ...factories import UserFactory
from ...factories import BuildingFactory
from ...factories import PropertyFactory
from ...factories import UnitFactory

models = importlib.import_module(settings.MODELS_MODULE + ".models")


class Command(BaseCommand):
    help = "Checks the entire Django project for potential problems."

    requires_system_checks = []

    def add_arguments(self, parser):
        try:
            default_accounts = settings.MULTIDB_COUNT
        except AttributeError:
            default_accounts = 1

        parser.add_argument(
            "--accounts",
            action="store",
            type=int,
            default=default_accounts,
            help="Number of accounts to create (default %(default)s)",
        )

        parser.add_argument(
            "--min-users",
            action="store",
            type=int,
            default=1,
            help="Min average number of users to create per account",
        )
        parser.add_argument(
            "--max-users",
            action="store",
            type=int,
            default=5,
            help="Max average number of users to create per account",
        )

        parser.add_argument(
            "--min-properties",
            dest="min_properties",
            action="store",
            type=int,
            default=1,
            help="Min average number of properties to create per account",
        )
        parser.add_argument(
            "--max-properties",
            dest="max_properties",
            action="store",
            type=int,
            default=30,
            help="Max number of properties to create per account",
        )

        parser.add_argument(
            "--min-buildings",
            dest="min_buildings",
            action="store",
            type=int,
            default=1,
            help="Min average number of buildings to create per property",
        )
        parser.add_argument(
            "--max-buildings",
            dest="max_buildings",
            action="store",
            type=int,
            default=10,
            help="Max average number of buildings to create per property",
        )

        parser.add_argument(
            "--min-units",
            dest="min_units",
            action="store",
            type=int,
            default=1,
            help="Min average number of units to create per building",
        )
        parser.add_argument(
            "--max-units",
            dest="max_units",
            action="store",
            type=int,
            default=10,
            help="Max average number of units to create per building",
        )

        parser.add_argument(
            "--rollback", action="store_true", help="Rollback (don't commit) database changes. Useful for testing"
        )

    def handle(
        self,
        *args,
        accounts: int,
        min_users: int,
        max_users: int,
        min_properties: int,
        max_properties: int,
        min_buildings: int,
        max_buildings: int,
        min_units: int,
        max_units: int,
        rollback: bool,
        **options,
    ):
        # make this deterministic
        reseed_random(0)

        accounts_count = 0
        users_count = 0
        properties_count = 0
        buildings_count = 0
        units_count = 0

        if "multidb" in settings.INSTALLED_APPS:
            assert accounts <= settings.MULTIDB_COUNT
            from multidb.middleware import MultiDbMiddleware

            account_context = MultiDbMiddleware.use_current_tenancy_slug
        elif "singleschema" in settings.INSTALLED_APPS:
            from singleschema.middleware import SingleSchemaMiddleware

            account_context = SingleSchemaMiddleware.use_current_tenancy_slug
        else:
            raise RuntimeError("Unrecognised configuration")

        for account_i in range(accounts):
            account_slug = f"tenant-{account_i}"
            with account_context(account_slug):
                account = AccountFactory.build(slug=account_slug)
                db_alias = router.db_for_write(models.Account, instance=account)
                with transaction.atomic(using=db_alias):
                    account.save()
                    accounts_count += 1

                    n_users = FuzzyInteger(min_users, max_users).fuzz()
                    users = UserFactory.create_batch(n_users, account=account, password="password")
                    users_count += len(users)

                    n_properties = FuzzyInteger(min_properties, max_properties).fuzz()
                    properties = PropertyFactory.create_batch(n_properties, account=account)
                    properties_count += len(properties)

                    n_buildings = FuzzyInteger(min_buildings, max_buildings).fuzz() * len(properties)
                    buildings = BuildingFactory.create_batch(
                        n_buildings,
                        property=properties,
                        account=account,
                    )
                    buildings_count += len(buildings)

                    n_units = FuzzyInteger(min_units, max_units).fuzz() * len(buildings)
                    units = UnitFactory.create_batch(
                        n_units,
                        building=buildings,
                        account=account,
                    )
                    units_count += len(units)

                    if accounts > 10:
                        print(".", end="", flush=True)
                    else:
                        print(account.slug, account.name)

                    if rollback:
                        transaction.set_rollback(True, using=db_alias)

        print()
        print(f"Accounts: {accounts_count}")
        print(f"Users: {users_count}")
        print(f"Properties: {properties_count}")
        print(f"Buildings: {buildings_count}")
        print(f"Units: {units_count}")
