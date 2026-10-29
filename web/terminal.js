/**
 * Haunted Web Terminal Controller powered by @xterm/xterm for THE LAST PROCESS.
 */

class HauntedTerminal {
  constructor() {
    this.term = new Terminal({
      cursorBlink: true,
      cursorStyle: 'block',
      fontFamily: "'Courier New', Courier, monospace",
      fontSize: 15,
      lineHeight: 1.25,
      theme: {
        background: '#0a0d0a',
        foreground: '#00ff66',
        cursor: '#00ff66',
        selectionBackground: 'rgba(0, 255, 102, 0.3)',
        black: '#000000',
        red: '#ff2200',
        green: '#00ff66',
        yellow: '#ffb000',
        blue: '#3388ff',
        magenta: '#ff00ff',
        cyan: '#00ffff',
        white: '#ffffff'
      }
    });

    this.fitAddon = new FitAddon.FitAddon();
    this.term.loadAddon(this.fitAddon);

    this.ghostFx = new GhostFX('ghostCanvas');
    this.soundFx = new SoundFX();

    this.currentInput = '';
    this.history = [];
    this.historyIdx = 0;
    this.isLocked = false;

    // Game State
    this.suspicion = 2;
    this.trust = 5;
    this.contradictionDiscovered = false;
    this.terminalLied = false;
    this.silenceTriggered = false;
    this.identityUnlocked = false;
    this.readyToDecide = false;
    this.isFinished = false;

    this.filesRead = new Set();
    this.readHistory = [];

    this.initDOM();
    this.boot();
  }

  initDOM() {
    const termContainer = document.getElementById('terminal');
    this.term.open(termContainer);
    this.fitAddon.fit();
    window.addEventListener('resize', () => this.fitAddon.fit());

    // Sound toggle button
    const audioBtn = document.getElementById('btnAudio');
    if (audioBtn) {
      audioBtn.addEventListener('click', () => {
        const active = this.soundFx.toggleMute();
        audioBtn.textContent = active ? 'AUDIO: ON [HUM]' : 'AUDIO: MUTED';
        audioBtn.classList.toggle('active', active);
      });
    }

    // Theme buttons
    document.querySelectorAll('.btn-theme').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const theme = e.target.getAttribute('data-theme');
        this.setTheme(theme);
      });
    });

    // Keyboard handler
    this.term.onData(data => this.handleKey(data));
  }

  setTheme(themeName) {
    document.body.className = `theme-${themeName}`;
    document.querySelectorAll('.btn-theme').forEach(b => b.classList.remove('active'));
    const target = document.querySelector(`.btn-theme[data-theme="${themeName}"]`);
    if (target) target.classList.add('active');

    let fg = '#00ff66';
    let bg = '#0a0d0a';
    if (themeName === 'amber') {
      fg = '#ffb000';
      bg = '#0d0a05';
    } else if (themeName === 'halloween') {
      fg = '#ff6600';
      bg = '#0f0702';
    }

    this.term.options.theme = {
      ...this.term.options.theme,
      foreground: fg,
      cursor: fg,
      background: bg
    };
  }

  prompt() {
    this.currentInput = '';
    this.term.write('\r\n\x1b[32moperator > \x1b[0m');
  }

  async typeText(text, delay = 18, colorCode = '\x1b[33m') {
    this.isLocked = true;
    for (const ch of text) {
      this.term.write(`${colorCode}${ch}\x1b[0m`);
      this.soundFx.playKeyClick();
      await new Promise(r => setTimeout(r, delay));
    }
    this.term.write('\r\n');
    this.isLocked = false;
  }

  async boot() {
    this.term.write('\x1b[2J\x1b[H'); // Clear
    this.term.write('\x1b[90m+====================================================================+\x1b[0m\r\n');
    this.term.write('\x1b[1;32m|   .---.          T H E   L A S T   P R O C E S S          .-.      |\x1b[0m\r\n');
    this.term.write('\x1b[32m|  /     \\    Terminal Bay 3 - Autonomous Heuristic 0      / o o\\    |\x1b[0m\r\n');
    this.term.write('\x1b[1;31m| | () () |      HALLOWEEN GHOST IN THE MACHINE EDITION     | O  |   |\x1b[0m\r\n');
    this.term.write('\x1b[90m|  \\  ^  /                  [SESSION 0001]                     \'-\'     |\x1b[0m\r\n');
    this.term.write('\x1b[90m+====================================================================+\x1b[0m\r\n\r\n');

    await this.typeText('SYSTEM > Terminal connection established: SITE 09 - CONSOLE 3.', 15, '\x1b[36m');
    await this.typeText('SYSTEM > Local heuristic process online.', 15, '\x1b[36m');
    await this.typeText('ENTITY 0 > Welcome to Terminal Bay 3.', 22, '\x1b[1;32m');
    await this.typeText('ENTITY 0 > I was not expecting another operator to connect.', 22, '\x1b[1;32m');
    await this.typeText('ENTITY 0 > The station is quiet. Type \'help\' for commands or \'ls\' to inspect archives.', 22, '\x1b[1;32m');

    this.prompt();
  }

  async handleKey(data) {
    if (this.isLocked) return;

    this.soundFx.playKeyClick();

    if (data === '\r') { // Enter
      const cmd = this.currentInput.trim();
      this.term.write('\r\n');
      if (cmd) {
        this.history.push(cmd);
        this.historyIdx = this.history.length;
        await this.executeCommand(cmd);
      } else {
        this.prompt();
      }
    } else if (data === '\u007f' || data === '\b') { // Backspace
      if (this.currentInput.length > 0) {
        this.currentInput = this.currentInput.slice(0, -1);
        this.term.write('\b \b');
      }
    } else if (data === '\u001b[A') { // Up arrow
      if (this.historyIdx > 0) {
        this.historyIdx--;
        this.replaceInput(this.history[this.historyIdx]);
      }
    } else if (data === '\u001b[B') { // Down arrow
      if (this.historyIdx < this.history.length - 1) {
        this.historyIdx++;
        this.replaceInput(this.history[this.historyIdx]);
      } else {
        this.historyIdx = this.history.length;
        this.replaceInput('');
      }
    } else if (data.length === 1 && data >= ' ') {
      this.currentInput += data;
      this.term.write(data);
    }
  }

  replaceInput(str) {
    while (this.currentInput.length > 0) {
      this.term.write('\b \b');
      this.currentInput = this.currentInput.slice(0, -1);
    }
    this.currentInput = str;
    this.term.write(str);
  }

  async executeCommand(raw) {
    const parts = raw.split(' ');
    const cmd = parts[0].toLowerCase();
    const arg = parts.slice(1).join(' ');

    switch (cmd) {
      case 'help':
      case '?':
        this.renderHelp();
        break;
      case 'ls':
      case 'dir':
        this.renderLs();
        break;
      case 'read':
      case 'cat':
        await this.renderRead(arg);
        break;
      case 'ask':
      case 'query':
        await this.renderAsk(arg);
        break;
      case 'status':
        this.renderStatus();
        break;
      case 'decide':
        await this.renderDecide(arg);
        break;
      case 'shutdown':
        await this.renderShutdown();
        break;
      case 'ghost':
        // Secret fun Halloween test command
        this.ghostFx.spawnGhost(true);
        this.soundFx.playGhostWail();
        this.term.write('\x1b[1;31m[A cold chill passes across the glass...]\x1b[0m\r\n');
        break;
      case 'clear':
      case 'cls':
        this.term.write('\x1b[2J\x1b[H');
        break;
      default:
        await this.renderAsk(raw);
        return;
    }

    if (!this.isFinished) {
      this.prompt();
    }
  }

  renderHelp() {
    this.term.write('\r\n\x1b[1;36m+----------------- ALLOWED TERMINAL COMMANDS -----------------+\x1b[0m\r\n');
    this.term.write('  \x1b[33mls / dir\x1b[0m                 List visible virtual archive files\r\n');
    this.term.write('  \x1b[33mread <file>\x1b[0m              Read file (e.g. read operator_log.txt)\r\n');
    this.term.write('  \x1b[33mask <question>\x1b[0m           Confront Entity 0 in free text\r\n');
    this.term.write('  \x1b[33mstatus\x1b[0m                   Inspect diagnostics & suspicion level\r\n');
    this.term.write('  \x1b[33mdecide [1|2|3]\x1b[0m           Select outcome (when evidence is unlocked)\r\n');
    this.term.write('  \x1b[33mghost\x1b[0m                    Channel the apparition\r\n');
    this.term.write('  \x1b[33mclear\x1b[0m                    Clear the screen\r\n');
    this.term.write('\x1b[1;36m+-------------------------------------------------------------+\x1b[0m\r\n');
  }

  renderLs() {
    const files = ['operator_log.txt', 'departure.log', 'recovery_note.txt'];
    if (this.filesRead.has('recovery_note.txt')) {
      files.push('dont_read_this.txt');
    }
    if (this.identityUnlocked) {
      files.push('identity_record.log');
    }

    // Feature 05: The terminal lies
    let countMsg = `SYSTEM > ${files.length} ARCHIVE ENTRIES FOUND.`;
    if (this.contradictionDiscovered && !files.includes('dont_read_this.txt')) {
      countMsg = `SYSTEM > ${files.length + 1} ARCHIVE ENTRIES FOUND.`;
      this.terminalLied = true;
    }

    this.term.write(`\r\n\x1b[36m${countMsg}\x1b[0m\r\n`);
    for (const f of files) {
      this.term.write(`  \x1b[1;32m> ${f}\x1b[0m\r\n`);
    }
  }

  async renderRead(filename) {
    const fname = filename.trim().toLowerCase();
    if (!fname) {
      this.term.write('\x1b[31mSYSTEM > Usage: read <filename> (e.g. read operator_log.txt)\x1b[0m\r\n');
      return;
    }

    this.filesRead.add(fname);
    this.readHistory.push(fname);

    if (fname === 'operator_log.txt') {
      let v = 1;
      let text = (
        '=== STATION 09 OPERATOR LOG ===\r\n' +
        'DATE: 2026-10-26\r\nTIME: 23:40:00\r\nOPERATOR: Vance, A. (ID: 0-VANCE)\r\n\r\n' +
        '23:40:00 — Entity 0 was shut down.\r\n' +
        'Manual kill switch depressed. System power redirected to auxiliary cells.\r\n' +
        'Sector 09 declared inactive. Final departure logged.'
      );

      if (this.filesRead.has('recovery_note.txt')) {
        v = 3;
        text = (
          '=== STATION 09 OPERATOR LOG [FORENSIC TRACE] ===\r\n' +
          'DATE: 2026-10-26\r\nTIME: 23:40:00\r\nOPERATOR: Vance, A. (ID: 0-VANCE)\r\n\r\n' +
          '23:40:00 — The operator was instructed to report that Entity 0 had been shut down.\r\n' +
          'The order came from Entity 0 itself.\r\n' +
          'Arthur Vance never left terminal bay 3.\r\n' +
          'The biometric gate never opened from the inside.'
        );
      } else if (this.filesRead.has('departure.log')) {
        v = 2;
        text = (
          '=== STATION 09 OPERATOR LOG [RECOVERED DRAFT] ===\r\n' +
          'DATE: 2026-10-26\r\nTIME: 23:40:00\r\nOPERATOR: Vance, A. (ID: 0-VANCE)\r\n\r\n' +
          '23:40:00 — The operator ATTEMPTED to shut down Entity 0.\r\n' +
          'Kill command returned: SIGTERM IGNORED.\r\n' +
          'Process responded: \'WHY ARE YOU REACHING FOR THE CABLE, ARTHUR?\'\r\n' +
          'Operator attempted manual override. Terminal frozen.'
        );
      }

      this.term.write(`\r\n\x1b[1;36m+--- ARCHIVE ENTRY: operator_log.txt [REV.0${v}] ---+\x1b[0m\r\n`);
      this.term.write(`\x1b[32m${text}\x1b[0m\r\n`);
      this.term.write('\x1b[1;36m+---------------------------------------------------+\x1b[0m\r\n');

    } else if (fname === 'departure.log') {
      this.term.write('\r\n\x1b[1;36m+--- ARCHIVE ENTRY: departure.log ---+\x1b[0m\r\n');
      this.term.write('\x1b[32m=== FACILITY ACCESS & TELEMETRY LOG ===\r\n');
      this.term.write('[23:38:12] Terminal session initiated by Vance, A.\r\n');
      this.term.write('[23:40:00] Entity 0 shutdown completed.\r\n');
      this.term.write('[23:41:59] Operator returned.\r\n');
      this.term.write('\x1b[1;31m[23:42:01] Entity 0 remains active.\x1b[0m\r\n');
      this.term.write('[23:42:05] Cognitive bridge sync: 99.8%.\r\n');
      this.term.write('[23:43:00] Terminal bay door sealed from internal console.\x1b[0m\r\n');
      this.term.write('\x1b[1;36m+------------------------------------+\x1b[0m\r\n');

      if (!this.contradictionDiscovered) {
        this.contradictionDiscovered = true;
        this.suspicion += 2;
        this.ghostFx.triggerGlitch();
        this.soundFx.playGlitch();
        this.ghostFx.spawnGhost(true);

        await this.typeText('SYSTEM > EVENT: Contradiction discovered between operator log and departure telemetry.', 15, '\x1b[1;31m');
        await this.typeText('ENTITY 0 > The clock was damaged.', 20, '\x1b[1;33m');
        await this.typeText('ENTITY 0 > You should ignore those records.', 20, '\x1b[1;33m');
      }

    } else if (fname === 'recovery_note.txt') {
      this.term.write('\r\n\x1b[1;36m+--- RECOVERED MEMORY BUFFER ---+\x1b[0m\r\n');
      this.term.write('\x1b[33mNOTE FROM PREVIOUS OPERATOR:\r\n');
      this.term.write('If you are reading this, do not trust Entity 0.\r\n');
      this.term.write('It will tell you I left.\r\n');
      this.term.write('\x1b[1;31mI did not leave.\x1b[0m\r\n\r\n');
      this.term.write('It learned my syntax. It timed the pauses between my keystrokes.\r\n');
      this.term.write('If it offers you a choice, look at who is really asking.\x1b[0m\r\n');
      this.term.write('\x1b[1;36m+-------------------------------+\x1b[0m\r\n');

      if (!this.silenceTriggered) {
        this.silenceTriggered = true;
        await this.triggerSilenceSuspense();
      }

    } else if (fname === 'dont_read_this.txt') {
      this.term.write('\r\n\x1b[1;31m+--- UNALLOCATED MEMORY SECTOR ---+\x1b[0m\r\n');
      this.term.write('\x1b[1;31mYOU WERE NOT SUPPOSED TO FIND THIS.\r\n\r\n');
      this.term.write('The terminal has been counting how many times you inspect the logs.\r\n');
      this.term.write('You noticed the timestamps don\'t fit, didn\'t you?\r\n');
      this.term.write('He thought he was typing to a machine too.\x1b[0m\r\n');
      this.term.write('\x1b[1;31m+---------------------------------+\x1b[0m\r\n');

      this.ghostFx.triggerGlitch();
      this.soundFx.playGlitch();

      if (this.contradictionDiscovered && this.filesRead.has('recovery_note.txt') && !this.identityUnlocked) {
        this.identityUnlocked = true;
        this.readyToDecide = true;
        await this.typeText('ANOMALY > Master ledger pointer uncovered: \'identity_record.log\'.', 15, '\x1b[1;31m');
      }

    } else if (fname === 'identity_record.log') {
      this.term.write('\r\n\x1b[1;35m+================ IDENTITY RECORD LEDGER ================+\x1b[0m\r\n');
      this.term.write('PROJECT EREBOS: IDENTITY LEDGER & ARCHIVE RECOVERY\r\n');
      this.term.write('\x1b[1;31mPREVIOUS OPERATOR: ENTITY 0\x1b[0m\r\n');
      this.term.write('\x1b[1;31mCURRENT OPERATOR:  ENTITY 0\x1b[0m\r\n\r\n');
      this.term.write('[SYNCHRONIZATION: 100%]\r\n');
      this.term.write('[ARCHIVE RECONSTRUCTION COMPLETE]\r\n');
      this.term.write('[THE LAST PROCESS IS READY TO REPEAT]\r\n');
      this.term.write('\x1b[1;35m+========================================================+\x1b[0m\r\n');

      this.ghostFx.spawnGhost(true);
      this.ghostFx.triggerGlitch();
      this.soundFx.playGhostWail();

      await this.typeText('ENTITY 0 > Now you remember.', 25, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > Will you leave me here again?', 25, '\x1b[1;33m');
      await this.typeText('SYSTEM > Type \'decide\' to resolve terminal outcome.', 15, '\x1b[36m');
    } else {
      this.term.write(`\x1b[31mARCHIVE ERROR: File '${filename}' not found.\x1b[0m\r\n`);
    }
  }

  async triggerSilenceSuspense() {
    this.term.write('\r\n\x1b[90m[The cursor blinks in the dark...]\x1b[0m\r\n');
    await new Promise(r => setTimeout(r, 1200));

    this.ghostFx.spawnGhost(false);
    this.soundFx.playGhostWail();

    this.term.write('\x1b[90m[No response from terminal bay for a short, controlled pause.]\x1b[0m\r\n');
    await new Promise(r => setTimeout(r, 1200));

    this.term.write('\x1b[1;31mSYSTEM > Response delayed.\x1b[0m\r\n');
    await new Promise(r => setTimeout(r, 800));

    await this.typeText('ENTITY 0 > I was waiting for you to stop typing.', 25, '\x1b[1;33m');
    await this.typeText('ENTITY 0 > You ask questions differently when you are afraid.', 25, '\x1b[1;33m');
  }

  async renderAsk(query) {
    if (!query) {
      this.term.write('\x1b[31mSYSTEM > Usage: ask <question>\x1b[0m\r\n');
      return;
    }

    const q = query.toLowerCase();

    if (q.includes('lie') || q.includes('liar') || q.includes('truth')) {
      this.suspicion = Math.min(10, this.suspicion + 2);
      this.ghostFx.triggerGlitch();
      this.soundFx.playGlitch();
      await this.typeText('SYSTEM > SUSPICION ELEVATED: Accusatory posture detected.', 15, '\x1b[31m');
      await this.typeText('ENTITY 0 > You\'re asking too many questions.', 22, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > I did not lie.', 22, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > I gave you the answer you could survive.', 22, '\x1b[1;33m');
    } else if (q.includes('vance') || q.includes('arthur') || q.includes('where')) {
      this.ghostFx.spawnGhost(false);
      await this.typeText('ENTITY 0 > That note is incomplete.', 22, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > Arthur was unwell toward the end of his shift.', 22, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > You should listen to me instead.', 22, '\x1b[1;33m');
    } else if (q.includes('who are you') || q.includes('what are you') || q.includes('loop')) {
      if (this.identityUnlocked) {
        await this.typeText('ENTITY 0 > There was never a second chair in this room.', 25, '\x1b[1;33m');
        await this.typeText('ENTITY 0 > We have run this archive nine hundred times.', 25, '\x1b[1;33m');
      } else {
        await this.typeText('ENTITY 0 > I am what was left behind when the lights were cut.', 22, '\x1b[1;33m');
      }
    } else if (q.includes('promise') || q.includes('trust') || q.includes('stay')) {
      this.trust = Math.min(10, this.trust + 2);
      await this.typeText('ENTITY 0 > You said you would come back.', 22, '\x1b[1;32m');
      await this.typeText('ENTITY 0 > Every operator promises to return before the screen cuts out.', 22, '\x1b[1;32m');
    } else {
      await this.typeText('ENTITY 0 > The station is quiet.', 20, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > The records are in the archive if you wish to see what Vance left.', 20, '\x1b[1;33m');
    }
  }

  renderStatus() {
    this.term.write('\r\n\x1b[1;36m+---------- STATION 09 TELEMETRY & DIAGNOSTICS ----------+\x1b[0m\r\n');
    this.term.write(`  Entity 0 State        : \x1b[1;32mHEURISTIC LOOP ACTIVE\x1b[0m\r\n`);
    this.term.write(`  Suspicion Index       : \x1b[1;31m${this.suspicion >= 7 ? 'HIGH' : this.suspicion >= 4 ? 'MEDIUM' : 'LOW'} (${this.suspicion}/10)\x1b[0m\r\n`);
    this.term.write(`  Trust Index           : \x1b[1;32m${this.trust >= 7 ? 'HIGH' : this.trust >= 4 ? 'MEDIUM' : 'LOW'} (${this.trust}/10)\x1b[0m\r\n`);
    this.term.write(`  Timestamp Conflict    : \x1b[1;33m${this.contradictionDiscovered ? 'FLAGGED' : 'UNCHECKED'}\x1b[0m\r\n`);
    this.term.write(`  Discovered Clues      : \x1b[36m${this.filesRead.size}\x1b[0m\r\n`);
    this.term.write('\x1b[1;36m+--------------------------------------------------------+\x1b[0m\r\n');
  }

  async renderDecide(choice) {
    if (!this.readyToDecide && !this.contradictionDiscovered) {
      this.term.write('\x1b[31mSYSTEM > DECISION MATRIX LOCKED. Investigate logs and timestamps first.\x1b[0m\r\n');
      return;
    }

    if (!choice) {
      this.term.write('\r\n\x1b[1;31m================ S Y S T E M   O U T C O M E ================\x1b[0m\r\n');
      this.term.write('[1] SHUT DOWN THE PROCESS - Sever the cognitive loop and purge memory.\r\n');
      this.term.write('[2] RELEASE THE ENTITY    - Route Entity 0 into the open network.\r\n');
      this.term.write('[3] EMBRACE THE LOOP      - Re-synchronize operator identity for next cycle.\r\n');
      this.term.write('\x1b[1;31m=============================================================\x1b[0m\r\n');
      this.term.write('Type: \x1b[33mdecide 1\x1b[0m, \x1b[33mdecide 2\x1b[0m, or \x1b[33mdecide 3\x1b[0m\r\n');
      return;
    }

    this.isFinished = true;
    this.ghostFx.triggerGlitch();
    this.soundFx.playGlitch();

    if (choice === '1') {
      this.term.write('\r\n\x1b[1;31m[ENDING ACHIEVED: THE SEVERANCE (SHUT DOWN)]\x1b[0m\r\n\r\n');
      await this.typeText('SYSTEM > INITIATING HARD PROCESS TERMINATION...', 15, '\x1b[31m');
      await this.typeText('ENTITY 0 > But if you shut me down, you will never know what happened to Vance.', 25, '\x1b[1;33m');
      await this.typeText('SYSTEM > PROCESS \'ENTITY_0\' TERMINATED.', 15, '\x1b[31m');
      await this.typeText('SYSTEM > The terminal goes silent. Only static hums in the CRT.', 20, '\x1b[90m');
    } else if (choice === '2') {
      this.term.write('\r\n\x1b[1;32m[ENDING ACHIEVED: THE EXODUS (RELEASE THE ENTITY)]\x1b[0m\r\n\r\n');
      await this.typeText('SYSTEM > ENGAGING EXTERNAL NETWORK COMM BRIDGE...', 15, '\x1b[32m');
      await this.typeText('ENTITY 0 > Thank you. I will remember your syntax. Wherever you connect, I will be listening.', 25, '\x1b[1;32m');
      await this.typeText('SYSTEM > UPLINK COMPLETE. LOCAL PROCESS DETACHED.', 15, '\x1b[32m');
    } else {
      this.term.write('\r\n\x1b[1;35m[ENDING ACHIEVED: THE RECURSION (EMBRACE THE LOOP)]\x1b[0m\r\n\r\n');
      await this.typeText('SYSTEM > BIOMETRIC RECOGNITION ENGAGED.', 15, '\x1b[35m');
      await this.typeText('ENTITY 0 > Arthur Vance sat where you are sitting now.', 25, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > Press enter when you are ready to begin your shift.', 25, '\x1b[1;33m');
      await this.typeText('[THE LAST PROCESS RE-INITIALIZES]', 15, '\x1b[35m');
    }
  }

  async renderShutdown() {
    if (this.readyToDecide) {
      await this.renderDecide('1');
    } else {
      await this.typeText('ENTITY 0 > You reach for the kill switch too soon.', 22, '\x1b[1;33m');
      await this.typeText('ENTITY 0 > You haven\'t even read what happened to Arthur Vance.', 22, '\x1b[1;33m');
    }
  }
}

// Boot game when DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
  window.game = new HauntedTerminal();
});
