from common.views import BaseSubtaskListView
from singleschema.middleware import current_tenant_id


class FilterTenantMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter_current_tenant()


class UnitListView(FilterTenantMixin, BaseSubtaskListView):
    pass
