"""Smoke test: one tiny call twice. 1st must be a live call, 2nd must come from the
cache.  Run: python3 llm_smoke.py"""
import llm_client as L

msgs = [{"role": "user", "content": "Reply with exactly: PATH: RRDD"}]
for i in (1, 2):
    r = L.chat(msgs, tag="smoke")
    print(f"call {i}: cached={r['cached']} tokens_in={r['prompt_tokens']} "
          f"tokens_out={r['output_tokens']} latency={r['gen_latency_s']}s "
          f"reason={r['done_reason']}\n  text={r['text']!r}")
assert L.chat(msgs, tag="smoke")["cached"], "cache is not working"
print("cache OK ->", L.CACHE_DIR)
