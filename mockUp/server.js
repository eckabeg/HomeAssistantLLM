const express = require('express');
const WebSocket = require('ws');
const http = require('http');

const app = express();
app.use(express.json());
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
app.post('/api/services/light/turn_on', (req, res) => {
    const message = { type: 'TURN_ON', payload: { value: req.body } };
    sockets.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    });
    res.send('Message sent to clients');
});

app.post('/api/services/light/turn_off', (req, res) => {
    const message = { type: 'TURN_OFF', payload: { value: req.body } };
    sockets.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    });
    res.send('Message sent to clients');
});

app.post('/api/services/climate/set_temperature', (req, res) => {
    const message = { type: 'SET_TEMPERATURE', payload: { value: req.body } };
    sockets.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    });
    res.send('Message sent to clients');
});

server.listen(9090, () => {
    console.log('Server running at http://localhost:9090');
});