from whoop_client import WhoopClient

client = WhoopClient('./config.yaml')
client.authenticate()
# Use the client...
print(client)
kd = client.get_keydata_all()

print(kd)
