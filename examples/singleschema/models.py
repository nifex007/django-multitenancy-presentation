import common.models as common_models
from django.db.models import ForeignKey
from django.db.models import RESTRICT

from .managers import TenantedManager


class Account(common_models.Account):
    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class User(common_models.User):
    account = ForeignKey(Account, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class Property(common_models.Project):
    account = ForeignKey(Account, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class Building(common_models.Task):
    account = ForeignKey(Account, on_delete=RESTRICT)
    property = ForeignKey(Property, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class Unit(common_models.Subtask):
    account = ForeignKey(Account, on_delete=RESTRICT)
    building = ForeignKey(Building, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"
