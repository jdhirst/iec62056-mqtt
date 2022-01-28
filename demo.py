from iec62056.client import Client

client = Client(port='/dev/ttyUSB0', target_baudrate=300)
client.read()
for d in client.data_sets:
    print(d)