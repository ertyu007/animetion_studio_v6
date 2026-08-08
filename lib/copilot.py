"""AI Copilot for generating episode skeletons via a local Ollama server."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional
import urllib.request


class CopilotError(RuntimeError):
    pass


DEFAULT_HOST = os.getenv("ANIMETION_OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("ANIMETION_OLLAMA_MODEL", "qwen3:8b")

SYSTEM_PROMPT = """\
คุณคือนักเขียนบทสคริปต์วิดีโอให้ความรู้ด้านการเขียนโปรแกรมเป็นภาษาไทย \
สำหรับช่อง "CodingThailand" บนแพลตฟอร์มวิดีโอสั้นแนวตั้ง (TikTok/YouTube Shorts) \
เสียงบรรยายเป็นภาษาไทย ให้เขียนด้วยภาษาพูดที่สนุกและเข้าใจง่าย เหมาะกับคนดู Gen Z

โครงสร้างวิดีโอต้องมี 5 ช่วงตามลำดับนี้เท่านั้น:
1. hook        — เปิดเรื่องด้วยคำถามหรือสถานการณ์ที่ชวนอยากรู้
2. concept     — อธิบายแนวคิดหลักของบทนี้
3. example     — ยกตัวอย่างการใช้งานจริงที่เห็นภาพชัดเจน
4. summary     — สรุปใจความสำคัญใน 1-2 ประโยค
5. cta         — ชวนกดติดตามและดูตอนต่อไป

ข้อบังคับสำคัญ (ถ้าผิด จะทำให้ validate ของโปรเจกต์ไม่ผ่าน):
- narration text: ห้ามยาวเกิน 120 ตัวอักษร และห้ามมีคำอังกฤษติดกัน 4 ตัวขึ้นไป
  (ศัพท์เทคนิคต้องเขียนเป็นคำอ่านไทย เช่น "อาร์เรย์" "ฟังก์ชัน" "บัฟเฟอร์")
- subtitle_beats: แต่ละช่วงต้องมี 2 ตัว แต่ละตัวห้ามยาวเกิน 35 ตัวอักษร
- ห้ามใช้เครื่องหมายดอกจันหรือมาร์กดาวน์ในข้อความ

ตอบเป็น JSON ล้วนเท่านั้น ห้ามมีข้อความอื่นใด โดยมีรูปแบบ:
{"title": "ชื่อตอนภาษาไทย", "tags": ["#hashtag1", "#hashtag2", "#hashtag3"],
 "cues": [
   {"key": "hook", "text": "...", "subtitle_beats": ["...", "..."]},
   {"key": "concept", "text": "...", "subtitle_beats": ["...", "..."]},
   {"key": "example", "text": "...", "subtitle_beats": ["...", "..."]},
   {"key": "summary", "text": "...", "subtitle_beats": ["...", "..."]},
   {"key": "cta", "text": "...", "subtitle_beats": ["...", "..."]}
 ]}
"""


def _post(payload: Dict[str, object], host: str, timeout: int) -> Dict[str, object]:
    request = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise CopilotError(
            f"cannot reach Ollama at {host} (is `ollama serve` running?): {exc}"
        ) from exc


def chat(model: str, prompt: str, *, host: str = DEFAULT_HOST, timeout: int = 900) -> str:
    """Send a single user message to Ollama and return the text reply."""
    payload: Dict[str, object] = {
        "model": model,
        "think": False,
        "stream": False,
        "options": {"temperature": 0.4, "num_predict": 8192},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    data = _post(payload, host, timeout)
    content = data.get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise CopilotError(f"empty model reply; done_reason={data.get('done_reason')!r}")
    return content


def _extract_json(text: str) -> Dict[str, object]:
    """Extract the last balanced JSON object from ``text`` (ignores markdown/prose)."""
    candidates = []
    start = 0
    while True:
        start = text.find("{", start)
        if start < 0:
            break
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start : index + 1])
                    break
        start = index + 1
    for raw in reversed(candidates):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    if candidates:
        raise CopilotError(
            f"model returned invalid JSON (tried {len(candidates)} candidate block(s)): "
            f"{candidates[-1][:400]}"
        )
    raise CopilotError(f"model did not return a JSON object. got: {text[:300]!r}")


def generate_episode(
    topic: str,
    *,
    model: str = DEFAULT_MODEL,
    host: str = DEFAULT_HOST,
    extra_instruction: str = "",
    max_retries: int = 3,
) -> Dict[str, object]:
    """Ask the LLM for a 5-cue episode skeleton for ``topic``, retrying on malformed JSON."""
    instruction = extra_instruction.strip()
    prompt = f"สร้างสคริปต์วิดีโอ 1 ตอน เรื่อง: {topic}"
    if instruction:
        prompt += f"\n\nข้อกำหนดเพิ่มเติมจากผู้ใช้: {instruction}"
    prompt += (
        "\n\nตอบเป็น JSON object เดียวเท่านั้น ครอบด้วย {{ }} โดยมี key: title, tags, cues "
        "(cues ต้องมี 5 ตัว key = hook, concept, example, summary, cta)"
    )
    last_error = "unknown error"
    for attempt in range(1, max_retries + 1):
        try:
            return _extract_json(chat(model, prompt, host=host))
        except CopilotError as exc:
            last_error = str(exc)
            print(f"  [retry {attempt}/{max_retries}] {last_error}")
    raise CopilotError(f"Ollama returned invalid output after {max_retries} attempts: {last_error}")
