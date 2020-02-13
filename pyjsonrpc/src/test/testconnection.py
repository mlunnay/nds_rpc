import socket

# Connect to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('192.168.1.3', 50042))
s.connect(('172.16.28.122', 50042))

# Send the data
message = '{"jsonrpc": "2.0", "method": "system.echo", "params": ["test", 2.2, true], "id": 234}'
print 'Sending : "%s"' % message
len_sent = s.send(message)

# Receive a response
response = s.recv(1024)
print 'Received: "%s"' % response

# Clean up
s.close()