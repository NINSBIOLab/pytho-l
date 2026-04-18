const net = require('net');
const fs = require('fs');

// Create data folder
const DATA_FOLDER = 'C:\\data';
if (!fs.existsSync(DATA_FOLDER)) fs.mkdirSync(DATA_FOLDER, { recursive: true });

// Create server - LISTEN ON ALL INTERFACES
const server = net.createServer((socket) => {
    const clientIP = socket.remoteAddress.replace(/^::ffff:/, '');
    const clientPort = socket.remotePort;

    console.log(`\n✅ CONNECTED: ${clientIP}:${clientPort}`);
    console.log(`⏰ Time: ${new Date().toLocaleString()}`);

    let receivedData = Buffer.from('');

    // When data arrives
    socket.on('data', (chunk) => {
        // Store as Buffer (not string)
        receivedData = Buffer.concat([receivedData, chunk]);
        
        console.log(`📥 Received ${chunk.length} bytes (Total: ${receivedData.length} bytes)`);
        
        // Show HEX (not ASCII text)
        const hexPreview = chunk.toString('hex').slice(0, 100);
        console.log(`🔢 HEX: ${hexPreview}${chunk.toString('hex').length > 100 ? '...' : ''}`);
        
        // Try to show printable characters only
        let printable = '';
        for (let i = 0; i < Math.min(chunk.length, 50); i++) {
            const code = chunk[i];
            if (code >= 32 && code <= 126) {
                printable += String.fromCharCode(code);
            } else if (code === 0x02) printable += '<STX>';
            else if (code === 0x03) printable += '<ETX>';
            else if (code === 0x05) printable += '<ENQ>';
            else if (code === 0x06) printable += '<ACK>';
            else if (code === 0x0d) printable += '<CR>';
            else if (code === 0x0a) printable += '<LF>';
            else printable += `[${code.toString(16)}]`;
        }
        console.log(`📝 Printable: ${printable}`);
    });

    // When connection closes
    socket.on('end', () => {
        console.log(`\n❌ DISCONNECTED: ${clientIP}:${clientPort}`);
        
        // Save everything received
        if (receivedData.length > 0) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `${DATA_FOLDER}/data_${timestamp}.bin`;
            fs.writeFileSync(filename, receivedData);
            console.log(`💾 Saved ${receivedData.length} bytes to: ${filename}`);
            
            // Save hex dump
            const hexFile = filename.replace('.bin', '.txt');
            let hexContent = `Time: ${new Date().toISOString()}\n`;
            hexContent += `Source: ${clientIP}:${clientPort}\n`;
            hexContent += `Total Bytes: ${receivedData.length}\n\n`;
            hexContent += receivedData.toString('hex').match(/.{1,64}/g).join('\n');
            fs.writeFileSync(hexFile, hexContent);
            console.log(`💾 Saved hex dump to: ${hexFile}`);
        } else {
            console.log(`⚠️ No data received`);
        }
    });

    socket.on('error', (err) => {
        console.log(`❌ Error: ${err.message}`);
    });
});

// LISTEN ON ALL INTERFACES - NOT the instrument's IP!
server.listen(50020, '0.0.0.0', () => {
    console.log(`
╔════════════════════════════════════════════════════════╗
║     SIMPLE ALINITY CI LISTENER                         ║
╠════════════════════════════════════════════════════════╣
║  Listening on:  0.0.0.0:50020 (all interfaces)        ║
║  Your computer will accept connections from ANY IP    ║
║  Saving data to: ${DATA_FOLDER}                        ║
╠════════════════════════════════════════════════════════╣
║  Make sure Alinity ci is configured to send to:       ║
║  YOUR COMPUTER'S IP address on port 50020             ║
╠════════════════════════════════════════════════════════╣
║  Waiting for Alinity ci to connect...                 ║
╚════════════════════════════════════════════════════════╝
`);
    
    // Show your computer's IP addresses
    const os = require('os');
    const interfaces = os.networkInterfaces();
    console.log('\n📡 Your computer\'s IP addresses:');
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            if (iface.family === 'IPv4' && !iface.internal) {
                console.log(`   → ${iface.address}`);
            }
        }
    }
    console.log('\n⚙️ Configure Alinity ci to send data to ONE of these IPs on port 50020\n');
});

server.on('error', (err) => {
    console.log(`Server error: ${err.message}`);
});