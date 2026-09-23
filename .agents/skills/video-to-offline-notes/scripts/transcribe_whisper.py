# -*- coding: utf-8 -*-
"""Whisper 转写：中文课程用 large-v3-turbo + zh。"""
import json
import os
import sys
import time

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from faster_whisper import WhisperModel  # noqa: E402

AUDIO = sys.argv[1] if len(sys.argv) > 1 else "audio_16k.wav"
OUT = sys.argv[2] if len(sys.argv) > 2 else "transcript.json"
MODEL = os.environ.get("WHISPER_MODEL", "large-v3-turbo")
DEVICE = os.environ.get("WHISPER_DEVICE", "cuda")
CTYPE = os.environ.get("WHISPER_CTYPE", "float16")

PROMPT = (
    "以下是一堂中文大学课程录音，讲的是软件工程与人工智能，主题是提示词工程"
    "（Prompt Engineering / Context Engineering）。"
    "涉及术语：LLM、大语言模型、token、prompt、context、上下文窗口、"
    "few-shot、zero-shot、chain-of-thought、CoT、ReAct、RAG、agent、"
    "指令遵循、幻觉、对齐、temperature、评测、SWE-bench。"
    "请输出规范的书面中文。"
)

print(f"[init] model={MODEL} device={DEVICE} compute={CTYPE}", flush=True)
t0 = time.time()
model = WhisperModel(MODEL, device=DEVICE, compute_type=CTYPE,
                     download_root=os.path.abspath("models"))
print(f"[init] loaded in {time.time() - t0:.1f}s", flush=True)

t0 = time.time()
segments, info = model.transcribe(
    AUDIO,
    language="zh",
    task="transcribe",
    beam_size=5,
    best_of=5,
    patience=1.0,
    temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    condition_on_previous_text=False,
    initial_prompt=PROMPT,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200),
    word_timestamps=False,
    no_speech_threshold=0.6,
    compression_ratio_threshold=2.4,
)

rows = []
for s in segments:
    rows.append({
        "id": len(rows),
        "start": round(s.start, 3),
        "end": round(s.end, 3),
        "text": s.text.strip(),
        "no_speech_prob": round(getattr(s, "no_speech_prob", 0.0), 4),
        "avg_logprob": round(getattr(s, "avg_logprob", 0.0), 4),
    })
    if len(rows) % 200 == 0:
        print(f"[seg] {len(rows)} ... t={rows[-1]['end']:.0f}s", flush=True)

elapsed = time.time() - t0
audio_dur = info.duration
last_end = rows[-1]["end"] if rows else 0.0

result = {
    "model": MODEL,
    "device": DEVICE,
    "compute_type": CTYPE,
    "language": info.language,
    "language_probability": round(info.language_probability, 4),
    "audio_duration": round(audio_dur, 3),
    "transcribe_seconds": round(elapsed, 1),
    "speedup": round(audio_dur / elapsed, 2) if elapsed else None,
    "segment_count": len(rows),
    "last_segment_end": last_end,
    "coverage_ratio": round(last_end / audio_dur, 4) if audio_dur else None,
    "segments": rows,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print("=" * 60, flush=True)
print(f"[done] segments={len(rows)} audio={audio_dur:.1f}s elapsed={elapsed:.1f}s "
      f"speedup={audio_dur / elapsed:.1f}x", flush=True)
print(f"[check] last_end={last_end:.1f}s coverage={last_end / audio_dur * 100:.2f}%", flush=True)
print(f"[out] {OUT}", flush=True)
