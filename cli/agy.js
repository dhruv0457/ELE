#!/usr/bin/env node

// ═══════════════════════════════════════════════════════════════
//  FIRST CLI × ELE AGENT — Next-Gen AI Developer Terminal
//  Clean • Minimal • Full-Screen • Live LLM Streaming • Jarvis
// ═══════════════════════════════════════════════════════════════

import fs from 'fs';
import path from 'path';
import { exec, spawn } from 'child_process';
import os from 'os';

// ─── ANSI PRIMITIVES ──────────────────────────────────────────
const E = '\x1b';
const fg = (r, g, b) => `${E}[38;2;${r};${g};${b}m`;
const bg = (r, g, b) => `${E}[48;2;${r};${g};${b}m`;
const R  = `${E}[0m`;
const BD = `${E}[1m`;
const IT = `${E}[3m`;
const DM = `${E}[2m`;
const HIDE   = `${E}[?25l`;
const SHOW   = `${E}[?25h`;
const CLR    = `${E}[2J${E}[H`;
const ELINE  = `${E}[2K`;
const ALT_ON  = `${E}[?1049h`;
const ALT_OFF = `${E}[?1049l`;
const at = (x, y) => `${E}[${y};${x}H`;

// ─── PROFESSIONAL MINIMAL COLOR PALETTE ───────────────────────
const P = {
  base:      bg(12, 12, 16),      // Deep matte background
  surface:   bg(20, 20, 26),
  raised:    bg(26, 28, 36),
  selected:  bg(35, 42, 54),

  white:     fg(215, 218, 224),   // Crisp clean text
  soft:      fg(155, 160, 170),   // Secondary text
  muted:     fg(85, 90, 100),     // Subtle tertiary text
  faint:     fg(45, 50, 60),      // Borders, dividers

  accent:    fg(100, 180, 225),   // Primary soft teal-blue
  accentB:   fg(130, 205, 245),   // Highlight
  green:     fg(85, 195, 125),    // Status ok
  amber:     fg(225, 175, 75),    // Warnings
  red:       fg(220, 85, 85),     // Errors

  popupBdr:  fg(55, 62, 75),
};

const B = {
  tl: '╭', tr: '╮', bl: '╰', br: '╯',
  h: '─', v: '│', hl: '├', hr: '┤',
  sh: '┄',
};

const LOGO = [
  '  █▀▀ █ █▀█ █▀ ▀█▀   █▀▀ █   █',
  '  █▀  █ █▀▄ ▄█  █    █▄▄ █▄▄ █',
];

function renderLogo() {
  let out = '';
  for (const line of LOGO) {
    out += `${P.accent}${BD}${line}${R}\n`;
  }
  return out;
}

function strip(s) { return s.replace(/\x1b\[[0-9;]*m/g, ''); }

// ─── LOAD KEYS FROM ELE & ENVIRONMENT ─────────────────────────
function loadAllKeys() {
  const keys = {};
  const userHome = process.env.USERPROFILE || process.env.HOME || '';
  const searchFiles = [
    path.join('D:', 'ELE', 'backend', '.env'),
    path.join('D:', 'ELE', '.env'),
    path.join(userHome, '.ele-agent', '.env'),
    path.join(process.cwd(), '.env'),
  ];

  for (const file of searchFiles) {
    try {
      if (fs.existsSync(file)) {
        const content = fs.readFileSync(file, 'utf-8');
        for (const line of content.split('\n')) {
          const trimmed = line.trim();
          if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
            const [k, ...v] = trimmed.split('=');
            const keyName = k.trim();
            const val = v.join('=').trim().replace(/^['"]|['"]$/g, '');
            if (val && !keys[keyName]) {
              keys[keyName] = val;
            }
          }
        }
      }
    } catch {}
  }

  // Also include process.env
  for (const [k, v] of Object.entries(process.env)) {
    if (v && !keys[k]) keys[k] = v;
  }

  return keys;
}

const KEYS = loadAllKeys();

// ─── MODEL CATALOG ────────────────────────────────────────────
const MODELS = [
  { id: 'meta/llama-3.3-70b-instruct', provider: 'nvidia', name: 'Llama 3.3 70B (NVIDIA)', tag: 'ultra-fast', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'deepseek-ai/deepseek-r1',     provider: 'nvidia', name: 'DeepSeek R1 (NVIDIA)',   tag: 'deep reasoning', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'gemini-2.0-flash-exp',        provider: 'gemini', name: 'Gemini 2.0 Flash',       tag: 'multimodal', baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/' },
  { id: 'gpt-4o-mini',                 provider: 'openai', name: 'GPT-4o Mini',            tag: 'balanced',   baseUrl: 'https://api.openai.com/v1' },
  { id: 'llama-3.3-70b-versatile',     provider: 'groq',   name: 'Groq Llama 3.3',         tag: 'instant',    baseUrl: 'https://api.groq.com/openai/v1' },
  { id: 'qwen2.5-coder:latest',        provider: 'ollama', name: 'Ollama Qwen 2.5 Local',  tag: 'offline',    baseUrl: 'http://localhost:11434/v1' },
];

function getBestModel() {
  if (KEYS['NVIDIA_API_KEY']) return MODELS[0];
  if (KEYS['GEMINI_API_KEY']) return MODELS[2];
  if (KEYS['OPENAI_API_KEY']) return MODELS[3];
  if (KEYS['GROQ_API_KEY'])   return MODELS[4];
  return MODELS[0]; // fallback
}

// ─── COMMANDS ─────────────────────────────────────────────────
const COMMANDS = [
  { cmd: '/help',    desc: 'All commands & shortcuts',    icon: '?' },
  { cmd: '/model',   desc: 'Switch AI model',             icon: '◆' },
  { cmd: '/jarvis',  desc: 'Jarvis Voice/Agent mode',     icon: '◉' },
  { cmd: '/browse',  desc: 'Open URL in browser',         icon: '→' },
  { cmd: '/clear',   desc: 'Clear chat screen',           icon: '⊘' },
  { cmd: '/plan',    desc: 'Toggle plan mode',            icon: '▦' },
  { cmd: '/keys',    desc: 'View active ELE API keys',    icon: '🔑' },
  { cmd: '/logs',    desc: 'Session logs',                 icon: '≡' },
  { cmd: '/editor',  desc: 'Open workspace in VS Code',   icon: '⊡' },
  { cmd: '/exit',    desc: 'Quit terminal',               icon: '⏻' },
];

// ─── LOGGING ──────────────────────────────────────────────────
const LOG_DIR = path.join('D:', 'LOGS', 'hive');
const SESSION_LOG = `session_${new Date().toISOString().slice(0, 10)}.log`;
const START = Date.now();

function ensureLogs() {
  try { if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true }); } catch {}
}
function log(msg) {
  try { fs.appendFileSync(path.join(LOG_DIR, SESSION_LOG), `[${new Date().toISOString()}] ${msg}\n`); } catch {}
}

// ─── STATE ────────────────────────────────────────────────────
const S = {
  input: '',
  cursor: 0,
  history: [],
  histIdx: -1,
  histStash: '',
  messages: [],
  
  menuOpen: false,
  menuIdx: 0,
  menuItems: [],
  
  busy: false,
  spinFrame: 0,
  
  model: getBestModel(),
  planMode: false,
  
  jarvisOpen: false,
  jarvisText: '',
  jarvisAnimating: false,
  
  pendingAction: null,
};

const SPIN = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];

// ─── TERMINAL UTILS ───────────────────────────────────────────
const W = () => process.stdout.columns || 80;
const H = () => process.stdout.rows || 24;
const w = (...a) => process.stdout.write(a.join(''));
const sleep = ms => new Promise(r => setTimeout(r, ms));

function wrap(text, max) {
  const lines = [];
  for (const raw of text.split('\n')) {
    if (raw.length <= max) { lines.push(raw); continue; }
    const words = raw.split(' ');
    let cur = '';
    for (const word of words) {
      if ((cur + ' ' + word).length > max && cur) {
        lines.push(cur);
        cur = word;
      } else {
        cur = cur ? cur + ' ' + word : word;
      }
    }
    if (cur) lines.push(cur);
  }
  return lines;
}

function uptime() {
  const s = Math.floor((Date.now() - START) / 1000);
  const m = Math.floor(s / 60);
  return m > 0 ? `${m}m ${s % 60}s` : `${s}s`;
}

// ═══════════════════════════════════════════════════════════════
//  RENDER ENGINE
// ═══════════════════════════════════════════════════════════════
function render() {
  const cols = W();
  const rows = H();
  const contentW = Math.min(cols - 4, 100);
  const padL = Math.max(1, Math.floor((cols - contentW) / 2));
  const pad = ' '.repeat(padL);

  let buf = '';
  buf += HIDE;
  buf += CLR;
  buf += P.base;

  // ── Header ──
  buf += '\n';
  buf += pad + renderLogo();
  buf += pad + `${P.faint}${B.sh.repeat(contentW)}${R}\n`;

  // Status line
  const modelTag = `${P.accent}◆${R} ${P.soft}${S.model.name}${R}`;
  const eleTag = `${P.green}● ELE Backend Connected${R}`;
  const cwdTag = `${P.muted}${path.basename(process.cwd())}${R}`;
  const planTag = S.planMode ? `  ${P.amber}▦ plan${R}` : '';
  buf += pad + `  ${modelTag}  ${P.faint}·${R}  ${eleTag}  ${P.faint}·${R}  ${cwdTag}${planTag}\n\n`;

  // ── Messages ──
  const headerLines = 6;
  const footerLines = 5;
  const menuLines = S.menuOpen ? Math.min(S.menuItems.length + 2, 8) : 0;
  const jarvisLines = S.jarvisOpen ? 9 : 0;
  const availLines = Math.max(4, rows - headerLines - footerLines - menuLines - jarvisLines);

  const msgLines = [];
  for (const msg of S.messages) {
    const lines = formatMsg(msg, contentW - 4);
    for (const l of lines) msgLines.push(pad + '  ' + l);
    msgLines.push('');
  }

  const visibleMsgs = msgLines.slice(Math.max(0, msgLines.length - availLines));
  for (const line of visibleMsgs) buf += line + '\n';

  const fill = Math.max(0, availLines - visibleMsgs.length);
  for (let i = 0; i < fill; i++) buf += '\n';

  // ── Jarvis Popup ──
  if (S.jarvisOpen) {
    buf += renderJarvisPopup(contentW, padL);
  }

  // ── Slash Menu ──
  if (S.menuOpen && S.menuItems.length > 0) {
    buf += renderMenu(contentW, padL);
  }

  // ── Input Box ──
  buf += '\n';
  const promptChar = S.busy
    ? `${P.accent}${SPIN[S.spinFrame % SPIN.length]}${R}`
    : `${P.accent}›${R}`;

  buf += pad + `${P.faint}${B.tl}${B.h.repeat(contentW - 2)}${B.tr}${R}\n`;
  buf += pad + `${P.faint}${B.v}${R} ${promptChar} ${P.white}${S.input}${R}`;
  const inputUsed = 4 + strip(S.input).length;
  buf += ' '.repeat(Math.max(0, contentW - inputUsed - 1));
  buf += `${P.faint}${B.v}${R}\n`;
  buf += pad + `${P.faint}${B.bl}${B.h.repeat(contentW - 2)}${B.br}${R}\n`;

  // ── Footer ──
  const mem = Math.round(process.memoryUsage().rss / 1024 / 1024);
  buf += pad + `  ${P.muted}${DM}/ commands${R}   ${P.muted}${DM}↑↓ history${R}   ${P.muted}${DM}ctrl+c exit${R}`;
  buf += `   ${P.faint}${DM}${mem}MB · ${uptime()}${R}\n`;

  w(buf);

  // Position cursor inside input box
  const cursorRow = rows - 2;
  const cursorCol = padL + 4 + S.cursor;
  w(at(cursorCol, cursorRow));
  w(SHOW);
}

function formatMsg(msg, maxW) {
  const lines = [];
  if (msg.type === 'user') {
    lines.push(`${P.soft}you${R}`);
    for (const l of wrap(msg.text, maxW - 2)) lines.push(`${P.white}${l}${R}`);
  }
  else if (msg.type === 'thinking') {
    const icon = msg.done ? `${P.green}✓${R}` : `${P.accent}${SPIN[S.spinFrame % SPIN.length]}${R}`;
    const dur = msg.duration ? ` ${P.muted}${DM}${(msg.duration / 1000).toFixed(1)}s${R}` : '';
    lines.push(`${icon} ${P.muted}${IT}thinking${R}${dur}`);
    if (msg.text && !msg.collapsed) {
      for (const l of wrap(msg.text, maxW - 4)) lines.push(`  ${P.muted}${DM}${IT}${l}${R}`);
    }
  }
  else if (msg.type === 'agent') {
    lines.push(`${P.accent}ele agent${R}  ${P.faint}${DM}${S.model.name}${R}`);
    for (const l of wrap(msg.text, maxW - 2)) lines.push(`${P.white}${l}${R}`);
  }
  else if (msg.type === 'info') {
    lines.push(`${P.soft}${msg.text}${R}`);
  }
  else if (msg.type === 'error') {
    lines.push(`${P.red}${msg.text}${R}`);
  }
  else if (msg.type === 'system') {
    for (const l of wrap(msg.text, maxW - 2)) lines.push(`${P.soft}${l}${R}`);
  }
  return lines;
}

function renderMenu(contentW, padL) {
  const pad = ' '.repeat(padL);
  const menuW = Math.min(44, contentW - 4);
  let out = '';
  out += pad + `  ${P.popupBdr}${B.tl}${B.h.repeat(menuW - 2)}${B.tr}${R}\n`;
  for (let i = 0; i < S.menuItems.length; i++) {
    const item = S.menuItems[i];
    const sel = i === S.menuIdx;
    const arrow = sel ? `${P.accent}${BD}›${R}` : ' ';
    const cmdC = sel ? `${P.accentB}${BD}` : `${P.soft}`;
    const descC = sel ? `${P.white}` : `${P.muted}`;
    const bgC = sel ? P.selected : '';
    const cmdStr = item.cmd.padEnd(10);
    const descStr = item.desc.substring(0, menuW - 18);
    out += pad + `  ${P.popupBdr}${B.v}${R}${bgC} ${arrow} ${P.muted}${item.icon}${R}${bgC} ${cmdC}${cmdStr}${R}${bgC}${descC}${DM}${descStr}${R}`;
    const lineUsed = 5 + 2 + 10 + descStr.length;
    out += ' '.repeat(Math.max(0, menuW - lineUsed - 1));
    out += `${P.popupBdr}${B.v}${R}\n`;
  }
  out += pad + `  ${P.popupBdr}${B.bl}${B.h} ${P.muted}${DM}↑↓ enter esc${R} ${P.popupBdr}${B.h.repeat(Math.max(1, menuW - 17))}${B.br}${R}\n`;
  return out;
}

function renderJarvisPopup(contentW, padL) {
  const pad = ' '.repeat(padL);
  const popW = Math.min(58, contentW - 4);
  const centerPad = ' '.repeat(Math.max(0, Math.floor((contentW - popW) / 2)));
  let out = '';
  out += '\n' + pad + centerPad + `${P.popupBdr}${B.tl}${B.h.repeat(popW - 2)}${B.tr}${R}\n`;
  out += pad + centerPad + `${P.popupBdr}${B.v}${R}${P.raised}  ${P.accent}${BD}◉ ELE JARVIS VOICE ASSISTANT${R}${P.raised}`;
  out += ' '.repeat(Math.max(0, popW - 32)) + `${P.popupBdr}${B.v}${R}\n`;
  out += pad + centerPad + `${P.popupBdr}${B.hl}${B.h.repeat(popW - 2)}${B.hr}${R}\n`;
  const jarvisLines = wrap(S.jarvisText || 'Voice Engine Active. Listening for requests...', popW - 6);
  for (const line of jarvisLines) {
    out += pad + centerPad + `${P.popupBdr}${B.v}${R}  ${P.white}${line}${R}`;
    out += ' '.repeat(Math.max(0, popW - strip(line).length - 4)) + `${P.popupBdr}${B.v}${R}\n`;
  }
  for (let i = jarvisLines.length; i < 3; i++) {
    out += pad + centerPad + `${P.popupBdr}${B.v}${R}${' '.repeat(popW - 2)}${P.popupBdr}${B.v}${R}\n`;
  }
  out += pad + centerPad + `${P.popupBdr}${B.bl}${B.h} ${P.muted}${DM}esc to dismiss${R} ${P.popupBdr}${B.h.repeat(Math.max(1, popW - 19))}${B.br}${R}\n`;
  return out;
}

function updateMenu() {
  if (S.input.startsWith('/')) {
    const q = S.input.split(' ')[0].toLowerCase();
    S.menuItems = COMMANDS.filter(c => c.cmd.startsWith(q));
    S.menuOpen = S.menuItems.length > 0;
    S.menuIdx = Math.min(S.menuIdx, Math.max(0, S.menuItems.length - 1));
  } else {
    S.menuOpen = false;
    S.menuItems = [];
    S.menuIdx = 0;
  }
}

// ═══════════════════════════════════════════════════════════════
//  LIVE STREAMING ENGINE (NVIDIA NIM / OPENAI / GEMINI / GROQ)
// ═══════════════════════════════════════════════════════════════
async function callStreamingLLM(prompt) {
  S.busy = true;
  const currentModel = S.model;
  
  // Resolve API Key
  let apiKey = '';
  if (currentModel.provider === 'nvidia') apiKey = KEYS['NVIDIA_API_KEY'] || '';
  else if (currentModel.provider === 'gemini') apiKey = KEYS['GEMINI_API_KEY'] || '';
  else if (currentModel.provider === 'openai') apiKey = KEYS['OPENAI_API_KEY'] || '';
  else if (currentModel.provider === 'groq')   apiKey = KEYS['GROQ_API_KEY'] || '';

  const thinkMsg = { type: 'thinking', text: '', done: false, collapsed: false, startTime: Date.now() };
  S.messages.push(thinkMsg);

  const agentMsg = { type: 'agent', text: '' };
  S.messages.push(agentMsg);
  render();

  // If no API key is available, run graceful fallback
  if (!apiKey && currentModel.provider !== 'ollama') {
    thinkMsg.text = 'No API key set for ' + currentModel.provider + '. Running local assistant response.';
    thinkMsg.done = true;
    thinkMsg.duration = 400;
    agentMsg.text = `No API key found for ${currentModel.name}.\n\nYou can set keys in D:\\ELE\\backend\\.env or run /keys to inspect loaded credentials.`;
    S.busy = false;
    render();
    return;
  }

  const spinnerIv = setInterval(() => {
    S.spinFrame++;
    render();
  }, 80);

  try {
    const url = `${currentModel.baseUrl.replace(/\/$/, '')}/chat/completions`;
    const headers = {
      'Content-Type': 'application/json',
    };
    if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;

    const systemPrompt = "You are ELE, an intelligent developer assistant and JARVIS-style terminal copilot. You provide precise, concise, and helpful developer assistance.";

    const messagesPayload = [
      { role: 'system', content: systemPrompt },
      ...S.messages.filter(m => m.type === 'user' || (m.type === 'agent' && m !== agentMsg)).slice(-8).map(m => ({
        role: m.type === 'user' ? 'user' : 'assistant',
        content: m.text
      })),
      { role: 'user', content: prompt }
    ];

    const body = JSON.stringify({
      model: currentModel.id,
      messages: messagesPayload,
      stream: true,
      temperature: 0.7,
      max_tokens: 2048,
    });

    const response = await fetch(url, { method: 'POST', headers, body });

    if (!response.ok) {
      const errTxt = await response.text();
      throw new Error(`HTTP ${response.status}: ${errTxt.substring(0, 150)}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let inThinkTag = false;

    thinkMsg.done = true;
    thinkMsg.duration = Date.now() - thinkMsg.startTime;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data:')) continue;
        const dataStr = trimmed.replace(/^data:\s*/, '');
        if (dataStr === '[DONE]') continue;

        try {
          const parsed = JSON.parse(dataStr);
          const delta = parsed.choices?.[0]?.delta;
          const token = delta?.content || delta?.reasoning_content || '';
          
          if (token) {
            // Check for reasoning tags (like DeepSeek R1 <think>)
            if (token.includes('<think>')) inThinkTag = true;
            if (token.includes('</think>')) { inThinkTag = false; continue; }

            if (inThinkTag || delta?.reasoning_content) {
              thinkMsg.text += token.replace(/<think>|<\/think>/g, '');
            } else {
              agentMsg.text += token;
            }
            render();
          }
        } catch {}
      }
    }

    log(`LLM (${currentModel.name}): ${agentMsg.text.substring(0, 100)}...`);
  } catch (err) {
    thinkMsg.done = true;
    agentMsg.text = `Error connecting to ${currentModel.name}: ${err.message}\nCheck your internet connection or run /keys to verify credentials.`;
    log(`ERROR: ${err.message}`);
  } finally {
    clearInterval(spinnerIv);
    S.busy = false;
    render();
  }
}

// ═══════════════════════════════════════════════════════════════
//  JARVIS OVERLAY
// ═══════════════════════════════════════════════════════════════
async function openJarvis() {
  S.jarvisOpen = true;
  S.jarvisText = '';
  S.jarvisAnimating = true;
  render();

  const greeting = `ELE Jarvis Engine active.\nConnected to: ${S.model.name}\nReady to assist with files, terminal commands, or browser actions.`;
  for (let i = 0; i < greeting.length; i++) {
    S.jarvisText += greeting[i];
    if (i % 3 === 0) {
      render();
      await sleep(15);
    }
  }
  S.jarvisAnimating = false;
  render();
}

function closeJarvis() {
  S.jarvisOpen = false;
  S.jarvisText = '';
  render();
}

// ═══════════════════════════════════════════════════════════════
//  COMMAND DISPATCH
// ═══════════════════════════════════════════════════════════════
async function execute(input) {
  const trimmed = input.trim();
  if (!trimmed) return;

  S.history.push(trimmed);
  S.histIdx = -1;
  log(`USER: ${trimmed}`);

  const parts = trimmed.split(' ');
  const cmd = parts[0].toLowerCase();
  const args = parts.slice(1).join(' ');

  switch (cmd) {
    case '/help': return cmdHelp();
    case '/model': return cmdModel();
    case '/jarvis': return openJarvis();
    case '/keys': return cmdKeys();
    case '/browse': return cmdBrowse(args);
    case '/clear': return cmdClear();
    case '/plan': return cmdPlan();
    case '/logs': return cmdLogs();
    case '/editor': return cmdEditor(args);
    case '/exit': case '/quit': return cmdExit();
    default:
      if (trimmed.startsWith('/')) {
        S.messages.push({ type: 'error', text: `Unknown command: ${cmd}` });
      } else {
        S.messages.push({ type: 'user', text: trimmed });
        render();
        return callStreamingLLM(trimmed);
      }
  }
}

function cmdHelp() {
  let t = '';
  for (const c of COMMANDS) {
    t += `${c.icon}  ${c.cmd.padEnd(10)} ${c.desc}\n`;
  }
  t += '\nShortcuts\n';
  t += '↑ ↓       History\n';
  t += '/         Autocomplete\n';
  t += 'ctrl+c    Exit';
  S.messages.push({ type: 'system', text: t });
}

function cmdModel() {
  let t = 'Select model:\n';
  for (let i = 0; i < MODELS.length; i++) {
    const m = MODELS[i];
    const active = m.name === S.model.name ? ' ← active' : '';
    t += `  [${i + 1}] ${m.name} (${m.tag})${active}\n`;
  }
  t += '\nType 1-' + MODELS.length + ' to switch.';
  S.messages.push({ type: 'system', text: t });
  S.pendingAction = 'model';
}

function cmdKeys() {
  let t = 'Active ELE API Keys:\n';
  const checkKeys = ['NVIDIA_API_KEY', 'GEMINI_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GROQ_API_KEY'];
  for (const k of checkKeys) {
    const val = KEYS[k];
    if (val) {
      t += `  ✓ ${k.padEnd(20)} ${val.slice(0, 6)}••••${val.slice(-4)}\n`;
    } else {
      t += `  ○ ${k.padEnd(20)} not set\n`;
    }
  }
  t += `\nLoaded from: D:\\ELE\\backend\\.env & ~/.ele-agent/.env`;
  S.messages.push({ type: 'system', text: t });
}

function cmdBrowse(url) {
  const target = url || 'https://google.com';
  const c = process.platform === 'win32' ? `start chrome "${target}"` : `open "${target}"`;
  exec(c);
  S.messages.push({ type: 'info', text: `Opened browser to: ${target}` });
}

function cmdClear() {
  S.messages = [];
  S.messages.push({ type: 'info', text: 'Chat cleared.' });
}

function cmdPlan() {
  S.planMode = !S.planMode;
  S.messages.push({ type: 'info', text: S.planMode ? 'Plan mode active.' : 'Plan mode off.' });
}

function cmdLogs() {
  try {
    const logPath = path.join(LOG_DIR, SESSION_LOG);
    if (!fs.existsSync(logPath)) { S.messages.push({ type: 'info', text: 'No logs yet.' }); return; }
    const lines = fs.readFileSync(logPath, 'utf-8').trim().split('\n').slice(-10);
    S.messages.push({ type: 'system', text: 'Recent logs:\n' + lines.join('\n') });
  } catch {
    S.messages.push({ type: 'info', text: 'Could not read logs.' });
  }
}

function cmdEditor(file) {
  const target = file || '.';
  exec(`code "${target}"`);
  S.messages.push({ type: 'info', text: `Opened in VS Code.` });
}

function cmdExit() {
  log('Session ended.');
  w(CLR, SHOW, ALT_OFF);
  console.log(`\n  ${strip(P.accent)}Goodbye.\n`);
  process.exit(0);
}

// ═══════════════════════════════════════════════════════════════
//  INPUT HANDLER
// ═══════════════════════════════════════════════════════════════
function onKey(data) {
  const k = data.toString('utf-8');

  if (k === '\x03') { cmdExit(); return; }

  if (S.jarvisOpen && !S.jarvisAnimating) {
    if (k === '\x1b') { closeJarvis(); return; }
    return;
  }
  if (S.jarvisAnimating) return;
  if (S.busy) return;

  if (S.pendingAction === 'model') {
    const n = parseInt(k);
    if (n >= 1 && n <= MODELS.length) {
      S.model = MODELS[n - 1];
      S.messages.push({ type: 'info', text: `Switched model to ${S.model.name}` });
      log(`Model switched to ${S.model.name}`);
    }
    S.pendingAction = null;
    render();
    return;
  }

  if (k === '\x1b') {
    if (S.menuOpen) { S.menuOpen = false; render(); }
    return;
  }

  // Up
  if (k === '\x1b[A') {
    if (S.menuOpen) {
      S.menuIdx = Math.max(0, S.menuIdx - 1);
    } else if (S.history.length > 0) {
      if (S.histIdx === -1) S.histStash = S.input;
      if (S.histIdx < S.history.length - 1) {
        S.histIdx++;
        S.input = S.history[S.history.length - 1 - S.histIdx];
        S.cursor = S.input.length;
      }
    }
    render(); return;
  }

  // Down
  if (k === '\x1b[B') {
    if (S.menuOpen) {
      S.menuIdx = Math.min(S.menuItems.length - 1, S.menuIdx + 1);
    } else if (S.histIdx >= 0) {
      S.histIdx--;
      S.input = S.histIdx < 0 ? S.histStash : S.history[S.history.length - 1 - S.histIdx];
      S.cursor = S.input.length;
    }
    render(); return;
  }

  if (k === '\x1b[D') { if (S.cursor > 0) S.cursor--; render(); return; }
  if (k === '\x1b[C') { if (S.cursor < S.input.length) S.cursor++; render(); return; }
  if (k === '\x01' || k === '\x1b[H') { S.cursor = 0; render(); return; }
  if (k === '\x05' || k === '\x1b[F') { S.cursor = S.input.length; render(); return; }

  // Enter
  if (k === '\r' || k === '\n') {
    if (S.menuOpen && S.menuItems.length > 0) {
      const sel = S.menuItems[S.menuIdx];
      if (sel.cmd === '/browse' || sel.cmd === '/editor') {
        S.input = sel.cmd + ' ';
        S.cursor = S.input.length;
        S.menuOpen = false;
        render();
      } else {
        S.input = sel.cmd;
        S.menuOpen = false;
        const inp = S.input;
        S.input = ''; S.cursor = 0;
        execute(inp).then(() => render());
      }
    } else if (S.input.trim()) {
      const inp = S.input;
      S.input = ''; S.cursor = 0; S.menuOpen = false;
      execute(inp).then(() => render());
    }
    return;
  }

  // Backspace
  if (k === '\x7f' || k === '\b') {
    if (S.cursor > 0) {
      S.input = S.input.slice(0, S.cursor - 1) + S.input.slice(S.cursor);
      S.cursor--;
      updateMenu();
      render();
    }
    return;
  }

  if (k === '\x15') { S.input = ''; S.cursor = 0; S.menuOpen = false; render(); return; }
  if (k === '\x17') {
    const before = S.input.slice(0, S.cursor).replace(/\S+\s*$/, '');
    S.input = before + S.input.slice(S.cursor);
    S.cursor = before.length;
    updateMenu(); render(); return;
  }
  if (k === '\x1b[3~') {
    if (S.cursor < S.input.length) {
      S.input = S.input.slice(0, S.cursor) + S.input.slice(S.cursor + 1);
      updateMenu(); render();
    }
    return;
  }

  if (k.length === 1 && k >= ' ') {
    S.input = S.input.slice(0, S.cursor) + k + S.input.slice(S.cursor);
    S.cursor++;
    updateMenu(); render();
    return;
  }

  if (k.length > 1 && !k.startsWith('\x1b')) {
    S.input = S.input.slice(0, S.cursor) + k + S.input.slice(S.cursor);
    S.cursor += k.length;
    updateMenu(); render();
  }
}

// ═══════════════════════════════════════════════════════════════
//  STARTUP BOOT
// ═══════════════════════════════════════════════════════════════
async function boot() {
  ensureLogs();
  log('─'.repeat(50));
  log(`SESSION START · ${os.platform()} · Node ${process.version}`);
  log(`Model: ${S.model.name}`);

  w(ALT_ON, HIDE, CLR);

  const cols = W();
  const rows = H();
  const cx = Math.floor(cols / 2);
  const cy = Math.floor(rows / 2) - 2;

  for (let i = 0; i < LOGO.length; i++) {
    const lpad = Math.max(1, cx - Math.floor(LOGO[i].length / 2));
    w(at(lpad, cy + i));
    w(`${P.accent}${BD}${LOGO[i]}${R}`);
  }

  const tag = 'ELE Agent × First CLI';
  w(at(cx - Math.floor(tag.length / 2), cy + LOGO.length + 1));
  for (let i = 0; i < tag.length; i++) {
    w(`${P.muted}${DM}${tag[i]}${R}`);
    await sleep(10);
  }

  const steps = ['Loading ELE Credentials', 'Connecting Model Router', 'Ready'];
  for (const s of steps) {
    w(ELINE);
    w(at(cx - Math.floor(s.length / 2) - 1, cy + LOGO.length + 3));
    w(`${P.muted}${DM}${s}${R}`);
    await sleep(120);
  }

  await sleep(150);

  S.messages.push({
    type: 'info',
    text: `ELE Agent connected. Active model: ${S.model.name}\nType / for commands, or type any request.`
  });

  if (process.stdin.isTTY) process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', onKey);
  process.stdout.on('resize', () => render());
  process.on('SIGINT', cmdExit);
  process.on('SIGTERM', cmdExit);
  process.on('exit', () => { w(SHOW, ALT_OFF); });

  render();
}

boot().catch(err => {
  w(SHOW, ALT_OFF);
  console.error('Error:', err);
  process.exit(1);
});
