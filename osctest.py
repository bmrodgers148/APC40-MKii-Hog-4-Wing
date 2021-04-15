from pythonosc.udp_client import SimpleUDPClient

ip = "192.168.1.92"
port = 7001

client = SimpleUDPClient(ip, port)  # Create client


client.send_message("/playback/go/0", [45, 1, 000000 ])  # Send message with int, float and string