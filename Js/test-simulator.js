const net = require('net');

const ASTM = {
    STX: '\x02',
    ETX: '\x03',
    ENQ: '\x05',
    ACK: '\x06',
    NAK: '\x15',
    CR: '\x0d'
};

function calculateChecksum(message) {
    let checksum = 0;
    const startIdx = message.indexOf(ASTM.STX) + 1;
    const endIdx = message.indexOf(ASTM.ETX);
    
    for (let i = startIdx; i < endIdx; i++) {
        checksum ^= message.charCodeAt(i);
    }
    return checksum.toString(16).toUpperCase().padStart(2, '0');
}

function createASTMMessage() {
    // Build ASTM message
    let message = ASTM.STX;
    message += 'H|\\^&|||Alinity ci|||||||P|E1394-97\r';
    message += 'P|1||123456789||John Doe||M|||19800101\r';
    message += 'O|1|SAMPLE001||^^^GLU^^^ALT^^^AST||202601181200|R\r';
    message += 'R|1|^^^GLU|95|mg/dL|N||F|||202601181200\r';
    message += 'R|2|^^^ALT|32|U/L|N||F|||202601181200\r';
    message += 'R|3|^^^AST|28|U/L|N||F|||202601181200\r';
    message += 'L|1|N\r';
    message += ASTM.ETX;
    message += calculateChecksum(message);
    
    return message;
}

function simulateAlinityConnection() {
    const client = new net.Socket();
    const HOST = '127.0.0.1';
    const PORT = 50020;
    
    client.connect(PORT, HOST, () => {
        console.log('Simulator connected to listener');
        
        // Send ENQ first
        client.write(ASTM.ENQ);
        console.log('Sent: ENQ');
    });
    
    client.on('data', (data) => {
        const response = data.toString('binary');
        console.log(`Received: ${response === ASTM.ACK ? 'ACK' : response === ASTM.NAK ? 'NAK' : 'Other'}`);
        
        if (response === ASTM.ACK) {
            // Send the actual message in chunks
            const message = createASTMMessage();
            console.log(`Sending message (${message.length} bytes)...`);
            
            // Send in chunks to simulate real behavior
            let sent = 0;
            const chunkSize = 50;
            
            const sendChunk = () => {
                const chunk = message.substring(sent, sent + chunkSize);
                if (chunk) {
                    client.write(chunk);
                    sent += chunk.length;
                    setTimeout(sendChunk, 50);
                } else {
                    console.log('Message sent completely');
                }
            };
            
            sendChunk();
        }
    });
    
    client.on('close', () => {
        console.log('Connection closed');
    });
    
    client.on('error', (err) => {
        console.error('Error:', err.message);
    });
}

// Run simulator
simulateAlinityConnection();