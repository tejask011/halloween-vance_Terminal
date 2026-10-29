/**
 * Local Web Server for THE LAST PROCESS Haunted Web Terminal.
 * Powered by Express & @xterm/xterm.
 * Run: npm start
 */

const express = require('express');
const path = require('path');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Serve static web UI files
app.use(express.static(path.join(__dirname, 'web')));

// Serve node_modules for xterm.js assets
app.use('/node_modules', express.static(path.join(__dirname, 'node_modules')));

// Optional Ollama proxy to allow browser frontend to query local open-weight AI without CORS issues
app.post('/api/ollama', async (req, res) => {
  const { prompt, model = 'llama3.2' } = req.body;
  try {
    const response = await fetch('http://127.0.0.1:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        stream: false,
        options: { temperature: 0.7, num_predict: 75 }
      })
    });
    if (response.ok) {
      const data = await response.json();
      return res.json({ success: true, response: data.response });
    }
    res.status(502).json({ success: false, error: 'Ollama returned non-200 status' });
  } catch (err) {
    res.status(503).json({ success: false, error: 'Local Ollama not reachable' });
  }
});

// Fallback to index.html
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'web', 'index.html'));
});

const server = http.createServer(app);

server.listen(PORT, () => {
  console.log('\n====================================================================');
  console.log('       T H E   L A S T   P R O C E S S  -  H A U N T E D   T E R M I N A L');
  console.log('       Hacktoberfest 2026: Ghost in the Machine Edition');
  console.log('====================================================================');
  console.log(`[+] CRT Web Terminal is live at: http://localhost:${PORT}`);
  console.log('    - Floating ghost apparitions & glowing red eyes');
  console.log('    - Retro scanlines, CRT screen shake, and glitch bursts');
  console.log('    - Web Audio ambient reactor hum & typewriter clicks');
  console.log('====================================================================\n');
});
