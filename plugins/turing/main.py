from saaya.utils import PluginManager
from saaya.event import GroupMessage
from private import test_groups, turingKey
import requests
import json

url = 'http://openapi.tuling123.com/openapi/api/v2'

data = {
    'reqType': 0,
    'perception': {
        'inputText': {
            'text': 'test'
        }
    },
    'userInfo': {
        'apiKey': turingKey,
        'userId': 'placeholder'
    }
}


def getResponse(sentence, uid):
    data['userInfo']['userId'] = uid
    data['perception']['inputText']['text'] = sentence
    res = requests.post(url, json.dumps(data))
    return json.loads(res.text)['results'][0]['values']['text']


@PluginManager.registerEvent('GroupMessage')
def turing(event: GroupMessage):
    if event.group.uid in test_groups:
        msg = event.message.getContent()
        if msg.startswith(' '):
            event.group.sendMessage(getResponse(msg[1:], event.sender.uid))
