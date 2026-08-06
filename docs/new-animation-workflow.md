# คู่มือสร้างอนิเมชั่นใหม่ใน Animetion Studio v6

> เอกสารนี้คือ "กฎเกณฑ์" สำหรับสร้าง episode ใหม่ — ให้ใช้เป็นสเปกสำหรับ AI/ผู้สร้าง
> ทุก episode ใหม่ต้องผ่านเกณฑ์ทั้งหมดในเอกสารนี้ก่อน render

## 1. เริ่มจากสิ่งที่ต้องทำ (ลำดับบังคับ)

1. เขียนบทพูดและกำหนด cue ใน `content/<episode>.py`
2. สร้าง scene ใน `scenes/<episode>.py`
3. ลงทะเบียน episode ใน `content/registry.py`
4. ตรวจความถูกต้องด้วย `python cli.py validate all`
5. Preview ก่อน render

ห้ามข้ามขั้นตอน 4-5 เพราะเป็นเกตที่กันไม่ให้ render พังตอนท้าย

## 2. โครงสร้างไฟล์ที่ควรรู้

- `content/<episode>.py` — กำหนด narration, cue, subtitle และ metadata (data เท่านั้น ไม่มี Manim)
- `scenes/<episode>.py` — กำหนดภาพและการเล่น animation
- `lib/components.py` — UI components ที่ใช้ซ้ำ เช่น CodePanel, MemoryNode, Caption
- `lib/scene_base.py` — base scene ที่จัดการ caption และ play_cue
- `lib/timeline.py` — `beat(...)` และ scheduling
- `lib/motion.py` — helpers สำหรับ animation ที่ใช้บ่อย
- `lib/settings.py` — สี ขนาด ตำแหน่ง layout

## 3. กฎสำคัญของ v6 (ห้ามละเมิดเด็ดขาด)

- ใช้ `play_cue()` เพื่อสลับ cue ทีละช่วง
- ใช้ `beat(lambda: ...)` เพื่อส่ง animation factory ทีละ beat
- อย่าใส่ animation ทั้ง section ใน `Succession` เดียว
- อย่าเรียก `get_run_time()` หรือ setup future objects ล่วงหน้า
- ให้สร้าง object ใน beat ที่จะใช้จริงเท่านั้น
- สีทุกสีต้องมาจาก `SETTINGS.palette` เท่านั้น ห้าม hardcode สีใหม่ใน scene
- component ที่ใช้ซ้ำต้องสร้างจาก `lib/components.py` อย่าทำใหม่ใน scene

## 4. กฎการเขียนบทพูด (content)

### 4.1 โครงสร้างเนื้อหาที่ต้องมี (ทุกตอน)

ทุกตอนต้องมีโครงสร้างครบ 5 ช่วง ตามลำดับ:

1. **hook** — คำถาม/สถานการณ์ชวนติดตาม (ปลุกความอยากรู้)
2. **concept** — อธิบายแนวคิดหลัก
3. **example** — ตัวอย่างรูปธรรม/โค้ด/การเปรียบเทียบ
4. **summary** — สรุปเป็นข้อสั้นกระชับ
5. **cta** — คำถามทิ้งท้าย/ชวนคอมเมนต์

### 4.2 กฎต่อ cue

- 1 cue = 1 ไอเดียเท่านั้น (ห้ามยัดหลายแนวคิดใน cue เดียว)
- ทุก cue ต้องมี `subtitle_beats` เป็นวลีสั้น ๆ อ่านจบใน 1 วินาที
- แต่ละวลี subtitle ห้ามยาวเกิน ~35 ตัวอักษร
- ตัวเลข/ค่าที่พูดในเสียง ต้องตรงกับตัวเลขบนจอเป๊ะ ๆ
- ทุก cue ต้องมี visual (scene) ที่ match กัน — ห้ามมี cue ที่ไม่มีภาพ
- ชื่อ cue ใช้ snake_case สั้น ๆ เช่น `hook`, `oop_intro`, `summary`

### 4.3 กฎการออกเสียงศัพท์ภาษาอังกฤษ (คำอ่าน) — บังคับ

- ทุกศัพท์ eng/เทคนิคที่พูดในเสียง **ต้องใช้คำอ่านไทยที่ฟังแล้วชัดเจน** อย่าทิ้งคำ eng เปล่า ๆ
  เพราะ TTS เสียงไทย (th-TH) จะอ่านศัพท์ eng เพี้ยนจนผู้ฟังงง
- บนจอ (โค้ด/ป้าย/หัวข้อ) เขียนเป็นศัพท์ eng หรือโค้ดจริง แต่**เสียงบรรยายต้องพูดคำอ่านไทย**
- ใช้คำอ่านเดียวกันทั้งตอนและทั้งโปรเจกต์ (ห้ามสลับคำอ่านไปมา)
- ถ้าเป็นชื่อฟังก์ชันยาว ให้เติมคำว่า "คำสั่ง" นำหน้า แล้วตามด้วยคำอ่าน
- ตัวอย่างคำอ่านมาตรฐานของโปรเจกต์:

| ศัพท์ | คำอ่าน |
|---|---|
| LED | แอลอีดี |
| C (ภาษา) | ซี |
| loop | ลูป |
| delay | ดีเลย์ |
| pinMode | พินโหมด |
| digitalWrite | ดิจิทัล ไรท์ |
| OUTPUT | เอาต์พุต |
| HIGH / LOW | ไฮ / โลว์ |
| class / object | คลาส / ออบเจกต์ |
| method | เมทอด |
| attribute | แอตทริบิวต์ |

### 4.4 กฎช่องพักหายใจ — บังคับ

- แบ่งบทบรรยายเป็น**ช่วงหายใจสั้น ๆ** ประมาณ 15-30 ตัวอักษรต่อช่วง
- ใช้เครื่องหมาย `,` สำหรับพักสั้น และ `.` หรือ `...` สำหรับพักยาว
- ก่อนขึ้นศัพท์ใหม่หรือแนวคิดใหม่ ต้องมีพักเล็กน้อย
- ห้ามบรรยายรัวยาวเป็นก้อนเดียวเกิน ~120 ตัวอักษร
- ช่วงพักทำให้จังหวะภาพ (beat) ตรงกับเสียง และผู้ฟังตามทัน
- หลังแก้บท ให้อ่านออกเสียงจริง ถ้ารู้สึกอึดอัดหรือหายใจไม่ทัน แปลว่าต้องเพิ่มช่องพัก

### 4.5 สิ่งที่ต้องคิดเพิ่ม

- **Glossary**: ใส่ตารางคำอ่านท้ายไฟล์ `content/` ทุกไฟล์ กันคำอ่านเพี้ยนหรือสลับ
- **ตัวเลข**: TTS อ่านตัวเลขเป็นคำไทยอัตโนมัติ ("13" → "สิบสาม") ตรวจให้ตรงกับตัวเลขบนจอ
- **คำผสม eng-ไทย**: หลีกเลี่ยงคำที่ TTS สะดุด เช่น `click`, `start`, `button` — ให้แทนด้วยคำไทยล้วนหรือคำอ่าน
- **การเว้นวรรค**: เว้นวรรคระหว่างคำในข้อความบรรยายเสมอ (ตามสไตล์ไฟล์ content เดิม) ช่วยให้ TTS แบ่งคำได้ถูก
- **เสียง vs จอ**: เสียงกับซับไตเติลอ่านเรื่องเดียวกัน แต่เขียนต่างกันได้ — เสียงใช้คำอ่านไทย, จอใช้ศัพท์/โค้ดจริง
- **ทดสอบด้วยหู**: อ่านบทออกเสียงจริงก่อน commit ทุกครั้ง ถ้าติดขัดให้แก้ก่อน

### 4.6 ตัวอย่าง content

```python
from content.models import Episode
from lib.narration import NarrationCue, THAI_FEMALE

SCRIPT = Episode(
    key="my_topic",
    title="หัวข้อตอน",
    scene_file="scenes/my_topic_scene.py",
    scene_class="MyTopicV1",
    tags=("#Tag1", "#Tag2"),
    cues=(
        NarrationCue(
            key="hook",
            text="ข้อความบรรยายภาษาไทยทั้งประโยค",
            subtitle_beats=(
                "วลีสั้น 1",
                "วลีสั้น 2",
                "วลีสั้น 3",
            ),
        ),
    ),
)
```

หมายเหตุ:
- ใช้ model มาตรฐาน `Episode` และ `NarrationCue` เท่านั้น ห้ามนิยาม dataclass เอง
- ห้ามใช้ `slots=True` (โปรเจกต์ยังรันบน Python 3.9)
- จำนวน `subtitle_beats` ต้องเท่ากับจำนวน `beat(...)` ใน scene ของ cue นั้น

## 5. กฎการเขียน scene (ห้ามพังตอน render)

### 5.1 กฎบังคับ

- คลาส scene ต้องสืบทอด `NarratedScene`
- เรียก `SCRIPT.cue("key")` ด้วย key ที่มีอยู่จริงใน `content/` เท่านั้น
- เรียก `self.play_cue(cue, (beats...), cleanup=group)` ทุก cue
- ใช้ `beat(lambda: <animation>, weight=..., caption=cue.subtitle_beats[i])`
  - `caption` ต้องใช้ index ตามลำดับ และ index ต้องไม่เกินจำนวน `subtitle_beats`
  - `weight` ต้องเป็นบวกเสมอ (บ่งชี้สัดส่วนเวลาภายใน cue)
- เรียก `self.build_stage()` ในตอนเริ่มต้นของ `construct`
- ทุกฟังก์ชัน `show_*` ต้องปิดท้ายด้วย `cleanup=group` (FadeOut ทั้ง section)
- ห้ามเรียก `get_run_time()`, `VisualPlan`, `prepare_for_reveal`, `narration_beats`

### 5.2 ตัวอย่าง flow ของ scene

```python
class MyEpisodeV1(NarratedScene):
    def construct(self) -> None:
        self.build_stage()
        self.show_intro()
        self.show_demo()
        self.show_takeaway()
```

```python
def show_demo(self) -> None:
    cue = SCRIPT.cue("demo")
    self.play_cue(
        cue,
        (
            beat(lambda: reveal_header(header), weight=0.9, caption=cue.subtitle_beats[0]),
            beat(lambda: reveal_code(code), weight=1.2, caption=cue.subtitle_beats[1]),
        ),
        cleanup=group,
    )
```

### 5.3 กฎ layout (หลบ TikTok UI)

- เนื้อหาทุกอย่างต้องอยู่ใน safe zone: `safe_width=7.8`, `safe_top=6.55`, `safe_bottom=-6.30` (ดู `lib/settings.py`)
- caption อยู่ที่ `caption_y=-4.00` เพื่อหลบ TikTok UI ด้านล่าง — ห้ามย้ายลงไปต่ำกว่านี้
- ความกว้างรวมของ content (โค้ด/การ์ด/กริด) ต้องไม่เกิน `7.8` หน่วย
- เครดิต `@ertyu0075` มุมซ้ายล่าง — ห้ามทับ

### 5.4 กฎ animation

- ข้อความทั่วไป/หัวข้อ → `Write`
- โค้ดและ terminal → `AddTextLetterByLetter` เท่านั้น
- ใช้ `AnimationGroup` ใน beat เดียวสำหรับหลาย animation พร้อม `lag_ratio` 0.15-0.25
- `.animate.move_to(...)` ต้องถูกส่งตรงเข้า `Scene.play()` ตอนถึงคิวเท่านั้น

## 6. กฎ timing / audio

- เวลา cue ทั้งหมดมาจากความยาว MP3 จริง (อ่านด้วย Mutagen) — ห้ามตั้งเวลาเอง
- หลังแก้ข้อความบทพูดทุกครั้ง ต้องรัน `python cli.py audio all --force` (ล้าง cache เก่า)
- ก่อน render final ต้องตรวจ `python cli.py status --strict` คืนค่า 0 (มีเสียงครบทุก cue)
- ห้าม render final ในขณะที่ยังมี cue ที่ไม่มีเสียง (จะ sync เพี้ยน)

## 7. เกตก่อน render (checklist บังคับ)

รันให้ครบตามลำดับ แล้วค่อย render:

```powershell
python cli.py list
python cli.py validate all
python -m pytest
python cli.py audio all
python cli.py status --strict
python cli.py preview <episode>
python cli.py render <episode> --preset draft
python cli.py render <episode> --preset final
```

- `validate` ต้องไม่มี ERROR
- `pytest` ต้องผ่านทั้งหมด
- `status --strict` ต้องคืน 0
- ห้ามข้ามขั้น preview ไป render final ทีเดียว

## 8. สิ่งที่ validate ตรวจได้ vs ตรวจไม่ได้

### ตรวจได้อัตโนมัติ (`python cli.py validate all`)

- scene path อยู่ใน project root และไฟล์มีจริง
- scene class มีจริงในไฟล์ scene
- cue key ไม่ซ้ำกัน
- ข้อความบรรยายไม่ว่างเปล่า
- ชื่อ voice อยู่ในรูปแบบ `xx-XX-...Neural`
- highlight markup สมดุล
- subtitle ไม่ยาวเกิน 35 ตัวอักษร
- บทบรรยาย (`cue.text`) ไม่ยาวเกิน 120 ตัวอักษร และไม่มีศัพท์ eng ที่ยาวเกิน 3 ตัวโดยไม่มีคำอ่านไทย
- `min_duration` ต้องเป็นบวก
- ห้ามมี legacy API (`VisualPlan`, `get_run_time`, `prepare_for_reveal`, `narration_beats`)
- scene ต้องมี `play_cue()`
- `SCRIPT.cue("key")` ใน scene ต้องเป็น key ที่มีอยู่จริง
- จำนวน `beat` ใน `play_cue` ต้องเท่ากับจำนวน `subtitle_beats` ของ cue นั้น
- `caption=cue.subtitle_beats[i]` ต้องไม่เกินขอบเขตของ `subtitle_beats`
- `beat(weight=...)` ต้องเป็นบวก
- ทุก cue ต้องถูกเล่นด้วย `play_cue` ครบ (ห้าม cue ที่ไม่มีภาพ)
- `build_stage()` ต้องไม่มี argument (progress dots ถูกลบออกไปแล้ว)

### ตรวจไม่ได้ (ต้องใช้ดุลยพินิจ — กฎข้อ 4, 5)

- ตัวเลขในเสียงตรงกับตัวเลขบนจอ
- เนื้อหาอยู่ใน safe zone
- render MP4, ฟอนต์ไทย, เสียงจริงทำงานบนเครื่อง

> เหลือจุดที่ตรวจไม่ได้เพียงไม่กี่จุด ซึ่งส่วนใหญ่ตรวจได้ตอน preview

## 9. กฎ repo / commit

- แก้ 3 ไฟล์นี้ด้วยกันเสมอ: `content/<episode>.py`, `scenes/<episode>.py`, `content/registry.py`
- หลังลง registry ต้องเห็นใน `python cli.py list` ก่อนทำอย่างอื่น
- ปัญหาที่พบใหม่ ให้บันทึกต่อท้าย `docs/PROBLEM_LOG.md` พร้อมวิธีแก้
- ห้ามใช้ชื่อ `scene_class` ซ้ำกับ episode อื่น

## 10. ตัวอย่างรายการตรวจก่อนส่ง (AI checklist)

เมื่อสร้าง episode ใหม่เสร็จ ให้ตรวจว่า:

- [ ] มีครบ 5 ช่วง: hook, concept, example, summary, cta
- [ ] ใช้ `Episode` + `NarrationCue` (ไม่นิยาม dataclass เอง)
- [ ] ใช้ `slots=True` หรือไม่ — ต้องไม่มี
- [ ] ผ่าน `python cli.py validate all` (จับอัตโนมัติ: cue key ตรงกัน, จำนวน beat = จำนวน subtitle_beats, caption index อยู่ในช่วง, weight เป็นบวก, ทุก cue ถูกเล่น, build_stage ไม่มี argument, subtitle ≤ 35 ตัว, บทบรรยาย ≤ 120 ตัว + ไม่มีคำ eng ไม่มีคำอ่าน, min_duration เป็นบวก)
- [ ] ผ่าน `python -m pytest` + `python cli.py status --strict`
- [ ] ตัวเลขในเสียงตรงกับบนจอ
- [ ] สีทั้งหมดมาจาก `SETTINGS.palette`
- [ ] content อยู่ใน safe zone (กว้าง ≤ 7.8)
- [ ] ใช้ `Write` กับข้อความทั่วไป, `AddTextLetterByLetter` กับโค้ด
- [ ] preview ผ่านก่อน render final
