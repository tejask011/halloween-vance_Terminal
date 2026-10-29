/**
 * Gothic Horror Web Audio Synthesizer for THE LAST PROCESS.
 * Real-time synthesis:
 * - Howling graveyard wind
 * - Accelerating psychological heartbeat
 * - Funeral church bell tolling
 * - Thunder crashes & lightning static
 * - Demonic frequency glitches & screams
 * - Mechanical keyboard clicks
 */

class SoundFX {
  constructor() {
    this.ctx = null;
    this.muted = true; // Click to enable
    this.windGain = null;
    this.heartbeatTimer = null;
    this.heartbeatBpm = 55;
    this.heartbeatActive = false;
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
      this.stopAtmosphere();
    } else {
      this.startAtmosphere();
      this.startHeartbeat(55);
    }
    return !this.muted;
  }

  startAtmosphere() {
    if (this.muted || !this.ctx) return;
    this.stopAtmosphere();

    // 1. Howling Graveyard Wind (Pink noise + sweeping resonant bandpass)
    const bufferSize = this.ctx.sampleRate * 3;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      output[i] = (b0 + b1 + b2) * 0.3;
    }

    const windSource = this.ctx.createBufferSource();
    windSource.buffer = noiseBuffer;
    windSource.loop = true;

    const windFilter = this.ctx.createBiquadFilter();
    windFilter.type = 'bandpass';
    windFilter.frequency.setValueAtTime(320, this.ctx.currentTime);
    windFilter.Q.setValueAtTime(4.0, this.ctx.currentTime);

    // LFO for howling wind frequency modulation
    const windLFO = this.ctx.createOscillator();
    windLFO.frequency.setValueAtTime(0.15, this.ctx.currentTime);
    const windLFOGain = this.ctx.createGain();
    windLFOGain.gain.setValueAtTime(220, this.ctx.currentTime);
    windLFO.connect(windLFOGain);
    windLFOGain.connect(windFilter.frequency);
    windLFO.start();

    this.windGain = this.ctx.createGain();
    this.windGain.gain.setValueAtTime(0.06, this.ctx.currentTime);

    windSource.connect(windFilter);
    windFilter.connect(this.windGain);
    this.windGain.connect(this.ctx.destination);

    windSource.start();
    this.windSource = windSource;
    this.windLFO = windLFO;
  }

  stopAtmosphere() {
    if (this.windSource) {
      try { this.windSource.stop(); } catch(e) {}
      this.windSource = null;
    }
    if (this.windLFO) {
      try { this.windLFO.stop(); } catch(e) {}
      this.windLFO = null;
    }
    this.stopHeartbeat();
  }

  startHeartbeat(bpm = 55) {
    this.heartbeatBpm = bpm;
    if (this.heartbeatActive || this.muted) return;
    this.heartbeatActive = true;
    this.runHeartbeatCycle();
  }

  setHeartbeatRate(bpm) {
    this.heartbeatBpm = Math.min(130, Math.max(50, bpm));
  }

  runHeartbeatCycle() {
    if (!this.heartbeatActive || this.muted || !this.ctx) return;
    this.playHeartbeatThump(true); // Lub
    setTimeout(() => {
      this.playHeartbeatThump(false); // Dub
    }, 180);

    const interval = (60 / this.heartbeatBpm) * 1000;
    this.heartbeatTimer = setTimeout(() => {
      this.runHeartbeatCycle();
    }, interval);
  }

  stopHeartbeat() {
    this.heartbeatActive = false;
    if (this.heartbeatTimer) {
      clearTimeout(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  playHeartbeatThump(isFirst) {
    if (this.muted || !this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    const startFreq = isFirst ? 68 : 55;
    osc.frequency.setValueAtTime(startFreq, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(30, this.ctx.currentTime + 0.14);

    gain.gain.setValueAtTime(0.18, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.14);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + 0.15);
  }

  playFuneralBell() {
    if (this.muted || !this.ctx) return;
    const freqs = [110, 220, 330, 442, 650];
    const decay = 3.5;

    freqs.forEach((f, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      const amp = 0.08 / (idx + 1);
      gain.gain.setValueAtTime(amp, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + decay);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + decay + 0.1);
    });
  }

  playThunderCrash() {
    if (this.muted || !this.ctx) return;
    // Massive distorted thunder rumble
    const bufferSize = this.ctx.sampleRate * 2.5;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.8));
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(160, this.ctx.currentTime);
    filter.frequency.linearRampToValueAtTime(60, this.ctx.currentTime + 2.0);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.35, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 2.4);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);

    noise.start();
  }

  playScreamingGlitch() {
    if (this.muted || !this.ctx) return;
    // Screaming frequency modulation zap
    const carrier = this.ctx.createOscillator();
    const mod = this.ctx.createOscillator();
    const modGain = this.ctx.createGain();
    const gain = this.ctx.createGain();

    carrier.type = 'sawtooth';
    carrier.frequency.setValueAtTime(750, this.ctx.currentTime);
    carrier.frequency.exponentialRampToValueAtTime(140, this.ctx.currentTime + 0.6);

    mod.type = 'square';
    mod.frequency.setValueAtTime(80, this.ctx.currentTime);
    modGain.gain.setValueAtTime(400, this.ctx.currentTime);

    mod.connect(modGain);
    modGain.connect(carrier.frequency);

    gain.gain.setValueAtTime(0.22, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.6);

    carrier.connect(gain);
    gain.connect(this.ctx.destination);

    carrier.start();
    mod.start();
    carrier.stop(this.ctx.currentTime + 0.65);
    mod.stop(this.ctx.currentTime + 0.65);
  }

  playKeyClick() {
    if (this.muted || !this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(250 + Math.random() * 180, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(70, this.ctx.currentTime + 0.03);

    gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.03);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + 0.04);
  }

  playGhostWail() {
    if (this.muted || !this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(520, this.ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(240, this.ctx.currentTime + 1.4);

    gain.gain.setValueAtTime(0.001, this.ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.12, this.ctx.currentTime + 0.3);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 1.4);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + 1.5);
  }
}
