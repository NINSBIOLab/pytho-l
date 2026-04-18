const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 8080;
const DATA_FOLDER = '/data';

app.get('/', (req, res) => {
    res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Alinity ci Dashboard</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1 { color: #2c3e50; }
            .container { max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #3498db; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .result-positive { background-color: #ffcccc; }
            .result-negative { background-color: #ccffcc; }
            .timestamp { color: #7f8c8d; font-size: 12px; }
            .refresh { margin-top: 20px; color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Alinity ci Results Dashboard</h1>
            <div id="results">Loading...</div>
            <div class="refresh">Auto-refreshes every 30 seconds</div>
        </div>
        <script>
            async function loadResults() {
                try {
                    const response = await fetch('/api/results');
                    const data = await response.json();
                    const resultsDiv = document.getElementById('results');
                    
                    if (data.length === 0) {
                        resultsDiv.innerHTML = '<p>No results yet. Waiting for Alinity ci data...</p>';
                        return;
                    }
                    
                    let html = '<table><tr><th>Time</th><th>Sample ID</th><th>Test</th><th>Result</th><th>Units</th><th>Status</th></tr>';
                    
                    data.forEach(row => {
                        html += \`<tr>
                            <td>\${new Date(row.timestamp).toLocaleString()}</td>
                            <td>\${row.sampleId || 'N/A'}</td>
                            <td>\${row.testCode}</td>
                            <td>\${row.result}</td>
                            <td>\${row.units}</td>
                            <td>\${row.abnormalFlag || 'Normal'}</td>
                        </tr>\`;
                    });
                    
                    html += '</table>';
                    resultsDiv.innerHTML = html;
                } catch (error) {
                    console.error('Error loading results:', error);
                    document.getElementById('results').innerHTML = '<p>Error loading results</p>';
                }
            }
            
            loadResults();
            setInterval(loadResults, 30000);
        </script>
    </body>
    </html>
    `);
});

app.get('/api/results', (req, res) => {
    try {
        const files = fs.readdirSync(DATA_FOLDER)
            .filter(f => f.startsWith('results_') && f.endsWith('.json'))
            .sort()
            .reverse()
            .slice(0, 100);
        
        let allResults = [];
        
        files.forEach(file => {
            const content = fs.readFileSync(path.join(DATA_FOLDER, file), 'utf8');
            const data = JSON.parse(content);
            if (data.results) {
                allResults.push(...data.results);
            }
        });
        
        // Filter only result records (R type)
        const testResults = allResults.filter(r => r.recordType === 'R' || r.testCode);
        res.json(testResults.slice(0, 200));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Web dashboard running on http://localhost:${PORT}`);
});