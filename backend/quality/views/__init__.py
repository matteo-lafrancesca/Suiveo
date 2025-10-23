from .clients import ClientViewSet
from .employees import EmployeeViewSet
from .binomes.base import BinomeViewSet
from .calls import CallViewSet
from .binomes.tableau_suivi import TableauSuiviMixin
from .binomes.planning import PlanningMixin
from .call_template import CallTemplateViewSet

__all__ = [
    "ClientViewSet",
    "EmployeeViewSet",
    "BinomeViewSet",
    "CallViewSet",
    "CallTemplateViewSet",
    "FieldVisitViewSet",
    "FieldVisitTemplateViewSet",
]
