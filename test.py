from wit import Wit

def send(request, response):
    print 'Sending to user...', response['text']
def my_action(request):
    print 'Received from user...', request['text']

actions = {
    'send': send,
    'my_action': my_action,
}

access_token = '5U7WOSQ7QB3OBE47OFRUHQDLRKH6PF7P'

client = Wit(access_token=access_token, actions=actions)
resp = client.message('la chota quiere que me baje del coche por pasarme un semaforo ayuda')
#print str(resp)

asText = ""
for i in resp['entities']:
	section = resp['entities'][i] #number, entitie, etc
	for entitie in section:
		asText+='%s %s% \n'%(entitie['confidence'],entitie['value'])
		print entitie
	