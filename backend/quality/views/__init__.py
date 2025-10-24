from .clients import ClientViewSet
from .employees import EmployeeViewSet
from .binomes import BinomeViewSet
from .calls import CallViewSet
from .call_template import CallTemplateViewSet

__all__ = [
    "ClientViewSet",
    "EmployeeViewSet",
    "BinomeViewSet",
    "CallViewSet",
    "CallTemplateViewSet",
]
