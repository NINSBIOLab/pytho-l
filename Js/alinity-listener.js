const net = require('net');
const fs = require('fs');

const DATA_FOLDER = 'C:\\data';
if (!fs.existsSync(DATA_FOLDER)) fs.mkdirSync(DATA_FOLDER, { recursive: true });

let connectionCount = 0;

const server = net.createServer((socket) => {
    const clientIP = socket.remoteAddress.replace(/^::ffff:/, '');
    const connectionId = ++connectionCount;

    console.log(`\n🔌 [${connectionId}] CONNECTED: ${clientIP}`);

    let receivedData = Buffer.from('');
    let state = 'IDLE'; // IDLE, READY_TO_RECEIVE, RECEIVING

    socket.on('data', (chunk) => {
        const hex = chunk.toString('hex');
        console.log(`[${connectionId}] 📥 Received ${chunk.length} bytes: 0x${hex}`);




        if (chunk.length > 0) {
            saveData(chunk, clientIP, connectionId, 'unexpected');
        }

    });

    socket.on('end', () => {
        console.log(`[${connectionId}] ❌ DISCONNECTED`);
        if (receivedData.length > 0) {
            console.log(`[${connectionId}] 💾 Saving ${receivedData.length} bytes on disconnect`);
            saveData(receivedData, clientIP, connectionId, 'disconnect');
        }
    });

    socket.on('error', (err) => {
        console.log(`[${connectionId}] ❌ Socket error: ${err.message}`);
    });

    // Send an initial query to the instrument (try to trigger it)
    setTimeout(() => {
        console.log(`[${connectionId}] 🔍 Sending initial ENQ to instrument...`);
        socket.write(Buffer.from([0x05])); // Send ENQ
        console.log(`[${connectionId}] >>> Sent ENQ (0x05)`);
    }, 100);
});

function saveData(data, clientIP, connectionId, type = 'normal') {
    if (!data || data.length === 0) return;

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${DATA_FOLDER}/data_${timestamp}_conn${connectionId}_${type}.bin`;
    fs.writeFileSync(filename, data);
    console.log(`[${connectionId}] 💾 Saved: ${filename} (${data.length} bytes)`);

    // Save hex dump for analysis
    const hexFile = filename.replace('.bin', '.txt');
    let content = `Connection: ${connectionId}\n`;
    content += `Time: ${new Date().toISOString()}\n`;
    content += `Source: ${clientIP}\n`;
    content += `Type: ${type}\n`;
    content += `Bytes: ${data.length}\n\n`;
    content += `HEX DUMP:\n${'='.repeat(60)}\n`;
    content += data.toString('hex').match(/.{1,64}/g).join('\n');
    content += `\n\nASCII VIEW:\n${'='.repeat(60)}\n`;
    content += data.toString('ascii').replace(/[\x00-\x1f]/g, '.');
    fs.writeFileSync(hexFile, content);
    console.log(`[${connectionId}] 💾 Saved hex: ${hexFile}`);

    // Try to parse if it looks like ASTM
    const ascii = data.toString('ascii');
    if (ascii.includes('|') || ascii.includes('^')) {
        console.log(`\n📊 POSSIBLE ASTM DATA DETECTED:`);
        console.log('='.repeat(60));
        const lines = ascii.split('\r');
        lines.forEach(line => {
            if (line.trim()) {
                console.log(line);
            }
        });
        console.log('='.repeat(60) + '\n');
    }
}

// Listen on all interfaces
server.listen(50020, '0.0.0.0', () => {
    console.log(`
╔════════════════════════════════════════════════════════════════╗
║     ALINITY CI LISTENER - FULL HANDSHAKE                      ║
╠════════════════════════════════════════════════════════════════╣
║  Listening on: 0.0.0.0:50020                                  ║
║  Data folder:  ${DATA_FOLDER}                                  ║
╠════════════════════════════════════════════════════════════════╣
║  Features:                                                    ║
║  - Responds to ENQ with ACK                                   ║
║  - Sends initial ENQ to trigger instrument                    ║
║  - Saves ALL data received                                    ║
║  - Creates hex dumps for analysis                             ║
╠════════════════════════════════════════════════════════════════╣
║  Waiting for connections...                                   ║
╚════════════════════════════════════════════════════════════════╝
`);
});

server.on('error', (err) => {
    console.log(`Server error: ${err.message}`);
});