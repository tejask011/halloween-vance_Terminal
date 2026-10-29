/**
 * Ghost FX & Halloween Canvas Animation Engine for THE LAST PROCESS.
 * Renders floating ethereal ghosts, glowing red eyes in the dark, and screen glitches.
 */

class GhostFX {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.ghosts = [];
    this.redEyes = [];
    this.glitchActive = false;
    this.glitchFrames = 0;
    
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.loop();

    // Periodically spawn red eyes in the corner
    setInterval(() => {
      if (Math.random() < 0.4 && this.redEyes.length < 2) {
        this.spawnRedEyes();
      }
    }, 12000);

    // Periodically drift a gentle ghost
    setInterval(() => {
      if (this.ghosts.length === 0 && Math.random() < 0.5) {
        this.spawnGhost(false);
      }
    }, 20000);
  }

  resize() {
    this.canvas.width = this.canvas.parentElement.clientWidth;
    this.canvas.height = this.canvas.parentElement.clientHeight;
  }

  spawnGhost(isAgitated = false) {
    const startFromLeft = Math.random() < 0.5;
    this.ghosts.push({
      x: startFromLeft ? -80 : this.canvas.width + 80,
      y: 50 + Math.random() * (this.canvas.height - 180),
      vx: (startFromLeft ? 1 : -1) * (isAgitated ? 2.5 : 1.2),
      size: 40 + Math.random() * 30,
      alpha: 0.0,
      maxAlpha: isAgitated ? 0.75 : 0.4,
      targetAlpha: isAgitated ? 0.75 : 0.4,
      phase: Math.random() * Math.PI * 2,
      isAgitated: isAgitated
    });
  }

  spawnRedEyes() {
    const padding = 60;
    const cornerX = Math.random() < 0.5 ? padding : this.canvas.width - padding - 40;
    const cornerY = Math.random() < 0.5 ? padding : this.canvas.height - padding - 20;

    this.redEyes.push({
      x: cornerX,
      y: cornerY,
      alpha: 0,
      state: 'fading_in',
      timer: 0,
      duration: 120 + Math.floor(Math.random() * 100)
    });
  }

  triggerGlitch() {
    this.glitchActive = true;
    this.glitchFrames = 8;
    const container = document.querySelector('.crt-screen-container');
    if (container) {
      container.classList.add('screen-shake');
      setTimeout(() => container.classList.remove('screen-shake'), 400);
    }
  }

  loop() {
    requestAnimationFrame(() => this.loop());
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // 1. Draw and update ghosts
    for (let i = this.ghosts.length - 1; i >= 0; i--) {
      const g = this.ghosts[i];
      g.x += g.vx;
      g.phase += 0.05;
      const waveY = g.y + Math.sin(g.phase) * 15;

      // Alpha fade in/out
      if (g.alpha < g.targetAlpha) {
        g.alpha += 0.01;
      }

      this.drawGhost(g.x, waveY, g.size, g.alpha, g.isAgitated);

      // Remove ghost once offscreen
      if ((g.vx > 0 && g.x > this.canvas.width + 120) || (g.vx < 0 && g.x < -120)) {
        this.ghosts.splice(i, 1);
      }
    }

    // 2. Draw and update red eyes
    for (let i = this.redEyes.length - 1; i >= 0; i--) {
      const eye = this.redEyes[i];
      eye.timer++;

      if (eye.state === 'fading_in') {
        eye.alpha += 0.02;
        if (eye.alpha >= 0.8) eye.state = 'watching';
      } else if (eye.state === 'watching') {
        if (eye.timer > eye.duration) eye.state = 'fading_out';
      } else if (eye.state === 'fading_out') {
        eye.alpha -= 0.02;
        if (eye.alpha <= 0) {
          this.redEyes.splice(i, 1);
          continue;
        }
      }

      this.drawRedEyes(eye.x, eye.y, eye.alpha);
    }

    // 3. Draw glitch noise
    if (this.glitchActive) {
      this.drawGlitchNoise();
      this.glitchFrames--;
      if (this.glitchFrames <= 0) this.glitchActive = false;
    }
  }

  drawGhost(x, y, size, alpha, isAgitated) {
    this.ctx.save();
    this.ctx.globalAlpha = alpha;
    this.ctx.fillStyle = isAgitated ? 'rgba(255, 60, 60, 0.5)' : 'rgba(180, 255, 220, 0.35)';
    this.ctx.shadowColor = isAgitated ? '#ff0033' : '#00ffaa';
    this.ctx.shadowBlur = 18;

    // Head
    this.ctx.beginPath();
    this.ctx.arc(x, y, size * 0.5, Math.PI, 0, false);
    
    // Flowing wavy tail
    const step = (size * 1.0) / 4;
    this.ctx.lineTo(x + size * 0.5, y + size * 0.8);
    this.ctx.quadraticCurveTo(x + size * 0.3, y + size * 0.6, x + size * 0.2, y + size * 0.8);
    this.ctx.quadraticCurveTo(x, y + size * 0.6, x - size * 0.2, y + size * 0.8);
    this.ctx.quadraticCurveTo(x - size * 0.3, y + size * 0.6, x - size * 0.5, y + size * 0.8);
    this.ctx.closePath();
    this.ctx.fill();

    // Hollow dark eyes
    this.ctx.fillStyle = '#080808';
    this.ctx.beginPath();
    this.ctx.ellipse(x - size * 0.18, y - size * 0.05, size * 0.08, size * 0.14, 0, 0, Math.PI * 2);
    this.ctx.ellipse(x + size * 0.18, y - size * 0.05, size * 0.08, size * 0.14, 0, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawRedEyes(x, y, alpha) {
    this.ctx.save();
    this.ctx.globalAlpha = alpha;
    this.ctx.fillStyle = '#ff1122';
    this.ctx.shadowColor = '#ff0000';
    this.ctx.shadowBlur = 12;

    // Left eye
    this.ctx.beginPath();
    this.ctx.ellipse(x, y, 6, 9, 0.2, 0, Math.PI * 2);
    this.ctx.fill();

    // Right eye
    this.ctx.beginPath();
    this.ctx.ellipse(x + 22, y, 6, 9, -0.2, 0, Math.PI * 2);
    this.ctx.fill();

    // Slit pupil
    this.ctx.fillStyle = '#000000';
    this.ctx.fillRect(x - 1, y - 6, 2, 12);
    this.ctx.fillRect(x + 21, y - 6, 2, 12);

    this.ctx.restore();
  }

  drawGlitchNoise() {
    this.ctx.save();
    for (let i = 0; i < 5; i++) {
      const sliceY = Math.random() * this.canvas.height;
      const sliceH = 4 + Math.random() * 20;
      this.ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
      this.ctx.fillRect(0, sliceY, this.canvas.width, sliceH);
    }
    this.ctx.restore();
  }
}

