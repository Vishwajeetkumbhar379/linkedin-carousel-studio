// Remote MCP server (Streamable HTTP, JSON responses) for Claude chat / claude.ai custom connectors.
// It only ever reads PUBLIC URLs and text you pass in; it has no access to your machine.
// URL: https://<worker>.<subdomain>.workers.dev/mcp/<MCP_SECRET>

const UA = "free-llm-helper/0.1";
const SYSTEM = "You are a precise assistant doing bulk reading for another AI. Be terse and factual. Quote names, " +
  "numbers and errors exactly. Never invent anything that is not in the input; say 'not found' instead.";
const CHUNK = 14000;
const MAX_INPUT = 400000;

const SECRET_PATTERNS = [
  /-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/g,
  /\b(?:sk-ant-|sk-or-v1-|sk-proj-|sk-)[A-Za-z0-9_\-]{16,}/g,
  /\b(?:gsk_|nvapi-|xai-|hf_|glpat-|npm_|pypi-)[A-Za-z0-9_\-]{16,}/g,
  /\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}/g,
  /\bAIza[0-9A-Za-z_\-]{30,}/g,
  /\b(?:AKIA|ASIA)[0-9A-Z]{16}\b/g,
  /\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}/g,
];

export function scrub(text) {
  let n = 0;
  for (const re of SECRET_PATTERNS) text = text.replace(re, () => (n++, "[REDACTED]"));
  return [text, n];
}

function providers(env) {
  const list = [];
  const add = (name, url, key, model) => key && list.push({ name, url, key, model });
  add("groq", "https://api.groq.com/openai/v1", env.GROQ_API_KEY, env.GROQ_MODEL || "openai/gpt-oss-120b");
  add("nvidia", "https://integrate.api.nvidia.com/v1", env.NVIDIA_API_KEY, env.NVIDIA_MODEL || "moonshotai/kimi-k3");
  if (env.AI) list.push({ name: "workers-ai", binding: env.AI, model: env.CF_MODEL || "@cf/meta/llama-3.3-70b-instruct-fp8-fast" });
  add("openrouter", "https://openrouter.ai/api/v1", env.OPENROUTER_API_KEY,
      env.OPENROUTER_MODEL || "nvidia/nemotron-3-super-120b-a12b:free");
  add("mistral", "https://api.mistral.ai/v1", env.MISTRAL_API_KEY, env.MISTRAL_MODEL || "ministral-14b-latest");
  add("llm7", "https://api.llm7.io/v1", env.LLM7_API_KEY, env.LLM7_MODEL || "deepseek-v4-pro");
  return list;
}

async function callOne(p, system, user, maxTokens) {
  const messages = [{ role: "system", content: system }, { role: "user", content: user }];
  if (p.binding) {
    const r = await p.binding.run(p.model, { messages, max_tokens: maxTokens });
    return (r.response || r.choices?.[0]?.message?.content || "").trim();
  }
  const r = await fetch(`${p.url}/chat/completions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${p.key}`, "Content-Type": "application/json", "User-Agent": UA },
    body: JSON.stringify({ model: p.model, max_tokens: maxTokens, messages }),
  });
  if (!r.ok) throw new Error(`${p.name} ${r.status}: ${(await r.text()).slice(0, 200)}`);
  const j = await r.json();
  return (j.choices?.[0]?.message?.content || "").replace(/<think>[\s\S]*?<\/think>/g, "").trim();
}

export async function chat(env, system, user, maxTokens = 1500, used = []) {
  const errors = [];
  for (const p of providers(env)) {
    try {
      const text = await callOne(p, system, user, maxTokens);
      if (!text) throw new Error(`${p.name}: empty reply`);
      used.push(`${p.name}/${p.model}`);
      return text;
    } catch (e) {
      errors.push(String(e.message || e));
    }
  }
  throw new Error(errors.length ? "All free providers failed: " + errors.join(" | ") : "No provider keys configured");
}

function isPrivateHost(host) {
  return /^(localhost|127\.|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.|0\.|\[?::1\]?|metadata)/i.test(host);
}

async function fetchText(url) {
  const u = new URL(url);
  if (!/^https?:$/.test(u.protocol) || isPrivateHost(u.hostname)) throw new Error(`blocked URL: ${url}`);
  const r = await fetch(u, { headers: { "User-Agent": UA } });
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  let t = (await r.text()).slice(0, 3_000_000);
  if (/<html|<body/i.test(t.slice(0, 5000))) {
    t = t.replace(/<(script|style|noscript|svg|nav|footer|header)[^>]*>[\s\S]*?<\/\1>/gi, " ")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"');
  }
  return t.replace(/[ \t]+/g, " ").replace(/\n\s*\n+/g, "\n\n").trim();
}

export function chunks(text, size = CHUNK) {
  const out = [];
  for (let i = 0; i < text.length; i += size) out.push(text.slice(i, i + size));
  return out;
}

async function gather(urls = [], text = "") {
  const parts = [], skipped = [];
  let redactions = 0;
  for (const url of urls) {
    try { parts.push(`===== ${url} =====\n${await fetchText(url)}`); } catch (e) { skipped.push(String(e.message || e)); }
  }
  if (text) parts.push(`===== provided text =====\n${text}`);
  let [all, n] = scrub(parts.join("\n\n").slice(0, MAX_INPUT));
  redactions += n;
  return { text: all, skipped, redactions };
}

async function mapReduce(env, text, mapPrompt, reducePrompt, used) {
  const pieces = chunks(text);
  if (!pieces.length) return "Nothing readable in the given sources.";
  if (pieces.length === 1) return chat(env, SYSTEM, `${mapPrompt}\n\n${pieces[0]}`, 1500, used);
  const notes = await Promise.all(pieces.map((p, i) =>
    chat(env, SYSTEM, `${mapPrompt}\n\nThis is part ${i + 1} of ${pieces.length}.\n\n${p}`, 1200, used)));
  let joined = notes.map((n, i) => `--- part ${i + 1} ---\n${n}`).join("\n\n");
  while (joined.length > CHUNK) {
    joined = (await Promise.all(chunks(joined).map(g =>
      chat(env, SYSTEM, `Merge these notes, keep every concrete fact:\n\n${g}`, 1200, used)))).join("\n\n");
  }
  return chat(env, SYSTEM, `${reducePrompt}\n\n${joined}`, 1500, used);
}

function footer(g, used, out) {
  const bits = [`via ${[...new Set(used)].join(", ") || "none"}`,
    `read ${g.text.length.toLocaleString()} chars -> returned ${out.length.toLocaleString()}`];
  if (g.redactions) bits.push(`${g.redactions} secret(s) redacted`);
  if (g.skipped.length) bits.push(`skipped: ${g.skipped.slice(0, 5).join("; ")}`);
  return `\n\n[free-llm-helper: ${bits.join(" | ")}]`;
}

const URLS = { type: "array", items: { type: "string" }, description: "Public http(s) URLs to read" };
export const TOOLS = [
  { name: "free_summarize_url",
    description: "Read long public web pages/docs/PDF-text with a FREE model and return a short summary, so the page never enters your context.",
    inputSchema: { type: "object", properties: { urls: URLS, focus: { type: "string" }, max_words: { type: "integer", default: 250 } }, required: ["urls"] } },
  { name: "free_ask",
    description: "Answer a question from public URLs (and/or provided text) with a FREE model; returns a cited answer. Verify before relying on it.",
    inputSchema: { type: "object", properties: { question: { type: "string" }, urls: URLS, text: { type: "string" } }, required: ["question"] } },
  { name: "free_draft",
    description: "Write a first draft (post, email, outline) with a FREE model from instructions and optional URLs. Polish it yourself.",
    inputSchema: { type: "object", properties: { instructions: { type: "string" }, urls: URLS, max_words: { type: "integer", default: 400 } }, required: ["instructions"] } },
];

export async function callTool(env, name, a) {
  const used = [];
  if (name === "free_summarize_url") {
    const g = await gather(a.urls || []);
    const f = a.focus ? ` Focus on: ${a.focus}.` : "";
    const out = await mapReduce(env, g.text, `Summarize this in bullet points.${f} Keep names, numbers, dates.`,
      `Combine these notes into one summary. Hard limit: ${a.max_words || 250} words.${f}`, used);
    return out + footer(g, used, out);
  }
  if (name === "free_ask") {
    const g = await gather(a.urls || [], a.text || "");
    const out = await mapReduce(env, g.text,
      `Question: ${a.question}\nExtract everything relevant with quotes, or reply NOTHING RELEVANT.`,
      `Question: ${a.question}\nAnswer from these notes only, cite sources, say 'not found' if they do not answer it.`, used);
    return out + footer(g, used, out);
  }
  if (name === "free_draft") {
    const g = await gather(a.urls || []);
    const ctx = g.text.length > CHUNK
      ? await mapReduce(env, g.text, `Extract facts for: ${a.instructions}`, "Merge these facts.", used) : g.text;
    const [instr] = scrub(a.instructions);
    const out = await chat(env, "You are a skilled writer. Write exactly what is asked, no preamble.",
      `Task: ${instr}\nMax ${a.max_words || 400} words.\n\nContext:\n${ctx || "(none)"}`, 2500, used);
    return out + footer(g, used, out);
  }
  throw new Error(`Unknown tool ${name}`);
}

export async function handleRpc(env, msg) {
  const { id, method, params = {} } = msg;
  if (id === undefined || id === null) return null; // notification
  const ok = result => ({ jsonrpc: "2.0", id, result });
  if (method === "initialize") {
    return ok({ protocolVersion: params.protocolVersion || "2025-06-18", capabilities: { tools: {} },
      serverInfo: { name: "free-llm-helper", version: "0.1.0" } });
  }
  if (method === "tools/list") return ok({ tools: TOOLS });
  if (method === "ping") return ok({});
  if (method === "tools/call") {
    try {
      return ok({ content: [{ type: "text", text: await callTool(env, params.name, params.arguments || {}) }] });
    } catch (e) {
      return ok({ content: [{ type: "text", text: `free-llm-helper error: ${e.message || e}` }], isError: true });
    }
  }
  return { jsonrpc: "2.0", id, error: { code: -32601, message: `Method not found: ${method}` } };
}

function timingSafeEqual(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/mcp\/([^/]+)\/?$/);
    if (!m || !env.MCP_SECRET || !timingSafeEqual(m[1], env.MCP_SECRET)) return new Response("Not found", { status: 404 });
    if (request.method === "GET") return new Response("Method not allowed", { status: 405, headers: { Allow: "POST" } });
    if (request.method === "DELETE") return new Response(null, { status: 204 });
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
    let body;
    try { body = await request.json(); } catch { return Response.json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }, { status: 400 }); }
    const replies = (await Promise.all((Array.isArray(body) ? body : [body]).map(msg => handleRpc(env, msg)))).filter(Boolean);
    if (!replies.length) return new Response(null, { status: 202 });
    return Response.json(Array.isArray(body) ? replies : replies[0]);
  },
};
