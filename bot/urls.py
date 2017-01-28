from django.conf.urls import include, url
from .views import BotView

urlpatterns = [
	url(r'^7ceba258cd1fa6adaacd4a3541c299c8948d0261401ce4c271/?$',MessageView.as_view() ),
	url(r'^8cd1fa6adaacd4948d0261401ce4c2717ceba25a3541c299c8/?$',PostbackView.as_view() ),
	#url(r'^a3541c299c8948d0261401ce4c2717ceba258cd1fa6adaacd4/?$',OptinsView.as_view() ),
	
	]