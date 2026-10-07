const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');

async function main() {
  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const port = 9222;
  const chrome = spawn(chromePath, [
    '--headless=new',
    `--remote-debugging-port=${port}`,
    '--window-size=1280,800',
    'http://localhost:8080'
  ]);

  // Wait for Chrome remote debugging to be ready
  let versionData = null;
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 200));
    try {
      versionData = await new Promise((resolve, reject) => {
        http.get(`http://localhost:${port}/json/version`, res => {
          let raw = '';
          res.on('data', chunk => raw += chunk);
          res.on('end', () => resolve(JSON.parse(raw)));
        }).on('error', reject);
      });
      if (versionData) break;
    } catch (e) {}
  }

  // Get pages
  const pages = await new Promise((resolve, reject) => {
    http.get(`http://localhost:${port}/json`, res => {
      let raw = '';
      res.on('data', chunk => raw += chunk);
      res.on('end', () => resolve(JSON.parse(raw)));
    }).on('error', reject);
  });

  const page = pages.find(p => p.url.includes('8080')) || pages[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);

  let id = 1;
  function send(method, params = {}) {
    return new Promise((resolve) => {
      const curId = id++;
      const handler = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id === curId) {
          ws.removeEventListener('message', handler);
          resolve(msg.result);
        }
      };
      ws.addEventListener('message', handler);
      ws.send(JSON.stringify({ id: curId, method, params }));
    });
  }

  await new Promise(r => ws.onopen = r);

  // Wait until track cards are populated
  for (let i = 0; i < 50; i++) {
    const res = await send('Runtime.evaluate', {
      expression: 'document.querySelectorAll(".track-card:not(.empty)").length'
    });
    if (res && res.result && res.result.value >= 4) {
      break;
    }
    await new Promise(r => setTimeout(r, 100));
  }

  // Brief pause for render to stabilize
  await new Promise(r => setTimeout(r, 400));

  // If modal mode requested, click hamburger menu
  if (process.argv[3] === 'modal') {
    await send('Runtime.evaluate', {
      expression: 'document.getElementById("btn-config") && document.getElementById("btn-config").click();'
    });
    await new Promise(r => setTimeout(r, 400));
  }

  // Capture screenshot
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  const buffer = Buffer.from(shot.data, 'base64');
  const outPath = process.argv[2] || 'C:\\Users\\comme\\.gemini\\antigravity\\brain\\b10cd155-94b3-420b-88f6-48db248fdbcc\\cockpit_clip_highlight_verified.png';
  fs.writeFileSync(outPath, buffer);
  console.log('SCREENSHOT SAVED to ' + outPath);

  ws.close();
  chrome.kill();
  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
