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
resp = client.message('El poli me detuvo por venir hablando en el celular')
print 'Yay, got Wit.ai response: ' + str(resp)
