# Preserved preflight failure

The first real Ollama call (sat_01, B, repetition 0) exceeded 120 seconds during local CPU inference. No model output was returned. This infrastructure observation is retained here, not pooled with the subsequent 300-second protocol. The machine has about 8 GB RAM and no GPU use was reported by Ollama. Do not interpret the timeout as a semantic or reasoning error. All original calls, checkpoints, metadata and the failed run artifact are preserved.
