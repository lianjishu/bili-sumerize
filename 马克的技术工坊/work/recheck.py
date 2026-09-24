# -*- coding: utf-8 -*-
"""定点复转：从 audio.mp3 截取片段，用自定义 initial_prompt 重转，用于确认专有名词。
用法: WHISPER_PROMPT="..." python recheck.py <start> <dur> <out.txt>
"""
import os, sys, time
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
from faster_whisper import WhisperModel

MODEL = os.environ.get("WHISPER_MODEL", "../models/faster-whisper-large-v3-turbo")
DEVICE = os.environ.get("WHISPER_DEVICE", "cuda")
CTYPE = os.environ.get("WHISPER_CTYPE", "float16")
PROMPT = os.environ.get("WHISPER_PROMPT", "")
start, dur, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]

model = WhisperModel(MODEL, device=DEVICE, compute_type=CTYPE)
segs, info = model.transcribe(
    "work/audio.mp3", language="zh", task="transcribe",
    beam_size=5, best_of=5, patience=1.0,
    temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    condition_on_previous_text=False,
    initial_prompt=PROMPT,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=400, speech_pad_ms=150),
    word_timestamps=True,
    clip_timestamps=[start, start + dur],
)
rows = []
for s in segs:
    rows.append(f"[{int(s.start)//60:02d}:{int(s.start)%60:02d}] {s.text.strip()}")
open(out, "w", encoding="utf-8").write("\n".join(rows))
print("lines", len(rows), "->", out)
