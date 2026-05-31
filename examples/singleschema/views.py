from common.views import BaseUnitListView
from singleschema.middleware import current_tenant_id


class FilterTenantMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter_current_tenant()


class UnitListView(FilterTenantMixin, BaseUnitListView):
    pass
