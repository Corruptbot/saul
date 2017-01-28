from django.conf.urls import include, url
from .views import BotView

urlpatterns = [
	url(r'^7ceba258cd1fa6adaacd4a3541c299c8948d0261401ce4c271/?$', BotView.as_view() ),
	]