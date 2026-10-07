import { test } from "node:test";
import assert from "node:assert/strict";
import worker, { scrub, chunks, handleRpc } from "../src/index.js";

const env = { MCP_SECRET: "s3cret-path-token", AI: { run: async () => ({ response: "fake summary" }) } };
const post = (path, body) => worker.fetch(new Request(`https://x.dev${path}`, { method: "POST", body: JSON.stringify(body) }), env);

test("scrub removes keys", () => {
  const [t, n] = scrub("a sk-ant-api03-abcdefghijklmnopqrstu b gsk_abcdefghijklmnopqrstuvwx");
  assert.ok(!t.includes("sk-ant") && !t.includes("gsk_") && n === 2);
});

test("chunks split long text", () => assert.equal(chunks("x".repeat(30000), 14000).length, 3));

test("wrong secret path is 404", async () => {
  assert.equal((await post("/mcp/wrong", { jsonrpc: "2.0", id: 1, method: "tools/list" })).status, 404);
  assert.equal((await post("/", {})).status, 404);
});

test("initialize, list and call over MCP", async () => {
  const init = await (await post("/mcp/s3cret-path-token", { jsonrpc: "2.0", id: 1, method: "initialize", params: {} })).json();
  assert.equal(init.result.serverInfo.name, "free-llm-helper");
  const list = await (await post("/mcp/s3cret-path-token", { jsonrpc: "2.0", id: 2, method: "tools/list" })).json();
  assert.deepEqual(list.result.tools.map(t => t.name), ["free_summarize_url", "free_ask", "free_draft"]);
  const call = await (await post("/mcp/s3cret-path-token", { jsonrpc: "2.0", id: 3, method: "tools/call",
    params: { name: "free_ask", arguments: { question: "what?", text: "the answer is 42" } } })).json();
  assert.match(call.result.content[0].text, /fake summary[\s\S]*via workers-ai/);
  const note = await post("/mcp/s3cret-path-token", { jsonrpc: "2.0", method: "notifications/initialized" });
  assert.equal(note.status, 202);
});

test("private URLs are refused", async () => {
  const r = await handleRpc(env, { jsonrpc: "2.0", id: 4, method: "tools/call",
    params: { name: "free_summarize_url", arguments: { urls: ["http://169.254.169.254/latest"] } } });
  assert.match(r.result.content[0].text, /blocked URL/);
});
