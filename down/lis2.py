from flask import Flask, render_template_string, jsonify
import sqlite3
import threading
import socket

app = Flask(__name__)

# Simple database to store results
def init_db():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  sample_id TEXT,
                  test_code TEXT,
                  result TEXT,
                  units TEXT)''')
    conn.commit()
    conn.close()

def store_result(sample_id, test_code, result, units):
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("INSERT INTO results (sample_id, test_code, result, units) VALUES (?,?,?,?)",
              (sample_id, test_code, result, units))
    conn.commit()
    conn.close()

# HTML dashboard
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Alinity ci Results</title>
    <meta http-equiv="refresh" content="10">
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Alinity ci Results Dashboard</h1>
    <table>
        <tr><th>Time</th><th>Sample ID</th><th>Test</th><th>Result</th><th>Units</th></tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
            <td>{{ row[4] }}</td>
            <td>{{ row[5] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

@app.route('/')
def dashboard():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, rows=rows)

@app.route('/api/results')
def api_results():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, sample_id, test_code, result, units FROM results ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return jsonify([{'timestamp': r[0], 'sample_id': r[1], 'test': r[2], 'result': r[3], 'units': r[4]} for r in rows])

if __name__ == '__main__':
    init_db()
    # Start listener in background thread
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()
    # Start web server
    app.run(host='0.0.0.0', port=8080, debug=False)