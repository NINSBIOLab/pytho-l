import socket
import signal
import sys

HOST = '0.0.0.0'
PORT = 50020

ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'

# Global flag for shutdown
running = True

def signal_handler(sig, frame):
    global running
    print("\n\n🛑 Shutting down...")
    running = False
    sys.exit(0)

# Register Ctrl+C handler
signal.signal(signal.SIGINT, signal_handler)

# Create server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
server.settimeout(1)  # Allow checking running flag every second

print(f"Listening on {HOST}:{PORT}")
print("Waiting for Alinity ci...")
print("Press Ctrl+C to stop\n")

try:
    while running:
        try:
            client, addr = server.accept()
            print(f"\n✅ Connected: {addr[0]}:{addr[1]}")
            
            while running:
                try:
                    client.settimeout(1)
                    data = client.recv(4096)
                    if not data:
                        break
                    
                    print(f"\n📥 Received {len(data)} bytes: {data}")
                    
                    if data == ENQ:
                        client.send(ACK)
                        # print(">>> Sent ACK")
                    elif data == EOT:
                        # print(">>> EOT received")
                        break
                    else:
                        # print(f"Data hex: {data.hex()}")
                        # print(f"Data ASCII: {data.decode('ascii', errors='replace')}")
                        client.send(ACK)
                        print(">>> Sent ACK")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    break
            
            client.close()
            print(f"❌ Disconnected\n")
            
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"Accept error: {e}")
                
except KeyboardInterrupt:
    print("\n\n🛑 Stopped by user")
finally:
    server.close()
    print("Server closed")
    
# import socket

# HOST = '0.0.0.0'
# PORT = 50020

# ENQ = b'\x05'
# ACK = b'\x06'
# EOT = b'\x04'

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server.bind((HOST, PORT))
# server.listen(5)

# print(f"Listening on {HOST}:{PORT}")
# print("Waiting for Alinity ci...\n")

# while True:
#     client, addr = server.accept()
#     print(f"\n✅ Connected: {addr[0]}:{addr[1]}")
    
#     while True:
#         try:
#             data = client.recv(8192)
#             if not data:
#                 break
            
#             print(f"\n📥 Received: {data}")
            
#             # Respond to ENQ with ACK
#             if data == ENQ:
#                 client.send(ACK)
#                 # print(">>> Sent ACK (0x06)")
#             # Respond to EOT with nothing (end transmission)
#             elif data == EOT:
#                 # print(">>> EOT received, ending transmission")
#                 break
#             else:
#                 # This is actual data!
#                 # print(f"\n🎯 DATA RECEIVED:")
#                 # print(f"Hex: {data.hex()}")
#                 # print(f"ASCII: {data.decode('ascii', errors='replace')}")
                
#                 # Send ACK for data too
#                 client.send(ACK)
#                 # print(">>> Sent ACK")
                
#         except Exception as e:
#             print(f"Error: {e}")
#             break
    
#     client.close()
#     print(f"❌ Disconnected\n")