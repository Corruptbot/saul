#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
# Create your views here.
import json, requests, random, re, os
from pprint import pprint
from django.views import generic
from django.http.response import HttpResponse
from fbWrapper.bot import Bot, Element, Button,QuickReply,QuickLocationReply
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import *
from reglamento import *
from wit import Wit

def send(request, response):print 'Sending to user...', response['text']
def my_action(request):print 'Received from user...', request['text']

actions = {'send': send,'my_action': my_action}
witT = '5U7WOSQ7QB3OBE47OFRUHQDLRKH6PF7P'
PAGE_ACCESS_TOKEN = 'EAAUTEIO8s5ABAA4y3lVMrXsZBEiyGJ6isIvcLGhbfYdMzjWoBmvNZBUObrt9bHikhLKugvOuLVjvJ16w8DAVxL3ZAILWmK8KfPMiAZAggqyDRlyJ28ONdXpoeUw1JJhgQpPbmaD16HuAQkihebd9JL8HS33IHlgqHkNdNJrvWAZDZD'#os.getenv('token') #cargar al server
VERIFY_TOKEN = "v4l1d4710n70k3n"

WIT = Wit(access_token=witT, actions=actions)
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
                user,created = Account.objects.get_or_create(fb_user=int(message['sender']['id']))
                print message
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                #if 'read' in message: #Lo acaba de leer
                if 'postback' in message:
                    payload = message['postback']['payload']
                    if payload == 'START':
                        initConversation(message)
                    elif payload == 'velocidad':
                        quicks = []
                        quicks.append(QuickLocationReply() )
                        bot.send_quick_replies(user.fb_user,"Donde te encuentras?",quicks)
                        user.setState(33) #En vehiculo y relacionado a velocidad
                    elif payload == 'circular':
                        for text in giro_indebido:
                            bot.send_text_message(user.fb_user,text)

                    elif payload == 'alto':
                        for text in alto_info:
                            bot.send_text_message(user.fb_user,text)

                    print message['postback']['payload']
                    continue
                elif 'message' in message:
                    if 'attachments' in message['message']:
                        for attachment in message['message']['attachments']:
                            if attachment['type']=='location':
                                coor = attachment['payload']['coordinates']
                                for i in velocidad_info:
                                    bot.send_text_message(user.fb_user,i)
                                current_cost = 73.57
                                bot.send_text_message(user.fb_user,"El limite de velocidad en: Calle San Luis Potosi es 40km/hr que pertenece a Fracción I,II y III\nPrecio de la multa")
                                bot.send_image_url(user.fb_user,"https://s3-us-west-2.amazonaws.com/cuadra-apps/Art9.png")                                
                                bot.send_text_message(user.fb_user,"La Unidad de Cuenta de CDMX vale %s, la multa costaria entre $%s y $%s"%(current_cost,current_cost*10,current_cost*20))
                                bot.send_text_message(user.fb_user,"Podrias compartirme la matricula del oficial?")
                                
                                #print coor['lat']
                                #print coor['long']
                        continue
                    elif 'quick_reply' in message['message']:
                        payload = message['message']['quick_reply']['payload']

                        if payload == 'i_tramite':
                            bot.send_text_message(message['sender']['id'],'Aun no esta disponible')
                            initConversation(message)
                        elif payload == 'i_transito':
                            initTransit(message)
                            
                        elif payload == '2_moto':
                            pass
                        elif payload == '2_auto':
                            askAutoContext(message)
                        elif payload == 'correct_proc':
                            #BYE
                            pass
                        elif payload == 'wrong_proc':
                            askProcProblems(user.fb_user)
                            pass
                        else:
                            print "QUICK"
                        continue
         
                    sent_text = message['message']['text']
                    resp = WIT.message(sent_text)
                    
                    asText = ""
                    
                    vals = set()
                    nums = set()
                    for i in resp['entities']:
                        section = resp['entities'][i] #number, entitie, etc
                        for entitie in section:
                            print type(entitie['confidence'])
                            if entitie['confidence'] == 1: #If is number
                                nums.add(entitie['value'])
                            else:
                                vals.add(entitie['value'])
                            asText+=('%s %s \n'%(entitie['confidence'],entitie['value']))
                            print entitie

                    if 'ayuda' in vals or 'Saludo' in vals:
                        initConversation()

                    if 'policia' in vals and nums: #Match de policia y matricula
                        for element in nums:    #iterar entre numeros obtenidos
                            if len(str(element)) == 6: #MAtricula
                                poli = PoliciaTransito.objects.filter(p_id=int(element)).first()

                                if poli:
                                    bot.send_text_message(user.fb_user,'El policia con matricula '+str(poli.p_id)+' y nombre '+poli.name+" tiene la autoridad para infraccionarte ")
                                    askRightProcess(user.fb_user)
                                else:
                                    bot.send_text_message(user.fb_user,"El policia no tiene la autoridad para infraccionarte ")
                            break
                    if 'celular' in vals:
                        for i in distractor:
                            bot.send_text_message(user.fb_user,i)
                        continue    


                        #bot.send_text_message(user.fb_user, asText)
                    else:
                        pass
                        #initConversation(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.     
                elif 'read' in message:
                    continue
                elif 'delivery' in message:
                    continue
        return HttpResponse()

def initConversation(message): 
    sender = message['sender']['id']
    print sender
    post_facebook_message(sender, "Bienvenid@! en que puedo ayudarte?" )
    quicks = []
    button = QuickReply(content_type="text",title='Tramites',payload='i_tramite',image_url='http://www.cecyteh.edu.mx/images/menu/Tramites_servicios2.png')
    quicks.append(button)
    button = QuickReply(content_type="text",title='Transito',payload='i_transito',image_url='http://www.gomesdelima.adv.br/wp-content/uploads/2015/08/icon-transito-150x150.png')
    quicks.append(button)
    bot.send_quick_replies(message['sender']['id'],"Selecciona",quicks)

def initTransit(message): 
    sender = message['sender']['id']
    post_facebook_message(sender, 'Recuerda mantener la calma en todo momento y solicita la matricula y nombre del oficial')
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
    buttons = []
    button = Button(type="postback",title='Giro indebido',payload='circular')
    buttons.append(button)
    button = Button(type="postback",title='Exceso de velocidad',payload='velocidad')
    buttons.append(button)
    button = Button(type="postback",title='Pasarse alto',payload='alto')
    buttons.append(button)
    post_facebook_message(sender,"El agente no puede exigirte que bajes de tu auto si la infracción que cometiste no es grave, no permitas que te presionen\n")
    post_facebook_message(sender,"Nadie puede revisar tu auto sin una orden judicial")
    bot.send_button_message(sender,"Si es algun otro podrias explicarmelo o ayudame a identificar al oficial que te detuvo enviandome su matricula?",buttons)

def askRightProcess(sender):
    bot.send_text_message(sender,"EL PROCESO DE PAGAR MULTAS ES:")
    button = QuickReply(content_type="text",title='Si',payload='correct_proc')
    quicks.append(button)
    button = QuickReply(content_type="text",title='No',payload='wrong_proc')
    quicks.append(button)
    bot.send_quick_replies(sender,"Tu proceso se llevo asi?",quicks)

def askProcProblems(sender): 
    buttons = []
    button = Button(type="postback",title='Dinero en Efectivo(Mordida)',payload='circular')
    buttons.append(button)
    button = Button(type="postback",title='Violencia verbal',payload='velocidad')
    buttons.append(button)
    button = Button(type="postback",title='Abuso de Autoridad',payload='alto')
    buttons.append(button)
    bot.send_button_message(sender,"Otro?",buttons)

'''
curl -X POST -H "Content-Type: application/json" -d '{
  "setting_type" : "call_to_actions",
  "thread_state" : "existing_thread",
  "call_to_actions":[
    {
      "type":"postback",
      "title":"Ayuda",
      "payload":"START"
    },
    {
      "type":"postback",
      "title":"Descubre",
      "payload":"DISCOVER"
    }
  ]
}' "https://graph.facebook.com/v2.6/me/thread_settings?access_token=EAAUTEIO8s5ABAN8IFCYiFFR382wqvsRhfMJmS4TOQxBzmfGvoO4i0sgOcBptBApZCj5YT5ll7dZCTRZCD1B0e8zaZA85tU1PCgEUoLY710Rc4NgmQH5TvOwZBwFYSqF4MHCQB9fnn9FeRCX1J5EYzo7cBusBFAzrGYwsM5o23qwZDZD"
'''

