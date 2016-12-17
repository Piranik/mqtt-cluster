#!/usr/bin/python3
import sys
import _thread
import argparse
import time
import uuid

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    if args.server:
        client.subscribe("server/#")
    else:
        client.subscribe("client/"+args.uuid + "/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if "server" in msg.topic:
        print ("Topic: ", msg.topic+"\nMessage: "+str(msg.payload))  
        send_message("client/"+msg.payload.decode('utf-8')+'/something',"thanks")      
    elif "client" in msg.topic:
        print ("Topic: ", msg.topic+"\nMessage: "+str(msg.payload))        

def subscribe(threadName):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.host, args.port, 60)
    client.loop_forever()

def send_message(topic, message):
    mqttc = mqtt.Client("python_pub")
    mqttc.connect(args.host, args.port)
    mqttc.publish(topic, message)
    mqttc.loop(2) #timeout = 2s

def keep_alive(uuid):
    while True:
        send_message("server/keepalive",uuid)
        time.sleep(3)

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
parser.add_argument("-c", "--client", action="store_true",
                    help="set as client")
parser.add_argument("-s", "--server", action="store_true",
                    help="set as server")
parser.add_argument("-a", "--host", type=str,
                    help="MQTT broker address")
parser.add_argument("-p", "--port", type=int,default=1883,
                    help="MQTT broker port")
parser.add_argument("-m", "--message", type=str,
                    help="send message to the network")
parser.add_argument("-n", "--channel", type=str,
                    help="channel to send message")
parser.add_argument("-u", "--uuid", type=str,default=str(uuid.uuid4()),
                    help="id of the node")
args = parser.parse_args()
print(args)
if not args.client and not args.server:
    print("Must select --server or --client !")
    sys.exit(1)

if args.client:
    try:
        _thread.start_new_thread( keep_alive, (args.uuid, ) )
        _thread.start_new_thread( subscribe, ("Thread-1", ) )
    except:
       print ("Error: unable to start thread")
else:
    try:
       _thread.start_new_thread( subscribe, ("Thread-1", ) )
    except:
       print ("Error: unable to start thread")
while 1:
   time.sleep(1000)
