from rest_framework import routers
from .views import (
    ClientViewSet,
    EmployeeViewSet,
    BinomeViewSet,
    CallViewSet,
    CallTemplateViewSet,
    FieldVisitViewSet,
    FieldVisitTemplateViewSet,
)

router = routers.DefaultRouter()
router.register(r"clients", ClientViewSet)
router.register(r"employees", EmployeeViewSet)
router.register(r"binomes", BinomeViewSet)
router.register(r"calls", CallViewSet)
router.register(r"call-templates", CallTemplateViewSet)
router.register(r"field-visits", FieldVisitViewSet)
router.register(r"field-visit-templates", FieldVisitTemplateViewSet)

urlpatterns = router.urls
