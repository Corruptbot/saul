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
                    if message['postback']['payload'] == 'START':
                        initConversation(message)
                        
                    print message['postback']['payload']
                    continue
                elif 'message' in message:
                    {u'timestamp': 1485649341730, u'message': {u'text': u'Tramites', u'mid': u'mid.1485649341730:37fcf12738', u'seq': 35426, u'quick_reply': {u'payload': u'i_tramite'}}, u'recipient': {u'id': u'759711370868773'}, u'sender': {u'id': u'1751510654874973'}}

                    if 'quick_reply' in message['message']: #SOLO JALARA CON GEOLOCATION ?
                        payload = message['message']['quick_reply']['payload']
                        print payload
                        if payload == 'i_tramite':
                            bot.send_text_message(message['sender']['id'],'Aun no esta disponible')
                            initConversation()
                        elif payload == 'i_transito':
                            initTransit(message)
                        elif payload == '2_moto':
                            pass
                        elif payload == '2_auto':
                            askAutoContext(message)
                        elif payload == '2_bici':
                            pass
                        else:
                            print "QUICK"
                        continue
        
                    if 'attachments' in message['message']:
                        print message['message']['attachments']
                        
                        for attachment in message['message']['attachments']:
                            if attachment['type']=='location':
                                coor = attachment['payload']['coordinates']
                                print coor['lat']
                                print coor['long']
                        continue
                    

                    sent_text = message['message']['text']
                    if sent_text =='reset':
                        initConversation(message)
                    else:
                        bot.send_text_message(message['sender']['id'],message['message']['text'])
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.     
                elif 'read' in message:
                    continue
                elif 'delivery' in message:
                    continue
        return HttpResponse()

def initConversation(message): 
    sender = message['sender']['id']
    post_facebook_message(sender, "Bienvenido\nRecuerda mantener la calma en todo momento, en que puedo ayudarte?" )
    quicks = []
    button = QuickReply(content_type="text",title='Tramites',payload='i_tramite',image_url='http://www.cecyteh.edu.mx/images/menu/Tramites_servicios2.png')
    quicks.append(button)
    button = QuickReply(content_type="text",title='Transito',payload='i_transito',image_url='http://www.gomesdelima.adv.br/wp-content/uploads/2015/08/icon-transito-150x150.png')
    quicks.append(button)
    bot.send_quick_replies(message['sender']['id'],"Selecciona",quicks)

def initTransit(message): 
    sender = message['sender']['id']
    quicks = []
    button = QuickReply(content_type="text",title='Moto',payload='2_moto',image_url='http://www.fancyicons.com/free-icons/232/transport/png/256/motorcycle_256.png')
    quicks.append(button)
    button = QuickReply(content_type="text",title='Automovil',payload='2_auto',image_url='https://image.freepik.com/iconos-gratis/delantera-del-coche-sedan_318-64441.jpg')
    quicks.append(button)
    button = QuickReply(content_type="text",title='Bicicleta',payload='2_bici',image_url='http://www.iconarchive.com/download/i95552/iconsmind/outline/Bicycle.ico')
    quicks.append(button)
    bot.send_quick_replies(message['sender']['id'],"En que vehiculo te encuentras?",quicks)

def askAutoContext(message): 
    sender = message['sender']['id']



