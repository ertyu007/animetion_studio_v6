# คู่มือสร้างอนิเมชั่นใหม่ใน Animetion Studio v6

## 1. เริ่มจากสิ่งที่ต้องทำ

เมื่อจะสร้าง episode ใหม่ ให้ทำตามลำดับนี้:

1. สร้างไฟล์เนื้อหาใน `content/`
2. สร้างไฟล์ scene ใน `scenes/`
3. ลงทะเบียน episode ใน `content/registry.py`
4. ตรวจความถูกต้องด้วย `python cli.py validate all`
5. Preview ก่อน render

## 2. โครงสร้างไฟล์ที่ควรรู้

- `content/<episode>.py` — กำหนด narration, cue, subtitle และ metadata
- `scenes/<episode>.py` — กำหนดภาพและการเล่น animation
- `lib/components.py` — UI components ที่ใช้ซ้ำ เช่น CodePanel, MemoryNode, Caption
- `lib/scene_base.py` — base scene ที่จัดการ caption, progress และ play_cue
- `lib/timeline.py` — `beat(...)` และ scheduling
- `lib/motion.py` — helpers สำหรับ animation ที่ใช้บ่อย
- `lib/settings.py` — สี ขนาด ตำแหน่ง layout

## 3. กฎสำคัญของ v6

- ใช้ `play_cue()` เพื่อสลับ cue ทีละช่วง
- ใช้ `beat(lambda: ...)` เพื่อส่ง animation factory ทีละ beat
- อย่าใส่ animation ทั้ง section ใน `Succession` เดียว
- อย่าเรียก `get_run_time()` หรือ setup future objects ล่วงหน้า
- ให้สร้าง object ใน beat ที่จะใช้จริงเท่านั้น

## 4. ตัวอย่าง flow ของ scene

```python
class MyEpisodeV1(NarratedScene):
    def construct(self) -> None:
        self.build_stage(3)
        self.show_intro()
        self.show_demo()
        self.show_takeaway()
```

แต่ละฟังก์ชันควรมีโครงสร้างคล้ายนี้:

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

## 5. คำแนะนำสำหรับภาพและคำบรรยาย

- ใช้ `ThaiText` สำหรับข้อความภาษาไทย
- ใช้ `CodePanel` สำหรับโค้ด, `MemoryNode` สำหรับ object, `KeyCap` สำหรับปุ่ม/ชื่อ
- ใช้ `Caption` สำหรับ subtitle และควรปรับใน `lib/settings.py` ถ้าต้องการย้ายขึ้น/ลง
- ใช้สีจาก `SETTINGS.palette` เพื่อรักษา consistency

## 6. ตรวจและรัน

```powershell
python cli.py list
python cli.py validate all
python cli.py preview <episode>
python cli.py render <episode> --preset draft
python cli.py render <episode> --preset final
```

## 7. สิ่งที่ควรรู้ก่อนเริ่ม

- การ render ช้าและอาจใช้เวลาในตอนสร้าง video
- ควร preview ก่อน render แบบ final
- ถ้าเข้ามาใหม่ สามารถอ้างอิงโครงสร้างจากคู่มือนี้ หรือสร้างไฟล์ใหม่ใน content/ และ scenes/ ได้เลย
- ถ้าแก้ข้อความ/ตำแหน่ง ให้ตรวจที่ `lib/settings.py` และ `lib/scene_base.py` ก่อน
