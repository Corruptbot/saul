from django.conf.urls import include, url
from .views import BotView

urlpatterns = [
	url(r'^other/?$', BotView.as_view() ),
	]