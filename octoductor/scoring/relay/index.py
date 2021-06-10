import json

print('Loading function')

def handler(event, context):
    print("Received event for relay: " + json.dumps(event))
    return event
