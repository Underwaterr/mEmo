from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register("events", views.EventViewSet)
router.register("polls", views.PollViewSet)

urlpatterns = router.urls
