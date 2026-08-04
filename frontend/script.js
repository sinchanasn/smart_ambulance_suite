// Smart Ambulance Suite - Dynamic Frontend Controller

document.addEventListener('DOMContentLoaded', () => {
  initForms();
  initECGCanvas();
  initLiveVitals();
});

// Form Submissions and Navigation
function initForms() {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      window.location.href = 'patient.html';
    });
  }

  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    signupForm.addEventListener('submit', (e) => {
      e.preventDefault();
      window.location.href = 'success.html';
    });
  }
}

// ECG Canvas Renderer
function initECGCanvas() {
  const canvas = document.getElementById('ecgCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = canvas.width = canvas.parentElement.clientWidth;
  let height = canvas.height = canvas.parentElement.clientHeight || 280;

  window.addEventListener('resize', () => {
    width = canvas.width = canvas.parentElement.clientWidth;
    height = canvas.height = canvas.parentElement.clientHeight || 280;
  });

  let x = 0;
  const speed = 2;
  const midY = height / 2;
  const buffer = new Array(width).fill(midY);

  function getECGSample(t) {
    const period = 100;
    const pos = t % period;

    if (pos > 30 && pos < 35) return midY - 10; // P Wave
    if (pos >= 35 && pos < 40) return midY;
    if (pos >= 40 && pos < 43) return midY + 15; // Q Wave
    if (pos >= 43 && pos < 50) return midY - 90; // R Wave (Peak)
    if (pos >= 50 && pos < 55) return midY + 30; // S Wave
    if (pos >= 55 && pos < 65) return midY;
    if (pos >= 65 && pos < 75) return midY - 20; // T Wave
    
    // Slight random baseline noise
    return midY + (Math.random() * 2 - 1);
  }

  let step = 0;

  function render() {
    ctx.fillStyle = 'rgba(2, 6, 23, 0.2)';
    ctx.fillRect(0, 0, width, height);

    // Grid lines
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.08)';
    ctx.lineWidth = 1;
    for (let i = 0; i < width; i += 20) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, height);
      ctx.stroke();
    }
    for (let j = 0; j < height; j += 20) {
      ctx.beginPath();
      ctx.moveTo(0, j);
      ctx.lineTo(width, j);
      ctx.stroke();
    }

    // ECG Trace Line
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 2.5;
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#06b6d4';
    ctx.beginPath();

    for (let i = 0; i < speed; i++) {
      const y = getECGSample(step++);
      buffer[x] = y;
      x = (x + 1) % width;
    }

    ctx.moveTo(0, buffer[0]);
    for (let i = 1; i < width; i++) {
      if (i === x) {
        ctx.stroke();
        ctx.beginPath();
      } else {
        ctx.lineTo(i, buffer[i]);
      }
    }
    ctx.stroke();

    // Eraser head cursor
    ctx.fillStyle = '#ef4444';
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#ef4444';
    ctx.beginPath();
    ctx.arc(x, buffer[x], 4, 0, Math.PI * 2);
    ctx.fill();

    requestAnimationFrame(render);
  }

  render();
}

// Live Vitals Simulation for patient.html
function initLiveVitals() {
  const bpmElement = document.getElementById('vitalBpm');
  if (!bpmElement) return;

  setInterval(() => {
    const currentBpm = parseInt(bpmElement.innerText) || 72;
    const variation = Math.floor(Math.random() * 3) - 1;
    const newBpm = Math.max(60, Math.min(100, currentBpm + variation));
    bpmElement.innerText = newBpm;
  }, 2500);
}
