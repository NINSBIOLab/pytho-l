import socket
import signal
import sys

HOST = '0.0.0.0'
PORT = 50020

ENQ = b'\x05'
ACK = b'\x06'
NAK = b'\x15'
EOT = b'\x04'
STX = b'\x02'
ETX = b'\x03'

running = True

def signal_handler(sig, frame):
    global running
    print("\n\n🛑 Shutting down...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
server.settimeout(1)

print(f"Listening on {HOST}:{PORT}")
print("Waiting for Alinity ci...")
print("Press Ctrl+C to stop\n")

try:
    while running:
        try:
            client, addr = server.accept()
            print(f"\n✅ Connected: {addr[0]}:{addr[1]}")
            
            # Collect all data from this connection
            all_data = b''
            message_complete = False
            
            while running:
                try:
                    client.settimeout(2)
                    data = client.recv(4096)
                    if not data:
                        break
                    
                    print(f"📥 Received {len(data)} bytes")
                    
                    # Handle ENQ (instrument wants to send)
                    if data == ENQ:
                        client.send(ACK)
                        print(">>> Sent ACK")
                        continue
                    
                    # Handle EOT (end of transmission)
                    if data == EOT:
                        print(">>> EOT received - transmission complete")
                        message_complete = True
                        break
                    
                    # Collect all other data
                    all_data += data
                    
                    # Send ACK for each chunk
                    client.send(ACK)
                    print(">>> Sent ACK")
                    
                except socket.timeout:
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    break
            
            # After connection closes, save everything at once
            if all_data:
                print(f"\n{'='*60}")
                print(f"🎯 TOTAL DATA RECEIVED: {len(all_data)} bytes")
                print(f"{'='*60}")
                
                # Save to file
                filename = f"alinity_data_{addr[0]}.bin"
                with open(filename, 'wb') as f:
                    f.write(all_data)
                print(f"💾 Saved to: {filename}")
                
                # Print readable version
                print(f"\n📝 READABLE DATA:")
                print(f"{'='*60}")
                
                # Decode and clean
                text = all_data.decode('ascii', errors='replace')
                # Replace control chars
                text = text.replace('\x02', '[STX]')
                text = text.replace('\x03', '[ETX]')
                text = text.replace('\x04', '[EOT]')
                text = text.replace('\x05', '[ENQ]')
                text = text.replace('\x06', '[ACK]')
                
                # Split by lines
                lines = text.split('\r')
                for line in lines:
                    if line.strip():
                        print(line)
                
                print(f"{'='*60}\n")
            
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