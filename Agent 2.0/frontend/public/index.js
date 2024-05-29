const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Serve the frontend
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Proxy request to the Flask API
app.post('/api/outfit_recommendations', async (req, res) => {
    try {
        const response = await axios.post('http://127.0.0.1:5000/outfit_recommendations', req.body);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching outfit recommendations' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
