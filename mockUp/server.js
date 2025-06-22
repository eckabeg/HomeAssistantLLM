const express = require('express');
const WebSocket = require('ws');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server});

let sockets = [];

wss.on('connection', ws => {
    sockets.push(ws);
    console.log('Client connected');

    ws.on('close', () => {
        sockets = sockets.filter(s => s !== ws);
    });
});

// HTTP endpoint to trigger message
app.get('/api/services/light/turn_on', (req, res) => {
    const message = { type: 'UPDATE_STATE', payload: { value: 'Triggered from /send' } };
    sockets.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    });
    res.send('Message sent to clients');
});

app.get('/api/services/light/turn_off', (req, res) => {
    const message = { type: 'UPDATE_STATE', payload: { value: 'Triggered from /send' } };
    sockets.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    });
    res.send('Message sent to clients');
});

app.get('/api/services/climate/set_temperature', (req, res) => {
    const message = { type: 'UPDATE_STATE', payload: { value: 'Triggered from /send' } };
    sockets.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    });
    res.send('Message sent to clients');
});

server.listen(9090, () => {
    console.log('Server running at http://localhost:8000');
});