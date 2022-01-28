import json,re,multiprocessing,time
from iec62056.client import Client
from iec62056.dataset import DataSet
from paho.mqtt import client as mqtt_client

# Setup MQTT
broker = '172.16.19.76'
port = 1883
client_id = 'python-mqtt-1'
username = 'smartmeter'
password = 'Passw0rd'

# Setup meter
meter = Client(port='/dev/ttyUSB0', target_baudrate=300)

def snakify(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2.replace(" ", "_")

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, msg):
    msg_count = 0
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def update():
    meter.read()
    mclient = connect_mqtt()

    messages = []
    for d in meter.data_sets:
        topic = "smartmeter/" + snakify(d.measure_display) + "/" + snakify(d.mode_display)
        print("Topic: " + topic)
        for v in d.values:
            publish(mclient, topic, v.value)

def main():
    p = multiprocessing.Process(target=update)
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(30)

    # If thread is still active
    if p.is_alive():
        print("update is stuck, terminating it.")
        p.terminate()
        p.join()
    
if __name__ == "__main__":
    main()