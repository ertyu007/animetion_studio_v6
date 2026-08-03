# ปัญหาที่พบและแผนแก้ไข — Animetion Studio v6

> เอกสารนี้เป็นการ log ปัญหา ระหว่างรัน CLI ของ episode `oop_robot_factory`
> อัปเดตล่าสุด: 2026-08-03

---

## สถานะปัจจุบัน

| คำสั่ง | ผลลัพธ์ |
| ------ | ------- |
| `python cli.py list` | เห็น `oop_robot_factory` |
| `python cli.py preview oop_robot_factory` | ผ่านการ build command (render ใช้เวลานาน) |
| `python cli.py validate oop_robot_factory` | [OK] no validation issues |
| `python cli.py audio / status` | [OK] status ทำงาน ได้ |

---

## ปัญหาที่ 1 — `dataclass(slots=True)` ใช้กับ Python 3.9 ไม่ได้

**อาการ:**
```
TypeError: dataclass() got an unexpected keyword argument 'slots'
```

**สาเหตุ:** `slots=True` เพิ่มใน Python 3.10 แต่ venv โปรเจกต์เป็น **Python 3.9.12**

**ไฟล์/ตำแหน่ง:** `content/oop_robot_factory.py:19,33`

**วิธีแก้ (ทำแล้ว):** ลบ `slots=True` ออกทั้ง 2 จุด เปลี่ยนเป็น `@dataclass(frozen=True)`
**ทางเลือกยาว:** อัปเกรด venv เป็น Python 3.10+ แล้วคืน `slots=True` กลับ (ช่วยเรื่องหน่วยความจำกับ frozen dataclass)

---

## ปัญหาที่ 2 — เนื้อหา re-define model เอง ไม่ใช้ model มาตรฐานของโปรเจกต์ (รากของปัญหา)

`content/oop_robot_factory.py` สร้าง dataclass เอง (`EpisodeScript`, `Cue`) แต่โปรเจกมี model มาตรฐานอยู่แล้ว:

| Model | ไฟล์ | ฟิลด์ |
|---|---|---|
| `Episode` | `content/models.py` | `key, title, scene_file, scene_class, cues, tags` |
| `NarrationCue` | `lib/narration.py` | `key, text, voice, subtitle_beats, min_duration` |
| `VoiceProfile` | `lib/narration.py` | `name, rate, pitch, volume` |

ทุกคำสั่ง CLI อ้างอิง model มาตรฐาน:
- `cli.py:107` → `episode.scene_file`, `episode.scene_class`
- `cli.py:49,69` → `cue.key`, `cue.min_duration`
- `lib/validation.py:27,44` → `episode.scene_file`, `episode.scene_class`
- `lib/validation.py:64,66` → `cue.text`, `cue.voice.name`, `cue.subtitle_beats`
- `lib/models.py:8` → import `NarrationCue` จาก `lib.narration`

### 3.1 `Cue` ไม่มีฟิลด์ `text` / `voice`
- ไฟล์ใช้ `narration=` แต่ validation/CLI อ่าน `cue.text`
- ไฟล์ไม่มี `voice` แต่ validation ตรวจ `cue.voice.name`

### 3.2 `EpisodeScript` ไม่มี `scene_file`, `scene_class`
- `cli.py:107` เรียก `episode.scene_file` → AttributeError (ตอนนี้ผมต่อเติมเข้าไปใน struct แบบ band-aid)

### 3.3 ชื่อฟิลด์ metadata ไม่ตรง
- custom ใช้ `description`, `hashtags` แต่ standard ใช้ `tags`
- standard `Episode` มี `scene_file`, `scene_class` และ `cue()` method ครบ

---

## ปัญหาที่ 3 — ผมได้ทำ band-aid ชั่วคราวไว้แล้ว (ควร revert หรือ refactor)

ระหว่าง debug ผมทำไว้อนนี้ใน `content/oop_robot_factory.py`:
1. ลบ `slots=True` ออกจาก `Cue`, `EpisodeScript` → **เก็บไว้ได้** (ปัญหาที่ 1)
2. เพิ่ม `scene_file`, `scene_class` เข้า `EpisodeScript` และ set ค่า → **ควรแทนที่ด้วยการ refactor แบบ clean ข้างล่าง**

---

## แผนแก้ (Fix Plan)

### ทางเลือกที่แนะนำ — Refactor `content/oop_robot_factory.py` ให้ใช้ model มาตรฐาน

แก้ `SCRIPT` ให้สร้าง `content.models.Episode` ที่มี `cues` เป็น `NarrationCue` แทนที่จะนิยาม dataclass ซ้ำ:

```python
from content.models import Episode
from lib.narration import NA, THAI_FEMALE

SCRIPT = Episode(
    key="oop_robot_factory",
    title="OOP คืออะไร? เข้าใจด้วยโรงงานหุ่นยนต์",
    scene_file="scenes/oop_robot_factory_scene.py",
    scene_class="OOPRobotFactoryV1",
    cues=(),
    tags=("#Python", "#OOP", "#เขียนโปรแกรม", ...),   # แทน hashtags
)
# cues เป็น tuple ของ NarrationCue:
#   NarrationCue(key="hook", text="...", voice=THAI_FEMALE, subtitle_beats=(...))
```

ข้อดีของทางเลือกนี้:
- CLI / validate / audio / status ใช้ได้ทันที โดยไม่ต้องแก้ module อื่น
- truncate สอดคล้องกับ `docs/new-animation-workflow.md`
- แนวทางของ v6 คือ content เป็น data เท่านั้น (ตาม workflow doc)

### แก้ `lib/validation.py:16` — `Episode` type-hint
`lib/validation.py` import `Episode` จาก `content.models` อยู่แล้ว → หลัง refactor จะตรงกันเอง ไม่ต้องแก้เพิ่ม

### เช็คใน scene
`scenes/oop_robot_factory_scene.py` ต้องเรียก `SCRIPT.cue(...).subtitle_beats` ซึ่งหาได้ในทั้ง model เก่า/ใหม่ → ไม่ต้องแก้

### (ถ้าไม่ Want refactor) ทางเลือกสำรอง — ปรับ validation ให้ยืดหยุ่น
ลบ `Episode`/`NarrationCue` type-hint ออกจาก `validation.py` แล้วอ่านผ่าน `getattr()` แต่วิธีนี้ทำให้ต่อมาสับสนและไม่แนะนำ

---

## ขั้นตอนตรวจสอบหลังแก้

```powershell
python cli.py list
python cli.py validate oop_robot_factory
python cli.py status oop_robot_factory
python cli.py preview oop_robot_factory
```

---

## สรุป
- [x] แก้ `slots=True` กับ Python 3.9
- [x] Refactor `oop_robot_factory.py` ให้ใช้ `Episode`/`NarrationCue` แทน custom model — **ทำแล้ว**
- [x] รัน `validate` ผ่าน
- [x] รัน `preview` (build command) ผ่าน — ตัว render ใช้เวลานาน ขึ้นกับเครื่อง