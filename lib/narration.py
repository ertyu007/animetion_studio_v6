"""Edge TTS generation and deterministic audio caching."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple


_RATE = re.compile(r"([+-]?)(\d+)%")


@dataclass(frozen=True)
class VoiceProfile:
    name: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"


THAI_FEMALE = VoiceProfile("th-TH-PremwadeeNeural", rate="-5%", volume="+8%")
THAI_MALE = VoiceProfile("th-TH-NiwatNeural", rate="-7%", pitch="-2Hz", volume="-5%")


@dataclass(frozen=True)
class NarrationCue:
    key: str
    text: str
    voice: VoiceProfile = THAI_FEMALE
    subtitle_beats: Tuple[str, ...] = ()
    min_duration: float = 1.2


@dataclass(frozen=True)
class RenderedNarration:
    cue: NarrationCue
    media_path: Optional[Path]
    duration: float
    generated: bool = False
    error: str = ""


class EdgeTTSRenderer:
    MODES = {"auto", "cache", "off"}

    def __init__(self, cache_dir: Optional[Path] = None, mode: Optional[str] = None) -> None:
        root = Path(__file__).resolve().parent.parent
        env_dir = os.getenv("ANIMETION_NARRATION_DIR")
        self.cache_dir = Path(env_dir) if env_dir else (cache_dir or root / ".cache" / "narration")
        self.mode = (mode or os.getenv("ANIMETION_TTS", "auto")).strip().lower()
        if self.mode not in self.MODES:
            raise ValueError(f"ANIMETION_TTS must be one of {sorted(self.MODES)}")
        self.manifest_path = self.cache_dir / "manifest.json"

    def _payload(self, cue: NarrationCue) -> Dict[str, object]:
        return {"key": cue.key, "text": cue.text, "voice": asdict(cue.voice)}

    def cache_key(self, cue: NarrationCue) -> str:
        raw = json.dumps(self._payload(cue), ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:14]

    def media_path(self, cue: NarrationCue) -> Path:
        safe = re.sub(r"[^A-Za-z0-9_-]+", "-", cue.key).strip("-") or "cue"
        return self.cache_dir / f"{safe}-{self.cache_key(cue)}.mp3"

    @staticmethod
    def _rate_multiplier(rate: str) -> float:
        match = _RATE.fullmatch(rate.strip())
        if not match:
            return 1.0
        sign, number = match.groups()
        value = int(number) / 100
        return max(0.35, 1.0 - value) if sign == "-" else 1.0 + value

    def estimate_duration(self, cue: NarrationCue) -> float:
        compact = re.sub(r"\s+", "", cue.text)
        punctuation = len(re.findall(r"[,.!?…:;ๆฯ]|[，。！？]", cue.text))
        base = max(cue.min_duration, len(compact) / 11.4 + punctuation * 0.16)
        return max(cue.min_duration, base / self._rate_multiplier(cue.voice.rate))

    @staticmethod
    def probe_duration(path: Path) -> float:
        if not path.is_file() or path.stat().st_size <= 0:
            return 0.0
        try:
            from mutagen import File as MutagenFile

            audio = MutagenFile(str(path))
            if audio is not None and audio.info is not None:
                return max(0.0, float(audio.info.length))
        except Exception:
            return 0.0
        return 0.0

    async def _generate(self, cue: NarrationCue, destination: Path) -> None:
        import edge_tts

        communicator = edge_tts.Communicate(
            text=cue.text,
            voice=cue.voice.name,
            rate=cue.voice.rate,
            pitch=cue.voice.pitch,
            volume=cue.voice.volume,
        )
        await communicator.save(str(destination))

    def _load_manifest(self) -> Dict[str, object]:
        if not self.manifest_path.is_file():
            return {}
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def _write_manifest(self, result: RenderedNarration) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        data = self._load_manifest()
        data[result.cue.key] = {
            "cache_key": self.cache_key(result.cue),
            "file": result.media_path.name if result.media_path else None,
            "duration": round(result.duration, 3),
            "voice": asdict(result.cue.voice),
            "text": result.cue.text,
        }
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        temporary: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix="manifest-",
                suffix=".tmp",
                dir=str(self.cache_dir),
                delete=False,
            ) as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
                temporary = Path(handle.name)
            os.replace(temporary, self.manifest_path)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def render(self, cue: NarrationCue, force: bool = False) -> RenderedNarration:
        estimate = self.estimate_duration(cue)
        if self.mode == "off":
            return RenderedNarration(cue, None, estimate)

        destination = self.media_path(cue)
        if destination.is_file() and not force:
            duration = self.probe_duration(destination)
            if duration > 0:
                return RenderedNarration(cue, destination, max(duration, cue.min_duration))
            destination.unlink(missing_ok=True)

        if self.mode == "cache":
            return RenderedNarration(cue, None, estimate, error=f"missing narration cache: {destination.name}")

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        temporary: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".mp3",
                prefix="tts-",
                dir=str(self.cache_dir),
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
            asyncio.run(self._generate(cue, temporary))
            duration = self.probe_duration(temporary)
            if duration <= 0:
                raise RuntimeError("generated audio could not be probed")
            os.replace(temporary, destination)
            temporary = None
            result = RenderedNarration(cue, destination, max(duration, cue.min_duration), generated=True)
            self._write_manifest(result)
            return result
        except Exception as exc:
            return RenderedNarration(cue, None, estimate, error=str(exc))
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
