/**
 * Advanced Gothic Horror Canvas Engine for THE LAST PROCESS.
 * Features:
 * - Multi-layered rolling graveyard mist & fog
 * - Flying bats across the blood moon
 * - Eerie cemetery tombstones & silhouettes
 * - Real-time dripping blood from top bezel
 * - Blinking demonic red eyes in dark corners
 * - Sudden jumpscare apparition flash
 * - Lightning storm flashes
 */

class GhostFX {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');

    this.ghosts = [];
    this.redEyes = [];
    this.bats = [];
    this.bloodDrips = [];
    this.mistParticles = [];

    this.glitchActive = false;
    this.glitchFrames = 0;
    this.jumpscareActive = false;
    this.jumpscareTimer = 0;

    this.resize();
    window.addEventListener('resize', () => this.resize());

    this.initMist();
    this.initBloodDrips();
    this.loop();

    // Spawn bats periodically
    setInterval(() => {
      if (Math.random() < 0.6 && this.bats.length < 5) {
        this.spawnBat();
      }
    }, 4000);

    // Periodically spawn watching red eyes
    setInterval(() => {
      if (Math.random() < 0.5 && this.redEyes.length < 3) {
        this.spawnRedEyes();
      }
    }, 8000);

    // Floating ghost apparition
    setInterval(() => {
      if (this.ghosts.length === 0 && Math.random() < 0.6) {
        this.spawnGhost(false);
      }
    }, 15000);
  }

  resize() {
    this.canvas.width = this.canvas.parentElement.clientWidth;
    this.canvas.height = this.canvas.parentElement.clientHeight;
  }

  initMist() {
    this.mistParticles = [];
    for (let i = 0; i < 20; i++) {
      this.mistParticles.push({
        x: Math.random() * (this.canvas.width || 800),
        y: (this.canvas.height || 600) - Math.random() * 120,
        radius: 60 + Math.random() * 80,
        vx: 0.2 + Math.random() * 0.4,
        alpha: 0.08 + Math.random() * 0.12
      });
    }
  }

  initBloodDrips() {
    this.bloodDrips = [];
    const dripCount = 12;
    for (let i = 0; i < dripCount; i++) {
      this.bloodDrips.push({
        x: (this.canvas.width / dripCount) * i + Math.random() * 20,
        length: 8 + Math.random() * 15,
        maxLength: 35 + Math.random() * 90,
        speed: 0.15 + Math.random() * 0.35,
        width: 3 + Math.random() * 4,
        dropY: 0,
        isDropping: false
      });
    }
  }

  triggerLightning() {
    const flash = document.getElementById('lightningOverlay');
    if (flash) {
      flash.classList.add('flash-active');
      setTimeout(() => flash.classList.remove('flash-active'), 150);
      setTimeout(() => {
        flash.classList.add('flash-active');
        setTimeout(() => flash.classList.remove('flash-active'), 80);
      }, 220);
    }
  }

  triggerJumpscare() {
    this.jumpscareActive = true;
    this.jumpscareTimer = 35; // Frames to flash
    this.triggerLightning();
    this.triggerGlitch(true);
  }

  triggerGlitch(isViolent = false) {
    this.glitchActive = true;
    this.glitchFrames = isViolent ? 18 : 8;
    const container = document.querySelector('.crt-screen-container');
    if (container) {
      container.classList.add('screen-shake');
      setTimeout(() => container.classList.remove('screen-shake'), isViolent ? 600 : 350);
    }
  }

  spawnBat() {
    this.bats.push({
      x: -40,
      y: 40 + Math.random() * (this.canvas.height * 0.4),
      vx: 3 + Math.random() * 3,
      vy: (Math.random() - 0.5) * 1.5,
      size: 10 + Math.random() * 8,
      wingPhase: 0
    });
  }

  spawnGhost(isAgitated = false) {
    const fromLeft = Math.random() < 0.5;
    this.ghosts.push({
      x: fromLeft ? -80 : this.canvas.width + 80,
      y: 80 + Math.random() * (this.canvas.height - 200),
      vx: (fromLeft ? 1 : -1) * (isAgitated ? 3.0 : 1.3),
      size: 55 + Math.random() * 35,
      alpha: 0.0,
      maxAlpha: isAgitated ? 0.85 : 0.45,
      phase: Math.random() * Math.PI * 2,
      isAgitated: isAgitated
    });
  }

  spawnRedEyes() {
    const pad = 70;
    const x = Math.random() < 0.5 ? pad : this.canvas.width - pad - 50;
    const y = Math.random() < 0.5 ? pad : this.canvas.height - pad - 30;

    this.redEyes.push({
      x: x,
      y: y,
      alpha: 0,
      state: 'fade_in',
      timer: 0,
      duration: 140 + Math.floor(Math.random() * 100)
    });
  }

  loop() {
    requestAnimationFrame(() => this.loop());
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // 1. Draw Rolling Graveyard Mist
    this.drawMist();

    // 2. Draw Flying Bats
    this.drawBats();

    // 3. Draw Eerie Dripping Blood
    this.drawBloodDrips();

    // 4. Draw Floating Ghosts
    this.drawGhosts();

    // 5. Draw Watching Red Eyes
    this.drawRedEyes();

    // 6. Draw Glitch Slices
    if (this.glitchActive) {
      this.drawGlitchNoise();
      this.glitchFrames--;
      if (this.glitchFrames <= 0) this.glitchActive = false;
    }

    // 7. Terrifying Jumpscare Apparition Flash
    if (this.jumpscareActive) {
      this.drawJumpscareFace();
      this.jumpscareTimer--;
      if (this.jumpscareTimer <= 0) this.jumpscareActive = false;
    }
  }

  drawMist() {
    this.ctx.save();
    for (const m of this.mistParticles) {
      m.x += m.vx;
      if (m.x > this.canvas.width + m.radius) {
        m.x = -m.radius;
      }
      const grad = this.ctx.createRadialGradient(m.x, m.y, 10, m.x, m.y, m.radius);
      grad.addColorStop(0, `rgba(40, 90, 60, ${m.alpha})`);
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      this.ctx.fillStyle = grad;
      this.ctx.beginPath();
      this.ctx.arc(m.x, m.y, m.radius, 0, Math.PI * 2);
      this.ctx.fill();
    }
    this.ctx.restore();
  }

  drawBats() {
    this.ctx.save();
    this.ctx.fillStyle = 'rgba(15, 10, 15, 0.75)';
    this.ctx.shadowColor = '#000000';
    this.ctx.shadowBlur = 4;

    for (let i = this.bats.length - 1; i >= 0; i--) {
      const b = this.bats[i];
      b.x += b.vx;
      b.y += b.vy;
      b.wingPhase += 0.35;

      const wingY = Math.sin(b.wingPhase) * (b.size * 0.7);

      this.ctx.beginPath();
      this.ctx.ellipse(b.x, b.y, b.size * 0.3, b.size * 0.5, 0, 0, Math.PI * 2);
      // Left wing
      this.ctx.moveTo(b.x, b.y);
      this.ctx.quadraticCurveTo(b.x - b.size, b.y - wingY - b.size * 0.5, b.x - b.size * 1.5, b.y + wingY);
      this.ctx.lineTo(b.x, b.y + b.size * 0.2);
      // Right wing
      this.ctx.moveTo(b.x, b.y);
      this.ctx.quadraticCurveTo(b.x + b.size, b.y - wingY - b.size * 0.5, b.x + b.size * 1.5, b.y + wingY);
      this.ctx.lineTo(b.x, b.y + b.size * 0.2);
      this.ctx.fill();

      if (b.x > this.canvas.width + 60) {
        this.bats.splice(i, 1);
      }
    }
    this.ctx.restore();
  }

  drawBloodDrips() {
    this.ctx.save();
    this.ctx.fillStyle = '#8b0000';
    this.ctx.shadowColor = '#ff0000';
    this.ctx.shadowBlur = 8;

    for (const d of this.bloodDrips) {
      if (d.length < d.maxLength) {
        d.length += d.speed;
      } else if (!d.isDropping) {
        d.isDropping = true;
        d.dropY = d.length;
      }

      // Render hanging drip
      this.ctx.beginPath();
      this.ctx.roundRect(d.x, 0, d.width, d.length, [0, 0, d.width / 2, d.width / 2]);
      this.ctx.fill();

      // Teardrop droplet
      this.ctx.beginPath();
      this.ctx.arc(d.x + d.width / 2, d.length + d.width * 0.8, d.width * 0.9, 0, Math.PI * 2);
      this.ctx.fill();

      // Falling bead of blood
      if (d.isDropping) {
        d.dropY += 3.5;
        this.ctx.beginPath();
        this.ctx.arc(d.x + d.width / 2, d.dropY, d.width * 0.6, 0, Math.PI * 2);
        this.ctx.fill();

        if (d.dropY > this.canvas.height) {
          d.isDropping = false;
          d.length = 8;
          d.maxLength = 35 + Math.random() * 85;
        }
      }
    }
    this.ctx.restore();
  }

  drawGhosts() {
    this.ctx.save();
    for (let i = this.ghosts.length - 1; i >= 0; i--) {
      const g = this.ghosts[i];
      g.x += g.vx;
      g.phase += 0.05;
      const waveY = g.y + Math.sin(g.phase) * 18;

      if (g.alpha < g.maxAlpha) {
        g.alpha += 0.015;
      }

      this.ctx.globalAlpha = g.alpha;
      this.ctx.fillStyle = g.isAgitated ? 'rgba(255, 30, 40, 0.55)' : 'rgba(160, 255, 200, 0.4)';
      this.ctx.shadowColor = g.isAgitated ? '#ff0000' : '#00ff88';
      this.ctx.shadowBlur = 24;

      // Head
      this.ctx.beginPath();
      this.ctx.arc(g.x, waveY, g.size * 0.5, Math.PI, 0, false);
      // Flowing ghost trail
      this.ctx.lineTo(g.x + g.size * 0.5, waveY + g.size * 0.9);
      this.ctx.quadraticCurveTo(g.x + g.size * 0.25, waveY + g.size * 0.6, g.x, waveY + g.size * 0.9);
      this.ctx.quadraticCurveTo(g.x - g.size * 0.25, waveY + g.size * 0.6, g.x - g.size * 0.5, waveY + g.size * 0.9);
      this.ctx.closePath();
      this.ctx.fill();

      // Sunken dark eyes
      this.ctx.fillStyle = '#050505';
      this.ctx.beginPath();
      this.ctx.ellipse(g.x - g.size * 0.18, waveY - g.size * 0.05, g.size * 0.1, g.size * 0.16, 0, 0, Math.PI * 2);
      this.ctx.ellipse(g.x + g.size * 0.18, waveY - g.size * 0.05, g.size * 0.1, g.size * 0.16, 0, 0, Math.PI * 2);
      this.ctx.fill();

      // Agitated shrieking mouth
      if (g.isAgitated) {
        this.ctx.beginPath();
        this.ctx.ellipse(g.x, waveY + g.size * 0.22, g.size * 0.12, g.size * 0.22, 0, 0, Math.PI * 2);
        this.ctx.fill();
      }

      if ((g.vx > 0 && g.x > this.canvas.width + 120) || (g.vx < 0 && g.x < -120)) {
        this.ghosts.splice(i, 1);
      }
    }
    this.ctx.restore();
  }

  drawRedEyes() {
    this.ctx.save();
    for (let i = this.redEyes.length - 1; i >= 0; i--) {
      const eye = this.redEyes[i];
      eye.timer++;

      if (eye.state === 'fade_in') {
        eye.alpha += 0.02;
        if (eye.alpha >= 0.9) eye.state = 'watch';
      } else if (eye.state === 'watch') {
        if (eye.timer > eye.duration) eye.state = 'fade_out';
      } else if (eye.state === 'fade_out') {
        eye.alpha -= 0.02;
        if (eye.alpha <= 0) {
          this.redEyes.splice(i, 1);
          continue;
        }
      }

      this.ctx.globalAlpha = eye.alpha;
      this.ctx.fillStyle = '#ff0011';
      this.ctx.shadowColor = '#ff0000';
      this.ctx.shadowBlur = 18;

      // Left eye
      this.ctx.beginPath();
      this.ctx.ellipse(eye.x, eye.y, 7, 10, 0.25, 0, Math.PI * 2);
      this.ctx.fill();

      // Right eye
      this.ctx.beginPath();
      this.ctx.ellipse(eye.x + 26, eye.y, 7, 10, -0.25, 0, Math.PI * 2);
      this.ctx.fill();

      // Slit pupils
      this.ctx.fillStyle = '#000000';
      this.ctx.fillRect(eye.x - 1, eye.y - 7, 2, 14);
      this.ctx.fillRect(eye.x + 25, eye.y - 7, 2, 14);
    }
    this.ctx.restore();
  }

  drawGlitchNoise() {
    this.ctx.save();
    for (let i = 0; i < 6; i++) {
      const sliceY = Math.random() * this.canvas.height;
      const sliceH = 6 + Math.random() * 25;
      this.ctx.fillStyle = Math.random() < 0.5 ? 'rgba(255, 0, 50, 0.35)' : 'rgba(0, 255, 120, 0.3)';
      this.ctx.fillRect(0, sliceY, this.canvas.width, sliceH);
    }
    this.ctx.restore();
  }

  drawJumpscareFace() {
    // Horrifying screeching face in monitor reflection
    this.ctx.save();
    const cx = this.canvas.width / 2;
    const cy = this.canvas.height / 2;
    const alpha = (this.jumpscareTimer / 35) * 0.85;

    this.ctx.globalAlpha = alpha;
    this.ctx.fillStyle = 'rgba(220, 220, 240, 0.4)';
    this.ctx.shadowColor = '#ff0033';
    this.ctx.shadowBlur = 40;

    // Distorted skull/demon head
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy, 140, 180, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // Giant hollow black eye sockets
    this.ctx.fillStyle = '#000000';
    this.ctx.beginPath();
    this.ctx.ellipse(cx - 50, cy - 35, 30, 48, -0.1, 0, Math.PI * 2);
    this.ctx.ellipse(cx + 50, cy - 35, 30, 48, 0.1, 0, Math.PI * 2);
    this.ctx.fill();

    // Agonized screaming jaw
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + 80, 45, 70, 0, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }
}
