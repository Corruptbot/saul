from django.shortcuts import render

# Create your views here.
import json, requests, random, re, os
from pprint import pprint
from django.views import generic
from django.http.response import HttpResponse
from fbWrapper.bot import Bot, Element, Button,QuickReply,QuickLocationReply
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

PAGE_ACCESS_TOKEN = os.getenv('token') #cargar al server
VERIFY_TOKEN = "v4l1d4710n70k3n"
print PAGE_ACCESS_TOKEN
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
                print message
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                #if 'read' in message: #Lo acaba de leer
                if 'postback' in message:
                    print message['postback']['payload']
                    continue
                if 'quick_reply' in message:
                    print message['quick_reply']['payload']
                    continue

                elif 'message' in message:
                    # Print the message to the terminal
                    if 'is_echo' in message['message']: 
                        continue
                    elif 'attachments' in message['message']:
                        print message['message']['attachments']
                        
                        for attachment in message['message']['attachments']:
                            if attachment['type']=='location':
                                coor = attachment['payload']['coordinates']
                                print coor['lat']
                                print coor['long']
                        continue

                    elif message['message']['text']=='img': #Enviar lista de imagenes
                        elements = []
                        element = Element(title="test", image_url="https://marco.org/media/2016/01/md101lla.png", subtitle="subtitle", item_url="http://arsenal.com")
                        elements.append(element)
                        element1 = Element(title="test1", image_url="https://marco.org/media/2016/01/md101lla.png", subtitle="subtitle", item_url="http://apple.com")
                        elements.append(element1)
                        bot.send_generic_message(message['sender']['id'], elements)
                    elif message['message']['text']=='moonman':
                        video = 'https://s3-us-west-2.amazonaws.com/cuadra-apps/moonman.mp4'
                        #bot.send_video_url(message['sender']['id'] ,video)
                    elif message['message']['text'] == 'button':
                        buttons = []
                        button = Button(type="web_url",url='https://petersapparel.parseapp.com',title='Show Website')
                        buttons.append(button)
                        button1 = Button(type="postback",title='Start chat',payload='My payload')
                        buttons.append(button1)
                        bot.send_button_message(message['sender']['id'],"Bienvenido",buttons)
                    elif message['message']['text'] == 'quick':
                        quicks = []
                        button = QuickLocationReply()
                        quicks.append(button)
                        button1 = QuickReply(content_type="text",title='red',image_url='http://petersfantastichats.com/img/red.png',payload='My payload')
                        quicks.append(button1)
                        bot.send_quick_replies(message['sender']['id'],"Selecciona",quicks)
                    else:
                        bot.send_text_message(message['sender']['id'],message['message']['text'])
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.     
                elif 'read' in message:
                    continue
                elif 'delivery' in message:
                    continue

        return HttpResponse()  