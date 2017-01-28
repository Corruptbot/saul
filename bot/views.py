from django.shortcuts import render

# Create your views here.
import json, requests, random, re, os
from pprint import pprint
import keys
from django.views import generic
from django.http.response import HttpResponse
from fbWrapper.bot import Bot, Element, Button,QuickReply,QuickLocationReply
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

PAGE_ACCESS_TOKEN = os.getenv('token') #cargar al server
VERIFY_TOKEN = "v4l1d4710n70k3n"
bot = Bot(PAGE_ACCESS_TOKEN)

# Helper function
def post_facebook_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    response=''
    for token in tokens:response+=token+" " #Re armar lo mandado
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

# Create your views here.
class BotView(generic.View):
    def get(self, request, *args, **kwargs): #Con esto facebook da la autorizacion al server
        if self.request.GET['hub.mode'] == 'subscribe' and self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
  		
  		# Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
  			#ECHO
  			bot.send_text_message(message['sender']['id'],message['message']['text'])

        return HttpResponse()  