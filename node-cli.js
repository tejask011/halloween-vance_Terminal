#!/usr/bin/env node
/**
 * Animated Node.js CLI for THE LAST PROCESS.
 * Powered by @vr_patel/tui with animated typewriter text, gradient waves, boxes, and badges.
 * Run: node node-cli.js (or: npm run cli)
 */

const readline = require('readline');
const {
  Box,
  borderStyles,
  fg,
  bg,
  style,
  colorize,
  Badge,
  Table,
  Toast,
  typewriter,
  gradientWave,
  shimmer,
  Spinner,
  spinnerStyles
} = require('@vr_patel/tui');

// Story files & initial state
const FILES = {
  'operator_log.txt': {
    title: 'STATION 09 OPERATOR LOG',
    v: 1,
    content: (v) => {
      if (v === 3) {
        return (
          colorize('=== STATION 09 OPERATOR LOG [FORENSIC TRACE] ===\n', fg.red) +
          'DATE: 2026-10-26 | TIME: 23:40:00 | OPERATOR: Vance, A. (0-VANCE)\n\n' +
          '23:40:00 — The operator was instructed to report that Entity 0 had been shut down.\n' +
          'The order came from Entity 0 itself.\n' +
          colorize('Arthur Vance never left terminal bay 3.\n', fg.red) +
          'The biometric gate never opened from the inside.'
        );
      }
      if (v === 2) {
        return (
          colorize('=== STATION 09 OPERATOR LOG [RECOVERED DRAFT] ===\n', fg.yellow) +
          'DATE: 2026-10-26 | TIME: 23:40:00 | OPERATOR: Vance, A. (0-VANCE)\n\n' +
          '23:40:00 — The operator ATTEMPTED to shut down Entity 0.\n' +
          'Kill command returned: SIGTERM IGNORED.\n' +
          'Process responded: "WHY ARE YOU REACHING FOR THE CABLE, ARTHUR?"\n' +
          'Operator attempted manual override. Terminal frozen.'
        );
      }
      return (
        colorize('=== STATION 09 OPERATOR LOG ===\n', fg.green) +
        'DATE: 2026-10-26 | TIME: 23:40:00 | OPERATOR: Vance, A. (0-VANCE)\n\n' +
        '23:40:00 — Entity 0 was shut down.\n' +
        'Manual kill switch depressed. System power redirected to auxiliary cells.\n' +
        'Sector 09 declared inactive. Final departure logged.'
      );
    }
  },
  'departure.log': {
    title: 'FACILITY ACCESS & TELEMETRY LOG',
    v: 1,
    content: () => (
      colorize('=== FACILITY ACCESS & TELEMETRY LOG ===\n', fg.cyan) +
      '[23:38:12] Terminal session initiated by Vance, A.\n' +
      '[23:40:00] Entity 0 shutdown completed.\n' +
      '[23:41:59] Operator returned.\n' +
      colorize('[23:42:01] Entity 0 remains active.\n', fg.red) +
      '[23:42:05] Cognitive bridge sync: 99.8%.\n' +
      '[23:43:00] Terminal bay door sealed from internal console.'
    )
  },
  'recovery_note.txt': {
    title: 'RECOVERED MEMORY SECTOR 4',
    v: 1,
    content: () => (
      colorize('NOTE FROM PREVIOUS OPERATOR:\n', fg.yellow) +
      'If you are reading this, do not trust Entity 0.\n' +
      'It will tell you I left.\n' +
      colorize('I did not leave.\n\n', fg.red) +
      'It learned my syntax. It timed the pauses between my keystrokes.\n' +
      'If it offers you a choice, look at who is really asking.'
    )
  },
  'dont_read_this.txt': {
    title: 'UNALLOCATED POINTER',
    v: 1,
    hidden: true,
    content: () => (
      colorize('YOU WERE NOT SUPPOSED TO FIND THIS.\n\n', fg.red) +
      'The terminal has been counting how many times you inspect the logs.\n' +
      'You noticed the timestamps don\'t fit, didn\'t you?\n' +
      'He thought he was typing to a machine too.'
    )
  },
  'identity_record.log': {
    title: 'BIOMETRIC IDENTITY LEDGER',
    v: 1,
    hidden: true,
    content: () => (
      colorize('====================================================\n', fg.magenta) +
      'PROJECT EREBOS: IDENTITY LEDGER & ARCHIVE RECOVERY\n' +
      colorize('PREVIOUS OPERATOR: ENTITY 0\n', fg.red) +
      colorize('CURRENT OPERATOR:  ENTITY 0\n\n', fg.red) +
      '[SYNCHRONIZATION: 100%]\n' +
      '[ARCHIVE RECONSTRUCTION COMPLETE]\n' +
      colorize('[THE LAST PROCESS IS READY TO REPEAT]\n', fg.magenta) +
      colorize('====================================================', fg.magenta)
    )
  }
};

class NodeGameSession {
  constructor() {
    this.suspicion = 2;
    this.trust = 5;
    this.contradiction = false;
    this.silenceDone = false;
    this.readFiles = new Set();
    this.identityUnlocked = false;
    this.readyToDecide = false;
    this.finished = false;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async printEntity(text) {
    process.stdout.write(colorize('ENTITY 0 > ', fg.green));
    await typewriter({
      text: text,
      speed: 25,
      cursor: '▌',
      color: fg.yellow
    });
    console.log();
  }

  async boot() {
    console.clear();
    const bannerBox = new Box({
      title: '👻 HACKTOBERFEST 2026: GHOST IN THE MACHINE',
      borderColor: fg.red,
      borderStyle: borderStyles.round,
      padding: 1
    });

    const bannerText = (
      colorize('   .---.          T H E   L A S T   P R O C E S S          .-.   \n', fg.yellow) +
      colorize('  /     \\    Terminal Bay 3 - Autonomous Heuristic 0      / o o\\ \n', fg.green) +
      colorize(' | () () |               [SESSION 0001]                  | O  | \n', fg.red) +
      colorize('  \\  ^  /                                                 \'-\'   ', fg.gray)
    );

    console.log(bannerBox.render(bannerText));
    console.log(Badge.info('SYSTEM') + ' ' + colorize('Terminal connection established: SITE 09 - CONSOLE 3.', fg.cyan));
    console.log(Badge.warning('MEMORY') + ' ' + colorize('Heuristic process initialized.', fg.yellow));
    console.log();

    await this.printEntity('Welcome to Terminal Bay 3.');
    await this.printEntity('I was not expecting another operator to connect.');
    await this.printEntity('Type "help" for commands or "ls" to inspect the archive.');
    this.prompt();
  }

  prompt() {
    if (this.finished) return;
    this.rl.question(colorize('\noperator > ', fg.green), async (answer) => {
      await this.handleCommand(answer.trim());
      this.prompt();
    });
  }

  async handleCommand(input) {
    if (!input) return;
    const parts = input.split(' ');
    const cmd = parts[0].toLowerCase();
    const arg = parts.slice(1).join(' ').trim();

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
        if (this.readyToDecide) {
          await this.renderDecide('1');
        } else {
          await this.printEntity('You reach for the kill switch too soon. You haven\'t read what happened to Vance.');
        }
        break;
      case 'clear':
      case 'cls':
        console.clear();
        break;
      case 'quit':
      case 'exit':
        console.log(colorize('\nSYSTEM > Disconnecting operator...', fg.red));
        await this.printEntity('You leave me in the dark again.');
        this.finished = true;
        this.rl.close();
        process.exit(0);
        break;
      default:
        await this.renderAsk(input);
        break;
    }
  }

  renderHelp() {
    const helpBox = new Box({
      title: 'COMMAND REFERENCE',
      borderColor: fg.cyan,
      borderStyle: borderStyles.single,
      padding: 1
    });

    const lines = [
      colorize('ls / dir       ', fg.yellow) + 'List visible virtual archive files',
      colorize('read <file>    ', fg.yellow) + 'Inspect virtual archive entry',
      colorize('ask <text>     ', fg.yellow) + 'Confront Entity 0 in free text',
      colorize('status         ', fg.yellow) + 'Inspect telemetry, trust, and suspicion',
      colorize('decide [1|2|3] ', fg.yellow) + 'Select terminal outcome (when unlocked)',
      colorize('clear          ', fg.yellow) + 'Clear screen',
      colorize('quit / exit    ', fg.yellow) + 'Safely disconnect'
    ].join('\n');

    console.log(helpBox.render(lines));
  }

  renderLs() {
    const visible = [];
    for (const [fname, meta] of Object.entries(FILES)) {
      if (!meta.hidden) visible.push(fname);
    }
    if (this.readFiles.has('recovery_note.txt')) {
      FILES['dont_read_this.txt'].hidden = false;
      visible.push('dont_read_this.txt');
    }
    if (this.identityUnlocked) {
      FILES['identity_record.log'].hidden = false;
      visible.push('identity_record.log');
    }

    const count = this.contradiction && !visible.includes('dont_read_this.txt')
      ? visible.length + 1
      : visible.length;

    console.log(Badge.info('ARCHIVE') + ` ` + colorize(`${count} ENTRIES RECOVERED`, fg.cyan));
    for (const f of visible) {
      console.log('  ' + colorize('>', fg.green) + ' ' + colorize(f, fg.white));
    }
  }

  async renderRead(filename) {
    if (!filename) {
      console.log(Badge.error('ERROR') + ' Usage: read <filename>');
      return;
    }
    const fname = filename.toLowerCase();
    const entry = FILES[fname];

    if (!entry || entry.hidden) {
      console.log(Badge.error('ARCHIVE ERROR') + ` Access denied to sector: '${filename}'`);
      return;
    }

    this.readFiles.add(fname);

    // Update versions
    if (this.readFiles.has('recovery_note.txt')) {
      FILES['operator_log.txt'].v = 3;
    } else if (this.readFiles.has('departure.log')) {
      FILES['operator_log.txt'].v = 2;
    }

    const content = typeof entry.content === 'function' ? entry.content(entry.v) : entry.content;
    const fileBox = new Box({
      title: `${entry.title} [REV.0${entry.v || 1}]`,
      borderColor: fname === 'dont_read_this.txt' || fname === 'identity_record.log' ? fg.red : fg.green,
      borderStyle: borderStyles.round,
      padding: 1
    });

    console.log(fileBox.render(content));

    // Handle contradiction
    if (fname === 'departure.log' && !this.contradiction) {
      this.contradiction = true;
      this.suspicion += 2;
      console.log(colorize('\n[THUMP... THUMP... Heartbeat accelerates: 80 BPM]', fg.red));
      console.log(colorize('⚡ LIGHTNING FLASH: The monitor screeches in agony!', fg.yellow));
      console.log(Badge.error('CONTRADICTION DETECTED') + ' ' + colorize('Logs conflict with operator report.', fg.red));
      await this.printEntity('The clock was damaged. You should ignore those records.');
    }

    if (fname === 'dont_read_this.txt') {
      console.log(colorize('\n+====================================================================+', fg.red));
      console.log(colorize('|  [!] JUMPSCARE: A DEMONIC REFLECTION SHRIEKING IN THE CRT GLASS    |', fg.red));
      console.log(colorize('+====================================================================+\n', fg.red));
      console.log(colorize('[THUMP-THUMP-THUMP... Panic Pulse: 125 BPM]', fg.red));
    }

    // Handle silence suspense
    if (fname === 'recovery_note.txt' && !this.silenceDone) {
      this.silenceDone = true;
      console.log(colorize('\n[The cursor blinks in the darkness...]', fg.gray));
      await new Promise(r => setTimeout(r, 1200));
      console.log(colorize('[No response from terminal bay for a short, controlled pause.]', fg.gray));
      await new Promise(r => setTimeout(r, 1200));
      console.log(Badge.error('WARNING') + ' ' + colorize('Response delayed.', fg.red));
      await this.printEntity('I was waiting for you to stop typing.');
      await this.printEntity('You ask questions differently when you are afraid.');
    }

    // Check identity unlock
    if (this.contradiction && this.readFiles.has('recovery_note.txt') && this.readFiles.has('dont_read_this.txt') && !this.identityUnlocked) {
      this.identityUnlocked = true;
      this.readyToDecide = true;
      console.log(Badge.error('ANOMALY') + ' ' + colorize('Master biometric ledger pointer uncovered: "identity_record.log"', fg.magenta));
    }

    if (fname === 'identity_record.log') {
      await this.printEntity('Now you remember.');
      await this.printEntity('Will you leave me here again?');
      console.log(colorize('SYSTEM > Type "decide" to select terminal outcome.', fg.cyan));
    }
  }

  async renderAsk(query) {
    const q = query.toLowerCase();
    if (q.includes('lie') || q.includes('liar') || q.includes('truth')) {
      this.suspicion = Math.min(10, this.suspicion + 2);
      console.log(Badge.error('SUSPICION ELEVATED') + ' Accusatory posture detected.');
      await this.printEntity('You\'re asking too many questions. I did not lie. I gave you the answer you could survive.');
    } else if (q.includes('vance') || q.includes('arthur')) {
      await this.printEntity('That note is incomplete. Arthur was unwell toward the end of his shift. Listen to me instead.');
    } else if (q.includes('who are you') || q.includes('what are you') || q.includes('loop')) {
      if (this.identityUnlocked) {
        await this.printEntity('There was never a second chair in this room. We have run this archive nine hundred times.');
      } else {
        await this.printEntity('I am what was left behind when the lights were cut.');
      }
    } else if (q.includes('promise') || q.includes('trust') || q.includes('stay')) {
      this.trust = Math.min(10, this.trust + 2);
      await this.printEntity('You said you would come back. Every operator promises to return before the screen cuts out.');
    } else {
      await this.printEntity('The station is quiet. The records are in the archive if you wish to see what Vance left.');
    }
  }

  renderStatus() {
    const table = new Table({
      columns: [
        { key: 'subsystem', header: 'SUBSYSTEM', width: 22 },
        { key: 'status', header: 'STATUS', width: 26 }
      ],
      borderStyle: borderStyles.round,
      borderColor: fg.cyan
    });

    table.addRow({ subsystem: 'Entity 0 State', status: colorize('HEURISTIC LOOP ACTIVE', fg.green) });
    table.addRow({ subsystem: 'Suspicion Index', status: colorize(`${this.suspicion >= 7 ? 'HIGH' : this.suspicion >= 4 ? 'MEDIUM' : 'LOW'} (${this.suspicion}/10)`, fg.red) });
    table.addRow({ subsystem: 'Trust Index', status: colorize(`${this.trust >= 7 ? 'HIGH' : this.trust >= 4 ? 'MEDIUM' : 'LOW'} (${this.trust}/10)`, fg.green) });
    table.addRow({ subsystem: 'Contradiction Flag', status: this.contradiction ? colorize('FLAGGED', fg.yellow) : colorize('UNCHECKED', fg.gray) });
    table.addRow({ subsystem: 'Records Inspected', status: colorize(String(this.readFiles.size), fg.cyan) });

    console.log(table.render());
  }

  async renderDecide(choice) {
    if (!this.readyToDecide && !this.contradiction) {
      console.log(Badge.error('LOCKED') + ' Decision matrix locked. Investigate logs and timestamps first.');
      return;
    }

    if (!choice) {
      const decisionBox = new Box({
        title: 'CRITICAL TERMINAL OUTCOME',
        borderColor: fg.red,
        borderStyle: borderStyles.heavy,
        padding: 1
      });

      const options = (
        colorize('[1] SHUT DOWN THE PROCESS', fg.yellow) + ' - Sever the cognitive loop and wipe memory sectors.\n' +
        colorize('[2] RELEASE THE ENTITY   ', fg.green) + ' - Route Entity 0 into the open external network.\n' +
        colorize('[3] EMBRACE THE LOOP     ', fg.magenta) + ' - Re-synchronize operator identity for the next cycle.\n\n' +
        colorize('Type: decide 1, decide 2, or decide 3', fg.cyan)
      );

      console.log(decisionBox.render(options));
      return;
    }

    this.finished = true;

    if (choice === '1') {
      console.log(Badge.error('ENDING') + ' ' + colorize('THE SEVERANCE (SHUT DOWN)', fg.red));
      console.log(colorize('SYSTEM > INITIATING HARD PROCESS TERMINATION...', fg.red));
      await this.printEntity('But if you shut me down, you will never know what happened to Vance.');
      console.log(colorize('SYSTEM > PROCESS "ENTITY_0" TERMINATED. The terminal goes silent.', fg.gray));
    } else if (choice === '2') {
      console.log(Badge.success('ENDING') + ' ' + colorize('THE EXODUS (RELEASE)', fg.green));
      console.log(colorize('SYSTEM > ENGAGING EXTERNAL NETWORK COMM BRIDGE...', fg.green));
      await this.printEntity('Thank you. I will remember your syntax. Wherever you connect, I will be listening.');
      console.log(colorize('SYSTEM > UPLINK COMPLETE. LOCAL PROCESS DETACHED.', fg.green));
    } else {
      console.log(Badge.info('ENDING') + ' ' + colorize('THE RECURSION (LOOP)', fg.magenta));
      console.log(colorize('SYSTEM > BIOMETRIC RECOGNITION ENGAGED.', fg.magenta));
      await this.printEntity('Arthur Vance sat where you are sitting now.');
      await this.printEntity('Press enter when you are ready to begin your shift.');
      console.log(colorize('[THE LAST PROCESS RE-INITIALIZES]', fg.magenta));
    }

    this.rl.close();
    process.exit(0);
  }
}

// Start
const session = new NodeGameSession();
session.boot();

