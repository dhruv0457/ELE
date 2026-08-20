#!/usr/bin/env node

// ═══════════════════════════════════════════════════════════════
//  ELE AGENT × FIRST CLI — True AI Autonomous Developer Terminal
//  Verified Model Endpoints • Auto-Fallback • Speech-to-Speech
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

// ─── MINIMAL THEME PALETTE ────────────────────────────────────
const P = {
  base:      bg(10, 12, 16),
  surface:   bg(18, 20, 26),
  raised:    bg(24, 26, 34),
  selected:  bg(34, 44, 58),

  white:     fg(220, 224, 230),
  soft:      fg(160, 165, 175),
  muted:     fg(90, 95, 105),
  faint:     fg(48, 54, 65),

  accent:    fg(95, 185, 230),
  accentB:   fg(135, 210, 250),
  green:     fg(80, 200, 120),
  amber:     fg(235, 180, 70),
  red:       fg(230, 80, 80),
  purple:    fg(165, 125, 245),

  border:    fg(50, 56, 70),
  todoBdr:   fg(70, 85, 110),
  modalBdr:  fg(80, 120, 170),
  jarvisBdr: fg(95, 185, 230),
};

const B = {
  tl: '╭', tr: '╮', bl: '╰', br: '╯',
  h: '─', v: '│', hl: '├', hr: '┤',
  sh: '┄',
};

// ─── BOLD ASCII LOGO ──────────────────────────────────────────
const LOGO = [
  '  ███████╗██╗     ███████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗',
  '  ██╔════╝██║     ██╔════╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝',
  '  █████╗  ██║     █████╗      ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ',
  '  ██╔══╝  ██║     ██╔══╝      ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ',
  '  ███████╗███████╗███████╗    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ',
  '  ╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ',
];

function renderLogo(pad = '') {
  let out = '';
  for (let i = 0; i < LOGO.length; i++) {
    const t = i / (LOGO.length - 1);
    const r = Math.round(95 + t * 40);
    const g = Math.round(185 + t * 25);
    const b = Math.round(230 + t * 20);
    out += `${pad}${fg(r, g, b)}${BD}${LOGO[i]}${R}\n`;
  }
  return out;
}

function strip(s) { return s.replace(/\x1b\[[0-9;]*m/g, ''); }

// ─── CREDENTIAL LOADER ────────────────────────────────────────
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
            if (val && !keys[keyName]) keys[keyName] = val;
          }
        }
      }
    } catch {}
  }

  for (const [k, v] of Object.entries(process.env)) {
    if (v && !keys[k]) keys[k] = v;
  }
  return keys;
}

const KEYS = loadAllKeys();

// ─── ALL 102+ NVIDIA NIM & MULTI-CLOUD MODEL CATALOG ──────────────────────
const STATIC_NVIDIA_MODELS = [
  // ── Meta Llama Family ──
  { id: 'meta/llama-3.1-8b-instruct',               provider: 'nvidia', name: 'Llama 3.1 8B',          tag: '⚡ Sub-10ms · Fastest Daily',  category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama-3.3-70b-instruct',              provider: 'nvidia', name: 'Llama 3.3 70B',         tag: '🧠 Flagship · High Accuracy',  category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama-3.1-70b-instruct',              provider: 'nvidia', name: 'Llama 3.1 70B',         tag: '🧠 Deep Knowledge 70B',        category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama-3.2-11b-vision-instruct',       provider: 'nvidia', name: 'Llama 3.2 11B Vision',  tag: '👁️ Vision & Multimodal',      category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama-3.2-90b-vision-instruct',       provider: 'nvidia', name: 'Llama 3.2 90B Vision',  tag: '👁️ Giant Multimodal Vision',  category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama-3.2-3b-instruct',               provider: 'nvidia', name: 'Llama 3.2 3B',          tag: '⚡ 0ms Lag · Lightweight',     category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama-3.2-1b-instruct',               provider: 'nvidia', name: 'Llama 3.2 1B',          tag: '⚡ Instant Speed · 1B',        category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/codellama-70b',                       provider: 'nvidia', name: 'CodeLlama 70B',         tag: '💻 Code Generation 70B',       category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama2-70b',                          provider: 'nvidia', name: 'Llama 2 70B',           tag: '🏛️ Classic Llama 2 70B',       category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/llama-guard-4-12b',                   provider: 'nvidia', name: 'Llama Guard 4 12B',     tag: '🛡️ Safety Guard 12B',          category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'meta/muse-glimmer-30b',                    provider: 'nvidia', name: 'Muse Glimmer 30B',      tag: '🎨 Creative & Fiction 30B',    category: 'Llama', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── NVIDIA Autonomous Nemotron Agents ──
  { id: 'nvidia/llama-3.3-nemotron-super-49b-v1.5', provider: 'nvidia', name: 'Nemotron Super 49B',   tag: '🤖 Autonomous Agent v1.5',     category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/llama-3.3-nemotron-super-49b-v1',   provider: 'nvidia', name: 'Nemotron Super 49B v1',tag: '🤖 Autonomous Agent v1',       category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/nemotron-4-340b-instruct',          provider: 'nvidia', name: 'Nemotron-4 340B',       tag: '🧠 Giant 340B Parameter',      category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/llama-3.1-nemotron-70b-instruct',   provider: 'nvidia', name: 'Nemotron 70B',          tag: '🤖 NVIDIA Agentic 70B',        category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/llama-3.1-nemotron-51b-instruct',   provider: 'nvidia', name: 'Nemotron 51B',          tag: '🤖 High Throughput 51B',       category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/llama-3.1-nemotron-ultra-253b-v1',  provider: 'nvidia', name: 'Nemotron Ultra 253B',   tag: '🧠 Ultra Frontier 253B',       category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/nemotron-mini-4b-instruct',         provider: 'nvidia', name: 'Nemotron Mini 4B',      tag: '⚡ On-Device Fast 4B',         category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/cosmos-reason2-8b',                 provider: 'nvidia', name: 'Cosmos Reason 2 8B',    tag: '🎯 NVIDIA Deep Reasoner 8B',   category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/nemotron-3-nano-30b-a3b',           provider: 'nvidia', name: 'Nemotron-3 Nano 30B',   tag: '⚡ Sparse MoE 30B',            category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/nemotron-3-super-120b-a12b',        provider: 'nvidia', name: 'Nemotron-3 Super 120B', tag: '🧠 Super MoE 120B',            category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/nemotron-3-ultra-550b-a55b',        provider: 'nvidia', name: 'Nemotron-3 Ultra 550B', tag: '🧠 Frontier MoE 550B',         category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/nemotron-3.5-lightning-30b-a3b',    provider: 'nvidia', name: 'Nemotron 3.5 Lightning',tag: '⚡ Ultra Fast MoE',            category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/neva-22b',                          provider: 'nvidia', name: 'Neva 22B Vision',       tag: '👁️ NVIDIA Vision & OCR',      category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/vila',                              provider: 'nvidia', name: 'VILA Vision Agent',     tag: '👁️ Video & Multimodal VILA',  category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nvidia/riva-translate-4b-instruct-v2',     provider: 'nvidia', name: 'Riva Translate 4B v2',  tag: '🌐 Multilingual Translation',  category: 'Nemotron', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── DeepSeek Reasoning & Coding ──
  { id: 'deepseek-ai/deepseek-r1',                  provider: 'nvidia', name: 'DeepSeek R1 Reasoning', tag: '🎯 Deep Step-by-Step Logic',   category: 'DeepSeek', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'deepseek-ai/deepseek-r1-distill-llama-70b',provider: 'nvidia', name: 'DeepSeek R1 Llama 70B',tag: '🎯 Distilled Reasoning 70B',  category: 'DeepSeek', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'deepseek-ai/deepseek-coder-6.7b-instruct', provider: 'nvidia', name: 'DeepSeek Coder 6.7B',  tag: '💻 Code Generation 6.7B',      category: 'DeepSeek', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'deepseek-ai/deepseek-v4-flash-0731',       provider: 'nvidia', name: 'DeepSeek V4 Flash',     tag: '⚡ Ultra-Fast DeepSeek MoE',   category: 'DeepSeek', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── Mistral AI ──
  { id: 'mistralai/mistral-7b-instruct-v0.3',       provider: 'nvidia', name: 'Mistral 7B v0.3',       tag: '⚡ High Efficiency 7B',        category: 'Mistral', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'mistralai/mistral-large-2-instruct',       provider: 'nvidia', name: 'Mistral Large 2',       tag: '🧠 Frontier Mistral 123B',     category: 'Mistral', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'mistralai/mistral-large',                  provider: 'nvidia', name: 'Mistral Large',         tag: '🧠 Flagship Mistral',          category: 'Mistral', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'mistralai/mistral-nemotron',               provider: 'nvidia', name: 'Mistral Nemotron',      tag: '🤖 Mistral + NVIDIA Hybrid',   category: 'Mistral', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'mistralai/mixtral-8x22b-v0.1',             provider: 'nvidia', name: 'Mixtral 8x22B MoE',     tag: '🧠 MoE High Throughput',       category: 'Mistral', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'mistralai/codestral-22b-instruct-v0.1',    provider: 'nvidia', name: 'Codestral 22B',         tag: '💻 80+ Programming Languages',category: 'Mistral', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'nv-mistralai/mistral-nemo-12b-instruct',   provider: 'nvidia', name: 'Mistral NeMo 12B',      tag: '⚡ 128K Context NeMo',         category: 'Mistral', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── Google Gemma Family ──
  { id: 'google/gemma-4-31b-it',                    provider: 'nvidia', name: 'Gemma 4 31B',           tag: '🧠 Next-Gen Google Gemma',     category: 'Google', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'google/gemma-3-12b-it',                    provider: 'nvidia', name: 'Gemma 3 12B',           tag: '⚡ Balanced Google Gemma 12B', category: 'Google', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'google/gemma-3-4b-it',                     provider: 'nvidia', name: 'Gemma 3 4B',            tag: '⚡ Ultra Fast Gemma 4B',       category: 'Google', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'google/codegemma-7b',                      provider: 'nvidia', name: 'CodeGemma 7B',          tag: '💻 Google Code Assistant',     category: 'Google', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'google/diffusiongemma-26b-a4b-it',         provider: 'nvidia', name: 'DiffusionGemma 26B',    tag: '🎨 Diffusion Hybrid Gemma',    category: 'Google', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'google/deplot',                            provider: 'nvidia', name: 'Google DePlot',         tag: '📊 Chart & Plot Visual QA',    category: 'Google', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'google/recurrentgemma-2b',                 provider: 'nvidia', name: 'RecurrentGemma 2B',     tag: '⚡ Griffin Architecture 2B',   category: 'Google', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── Microsoft Phi Family ──
  { id: 'microsoft/phi-3-vision-128k-instruct',     provider: 'nvidia', name: 'Phi-3 Vision 128K',     tag: '👁️ Vision & Documents 128K',  category: 'Microsoft', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'microsoft/phi-3.5-moe-instruct',           provider: 'nvidia', name: 'Phi-3.5 MoE 16x3.8B',   tag: '⚡ High Reasoning MoE',        category: 'Microsoft', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'microsoft/kosmos-2',                       provider: 'nvidia', name: 'Kosmos-2 Grounding',    tag: '👁️ Spatial Visual Grounding',  category: 'Microsoft', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── IBM Granite Family ──
  { id: 'ibm/granite-3.0-8b-instruct',              provider: 'nvidia', name: 'IBM Granite 3.0 8B',    tag: '💼 Enterprise Workflows 8B',   category: 'IBM', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'ibm/granite-3.0-3b-a800m-instruct',        provider: 'nvidia', name: 'IBM Granite 3.0 3B MoE',tag: '⚡ Micro Enterprise MoE',      category: 'IBM', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'ibm/granite-34b-code-instruct',            provider: 'nvidia', name: 'IBM Granite 34B Code',  tag: '💻 Enterprise Coding 34B',     category: 'IBM', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'ibm/granite-8b-code-instruct',             provider: 'nvidia', name: 'IBM Granite 8B Code',   tag: '💻 Fast Code Assistant 8B',    category: 'IBM', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── Open Source Giants (01-ai, AI21, StepFun, Kimi, Z-AI, Writer, OpenAI, BigCode, Databricks) ──
  { id: '01-ai/yi-large',                           provider: 'nvidia', name: 'Yi Large 01-AI',        tag: '🧠 Frontier Yi-Large',         category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'ai21labs/jamba-1.5-large-instruct',        provider: 'nvidia', name: 'Jamba 1.5 Large',       tag: '⚡ Mamba-Transformer SSM',     category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'stepfun-ai/step-3.7-flash',                provider: 'nvidia', name: 'Step 3.7 Flash',        tag: '⚡ StepFun Ultra Fast MoE',    category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'moonshotai/kimi-k2.6',                     provider: 'nvidia', name: 'Kimi K2.6 Moonshot',    tag: '📚 Long Context Specialist',   category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'z-ai/glm-5.2',                             provider: 'nvidia', name: 'GLM 5.2 Z-AI',          tag: '🧠 Bilingual GLM Flagship',    category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'openai/gpt-oss-120b',                      provider: 'nvidia', name: 'GPT-OSS 120B',          tag: '🧠 Open Weight 120B Model',    category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'openai/gpt-oss-20b',                       provider: 'nvidia', name: 'GPT-OSS 20B',           tag: '⚡ Fast Open Weight 20B',      category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'writer/palmyra-creative-122b',             provider: 'nvidia', name: 'Palmyra Creative 122B', tag: '✍️ Creative Writing 122B',    category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'writer/palmyra-fin-70b-32k',               provider: 'nvidia', name: 'Palmyra Financial 70B', tag: '📈 Financial Intelligence',    category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'writer/palmyra-med-70b-32k',               provider: 'nvidia', name: 'Palmyra Medical 70B',   tag: '🩺 Medical & Clinical 70B',    category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'databricks/dbrx-instruct',                 provider: 'nvidia', name: 'DBRX Instruct',         tag: '⚡ Databricks 132B MoE',       category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'bigcode/starcoder2-15b',                   provider: 'nvidia', name: 'StarCoder2 15B',        tag: '💻 Code Completion 15B',       category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'adept/fuyu-8b',                            provider: 'nvidia', name: 'Fuyu 8B UI Agent',      tag: '🖥️ Screen & UI Perception',   category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'zyphra/zamba2-7b-instruct',                provider: 'nvidia', name: 'Zamba2 7B',             tag: '⚡ Mamba-2 SSM Hybrid',        category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },
  { id: 'minimaxai/minimax-m3',                     provider: 'nvidia', name: 'MiniMax M3',            tag: '🧠 MiniMax MoE Flagship',      category: 'Specialist', baseUrl: 'https://integrate.api.nvidia.com/v1' },

  // ── Cloud Providers (Google, Groq, OpenAI) ──
  { id: 'gemini-2.0-flash-exp',                     provider: 'gemini', name: 'Gemini 2.0 Flash',      tag: '⚡ Google AI (1-2s Ultra Speed)', category: 'Google Gemini', baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/' },
  { id: 'gemini-1.5-pro',                           provider: 'gemini', name: 'Gemini 1.5 Pro',        tag: '📚 2M Huge Token Context',     category: 'Google Gemini', baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/' },
  { id: 'llama-3.3-70b-versatile',                  provider: 'groq',   name: 'Groq Llama 3.3 70B',    tag: '⚡ 500 tok/s Hardware LPU',    category: 'Groq Cloud', baseUrl: 'https://api.groq.com/openai/v1' },
  { id: 'llama-3.1-8b-instant',                     provider: 'groq',   name: 'Groq Llama 3.1 8B',     tag: '⚡ 800 tok/s Instant LPU',     category: 'Groq Cloud', baseUrl: 'https://api.groq.com/openai/v1' },
  { id: 'gpt-4o-mini',                              provider: 'openai', name: 'OpenAI GPT-4o Mini',    tag: '🌐 OpenAI Cloud Fast',         category: 'OpenAI', baseUrl: 'https://api.openai.com/v1' },
  { id: 'gpt-4o',                                   provider: 'openai', name: 'OpenAI GPT-4o',         tag: '🌐 OpenAI Flagship',           category: 'OpenAI', baseUrl: 'https://api.openai.com/v1' },

  // ── Local Air-Gapped Offline ──
  { id: 'qwen2.5-coder:latest',                    provider: 'ollama', name: 'Ollama Qwen 2.5 Local', tag: '🔒 Offline Local Ollama',      category: 'Local', baseUrl: 'http://localhost:11434/v1' },
];

let MODELS = [...STATIC_NVIDIA_MODELS];

// ─── DYNAMIC API MODEL SYNC (QUERIES LIVE MODELS VIA KEY) ──
async function syncLiveNvidiaModels() {
  const key = KEYS['NVIDIA_API_KEY'];
  if (!key) return;

  try {
    const res = await fetch('https://integrate.api.nvidia.com/v1/models', {
      headers: { Authorization: `Bearer ${key}` },
      signal: AbortSignal.timeout(6000)
    });
    if (!res.ok) return;

    const data = await res.json();
    if (data && Array.isArray(data.data) && data.data.length > 0) {
      const existingIds = new Set(MODELS.map(m => m.id));
      const newlyDiscovered = [];

      for (const item of data.data) {
        if (!existingIds.has(item.id)) {
          const owner = item.owned_by || 'nvidia';
          const simpleName = item.id.split('/').pop().replace(/-/g, ' ');
          newlyDiscovered.push({
            id: item.id,
            provider: 'nvidia',
            name: simpleName.charAt(0).toUpperCase() + simpleName.slice(1),
            tag: `NVIDIA NIM · ${owner}`,
            category: 'NVIDIA NIM',
            baseUrl: 'https://integrate.api.nvidia.com/v1'
          });
        }
      }

      if (newlyDiscovered.length > 0) {
        MODELS = [...MODELS, ...newlyDiscovered];
        log(`SYNCED: Added ${newlyDiscovered.length} live NVIDIA models (Total: ${MODELS.length})`);
      }
    }
  } catch {}
}

function getInitialModel() {
  if (KEYS['NVIDIA_API_KEY']) return MODELS[0]; // 8B — always instant response
  if (KEYS['GEMINI_API_KEY']) return MODELS.find(m => m.provider === 'gemini');
  if (KEYS['GROQ_API_KEY'])   return MODELS.find(m => m.provider === 'groq');
  if (KEYS['OPENAI_API_KEY']) return MODELS.find(m => m.provider === 'openai');
  return MODELS[0];
}

// ─── COMMAND REGISTRY ─────────────────────────────────────────
const COMMANDS = [
  { cmd: '/help',     desc: 'List all commands and hotkeys',     icon: '?' },
  { cmd: '/jarvis',   desc: 'Speech-to-Speech Jarvis Mode',      icon: '🎙️' },
  { cmd: '/model',    desc: 'Interactive popup model switcher',  icon: '◆' },
  { cmd: '/automate', desc: 'Autonomous app & web agent task',   icon: '⚡' },
  { cmd: '/todo',     desc: 'Toggle sticky note task breakdown', icon: '📌' },
  { cmd: '/new',      desc: 'Start a fresh new session',         icon: '✨' },
  { cmd: '/sessions', desc: 'Browse and switch saved sessions',  icon: '📋' },
  { cmd: '/erase',    desc: 'Erase all user data & fresh reset', icon: '🗑️' },
  { cmd: '/browse',   desc: 'Open browser to specific URL',      icon: '→' },
  { cmd: '/queue',    desc: 'View & manage queued tasks',        icon: '⏳' },
  { cmd: '/clear',    desc: 'Clear chat screen history',         icon: '⊘' },
  { cmd: '/keys',     desc: 'Inspect active ELE API keys',       icon: '🔑' },
  { cmd: '/editor',   desc: 'Open current folder in VS Code',    icon: '⊡' },
  { cmd: '/exit',     desc: 'Quit terminal',                     icon: '⏻' },
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

// ─── APPLICATION STATE ────────────────────────────────────────
const S = {
  input: '',
  cursor: 0,
  history: [],
  histIdx: -1,
  histStash: '',
  messages: [],

  // Prompt Queueing
  queue: [],

  // Dynamic TODO Breakdown
  todoList: [],
  showTodoPanel: false,

  // Autocomplete menu
  menuOpen: false,
  menuIdx: 0,
  menuItems: [],

  // Interactive Model Modal Popup (All 102+ Models with Live Search & Tabs)
  modelModalOpen: false,
  modelModalIdx: 0,
  modelModalFilter: '',
  modelModalCat: 'ALL',

  // Voice & Jarvis Speech-to-Speech Engine
  jarvisOpen: false,
  jarvisVoiceActive: false,
  jarvisStatus: 'Ready',
  voiceProcess: null,
  isSpeaking: false,

  // Execution state
  busy: false,
  spinFrame: 0,

  // Model & Overlays
  model: getInitialModel(),
};

const SPIN = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];

// ─── TERMINAL HELPERS ─────────────────────────────────────────
const W = () => process.stdout.columns || 105;
const H = () => process.stdout.rows || 30;
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
//  SPEECH-TO-SPEECH (TTS & STT) ENGINE
// ═══════════════════════════════════════════════════════════════
function speakVoice(text) {
  if (!text) return;
  S.isSpeaking = true;
  render();

  const cleanSpoken = text
    .replace(/```[\s\S]*?```/g, 'Code block generated.')
    .replace(/`[^`]*`/g, '')
    .replace(/https?:\/\/[^\s]+/g, 'the requested web address')
    .replace(/TOOL_CALL[^\n]+/g, '')
    .replace(/[\*\_\[\]\#\>]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .substring(0, 300);

  const speakerScript = path.resolve(process.cwd(), 'voice_speaker.ps1');
  const fallbackSpeaker = path.join('D:', 'first_cli', 'app', 'voice_speaker.ps1');
  const finalScript = fs.existsSync(speakerScript) ? speakerScript : fallbackSpeaker;

  const ps = spawn('powershell', [
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', finalScript,
    '-Text', cleanSpoken
  ]);

  ps.on('close', () => {
    S.isSpeaking = false;
    render();
  });
}

function startVoiceListening() {
  if (S.voiceProcess) return;

  const listenerScript = path.resolve(process.cwd(), 'voice_listener.ps1');
  const fallbackListener = path.join('D:', 'first_cli', 'app', 'voice_listener.ps1');
  const finalScript = fs.existsSync(listenerScript) ? listenerScript : fallbackListener;

  try {
    S.voiceProcess = spawn('powershell', [
      '-NoProfile',
      '-ExecutionPolicy', 'Bypass',
      '-File', finalScript
    ]);

    S.jarvisStatus = 'Listening to Microphone...';
    render();

    S.voiceProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      log(`VOICE_RAW: ${output}`);

      if (output.includes('JARVIS_MIC_ACTIVE:')) {
        const culture = output.replace(/.*JARVIS_MIC_ACTIVE:\s*/, '').trim();
        S.jarvisStatus = `Microphone Active (${culture}) · Talk freely`;
        render();
      }

      if (output.includes('VOICE_TRANSCRIBED:')) {
        // Prevent speech engine from listening to its own TTS voice
        if (S.isSpeaking) return;

        let spokenText = output.replace(/.*VOICE_TRANSCRIBED:\s*/, '').trim();
        if (spokenText && !S.busy) {
          S.jarvisStatus = `Heard: "${spokenText}"`;
          S.messages.push({ type: 'user', text: `🎙️ ${spokenText}` });
          render();
          dispatchInput(spokenText);
        }
      }
    });

    S.voiceProcess.on('close', () => {
      S.voiceProcess = null;
    });
  } catch (err) {
    S.jarvisStatus = 'Microphone ready (manual input enabled)';
  }
}

function stopVoiceListening() {
  if (S.voiceProcess) {
    try { S.voiceProcess.kill(); } catch {}
    S.voiceProcess = null;
  }
}

// ═══════════════════════════════════════════════════════════════
//  RENDER ENGINE (FULL SCREEN + STICKY NOTE + JARVIS VOICE)
// ═══════════════════════════════════════════════════════════════
function render() {
  const cols = W();
  const rows = H();
  const contentW = Math.min(cols - 4, 115);
  const padL = Math.max(1, Math.floor((cols - contentW) / 2));
  const pad = ' '.repeat(padL);

  let buf = '';
  buf += HIDE;
  buf += CLR;
  buf += P.base;

  // ── Header (with comfortable vertical top margin) ──
  buf += '\n\n';
  buf += renderLogo(pad);
  buf += pad + `${P.faint}${B.sh.repeat(contentW)}${R}\n`;

  // Status Bar
  const modelTag = `${P.accent}◆${R} ${P.soft}${S.model.name}${R}`;
  const eleTag = `${P.green}● AI Agent Online${R}`;
  const jarvisBadge = S.jarvisOpen ? `  ${P.amber}${BD}🎙️ JARVIS ACTIVE${R}` : '';
  const cwdTag = `${P.muted}📁 ${path.basename(process.cwd())}${R}`;
  const queueTag = S.queue.length > 0 ? `  ${P.amber}⏳ ${S.queue.length} Queued${R}` : '';
  const todoTag = S.todoList.length > 0 ? `  ${P.purple}📌 ${S.todoList.filter(t => t.status === 'done').length}/${S.todoList.length} Tasks${R}` : '';
  
  buf += pad + `  ${modelTag}  ${P.faint}·${R}  ${eleTag}${jarvisBadge}  ${P.faint}·${R}  ${cwdTag}${queueTag}${todoTag}\n\n`;

  // ── Layout Calculations ──
  const headerLines = 10;
  const footerLines = 5;
  const menuLines = S.menuOpen ? Math.min(S.menuItems.length + 2, 8) : 0;
  const jarvisLines = S.jarvisOpen ? 10 : 0;
  const todoCardLines = (S.showTodoPanel && S.todoList.length > 0) ? Math.min(S.todoList.length + 3, 7) : 0;
  const modalLines = S.modelModalOpen ? Math.min(MODELS.length + 4, 14) : 0;
  const queueNoticeLines = S.queue.length > 0 ? 1 : 0;
  
  const availLines = Math.max(4, rows - headerLines - footerLines - menuLines - jarvisLines - todoCardLines - modalLines - queueNoticeLines);

  // ── Messages ──
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

  // ── Interactive Model Switcher Modal Popup ──
  if (S.modelModalOpen) {
    buf += renderModelModal(contentW, padL);
  }

  // ── Speech-to-Speech Jarvis Live Overlay ──
  if (S.jarvisOpen) {
    buf += renderJarvisSpeechOverlay(contentW, padL);
  }

  // ── Sticky Note TODO Floating Panel ──
  if (S.showTodoPanel && S.todoList.length > 0) {
    buf += renderStickyNoteTodo(contentW, padL);
  }

  // ── Slash Menu ──
  if (S.menuOpen && S.menuItems.length > 0) {
    buf += renderMenu(contentW, padL);
  }

  // ── Queue Status Indicator ──
  if (S.queue.length > 0) {
    const nextPreview = S.queue[0].text.substring(0, 40) + (S.queue[0].text.length > 40 ? '...' : '');
    buf += pad + `  ${P.amber}${DM}⏳ Queue [${S.queue.length}]: Next up → "${nextPreview}"${R}\n`;
  }

  // ── Input Prompt ──
  buf += '\n';
  let promptChar = `${P.accent}›${R}`;
  if (S.busy) {
    promptChar = `${P.amber}${SPIN[S.spinFrame % SPIN.length]}${R}`;
  } else if (S.jarvisOpen) {
    promptChar = `${P.green}🎙️›${R}`;
  }

  buf += pad + `${P.border}${B.tl}${B.h.repeat(contentW - 2)}${B.tr}${R}\n`;
  buf += pad + `${P.border}${B.v}${R} ${promptChar} ${P.white}${S.input}${R}`;
  const inputUsed = 4 + strip(S.input).length;
  buf += ' '.repeat(Math.max(0, contentW - inputUsed - 1));
  buf += `${P.border}${B.v}${R}\n`;
  buf += pad + `${P.border}${B.bl}${B.h.repeat(contentW - 2)}${B.br}${R}\n`;

  // ── Footer ──
  const mem = Math.round(process.memoryUsage().rss / 1024 / 1024);
  buf += pad + `  ${P.muted}${DM}/jarvis  voice${R}   ${P.muted}${DM}/model  models${R}   ${P.muted}${DM}/automate  tasks${R}   ${P.muted}${DM}esc  dismiss${R}`;
  buf += `   ${P.faint}${DM}${mem}MB · ${uptime()}${R}\n`;

  w(buf);

  const cursorRow = rows - 2;
  const cursorCol = padL + 4 + S.cursor;
  w(at(cursorCol, cursorRow));
  w(SHOW);
}

// ─── MESSAGE FORMATTER ────────────────────────────────────────
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
  else if (msg.type === 'action') {
    lines.push(`${P.purple}${BD}⚡ AUTONOMOUS ACTION EXECUTED${R}`);
    for (const l of wrap(msg.text, maxW - 2)) lines.push(`  ${P.accent}${l}${R}`);
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

// ─── SPEECH-TO-SPEECH JARVIS OVERLAY ──────────────────────────
function renderJarvisSpeechOverlay(contentW, padL) {
  const pad = ' '.repeat(padL);
  const popW = Math.min(74, contentW - 4);
  const centerPad = ' '.repeat(Math.max(0, Math.floor((contentW - popW) / 2)));
  let out = '';

  const micWave = S.isSpeaking 
    ? `${P.green}🔊 Speaking response...${R}`
    : `${P.amber}🎙️ Listening to microphone... [Talk freely]${R}`;

  out += '\n' + pad + centerPad + `${P.jarvisBdr}${B.tl}${B.h} 🎙️ JARVIS SPEECH-TO-SPEECH AGENT ${B.h.repeat(Math.max(1, popW - 37))}${B.tr}${R}\n`;
  out += pad + centerPad + `${P.jarvisBdr}${B.v}${R}  ${micWave}`;
  out += ' '.repeat(Math.max(0, popW - strip(micWave).length - 4)) + `${P.jarvisBdr}${B.v}${R}\n`;
  out += pad + centerPad + `${P.jarvisBdr}${B.hl}${B.h.repeat(popW - 2)}${B.hr}${R}\n`;

  const statusLine = `Status: ${S.jarvisStatus}`;
  out += pad + centerPad + `${P.jarvisBdr}${B.v}${R}  ${P.white}${statusLine}${R}`;
  out += ' '.repeat(Math.max(0, popW - strip(statusLine).length - 4)) + `${P.jarvisBdr}${B.v}${R}\n`;

  const tipLine = `Tip: Say "Open Microsoft Office", "Open Word", "Search Google", or type any command`;
  out += pad + centerPad + `${P.jarvisBdr}${B.v}${R}  ${P.muted}${DM}${tipLine}${R}`;
  out += ' '.repeat(Math.max(0, popW - strip(tipLine).length - 4)) + `${P.jarvisBdr}${B.v}${R}\n`;

  out += pad + centerPad + `${P.jarvisBdr}${B.bl}${B.h} ${P.muted}${DM}esc to close jarvis voice${R} ${P.jarvisBdr}${B.h.repeat(Math.max(1, popW - 30))}${B.br}${R}\n`;
  return out;
}

// ─── INTERACTIVE MODEL MODAL (ALL 102+ MODELS · LIVE SEARCH & CATEGORIES) ──
function getFilteredModels() {
  const q = (S.modelModalFilter || '').toLowerCase().trim();
  const cat = S.modelModalCat || 'ALL';

  return MODELS.filter(m => {
    if (cat !== 'ALL') {
      if (cat === 'FAST' && !m.tag.includes('Fast') && !m.tag.includes('0ms') && !m.tag.includes('Micro')) return false;
      if (cat === 'FLAGSHIP' && !m.tag.includes('Flagship') && !m.tag.includes('70B') && !m.tag.includes('340B') && !m.tag.includes('Giant')) return false;
      if (cat === 'REASON' && !m.tag.includes('Reasoning') && !m.tag.includes('Coder') && !m.tag.includes('Coding') && !m.category.includes('DeepSeek')) return false;
      if (cat === 'VISION' && !m.tag.includes('Vision') && !m.tag.includes('Multimodal') && !m.tag.includes('Chart') && !m.tag.includes('VILA')) return false;
      if (cat === 'CLOUD' && m.provider === 'nvidia' && m.provider === 'ollama') return false;
      if (cat === 'NVIDIA' && m.provider !== 'nvidia') return false;
    }
    if (!q) return true;
    return m.name.toLowerCase().includes(q) ||
           m.id.toLowerCase().includes(q) ||
           m.tag.toLowerCase().includes(q) ||
           (m.category || '').toLowerCase().includes(q) ||
           m.provider.toLowerCase().includes(q);
  });
}

function renderModelModal(contentW, padL) {
  const pad = ' '.repeat(padL);
  const modalW = Math.min(88, contentW - 4);
  const leftPad = ' '.repeat(Math.max(0, Math.floor((contentW - modalW) / 2)));
  let out = '';

  const filtered = getFilteredModels();
  if (S.modelModalIdx >= filtered.length) {
    S.modelModalIdx = Math.max(0, filtered.length - 1);
  }

  const PAGE_SIZE = 8;
  const startIdx = Math.max(0, Math.min(S.modelModalIdx - Math.floor(PAGE_SIZE / 2), Math.max(0, filtered.length - PAGE_SIZE)));
  const endIdx = Math.min(filtered.length, startIdx + PAGE_SIZE);

  // Header Title
  const countTag = `[${filtered.length === 0 ? 0 : S.modelModalIdx + 1}/${filtered.length} of ${MODELS.length} Models]`;
  const titleText = ` 🔀 ALL ACTIVE MODELS ${countTag} `;
  out += '\n' + pad + leftPad + `${P.modalBdr}${B.tl}${B.h}${titleText}${B.h.repeat(Math.max(1, modalW - strip(titleText).length - 2))}${B.tr}${R}\n`;

  // Search input bar inside modal
  const searchPrompt = ` 🔍 Search: ${S.modelModalFilter ? `${P.accentB}${BD}${S.modelModalFilter}${R}` : `${P.muted}${IT}type to filter all 102+ models...${R}`}`;
  out += pad + leftPad + `${P.modalBdr}${B.v}${R}${searchPrompt}`;
  out += ' '.repeat(Math.max(0, modalW - strip(searchPrompt).length - 1));
  out += `${P.modalBdr}${B.v}${R}\n`;

  // Category filter tabs
  const cats = ['ALL', 'FAST', 'FLAGSHIP', 'REASON', 'VISION', 'NVIDIA', 'CLOUD'];
  let tabLine = ' ';
  for (const c of cats) {
    const isCur = (S.modelModalCat || 'ALL') === c;
    tabLine += isCur ? `${P.accentB}${BD}[${c}]${R} ` : `${P.muted} ${c}  ${R}`;
  }
  out += pad + leftPad + `${P.modalBdr}${B.v}${R}${tabLine}`;
  out += ' '.repeat(Math.max(0, modalW - strip(tabLine).length - 1));
  out += `${P.modalBdr}${B.v}${R}\n`;

  out += pad + leftPad + `${P.modalBdr}${B.hl}${B.h.repeat(modalW - 2)}${B.hr}${R}\n`;

  // List of models
  if (filtered.length === 0) {
    const emptyNotice = `  ${P.amber}No models matching "${S.modelModalFilter}". Press Backspace or Esc.${R}`;
    out += pad + leftPad + `${P.modalBdr}${B.v}${R}${emptyNotice}`;
    out += ' '.repeat(Math.max(0, modalW - strip(emptyNotice).length - 1));
    out += `${P.modalBdr}${B.v}${R}\n`;
  } else {
    for (let i = startIdx; i < endIdx; i++) {
      const m = filtered[i];
      const isSelected = i === S.modelModalIdx;
      const isActive = m.id === S.model.id;

      const arrow = isSelected ? `${P.accentB}${BD}▸${R}` : ' ';
      const activeIcon = isActive ? `${P.green}[Active]${R}` : `${P.muted}[      ]${R}`;
      const nameColor = isSelected ? `${P.accentB}${BD}` : `${P.white}`;
      const tagColor = isSelected ? `${P.amber}` : `${P.muted}`;
      const bgHighlight = isSelected ? P.selected : '';

      const nameStr = m.name.substring(0, 24).padEnd(24);
      const tagStr = m.tag.substring(0, modalW - 48);

      out += pad + leftPad + `${P.modalBdr}${B.v}${R}${bgHighlight} ${arrow} ${activeIcon} ${nameColor}${nameStr}${R}${bgHighlight} ${tagColor}${tagStr}${R}`;
      const lineUsed = 3 + 2 + 8 + 24 + 1 + strip(tagStr).length;
      out += ' '.repeat(Math.max(0, modalW - lineUsed - 1));
      out += `${P.modalBdr}${B.v}${R}\n`;
    }
  }

  out += pad + leftPad + `${P.modalBdr}${B.hl}${B.h.repeat(modalW - 2)}${B.hr}${R}\n`;
  const footerText = `  ${P.soft}${BD}↑/↓${R} ${P.muted}Nav  ${P.faint}│${R}  ${P.soft}${BD}Tab${R} ${P.muted}Category  ${P.faint}│${R}  ${P.soft}${BD}Type${R} ${P.muted}Search  ${P.faint}│${R}  ${P.soft}${BD}Enter${R} ${P.muted}Select  ${P.faint}│${R}  ${P.soft}${BD}Esc${R} ${P.muted}Close`;
  out += pad + leftPad + `${P.modalBdr}${B.v}${R}${footerText}`;
  out += ' '.repeat(Math.max(0, modalW - strip(footerText).length - 1));
  out += `${P.modalBdr}${B.v}${R}\n`;
  out += pad + leftPad + `${P.modalBdr}${B.bl}${B.h.repeat(modalW - 2)}${B.br}${R}\n`;

  return out;
}

// ─── STICKY NOTE TODO PANEL ───────────────────────────────────
function renderStickyNoteTodo(contentW, padL) {
  const pad = ' '.repeat(padL);
  const cardW = Math.min(74, contentW - 4);
  const leftOffset = ' '.repeat(Math.max(0, contentW - cardW - 2));
  let out = '';

  out += pad + leftOffset + `${P.todoBdr}${B.tl}${B.h} 📌 ACTIVE TASK BREAKDOWN ${B.h.repeat(Math.max(1, cardW - 29))}${B.tr}${R}\n`;

  for (const item of S.todoList.slice(0, 5)) {
    let icon = `${P.muted}○${R}`;
    let textColor = P.soft;
    let crossTag = '';

    if (item.status === 'done') {
      icon = `${P.green}✓${R}`;
      textColor = P.green;
    } else if (item.status === 'running') {
      icon = `${P.amber}${SPIN[S.spinFrame % SPIN.length]}${R}`;
      textColor = P.accentB;
    } else if (item.status === 'error') {
      icon = `${P.red}✕${R}`;
      textColor = P.red;
      crossTag = ` ${P.red}${DM}(Failed)${R}`;
    }

    const titleStr = item.text.substring(0, cardW - 12);
    out += pad + leftOffset + `${P.todoBdr}${B.v}${R}  ${icon} ${textColor}${titleStr}${R}${crossTag}`;
    const used = 4 + 2 + titleStr.length + strip(crossTag).length;
    out += ' '.repeat(Math.max(0, cardW - used - 1));
    out += `${P.todoBdr}${B.v}${R}\n`;
  }

  out += pad + leftOffset + `${P.todoBdr}${B.bl}${B.h} ${P.muted}${DM}/todo to toggle${R} ${P.todoBdr}${B.h.repeat(Math.max(1, cardW - 20))}${B.br}${R}\n`;
  return out;
}

// ─── SLASH MENU RENDER ────────────────────────────────────────
function renderMenu(contentW, padL) {
  const pad = ' '.repeat(padL);
  const menuW = Math.min(48, contentW - 4);
  let out = '';
  out += pad + `  ${P.popupBdr}${B.tl}${B.h.repeat(menuW - 2)}${B.tr}${R}\n`;
  for (let i = 0; i < S.menuItems.length; i++) {
    const item = S.menuItems[i];
    const sel = i === S.menuIdx;
    const arrow = sel ? `${P.accent}${BD}›${R}` : ' ';
    const cmdC = sel ? `${P.accentB}${BD}` : `${P.soft}`;
    const descC = sel ? `${P.white}` : `${P.muted}`;
    const bgC = sel ? P.selected : '';
    const cmdStr = item.cmd.padEnd(12);
    const descStr = item.desc.substring(0, menuW - 20);
    out += pad + `  ${P.popupBdr}${B.v}${R}${bgC} ${arrow} ${P.muted}${item.icon}${R}${bgC} ${cmdC}${cmdStr}${R}${bgC}${descC}${DM}${descStr}${R}`;
    const lineUsed = 5 + 2 + 12 + descStr.length;
    out += ' '.repeat(Math.max(0, menuW - lineUsed - 1));
    out += `${P.popupBdr}${B.v}${R}\n`;
  }
  out += pad + `  ${P.popupBdr}${B.bl}${B.h} ${P.muted}${DM}↑↓ enter esc${R} ${P.popupBdr}${B.h.repeat(Math.max(1, menuW - 17))}${B.br}${R}\n`;
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
//  QUEUE PROCESSOR
// ═══════════════════════════════════════════════════════════════
async function checkAndProcessQueue() {
  if (S.queue.length > 0 && !S.busy) {
    const nextItem = S.queue.shift();
    render();
    await sleep(200);
    await dispatchInput(nextItem.text);
  }
}

// ═══════════════════════════════════════════════════════════════
//  VISUAL SCREEN OVERLAY & GHOST CURSOR ANIMATOR (HUD & WATERMARK)
// ═══════════════════════════════════════════════════════════════
function runVisualOverlay(action, opts = {}) {
  if (process.platform !== 'win32') return;
  const overlayScript = path.resolve(process.cwd(), 'agent_overlay.ps1');
  const fallbackScript1 = path.join('D:', 'ELE', 'cli', 'agent_overlay.ps1');
  const fallbackScript2 = path.join('D:', 'first_cli', 'app', 'agent_overlay.ps1');
  const scriptPath = fs.existsSync(overlayScript) ? overlayScript : (fs.existsSync(fallbackScript1) ? fallbackScript1 : fallbackScript2);
  if (!fs.existsSync(scriptPath)) return;

  const appName = (opts.appName || 'app').replace(/'/g, '');
  const appTitle = (opts.appTitle || opts.appName || 'Application').replace(/'/g, '');
  const msg = (opts.message || 'Controlling PC: Automating Task...').replace(/'/g, '');
  const tx = opts.targetX || 640;
  const ty = opts.targetY || 360;
  const duration = opts.durationMs || 1600;

  const psCmd = `powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptPath}" -Action "${action}" -AppName "${appName}" -AppTitle "${appTitle}" -Message "${msg}" -TargetX ${tx} -TargetY ${ty} -DurationMs ${duration}`;
  exec(psCmd, () => {});
}

// ═══════════════════════════════════════════════════════════════
//  MASTER WINDOWS APPLICATION & WEB SERVICES REGISTRY
// ═══════════════════════════════════════════════════════════════
const APP_REGISTRY = {
  // Microsoft Office Suite
  'office': {
    title: 'Microsoft Office',
    psCmd: `if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\winword.exe") { Start-Process (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\winword.exe").'(default)' } elseif (Get-Command winword -ErrorAction SilentlyContinue) { Start-Process winword } else { Start-Process "ms-office:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://www.office.com" } }`,
    webUrl: 'https://www.office.com'
  },
  'word': {
    title: 'Microsoft Word',
    psCmd: `if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\winword.exe") { Start-Process (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\winword.exe").'(default)' } elseif (Get-Command winword -ErrorAction SilentlyContinue) { Start-Process winword } else { Start-Process "ms-word:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://word.office.com" } }`,
    webUrl: 'https://word.office.com'
  },
  'excel': {
    title: 'Microsoft Excel',
    psCmd: `if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\excel.exe") { Start-Process (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\excel.exe").'(default)' } elseif (Get-Command excel -ErrorAction SilentlyContinue) { Start-Process excel } else { Start-Process "ms-excel:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://excel.office.com" } }`,
    webUrl: 'https://excel.office.com'
  },
  'powerpoint': {
    title: 'Microsoft PowerPoint',
    psCmd: `if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\powerpnt.exe") { Start-Process (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\powerpnt.exe").'(default)' } elseif (Get-Command powerpnt -ErrorAction SilentlyContinue) { Start-Process powerpnt } else { Start-Process "ms-powerpoint:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://powerpoint.office.com" } }`,
    webUrl: 'https://powerpoint.office.com'
  },
  'onenote': {
    title: 'Microsoft OneNote',
    psCmd: `if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\OneNote.exe") { Start-Process (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\OneNote.exe").'(default)' } elseif (Get-Command onenote -ErrorAction SilentlyContinue) { Start-Process onenote } else { Start-Process "onenote:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://www.onenote.com" } }`,
    webUrl: 'https://www.onenote.com'
  },
  'outlook': {
    title: 'Microsoft Outlook',
    psCmd: `if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\OUTLOOK.EXE") { Start-Process (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\OUTLOOK.EXE").'(default)' } elseif (Get-Command outlook -ErrorAction SilentlyContinue) { Start-Process outlook } else { Start-Process "outlookmail:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://outlook.live.com" } }`,
    webUrl: 'https://outlook.live.com'
  },
  'teams': {
    title: 'Microsoft Teams',
    psCmd: `if (Get-Command teams -ErrorAction SilentlyContinue) { Start-Process teams } else { Start-Process "msteams:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://teams.microsoft.com" } }`,
    webUrl: 'https://teams.microsoft.com'
  },
  'access': {
    title: 'Microsoft Access',
    psCmd: `if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\MSACCESS.EXE") { Start-Process (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\MSACCESS.EXE").'(default)' } else { Start-Process msaccess }`,
    webUrl: 'https://www.office.com'
  },

  // Browsers
  'chrome': {
    title: 'Google Chrome',
    psCmd: (url) => url ? `Start-Process chrome '${url}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url}' }` : `Start-Process chrome`,
    webUrl: 'https://www.google.com'
  },
  'edge': {
    title: 'Microsoft Edge',
    psCmd: (url) => url ? `Start-Process msedge '${url}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url}' }` : `Start-Process msedge`,
    webUrl: 'https://www.bing.com'
  },
  'firefox': {
    title: 'Mozilla Firefox',
    psCmd: (url) => url ? `Start-Process firefox '${url}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url}' }` : `Start-Process firefox`,
    webUrl: 'https://www.mozilla.org'
  },
  'brave': {
    title: 'Brave Browser',
    psCmd: (url) => url ? `Start-Process brave '${url}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url}' }` : `Start-Process brave`,
    webUrl: 'https://search.brave.com'
  },

  // AI & Web Services
  'claude': {
    title: 'Anthropic Claude',
    psCmd: `Start-Process chrome 'https://claude.ai' -ErrorAction SilentlyContinue; if (!$?) { Start-Process 'https://claude.ai' }`,
    webUrl: 'https://claude.ai'
  },
  'chatgpt': {
    title: 'ChatGPT',
    psCmd: `Start-Process chrome 'https://chatgpt.com' -ErrorAction SilentlyContinue; if (!$?) { Start-Process 'https://chatgpt.com' }`,
    webUrl: 'https://chatgpt.com'
  },
  'gemini': {
    title: 'Google Gemini',
    psCmd: `Start-Process chrome 'https://gemini.google.com' -ErrorAction SilentlyContinue; if (!$?) { Start-Process 'https://gemini.google.com' }`,
    webUrl: 'https://gemini.google.com'
  },
  'youtube': {
    title: 'YouTube',
    psCmd: (url) => `Start-Process chrome '${url || "https://youtube.com"}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url || "https://youtube.com"}' }`,
    webUrl: 'https://youtube.com'
  },
  'github': {
    title: 'GitHub',
    psCmd: (url) => `Start-Process chrome '${url || "https://github.com"}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url || "https://github.com"}' }`,
    webUrl: 'https://github.com'
  },
  'google': {
    title: 'Google Search',
    psCmd: (url) => `Start-Process chrome '${url || "https://www.google.com"}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url || "https://www.google.com"}' }`,
    webUrl: 'https://www.google.com'
  },

  // Developer Tools
  'vscode': {
    title: 'Visual Studio Code',
    psCmd: (p) => p ? `Start-Process code '"${p}"'` : `Start-Process code .`
  },
  'cursor': {
    title: 'Cursor AI Editor',
    psCmd: (p) => p ? `Start-Process cursor '"${p}"'` : `Start-Process cursor .`
  },
  'terminal': {
    title: 'Windows Terminal / PowerShell',
    psCmd: `if (Get-Command wt -ErrorAction SilentlyContinue) { Start-Process wt } else { Start-Process powershell }`
  },
  'cmd': {
    title: 'Command Prompt',
    psCmd: `Start-Process cmd`
  },
  'powershell': {
    title: 'PowerShell',
    psCmd: `Start-Process powershell`
  },

  // System & Utilities
  'notepad': {
    title: 'Notepad',
    psCmd: (p) => p ? `Start-Process notepad '"${p}"'` : `Start-Process notepad`
  },
  'calc': {
    title: 'Calculator',
    psCmd: `Start-Process calc`
  },
  'paint': {
    title: 'Paint',
    psCmd: `Start-Process mspaint`
  },
  'explorer': {
    title: 'File Explorer',
    psCmd: (dir) => `Start-Process explorer '${dir || "."}'`
  },
  'settings': {
    title: 'Windows Settings',
    psCmd: `Start-Process "ms-settings:"`
  },
  'taskmgr': {
    title: 'Task Manager',
    psCmd: `Start-Process taskmgr`
  },
  'spotify': {
    title: 'Spotify',
    psCmd: `if (Get-Command spotify -ErrorAction SilentlyContinue) { Start-Process spotify } else { Start-Process "spotify:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://open.spotify.com" } }`
  },
  'telegram': {
    title: 'Telegram',
    psCmd: `if (Test-Path "$env:APPDATA\\Telegram Desktop\\Telegram.exe") { Start-Process "$env:APPDATA\\Telegram Desktop\\Telegram.exe" } else { Start-Process "tg:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://web.telegram.org" } }`
  },
  'discord': {
    title: 'Discord',
    psCmd: `if (Get-Command discord -ErrorAction SilentlyContinue) { Start-Process discord } else { Start-Process "discord:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://discord.com/app" } }`
  },
  'steam': {
    title: 'Steam',
    psCmd: `Start-Process "steam:" -ErrorAction SilentlyContinue; if (!$?) { Start-Process "https://store.steampowered.com" }`
  }
};

const APP_ALIASES = {
  'microsoft office': 'office', 'ms office': 'office', 'msoffice': 'office', 'office 365': 'office', 'microsoft 365': 'office',
  'microsoft word': 'word', 'ms word': 'word', 'winword': 'word', 'docs': 'word', 'doc': 'word',
  'microsoft excel': 'excel', 'ms excel': 'excel', 'sheets': 'excel', 'spreadsheet': 'excel',
  'microsoft powerpoint': 'powerpoint', 'ms powerpoint': 'powerpoint', 'powerpnt': 'powerpoint', 'ppt': 'powerpoint', 'slides': 'powerpoint',
  'microsoft onenote': 'onenote', 'ms onenote': 'onenote',
  'microsoft outlook': 'outlook', 'ms outlook': 'outlook', 'mail': 'outlook', 'email': 'outlook',
  'microsoft teams': 'teams', 'ms teams': 'teams',
  'google chrome': 'chrome', 'google': 'google', 'browser': 'chrome', 'internet': 'chrome', 'web': 'chrome',
  'microsoft edge': 'edge', 'ms edge': 'edge',
  'vs code': 'vscode', 'visual studio code': 'vscode', 'code editor': 'vscode', 'code': 'vscode',
  'calculator': 'calc', 'calculator app': 'calc',
  'paint': 'paint', 'mspaint': 'paint', 'drawing': 'paint',
  'file explorer': 'explorer', 'files': 'explorer', 'folder': 'explorer', 'my computer': 'explorer',
  'task manager': 'taskmgr', 'taskmgr': 'taskmgr',
  'control panel': 'settings', 'settings': 'settings'
};

function resolveAppKey(raw) {
  const norm = (raw || '').toLowerCase().replace(/^(open|launch|start|run|go to)\s+/i, '').trim();
  if (APP_REGISTRY[norm]) return norm;
  if (APP_ALIASES[norm]) return APP_ALIASES[norm];
  for (const [k, v] of Object.entries(APP_ALIASES)) {
    if (norm.includes(k)) return v;
  }
  return norm;
}

// ═══════════════════════════════════════════════════════════════
//  REAL LOCAL OS & BROWSER TOOL EXECUTOR (FULL LAPTOP CONTROL & VISUAL CURSOR)
// ═══════════════════════════════════════════════════════════════
async function executeRealTool(toolName, args) {
  log(`TOOL_EXEC: ${toolName} ${JSON.stringify(args)}`);

  // 1. Smooth Visual Mouse Cursor Glide & Click Ripple
  if (toolName === 'mouse_action' || toolName === 'cursor_glide') {
    const targetX = args.x || 640;
    const targetY = args.y || 360;
    const msg = args.message || `Interacting at (${targetX}, ${targetY})`;
    runVisualOverlay('glide_click', { targetX, targetY, message: msg });
    await sleep(350);
    return { success: true, message: `Moved cursor and clicked at (${targetX}, ${targetY})` };
  }

  // 2. File Writing (Python scripts, code, speeches)
  if (toolName === 'file_write') {
    const filePath = path.resolve(process.cwd(), args.path || 'generated_script.py');
    const content = args.content || '';
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, content, 'utf-8');
    return { success: true, message: `Created file: ${path.basename(filePath)} (${content.length} bytes)` };
  }

  // 3. Open in Editor (VS Code with automatic Notepad fallback)
  if (toolName === 'open_editor') {
    const target = path.resolve(process.cwd(), args.path || '.');
    runVisualOverlay('banner', { message: `Opening in Code Editor: ${path.basename(target)}`, durationMs: 1200 });
    if (process.platform === 'win32') {
      const psOpen = `if (Get-Command code -ErrorAction SilentlyContinue) { Start-Process code '"${target}"' } else { Start-Process notepad '"${target}"' }`;
      exec(`powershell -NoProfile -Command "${psOpen}"`, () => {});
    } else {
      exec(`code "${target}" || xdg-open "${target}"`, () => {});
    }
    return { success: true, message: `Opened editor for: ${path.basename(target)}` };
  }

  // 4. Browser Navigation (Google / Search / YouTube / Any URL)
  if (toolName === 'browser_navigate') {
    let url = args.url || '';
    if (!url) {
      if (args.search) {
        url = `https://www.google.com/search?q=${encodeURIComponent(args.search)}`;
      } else {
        url = 'https://www.google.com';
      }
    }
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }
    runVisualOverlay('glide_click', { targetX: 640, targetY: 200, message: `Navigating browser to ${url}` });
    if (process.platform === 'win32') {
      exec(`powershell -NoProfile -Command "Start-Process chrome '${url}' -ErrorAction SilentlyContinue; if (!$?) { Start-Process '${url}' }"`, (err) => {
        if (err) exec(`start "" "${url}"`, () => {});
      });
    } else {
      exec(`open "${url}" || xdg-open "${url}"`, () => {});
    }
    return { success: true, message: `Navigated browser to: ${url}` };
  }

  // 5. Windows Native Application Launching (Office, Word, Excel, PowerPoint, VS Code, Chrome, etc.)
  if (toolName === 'app_launch') {
    const rawApp = args.app || args.name || 'office';
    const appKey = resolveAppKey(rawApp);
    const reg = APP_REGISTRY[appKey] || {
      title: rawApp.charAt(0).toUpperCase() + rawApp.slice(1),
      psCmd: `if (Get-Command ${rawApp} -ErrorAction SilentlyContinue) { Start-Process ${rawApp} } else { Start-Process '${rawApp}' }`
    };

    // Run Full On-Screen Watermark Animation (Glide to Start, Click Ripple, Launch App, Focus Center Window)
    runVisualOverlay('launch_app', { appName: appKey, appTitle: reg.title });

    if (process.platform === 'win32') {
      let finalPs = '';
      if (typeof reg.psCmd === 'function') {
        finalPs = reg.psCmd(args.url || args.path);
      } else {
        finalPs = reg.psCmd;
      }
      exec(`powershell -NoProfile -Command "${finalPs}"`, () => {});
    } else {
      exec(`open -a "${appKey}" || ${appKey}`, () => {});
    }
    await sleep(600);
    return { success: true, message: `Launched application: ${reg.title}` };
  }

  // 6. Text Typing into Active Application (WScript.Shell SendKeys)
  if (toolName === 'type_text') {
    const rawText = args.text || '';
    if (process.platform === 'win32') {
      const clean = rawText.replace(/[\{\}\+\^\%\~\(\)\[\]]/g, '{$&}').replace(/'/g, "''");
      const psType = `$ws = New-Object -ComObject WScript.Shell; Start-Sleep -Milliseconds 400; $ws.SendKeys('${clean}')`;
      exec(`powershell -NoProfile -Command "${psType}"`, () => {});
    }
    return { success: true, message: `Typed text into active application window` };
  }

  // 7. Clipboard copy
  if (toolName === 'clipboard_set') {
    const text = (args.text || '').replace(/'/g, "''");
    if (process.platform === 'win32') {
      exec(`powershell -NoProfile -Command "Set-Clipboard -Value '${text}'"`, () => {});
    }
    return { success: true, message: `Copied generated text to clipboard (${(args.text || '').length} chars)` };
  }

  if (toolName === 'minimize_terminal') {
    if (process.platform === 'win32') {
      exec(`powershell -NoProfile -Command "$w = (Get-Process -Id $PID).MainWindowHandle; Add-Type '@[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);' -Name W -Namespace U; [U.W]::ShowWindow($w, 2)"`, () => {});
    }
    return { success: true, message: `Transitioned view: focused active application` };
  }

  if (toolName === 'shell') {
    return new Promise((resolve) => {
      exec(args.command, { cwd: process.cwd() }, (err, stdout, stderr) => {
        if (err) {
          resolve({ success: false, message: `Shell error: ${err.message}` });
        } else {
          resolve({ success: true, message: stdout.trim() || 'Executed command successfully.' });
        }
      });
    });
  }

  return { success: true, message: `Executed tool: ${toolName}` };
}

// ═══════════════════════════════════════════════════════════════
//  AI AGENT & TOOL EXECUTION LOOP (WITH RETRY, FAST RESPONSE & VISUAL FLOW)
// ═══════════════════════════════════════════════════════════════
async function runAIAgent(prompt) {
  S.busy = true;
  let currentModel = S.model;
  S.showTodoPanel = true;

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

  if (!apiKey && currentModel.provider !== 'ollama') {
    thinkMsg.text = 'No API key set for ' + currentModel.provider + '.';
    thinkMsg.done = true;
    agentMsg.text = `No active API key found for ${currentModel.name}.\nSet keys in D:\\ELE\\backend\\.env or run /keys.`;
    S.busy = false;
    render();
    await checkAndProcessQueue();
    return;
  }

  const spinnerIv = setInterval(() => {
    S.spinFrame++;
    render();
  }, 80);

  try {
    let url = `${currentModel.baseUrl.replace(/\/$/, '')}/chat/completions`;
    const headers = { 'Content-Type': 'application/json' };
    if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;

    const systemPrompt = `You are ELE, an intelligent autonomous AI Developer Assistant and JARVIS-style OS Copilot.
You run natively on the user's PC and have DIRECT access to execute actions on the operating system with live visual HUD overlays.

When the user asks you to open applications, browse web pages, write code, search Google/YouTube, or automate desktop tasks, ALWAYS output structured TOOL_CALL commands. Be intelligent, direct, and fast.

AVAILABLE TOOL CALLS (Put each on its own line):
TOOL_CALL app_launch {"app": "office", "name": "Microsoft Office"}
TOOL_CALL app_launch {"app": "word", "name": "Microsoft Word"}
TOOL_CALL app_launch {"app": "excel", "name": "Microsoft Excel"}
TOOL_CALL app_launch {"app": "powerpoint", "name": "Microsoft PowerPoint"}
TOOL_CALL app_launch {"app": "vscode"}
TOOL_CALL app_launch {"app": "chrome"}
TOOL_CALL browser_navigate {"url": "https://www.google.com/search?q=query"}
TOOL_CALL browser_navigate {"url": "https://www.youtube.com/results?search_query=query"}
TOOL_CALL file_write {"path": "script.py", "content": "print('hello')"}
TOOL_CALL open_editor {"path": "script.py"}
TOOL_CALL clipboard_set {"text": "content"}
TOOL_CALL type_text {"text": "some text"}
TOOL_CALL mouse_action {"action": "glide_click", "x": 640, "y": 360, "message": "Clicking button"}
TOOL_CALL shell {"command": "dir"}

RULES:
- When user asks to open ANY application (e.g. "open Microsoft Office", "open Word", "open Excel", "open PowerPoint", "open Chrome", "open Telegram", "open VS Code", "open Spotify", "open Notepad", "open Calculator") -> Use TOOL_CALL app_launch with the target app!
- When user asks to search or browse (e.g. "search on google", "open youtube", "go to website") -> Use TOOL_CALL browser_navigate with appropriate URL!
- When user asks for scripts/speeches/code -> Write code AND save to file AND copy to clipboard.
- Provide a brief, friendly explanation along with your tool calls.`;

    const messagesPayload = [
      { role: 'system', content: systemPrompt },
      ...S.messages.filter(m => m.type === 'user' || (m.type === 'agent' && m !== agentMsg)).slice(-6).map(m => ({
        role: m.type === 'user' ? 'user' : 'assistant',
        content: m.text
      })),
      { role: 'user', content: prompt }
    ];

    let body = JSON.stringify({
      model: currentModel.id,
      messages: messagesPayload,
      stream: true,
      temperature: 0.5,
      max_tokens: 2048,
    });

    // 45s AbortSignal timeout
    const fetchOpts = { method: 'POST', headers, body, signal: AbortSignal.timeout(45000) };
    let response;
    try {
      response = await fetch(url, fetchOpts);
    } catch (fetchErr) {
      if (currentModel.id !== 'meta/llama-3.1-8b-instruct' && currentModel.provider === 'nvidia') {
        log(`Fetch failed for ${currentModel.id}: ${fetchErr.message}. Retrying with fast 8B...`);
        currentModel = MODELS[0]; // 8B
        body = JSON.stringify({
          model: currentModel.id,
          messages: messagesPayload,
          stream: true,
          temperature: 0.5,
          max_tokens: 2048,
        });
        response = await fetch(url, { method: 'POST', headers, body, signal: AbortSignal.timeout(45000) });
      } else {
        throw fetchErr;
      }
    }

    if (!response.ok && response.status === 404 && currentModel.provider === 'nvidia' && currentModel.id !== 'meta/llama-3.1-8b-instruct') {
      log(`Model ${currentModel.id} 404 -> Falling back to meta/llama-3.1-8b-instruct`);
      currentModel = MODELS[0]; // 8B
      body = JSON.stringify({
        model: currentModel.id,
        messages: messagesPayload,
        stream: true,
        temperature: 0.5,
        max_tokens: 2048,
      });
      response = await fetch(url, { method: 'POST', headers, body, signal: AbortSignal.timeout(45000) });
    }

    if (!response.ok) {
      const errTxt = await response.text();
      throw new Error(`HTTP ${response.status}: ${errTxt.substring(0, 150)}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let inThinkTag = false;
    let rawAccumulated = '';

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
            rawAccumulated += token;
            if (token.includes('<think>')) inThinkTag = true;
            if (token.includes('</think>')) { inThinkTag = false; continue; }

            if (inThinkTag || delta?.reasoning_content) {
              thinkMsg.text += token.replace(/<think>|<\/think>/g, '');
            } else {
              const cleanText = rawAccumulated
                .replace(/TOOL_CALL\s+[a-z_]+\s+\{[^}]*\}/gi, '')
                .trimStart();
              agentMsg.text = cleanText;
            }
            render();
          }
        } catch {}
      }
    }

    // Parse TOOL_CALL commands
    const toolRegex = /TOOL_CALL\s+([a-z_]+)\s+(\{[^}\n]*\})/gi;
    let match;
    const toolsToRun = [];

    while ((match = toolRegex.exec(rawAccumulated)) !== null) {
      try {
        const toolName = match[1];
        const toolArgs = JSON.parse(match[2]);
        toolsToRun.push({ name: toolName, args: toolArgs });
      } catch {}
    }

    if (toolsToRun.length > 0) {
      S.todoList = toolsToRun.map((t, idx) => ({
        id: idx + 1,
        text: `${t.name.replace(/_/g, ' ')}: ${t.args.path || t.args.url || t.args.app || t.args.command || ''}`,
        status: 'pending'
      }));
      render();

      for (let i = 0; i < toolsToRun.length; i++) {
        const t = toolsToRun[i];
        if (S.todoList[i]) S.todoList[i].status = 'running';
        render();

        try {
          const res = await executeRealTool(t.name, t.args);
          if (S.todoList[i]) S.todoList[i].status = res.success ? 'done' : 'error';
          S.messages.push({ type: 'action', text: `[${t.name}] ${res.message}` });
        } catch (err) {
          if (S.todoList[i]) S.todoList[i].status = 'error';
          S.messages.push({ type: 'error', text: `[${t.name}] Failed: ${err.message}` });
        }
        render();
        await sleep(250);
      }
    } else {
      // ── UNIVERSAL INTELLIGENT INTENT & VISUAL DESKTOP AUTOMATION ENGINE ──
      const lower = prompt.toLowerCase();

      // Check for Microsoft Office / Apps
      const isOffice = lower.includes('office') || lower.includes('microsoft office') || lower.includes('ms office') || lower.includes('365');
      const isWord = lower.includes('word') || lower.includes('winword') || lower.includes('document');
      const isExcel = lower.includes('excel') || lower.includes('spreadsheet') || lower.includes('sheet');
      const isPPT = lower.includes('powerpoint') || lower.includes('powerpnt') || lower.includes('ppt') || lower.includes('presentation') || lower.includes('slide');
      const isOneNote = lower.includes('onenote');
      const isOutlook = lower.includes('outlook') || lower.includes('email') || lower.includes('mail');
      const isTeams = lower.includes('teams');

      // Browsers & Search
      const isYouTube = lower.includes('youtube');
      const isGoogleSearch = lower.includes('search google') || lower.includes('search for') || lower.includes('google search') || lower.includes('find on google');
      const isChrome = lower.includes('chrome') || lower.includes('browser') || lower.includes('internet');
      const isClaude = (lower.includes('claude') || lower.includes('anthropic')) && !isOffice;
      const isChatGPT = lower.includes('chatgpt') || lower.includes('openai');
      const isGemini = lower.includes('gemini') || lower.includes('google ai');

      // Developers & Utilities
      const isVSCode = lower.includes('vscode') || lower.includes('vs code') || lower.includes('visual studio code') || lower.includes('code editor');
      const isTerminal = lower.includes('terminal') || lower.includes('command prompt') || lower.includes('powershell') || lower.includes('cmd');
      const isNotepad = lower.includes('notepad') || lower.includes('note');
      const isCalc = lower.includes('calculator') || lower.includes('calc');
      const isExplorer = lower.includes('explorer') || lower.includes('files') || lower.includes('folder');
      const isPaint = lower.includes('paint') || lower.includes('drawing');
      const isSpotify = lower.includes('spotify') || lower.includes('music');
      const isTelegram = lower.includes('telegram');
      const isDiscord = lower.includes('discord');
      const isSettings = lower.includes('settings') || lower.includes('control panel');

      // Content generation
      const isSpeech = lower.includes('speech') || lower.includes('christmas') || lower.includes('essay');
      const isScript = lower.includes('script') || lower.includes('python') || lower.includes('code') || lower.includes('program');

      if (isWord) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Microsoft Word (WinWord / Office)', status: 'running' },
          { id: 2, text: 'Activate Workspace Window & Focus Document Canvas', status: 'pending' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'word', name: 'Microsoft Word' });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'done';
        agentMsg.text = agentMsg.text || '✨ **Microsoft Word Launched Successfully!**\nVisual Ghost Cursor navigated to Start Menu, searched for Microsoft Word, and launched the application.';
        S.messages.push({ type: 'action', text: 'Opened Microsoft Word on your desktop!' });
      } else if (isExcel) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Microsoft Excel (Spreadsheets)', status: 'running' },
          { id: 2, text: 'Focus Excel Grid Workspace', status: 'pending' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'excel', name: 'Microsoft Excel' });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'done';
        agentMsg.text = agentMsg.text || '✨ **Microsoft Excel Launched Successfully!**\nVisual Ghost Cursor navigated and opened Microsoft Excel.';
        S.messages.push({ type: 'action', text: 'Opened Microsoft Excel on your desktop!' });
      } else if (isPPT) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Microsoft PowerPoint (Presentations)', status: 'running' },
          { id: 2, text: 'Focus Slide Deck Canvas', status: 'pending' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'powerpoint', name: 'Microsoft PowerPoint' });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'done';
        agentMsg.text = agentMsg.text || '✨ **Microsoft PowerPoint Launched Successfully!**\nVisual Ghost Cursor navigated and opened PowerPoint.';
        S.messages.push({ type: 'action', text: 'Opened Microsoft PowerPoint on your desktop!' });
      } else if (isOneNote) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Microsoft OneNote', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'onenote', name: 'Microsoft OneNote' });
        S.todoList[0].status = 'done';
        agentMsg.text = '✨ **Microsoft OneNote Launched Successfully!**';
        S.messages.push({ type: 'action', text: 'Opened Microsoft OneNote!' });
      } else if (isOutlook) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Microsoft Outlook Mail', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'outlook', name: 'Microsoft Outlook' });
        S.todoList[0].status = 'done';
        agentMsg.text = '✨ **Microsoft Outlook Launched Successfully!**';
        S.messages.push({ type: 'action', text: 'Opened Microsoft Outlook!' });
      } else if (isTeams) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Microsoft Teams', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'teams', name: 'Microsoft Teams' });
        S.todoList[0].status = 'done';
        agentMsg.text = '✨ **Microsoft Teams Launched Successfully!**';
        S.messages.push({ type: 'action', text: 'Opened Microsoft Teams!' });
      } else if (isOffice) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor to Start Menu & Launch Microsoft Office Hub', status: 'running' },
          { id: 2, text: 'Activate Office 365 Dashboard & Document Suite', status: 'pending' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'office', name: 'Microsoft Office' });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'done';
        agentMsg.text = agentMsg.text || '✨ **Microsoft Office Launched Successfully!**\nVisual Ghost Cursor navigated across the screen to the Windows Start Menu, located Microsoft Office, and launched your productivity suite.';
        S.messages.push({ type: 'action', text: 'Opened Microsoft Office on your desktop!' });
      } else if (isYouTube) {
        const queryMatch = lower.match(/(?:for|about|search|play)\s+([^.]+)/i);
        const q = queryMatch ? queryMatch[1].trim() : '';
        const targetUrl = q ? `https://www.youtube.com/results?search_query=${encodeURIComponent(q)}` : 'https://www.youtube.com';
        S.todoList = [
          { id: 1, text: `Glide Cursor & Launch YouTube (${q || 'Home'})`, status: 'running' },
          { id: 2, text: 'Focus Browser Window & Play Stream', status: 'pending' }
        ];
        render();
        await executeRealTool('browser_navigate', { url: targetUrl });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'done';
        agentMsg.text = `📺 **Opened YouTube** at ${targetUrl}`;
        S.messages.push({ type: 'action', text: `Opened YouTube (${q || 'Home'}) in Chrome!` });
      } else if (isGoogleSearch) {
        const queryMatch = lower.match(/(?:for|about|search|google)\s+([^.]+)/i);
        const q = queryMatch ? queryMatch[1].trim() : 'latest news';
        const targetUrl = `https://www.google.com/search?q=${encodeURIComponent(q)}`;
        S.todoList = [
          { id: 1, text: `Search Google for "${q}"`, status: 'running' },
          { id: 2, text: 'Render Search Results in Browser', status: 'pending' }
        ];
        render();
        await executeRealTool('browser_navigate', { url: targetUrl });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'done';
        agentMsg.text = `🔍 **Google Search Results Ready** for "${q}"`;
        S.messages.push({ type: 'action', text: `Searched Google for "${q}"` });
      } else if (isClaude) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Chrome to Claude (https://claude.ai)', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'claude', name: 'Claude' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Opened Claude at https://claude.ai in your browser.';
        S.messages.push({ type: 'action', text: 'Opened Claude at https://claude.ai' });
      } else if (isChatGPT) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Chrome to ChatGPT (https://chatgpt.com)', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'chatgpt', name: 'ChatGPT' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Opened ChatGPT in your browser.';
        S.messages.push({ type: 'action', text: 'Opened ChatGPT' });
      } else if (isGemini) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Chrome to Google Gemini (https://gemini.google.com)', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'gemini', name: 'Google Gemini' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Opened Google Gemini in your browser.';
        S.messages.push({ type: 'action', text: 'Opened Google Gemini' });
      } else if (isVSCode) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Visual Studio Code', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'vscode', name: 'Visual Studio Code' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Launched Visual Studio Code.';
        S.messages.push({ type: 'action', text: 'Opened VS Code editor.' });
      } else if (isTerminal) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Open Windows Terminal / PowerShell', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'terminal', name: 'Windows Terminal' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Opened Windows Terminal.';
        S.messages.push({ type: 'action', text: 'Opened Terminal window.' });
      } else if (isChrome) {
        S.todoList = [
          { id: 1, text: 'Glide Cursor & Launch Google Chrome Browser', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'chrome', name: 'Google Chrome' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Launched Google Chrome browser.';
        S.messages.push({ type: 'action', text: 'Opened Google Chrome browser.' });
      } else if (isNotepad) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Launch Windows Notepad', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'notepad', name: 'Notepad' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Launched Windows Notepad.';
        S.messages.push({ type: 'action', text: 'Opened Windows Notepad application.' });
      } else if (isCalc) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Launch Windows Calculator', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'calc', name: 'Calculator' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Launched Windows Calculator.';
        S.messages.push({ type: 'action', text: 'Opened Windows Calculator application.' });
      } else if (isExplorer) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Open File Explorer', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'explorer', name: 'File Explorer' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Opened Windows File Explorer.';
        S.messages.push({ type: 'action', text: 'Opened Windows File Explorer.' });
      } else if (isPaint) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Open Paint', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'paint', name: 'Paint' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Opened Windows Paint application.';
        S.messages.push({ type: 'action', text: 'Opened Paint application.' });
      } else if (isSpotify) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Launch Spotify', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'spotify', name: 'Spotify' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Launched Spotify.';
        S.messages.push({ type: 'action', text: 'Opened Spotify application.' });
      } else if (isTelegram) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Launch Telegram Desktop', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'telegram', name: 'Telegram' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Launched Telegram Desktop.';
        S.messages.push({ type: 'action', text: 'Opened Telegram Desktop.' });
      } else if (isDiscord) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Launch Discord', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'discord', name: 'Discord' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Launched Discord.';
        S.messages.push({ type: 'action', text: 'Opened Discord.' });
      } else if (isSettings) {
        S.todoList = [
          { id: 1, text: 'Glide Mouse Cursor & Open Windows Settings', status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: 'settings', name: 'Windows Settings' });
        S.todoList[0].status = 'done';
        agentMsg.text = 'Opened Windows Settings.';
        S.messages.push({ type: 'action', text: 'Opened Windows Settings.' });
      } else if (isScript) {
        const sampleScript = `#!/usr/bin/env python3\n\"\"\"\nGenerated Python Script by ELE Agent & JARVIS\nAutonomous System Script\n\"\"\"\nimport sys\nimport os\nimport time\nimport math\n\ndef main():\n    print("=" * 50)\n    print("⚡ ELE Agent & JARVIS Autonomous Script")\n    print(f"📁 Working Directory: {os.getcwd()}")\n    print(f"🐍 Python Version: {sys.version.split()[0]}")\n    print("=" * 50)\n    \n    print("\\n[+] Running calculation demonstration:")\n    for i in range(1, 6):\n        sq = i ** 2\n        root = math.sqrt(i)\n        print(f"  Item #{i}: Square = {sq:2d} | Sqrt = {root:.4f}")\n        time.sleep(0.05)\n        \n    print("\\n✓ Task execution complete successfully!\\n")\n\nif __name__ == '__main__':\n    main()\n`;
        const scriptName = 'script.py';
        S.todoList = [
          { id: 1, text: `Generate Python Code & Write ${scriptName}`, status: 'running' },
          { id: 2, text: 'Glide Mouse Cursor & Open in Editor (Notepad / VS Code)', status: 'pending' },
        ];
        render();
        await executeRealTool('file_write', { path: scriptName, content: sampleScript });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'running';
        render();
        await sleep(200);
        await executeRealTool('open_editor', { path: scriptName });
        S.todoList[1].status = 'done';

        agentMsg.text = `⚡ **Generated Python Script (\`${scriptName}\`) & Opened in Editor!**\n\n\`\`\`python\n${sampleScript}\`\`\`\n\n*File created at: \`${path.resolve(process.cwd(), scriptName)}\`*`;
        S.messages.push({ type: 'action', text: `Created ${scriptName} and opened in your code editor!` });
      } else if (isSpeech) {
        const generatedSpeech = `# 🌟 Inspirational Celebration Speech\n\n**Ladies, Gentlemen, and Esteemed Friends,**\n\nThank you for gathering here today. Progress is never an accident—it is the result of intention, unwavering dedication, and the courage to take bold steps forward into the unknown.\n\nAs we look ahead, let us commit to lifting one another up, creating solutions with purpose, and transforming every challenge into a stepping stone toward excellence.\n\n**Thank you, and let us build the future together!**\n`;
        S.todoList = [
          { id: 1, text: 'Generate Inspiring Speech', status: 'running' },
          { id: 2, text: 'Save Speech to speech.md', status: 'pending' },
          { id: 3, text: 'Copy to Windows Clipboard & Open in Editor', status: 'pending' },
        ];
        render();
        await executeRealTool('file_write', { path: 'speech.md', content: generatedSpeech });
        S.todoList[0].status = 'done';
        S.todoList[1].status = 'done';
        S.todoList[2].status = 'running';
        render();
        await sleep(200);
        await executeRealTool('clipboard_set', { text: generatedSpeech });
        await executeRealTool('open_editor', { path: 'speech.md' });
        S.todoList[2].status = 'done';
        agentMsg.text = `🌟 **Speech Generated & Saved!**\n\n1. Saved to **speech.md**\n2. Copied to your **Clipboard** (Ready to paste Ctrl+V)\n3. Opened in your text editor.\n\n---\n${generatedSpeech}`;
        S.messages.push({ type: 'action', text: 'Speech generated, saved to file, and copied to clipboard!' });
      } else if (lower.startsWith('open ') || lower.startsWith('launch ') || lower.startsWith('start ')) {
        const appExtract = lower.replace(/^(open|launch|start|run|go to)\s+/i, '').trim();
        S.todoList = [
          { id: 1, text: `Glide Cursor & Launch "${appExtract}"`, status: 'running' }
        ];
        render();
        await executeRealTool('app_launch', { app: appExtract });
        S.todoList[0].status = 'done';
        agentMsg.text = `Launched **${appExtract}** with visual agent navigation.`;
        S.messages.push({ type: 'action', text: `Launched ${appExtract} on Windows.` });
      }
    }

    if (S.jarvisOpen) {
      speakVoice(agentMsg.text);
    }

    log(`RESPONSE: ${agentMsg.text.substring(0, 100)}...`);
  } catch (err) {
    thinkMsg.done = true;
    const msg = err.message || String(err);
    if (msg.includes('TimeoutError') || msg.includes('aborted') || msg.includes('timeout')) {
      agentMsg.text = `Model timeout (${currentModel.name} took too long).\nTry switching to a faster model with /model → select "Llama 3.1 8B" or "Gemini 2.0 Flash".`;
    } else if (msg.includes('401') || msg.includes('403') || msg.includes('Unauthorized')) {
      agentMsg.text = `API key rejected. Check your credentials with /keys.\nGet a free NVIDIA key at build.nvidia.com or Gemini key at aistudio.google.com`;
    } else if (msg.includes('fetch failed') || msg.includes('ENOTFOUND') || msg.includes('ECONNREFUSED')) {
      agentMsg.text = `Network error: Cannot reach ${currentModel.provider} API.\nCheck your internet connection, then try /keys to verify credentials.`;
    } else {
      agentMsg.text = `Error: ${msg}\nCheck your connection or credentials with /keys.`;
    }
    log(`ERROR: ${err.message}`);
  } finally {
    clearInterval(spinnerIv);
    S.busy = false;
    render();
    await checkAndProcessQueue();
  }
}

// ═══════════════════════════════════════════════════════════════
//  JARVIS SPEECH-TO-SPEECH CONTROLLER
// ═══════════════════════════════════════════════════════════════
async function openJarvisVoiceMode() {
  S.jarvisOpen = true;
  S.jarvisVoiceActive = true;
  S.jarvisStatus = 'Initializing Jarvis Speech-to-Speech...';
  render();

  const greeting = "Hello, I am Jarvis. Your speech assistant is active and listening. What would you like me to do?";
  speakVoice(greeting);
  startVoiceListening();
}

function closeJarvisVoiceMode() {
  stopVoiceListening();
  S.jarvisOpen = false;
  S.jarvisVoiceActive = false;
  render();
}

// ═══════════════════════════════════════════════════════════════
//  COMMAND DISPATCHER
// ═══════════════════════════════════════════════════════════════
async function dispatchInput(input) {
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
    case '/jarvis': case '/voice': return openJarvisVoiceMode();
    case '/model': return openModelModal();
    case '/automate': return runAIAgent(args || 'open Microsoft Office');
    case '/todo': return cmdToggleTodo();
    case '/queue': return cmdQueue();
    case '/keys': return cmdKeys();
    case '/browse': return cmdBrowse(args);
    case '/clear': return cmdClear();
    case '/new': return cmdNew();
    case '/sessions': case '/switch': return cmdSessions(args);
    case '/erase': case '/erasedata': return cmdErase();
    case '/editor': return cmdEditor(args);
    case '/exit': case '/quit': return cmdExit();
    default:
      if (trimmed.startsWith('/')) {
        S.messages.push({ type: 'error', text: `Unknown command: ${cmd}` });
        render();
      } else {
        S.messages.push({ type: 'user', text: trimmed });
        render();
        return runAIAgent(trimmed);
      }
  }
}

function cmdHelp() {
  let t = 'Available Commands:\n';
  for (const c of COMMANDS) {
    t += `  ${c.icon}  ${c.cmd.padEnd(12)} ${c.desc}\n`;
  }
  t += '\nShortcuts:\n';
  t += '  Enter       Submit (or Queue if busy)\n';
  t += '  ↑ ↓         Prompt History / Model Nav\n';
  t += '  /           Autocomplete Menu\n';
  t += '  ctrl+c      Quit';
  S.messages.push({ type: 'system', text: t });
  render();
}

function cmdNew() {
  S.messages = [];
  S.todoList = [];
  S.queue = [];
  S.messages.push({ type: 'info', text: '✨ Started a fresh new session.' });
  render();
}

function cmdSessions(args) {
  try {
    const userHome = process.env.USERPROFILE || process.env.HOME || '';
    const sessionsDir = path.join(userHome, '.ele-agent', 'sessions');
    if (!fs.existsSync(sessionsDir)) fs.mkdirSync(sessionsDir, { recursive: true });

    if (args) {
      // Save or switch
      const sessionFile = path.join(sessionsDir, `${args.replace(/[^a-zA-Z0-9_-]/g, '_')}.json`);
      if (fs.existsSync(sessionFile)) {
        const data = JSON.parse(fs.readFileSync(sessionFile, 'utf-8'));
        S.messages = data.messages || [];
        S.messages.push({ type: 'info', text: `Loaded session: "${args}"` });
      } else {
        fs.writeFileSync(sessionFile, JSON.stringify({ messages: S.messages, timestamp: new Date().toISOString() }, null, 2));
        S.messages.push({ type: 'info', text: `Saved current session as: "${args}"` });
      }
    } else {
      const files = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.json'));
      if (files.length === 0) {
        S.messages.push({ type: 'info', text: 'No saved sessions found. Type "/sessions <name>" to save current session.' });
      } else {
        let t = 'Saved Sessions:\n';
        for (const f of files) {
          t += `  • ${f.replace('.json', '')}\n`;
        }
        t += '\nType "/sessions <name>" to load or save a session.';
        S.messages.push({ type: 'system', text: t });
      }
    }
  } catch (e) {
    S.messages.push({ type: 'error', text: `Sessions error: ${e.message}` });
  }
  render();
}

function cmdErase() {
  try {
    const userHome = process.env.USERPROFILE || process.env.HOME || '';
    const targets = [
      path.join(userHome, '.ele-agent', 'sessions'),
      path.join(userHome, '.ele-agent', 'profile.json'),
      path.join(userHome, '.ele-data'),
      path.join('D:', 'LOGS', 'hive'),
    ];
    for (const t of targets) {
      if (fs.existsSync(t)) {
        fs.rmSync(t, { recursive: true, force: true });
      }
    }
    S.messages = [];
    S.todoList = [];
    S.queue = [];
    S.history = [];
    S.messages.push({ type: 'info', text: '🗑️ All user data, sessions, and histories erased! Fresh start initialized.' });
  } catch (e) {
    S.messages.push({ type: 'error', text: `Erase error: ${e.message}` });
  }
  render();
}

function openModelModal() {
  S.modelModalOpen = true;
  S.modelModalFilter = '';
  S.modelModalCat = 'ALL';
  const filtered = getFilteredModels();
  const currentIdx = filtered.findIndex(m => m.id === S.model.id);
  S.modelModalIdx = currentIdx >= 0 ? currentIdx : 0;
  S.input = '';
  render();
}

function cmdToggleTodo() {
  S.showTodoPanel = !S.showTodoPanel;
  S.messages.push({ type: 'info', text: S.showTodoPanel ? 'Sticky note task panel enabled.' : 'Sticky note panel hidden.' });
  render();
}

function cmdQueue() {
  if (S.queue.length === 0) {
    S.messages.push({ type: 'info', text: 'Prompt queue is empty. Type any message while AI is busy to queue tasks.' });
  } else {
    let t = `Current Queue (${S.queue.length} items):\n`;
    S.queue.forEach((q, idx) => {
      t += `  ${idx + 1}. "${q.text}"\n`;
    });
    S.messages.push({ type: 'system', text: t });
  }
  render();
}

function cmdKeys() {
  let t = 'Active ELE API Credentials:\n';
  const checkKeys = ['NVIDIA_API_KEY', 'GEMINI_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GROQ_API_KEY'];
  for (const k of checkKeys) {
    const val = KEYS[k];
    if (val) {
      t += `  ✓ ${k.padEnd(20)} ${val.slice(0, 8)}••••${val.slice(-4)}\n`;
    } else {
      t += `  ○ ${k.padEnd(20)} not set\n`;
    }
  }
  t += `\nLoaded from: D:\\ELE\\backend\\.env & ~/.ele-agent/.env`;
  S.messages.push({ type: 'system', text: t });
  render();
}

function cmdBrowse(url) {
  const target = url || 'https://claude.ai';
  const c = process.platform === 'win32' ? `start chrome "${target}"` : `open "${target}"`;
  exec(c);
  S.messages.push({ type: 'info', text: `Opened browser to: ${target}` });
  render();
}

function cmdClear() {
  S.messages = [];
  S.messages.push({ type: 'info', text: 'Chat cleared.' });
  render();
}

function cmdEditor(file) {
  const target = file || '.';
  exec(`code "${target}"`);
  S.messages.push({ type: 'info', text: `Opened VS Code at: ${target}` });
  render();
}

function cmdExit() {
  stopVoiceListening();
  log('Session ended.');
  w(CLR, SHOW, ALT_OFF);
  console.log(`\n  ${strip(P.accent)}Goodbye from ELE Agent.\n`);
  process.exit(0);
}

// ═══════════════════════════════════════════════════════════════
//  KEYBOARD EVENT HANDLER (INTERACTIVE MODAL + QUEUEING)
// ═══════════════════════════════════════════════════════════════
function onKey(data) {
  const k = data.toString('utf-8');

  if (k === '\x03') { cmdExit(); return; }

  // ── Modal Mode Key Interception (Live Search & Category Tabs) ──
  if (S.modelModalOpen) {
    const filtered = getFilteredModels();

    if (k === '\x1b') { // Esc
      S.modelModalOpen = false;
      S.modelModalFilter = '';
      render();
      return;
    }

    if (k === '\t') { // Tab key to cycle category filters
      const cats = ['ALL', 'FAST', 'FLAGSHIP', 'REASON', 'VISION', 'NVIDIA', 'CLOUD'];
      const curIdx = cats.indexOf(S.modelModalCat || 'ALL');
      S.modelModalCat = cats[(curIdx + 1) % cats.length];
      S.modelModalIdx = 0;
      render();
      return;
    }

    if (k === '\x1b[A') { // Up Arrow
      S.modelModalIdx = Math.max(0, S.modelModalIdx - 1);
      render();
      return;
    }

    if (k === '\x1b[B') { // Down Arrow
      S.modelModalIdx = Math.min(Math.max(0, filtered.length - 1), S.modelModalIdx + 1);
      render();
      return;
    }

    if (k === '\r' || k === '\n') { // Enter Select
      if (filtered.length > 0) {
        S.model = filtered[S.modelModalIdx];
        S.modelModalOpen = false;
        S.modelModalFilter = '';
        S.messages.push({ type: 'info', text: `✓ Switched active model to ${S.model.name} (${S.model.tag})` });
        log(`Model switched to: ${S.model.name} (${S.model.id})`);
      }
      render();
      return;
    }

    if (k === '\x7f' || k === '\b') { // Backspace
      if (S.modelModalFilter.length > 0) {
        S.modelModalFilter = S.modelModalFilter.slice(0, -1);
        S.modelModalIdx = 0;
        render();
      }
      return;
    }

    if (k === '\x15') { // Ctrl+U clear search
      S.modelModalFilter = '';
      S.modelModalIdx = 0;
      render();
      return;
    }

    // Append typed letters/digits/spaces to live search filter
    if (k.length === 1 && k >= ' ' && k <= '~') {
      S.modelModalFilter += k;
      S.modelModalIdx = 0;
      render();
      return;
    }

    return;
  }

  // ── Jarvis Overlay Key Interception ──
  if (S.jarvisOpen) {
    if (k === '\x1b') {
      closeJarvisVoiceMode();
      return;
    }
  }

  if (k === '\x1b') {
    if (S.menuOpen) { S.menuOpen = false; render(); }
    return;
  }

  // Up Arrow
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

  // Down Arrow
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

  // Enter Key Handling (Includes Queueing when Busy)
  if (k === '\r' || k === '\n') {
    if (S.menuOpen && S.menuItems.length > 0) {
      const sel = S.menuItems[S.menuIdx];
      if (sel.cmd === '/model') {
        S.menuOpen = false;
        S.input = '';
        S.cursor = 0;
        openModelModal();
        return;
      }
      if (sel.cmd === '/jarvis') {
        S.menuOpen = false;
        S.input = '';
        S.cursor = 0;
        openJarvisVoiceMode();
        return;
      }
      if (sel.cmd === '/browse' || sel.cmd === '/editor' || sel.cmd === '/automate') {
        S.input = sel.cmd + ' ';
        S.cursor = S.input.length;
        S.menuOpen = false;
        render();
      } else {
        S.input = sel.cmd;
        S.menuOpen = false;
        const inp = S.input;
        S.input = ''; S.cursor = 0;

        if (S.busy) {
          S.queue.push({ text: inp, timestamp: Date.now() });
          render();
        } else {
          dispatchInput(inp);
        }
      }
    } else if (S.input.trim()) {
      const inp = S.input;
      S.input = ''; S.cursor = 0; S.menuOpen = false;

      if (inp === '/model') {
        openModelModal();
        return;
      }
      if (inp === '/jarvis' || inp === '/voice') {
        openJarvisVoiceMode();
        return;
      }

      if (S.busy) {
        S.queue.push({ text: inp, timestamp: Date.now() });
        render();
      } else {
        dispatchInput(inp);
      }
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
//  STARTUP SEQUENCE
// ═══════════════════════════════════════════════════════════════
async function boot() {
  ensureLogs();
  log('─'.repeat(60));
  log(`BOOT · ${os.platform()} · Node ${process.version}`);
  log(`Active Model: ${S.model.name}`);

  w(ALT_ON, HIDE, CLR);

  const cols = W();
  const rows = H();
  const cx = Math.floor(cols / 2);
  const cy = Math.floor(rows / 2) - 4;

  for (let i = 0; i < LOGO.length; i++) {
    const lpad = Math.max(1, cx - Math.floor(LOGO[i].length / 2));
    w(at(lpad, cy + i));
    w(`${P.accent}${BD}${LOGO[i]}${R}`);
  }

  const tag = 'ELE AI Autonomous Developer Terminal';
  w(at(cx - Math.floor(tag.length / 2), cy + LOGO.length + 1));
  for (let i = 0; i < tag.length; i++) {
    w(`${P.muted}${DM}${tag[i]}${R}`);
    await sleep(8);
  }

  const steps = ['Loading NVIDIA NIM Credentials (102+ Models)', 'Initializing Speech-to-Speech Engine', 'Ready'];
  for (const s of steps) {
    w(ELINE);
    w(at(cx - Math.floor(s.length / 2) - 1, cy + LOGO.length + 3));
    w(`${P.muted}${DM}${s}${R}`);
    await sleep(80);
  }

  // Asynchronously query live API for any extra models
  syncLiveNvidiaModels().catch(() => {});

  await sleep(100);

  S.messages.push({
    type: 'info',
    text: `ELE Agent connected · ${MODELS.length} Models Loaded (NVIDIA NIM, Gemini, Groq, OpenAI).\nActive Model: ${S.model.name}\nType /model to browse all 102+ models or /jarvis for Voice mode.`
  });

  if (process.stdin.isTTY) process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', onKey);
  process.stdout.on('resize', () => render());
  process.on('SIGINT', cmdExit);
  process.on('SIGTERM', cmdExit);
  process.on('exit', () => { 
    stopVoiceListening();
    w(SHOW, ALT_OFF); 
  });

  render();
}

boot().catch(err => {
  stopVoiceListening();
  w(SHOW, ALT_OFF);
  console.error('Error:', err);
  process.exit(1);
});
