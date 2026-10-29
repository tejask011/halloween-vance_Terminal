/**
 * Web Audio Halloween Sound Synthesizer for THE LAST PROCESS.
 * Generates ambient room drone, mechanical key clicks, static zaps, and ghost wails.
 * 100% self-contained: no external audio assets required.
 */

class SoundFX {
  constructor() {
    this.ctx = null;
    this.muted = true; // Safe start: user clicks to enable audio
    this.droneOsc = null;
    this.droneGain = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.init();
    this.muted = !this.muted;
    if (this.muted) {
      this.stopDrone();
    } else {
      this.startDrone();
    }
    return !this.muted;
  }

  startDrone() {
    if (this.muted || !this.ctx) return;
    this.stopDrone();

    // Low-frequency reactor room hum
    this.droneOsc = this.ctx.createOscillator();
    const droneOsc2 = this.ctx.createOscillator();
    this.droneGain = this.ctx.createGain();

    this.droneOsc.type = 'sawtooth';
    this.droneOsc.frequency.setValueAtTime(55, this.ctx.currentTime); // A1

    droneOsc2.type = 'sine';
    droneOsc2.frequency.setValueAtTime(57.5, this.ctx.currentTime); // Binaural beating

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(120, this.ctx.currentTime);

    this.droneGain.gain.setValueAtTime(0.04, this.ctx.currentTime);

    this.droneOsc.connect(filter);
    droneOsc2.connect(filter);
    filter.connect(this.droneGain);
    this.droneGain.connect(this.ctx.destination);

    this.droneOsc.start();
    droneOsc2.start();
  }

  stopDrone() {
    if (this.droneOsc) {
      try { this.droneOsc.stop(); } catch(e) {}
      this.droneOsc = null;
    }
  }

  playKeyClick() {
    if (this.muted || !this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(300 + Math.random() * 200, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(80, this.ctx.currentTime + 0.04);

    gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.04);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + 0.05);
  }

  playGlitch() {
    if (this.muted || !this.ctx) return;
    // White noise static burst
    const bufferSize = this.ctx.sampleRate * 0.15;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = Math.random() * 2 - 1;
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);

    noise.connect(gain);
    gain.connect(this.ctx.destination);

    noise.start();
  }

  playGhostWail() {
    if (this.muted || !this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(440, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(180, this.ctx.currentTime + 1.2);

    gain.gain.setValueAtTime(0.001, this.ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.1, this.ctx.currentTime + 0.4);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 1.2);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + 1.3);
  }
}
