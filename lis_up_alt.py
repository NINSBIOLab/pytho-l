import socket
import signal
import sys
from datetime import datetime
import re

HOST = '172.16.1.115'
PORT = 50020

ENQ = b'\x05'
ACK = b'\x06'
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
server.settimeout(1)
server.bind((HOST, PORT))
server.listen(5)

print(f"""
╔════════════════════════════════════════════════════════╗
║         ALINITY CI LISTENER - STANDBY MODE             ║
╠════════════════════════════════════════════════════════╣
║  Status:     Waiting for instrument                    ║
║  Address:    {HOST}:{PORT}                        ║                
╚════════════════════════════════════════════════════════╝
""")

def clean_data(raw_data):
    """Remove STX, ETX, frame numbers, and checksums"""
    # Replace control characters
    cleaned = raw_data.replace(STX, b'').replace(ETX, b'')
    
    # Decode to string
    text = cleaned.decode('ascii', errors='replace')
    
    # Remove frame numbers at start of lines (e.g., "1H" -> "H")
    lines = text.split('\r\n')
    clean_lines = []
    
    for line in lines:
        if line:
            # Remove frame number (digits at start)
            cleaned_line = line
            while cleaned_line and cleaned_line[0].isdigit():
                cleaned_line = cleaned_line[1:]
            clean_lines.append(cleaned_line)
    
    return '\r\n'.join(clean_lines)

# def parse_results(cleaned_text):
#     """Extract and display results"""
#     print("\n" + "="*60)
#     print("📊 RESULTS:")
#     print("="*60)
    
#     lines = cleaned_text.split('\r\n')
    
#     for line in lines:
#         if not line:
#             continue
        
#         parts = line.split('|')
        
#         if line.startswith('P'):
#             # Patient record
#             if len(parts) > 5:
#                 print(f"👤 Patient: {parts[5]}")
                
#         elif line.startswith('O'):
#             # Order record
#             if len(parts) > 2:
#                 print(f"📋 Sample ID: {parts[2]}")
#             if len(parts) > 3:
#                 print(f"   Tests: {parts[3]}")
                
#         elif line.startswith('R'):
#             # Result record
#             if len(parts) > 3:
#                 test_name = parts[3].split('^')[1] if '^' in parts[3] else parts[3]
#                 result_value = parts[4] if len(parts) > 4 else ''
#                 units = parts[5] if len(parts) > 5 else ''
#                 reference = parts[8] if len(parts) > 8 else ''
                
#                 print(f"\n🔬 {test_name}:")
#                 print(f"   Result: {result_value} {units}")
#                 print(f"   Reference: {reference}")
                
#         elif line.startswith('L'):
#             print(f"\n🏁 End of message")
    
#     print("="*60)

# def split_messages(cleaned_text):
#     """Split ASTM text into separate messages using H...L blocks"""
#     lines = cleaned_text.split('\r\n')
    
#     messages = []
#     current_msg = []

#     for line in lines:
#         if line.startswith('H'):   # Start of new message
#             if current_msg:
#                 messages.append(current_msg)
#                 current_msg = []
#         current_msg.append(line)

#         if line.startswith('L'):   # End of message
#             messages.append(current_msg)
#             current_msg = []

#     # Catch any leftover
#     if current_msg:
#         messages.append(current_msg)

#     return messages


# def parse_single_message(lines, msg_no=1):
#     """Parse one ASTM message"""
#     print("\n" + "="*60)
#     print(f"📦 MESSAGE {msg_no}")
#     print("="*60)

#     for line in lines:
#         if not line:
#             continue

#         parts = line.split('|')

#         if line.startswith('P'):
#             if len(parts) > 5:
#                 print(f"👤 Patient: {parts[5]}")

#         elif line.startswith('O'):
#             if len(parts) > 2:
#                 print(f"📋 Sample ID: {parts[2]}")
#             if len(parts) > 4:
#                 test_info = parts[4]
#                 test_name = test_info.split('^')[3] if '^' in test_info else test_info
#                 print(f"🧪 Test: {test_name}")

#         elif line.startswith('R'):
#             if len(parts) > 3:
#                 test_info = parts[2]
#                 test_name = test_info.split('^')[3] if '^' in test_info else test_info

#                 result_value = parts[3] if len(parts) > 3 else ''
#                 units = parts[4] if len(parts) > 4 else ''
#                 reference = parts[5] if len(parts) > 5 else ''

#                 print(f"\n🔬 {test_name}")
#                 print(f"   Result: {result_value} {units}")
#                 print(f"   Reference: {reference}")

#         elif line.startswith('L'):
#             print("\n🏁 End of message")

#     print("="*60)

# def extract_basic_data(text):
#     lines = text.split('\n')

#     machine = ''
#     test_name = ''
#     result = ''
#     reference = ''

#     for line in lines:
#         parts = line.split('|')

#         # 🔹 Header → Machine name
#         if line.startswith('H'):
#             if len(parts) > 4:
#                 machine_info = parts[4]
#                 machine = machine_info.split('^')[0]

#         # 🔹 Result → Test, Value, Reference
#         elif line.startswith('R'):
#             if len(parts) > 5:
#                 test_info = parts[2]
#                 test_name = test_info.split('^')[3] if '^' in test_info else test_info

#                 result = parts[3]
#                 reference = parts[5]

#     # 🔹 Output
#     print("Machine :", machine)
#     print("Test    :", test_name)
#     print("Result  :", result)
#     print("Ref     :", reference)

# def parse_results(cleaned_text):
#     """Main function: handles single + multiple messages"""
#     messages = split_messages(cleaned_text)

#     print(f"\n✅ Total Messages Found: {len(messages)}")

#     for i, msg in enumerate(messages, start=1):
#         parse_single_message(msg, i) 

def parse_results(cleaned_text):
    """Extract and display results (single + multiple messages)"""
    
    print("\n" + "="*60)
    print("📊 RESULTS:")
    print("="*60)

    lines = cleaned_text.split('\r\n')

    messages = []
    current_msg = []

    # 🔹 Step 1: Split messages
    for line in lines:
        if not line:
            continue

        if line.startswith('H'):   # start of new message
            if current_msg:
                messages.append(current_msg)
                current_msg = []

        current_msg.append(line)

        if line.startswith('L'):   # end of message
            messages.append(current_msg)
            current_msg = []

    if current_msg:
        messages.append(current_msg)

    # 🔹 Step 2: Parse each message (reuse your logic)
    for msg_no, msg_lines in enumerate(messages, start=1):

        print(f"\n📦 MESSAGE {msg_no}")
        print("-"*60)

        for line in msg_lines:
            parts = line.split('|')

            if line.startswith('P'):
                if len(parts) > 5:
                    print(f"👤 Patient: {parts[5]}")

            elif line.startswith('O'):
                if len(parts) > 2:
                    print(f"📋 Sample ID: {parts[2]}")
                if len(parts) > 4:
                    match = re.search(r'\^\^\^(\d+)\^([^^]+)\^', parts[4])
                    if match:
                        test_id = match.group(1)
                        test_name = match.group(2)

                        print("Test ID  :", test_id)
                        print("Test Name:", test_name) 

            elif line.startswith('R'):
                if len(parts) > 5:

                    # 🔥 FIXED: correct ASTM field positions
                    test_info = parts[2]

                    # Only FINAL result (^F)
                    if '^F' not in test_info:
                        continue

                    test_name = test_info.split('^')[3] if '^' in test_info else test_info
                    result_value = parts[3]
                    units = parts[4]
                    reference = parts[5]

                    print(f"\n🔬 {test_name}:")
                    print(f"   Result: {result_value} {units}")
                    print(f"   Reference: {reference}")

            elif line.startswith('L'):
                print("\n🏁 End of message")

    print("="*60)

while running:
    try:
        client, addr = server.accept()
        
        all_data = b''
        
        while running:
            try:
                client.settimeout(10)
                data = client.recv(4096)
                
                if not data:
                    break
                
                if data == ENQ:
                    client.send(ACK)
                    continue
                
                if data == EOT:
                    break
                
                all_data += data
                client.send(ACK)
                
            except socket.timeout:
                break
        
        if all_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save raw data
            raw_filename = f"raw_{timestamp}.bin"
            with open(raw_filename, 'wb') as f:
                f.write(all_data)
            
            # Clean the data
            cleaned = clean_data(all_data)
            
            # Save cleaned data
            clean_filename = f"result_{timestamp}.txt"
            with open(clean_filename, 'w') as f:
                f.write(cleaned)
            
            print(f"\n📥 Results saved: {clean_filename}")
            
            # Parse and display
            parse_results(cleaned)
            
            print(f"\n   ✅ Back to standby mode...\n")
        
        client.close()
        
    except socket.timeout:
        continue
    except Exception as e:
        if running:
            print(f"Error: {e}")

print("Server closed")


# import socket
# import signal
# import sys
# from datetime import datetime

# HOST = '172.16.1.115'  # Your machine's IP
# PORT = 50020

# ENQ = b'\x05'
# ACK = b'\x06'
# EOT = b'\x04'

# running = True

# def signal_handler(sig, frame):
#     global running
#     print("\n\n🛑 Shutting down...")
#     running = False
#     sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# # Set timeout so accept() doesn't block forever
# server.settimeout(1)
# server.bind((HOST, PORT))
# server.listen(5)

# print(f"""
# ╔════════════════════════════════════════════════════════╗
# ║         ALINITY CI LISTENER - STANDBY MODE             ║
# ╠════════════════════════════════════════════════════════╣
# ║  Status:     Waiting for instrument                    ║
# ║  Address:    {HOST}:{PORT}                        ║        
# ║--------------------------------------------------------║
# ║  Ready to receive results                              ║
# ║  Press Ctrl+C to stop                                  ║
# ╚════════════════════════════════════════════════════════╝
# """)

# while running:
#     try:
#         # This will timeout every 1 second and check running flag
#         client, addr = server.accept()
        
#         all_data = b''
#         got_data = False
        
#         while running:
#             try:
#                 client.settimeout(10)
#                 data = client.recv(4096)
                
#                 if not data:
#                     break
                
#                 # Handle ENQ - respond with ACK
#                 if data == ENQ:
#                     client.send(ACK)
#                     continue
                
#                 # Handle EOT - end of transmission
#                 if data == EOT:
#                     break
                
#                 # Collect data
#                 all_data += data
#                 got_data = True
#                 client.send(ACK)
                
#             except socket.timeout:
#                 break
#             except Exception as e:
#                 print(f"Error receiving data: {e}")
#                 break
        
#         # Save if we got data
#         if got_data and all_data:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"result_{timestamp}.txt"
            
#             with open(filename, 'wb') as f:
#                 f.write(all_data)
            
#             print(f"\n📥 Result received and saved: {filename} ({len(all_data)} bytes)")
            
#             # Print summary
#             text = all_data.decode('ascii', errors='replace')
#             print(all_data)
#             print(text)

#             if 'R|' in text:
#                 lines = text.split('\r')
#                 for line in lines:
#                     if line.startswith('R|'):
#                         parts = line.split('|')
#                         if len(parts) >= 5:
#                             print(f"   🔬 {parts[3]} = {parts[4]} {parts[5] if len(parts) > 5 else ''}")
            
#             print(f"   ✅ Result saved. Back to standby mode...\n")
        
#         client.close()
        
#     except socket.timeout:
#         # Timeout occurred, just loop back and check running flag
#         continue
#     except Exception as e:
#         if running:
#             print(f"Error: {e}")

# print("Server closed successfully")

# import socket
# import signal
# import sys
# from datetime import datetime

# HOST = '172.16.1.115'
# PORT = 50020

# ENQ = b'\x05'
# ACK = b'\x06'
# EOT = b'\x04'

# running = True

# def signal_handler(sig, frame):
#     global running
#     print("\n\n🛑 Shutting down...")
#     running = False
#     sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server.bind((HOST, PORT))
# server.listen(5)

# print(f"""
# ╔════════════════════════════════════════════════════════╗
# ║         ALINITY CI LISTENER - STANDBY MODE             ║
# ╠════════════════════════════════════════════════════════╣
# ║  Status:     Waiting for instrument                    ║
# ║  Address:    {HOST}:{PORT}                        ║        
# ║--------------------------------------------------------║
# ║              Ready to receive results                  ║
# ╚════════════════════════════════════════════════════════╝
# """)

# while running:
#     try:
#         client, addr = server.accept()
        
#         all_data = b''
#         got_data = False
        
#         while True:
#             try:
#                 client.settimeout(10)
#                 data = client.recv(4096)
                
#                 if not data:
#                     break
                
#                 # Handle ENQ - respond with ACK
#                 if data == ENQ:
#                     client.send(ACK)
#                     continue
                
#                 # Handle EOT - end of transmission
#                 if data == EOT:
#                     break
                
#                 # Collect data
#                 all_data += data
#                 got_data = True
#                 client.send(ACK)
                
#             except socket.timeout:
#                 break
        
#         # Save if we got data
#         if got_data and all_data:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"result_{timestamp}.txt"
            
#             with open(filename, 'wb') as f:
#                 f.write(all_data)
            
#             print(f"\n📥 Result received and saved: {filename} ({len(all_data)} bytes)")
            
#             # Optional: Print a summary
#             text = all_data.decode('ascii', errors='replace')

#             # with open("Text.txt", 'wb') as f:
#             #     f.write(text)

#             if 'R|' in text:
#                 lines = text.split('\r')
#                 for line in lines:
#                     print(line)   
#                     if line.startswith('R|'):
#                         parts = line.split('|')
#                         if len(parts) >= 5:
#                             print(f"   🔬 {parts[3]} = {parts[4]} {parts[5] if len(parts) > 5 else ''}")
            
#             print(f"   ✅ Result saved. Back to standby mode...\n")
        
#         client.close()
        
#     except Exception as e:
#         if running:
#             print(f"Error: {e}")

# print("Server closed")