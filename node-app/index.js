'use strict';

const express = require('express');
const fs = require('fs');
const path = require('path');

const PORT = parseInt(process.env.PORT || '3000', 10);
const APP_NAME = process.env.APP_NAME || 'node-app';
const LOG_LEVEL = (process.env.LOG_LEVEL || 'info').toLowerCase();
const LOG_DIR = process.env.LOG_DIR || '/var/log/node-app';

const app = express();

function log(line) {
  const msg = `${new Date().toISOString()} ${APP_NAME} ${line}`;
  console.log(msg);

  try {
    fs.mkdirSync(LOG_DIR, { recursive: true });
    fs.appendFileSync(path.join(LOG_DIR, 'app.log'), msg + '\n', { encoding: 'utf8' });
  } catch (_) {
    // stdout is the primary log destination; file logging is best-effort.
  }
}

app.get('/', (req, res) => {
  const payload = {
    service: APP_NAME,
    language: 'node',
    message: 'Hello from Express',
    timestamp: new Date().toISOString(),
  };

  if (LOG_LEVEL !== 'silent') {
    log(`GET / ${JSON.stringify(payload)}`);
  }

  res.status(200).json(payload);
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.listen(PORT, '0.0.0.0', () => {
  log(`Listening on 0.0.0.0:${PORT}`);
});

