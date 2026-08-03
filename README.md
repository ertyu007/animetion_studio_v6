# Animetion Studio v6

โปรเจกต์ Manim แนวตั้ง 9:16 สำหรับ motion graphic อธิบายเทคโนโลยี พร้อมเสียงบรรยายภาษาไทย

## สิ่งที่ออกแบบใหม่

- ดีไซน์ **Neon Blueprint**: พื้นหลังกริดเข้ม การ์ดเส้นเรือง caption แถบเดียว และ progress dots
- ข้อความทั่วไปใช้ `Write` เพื่อวาด stroke ของ glyph
- โค้ดและ terminal ใช้ `AddTextLetterByLetter` เท่านั้น
- ไม่มี `VisualPlan`, `narration_beats`, `prepare_for_reveal` หรือการเรียก `get_run_time()`
- ทุก animation เป็น factory เช่น `beat(lambda: reveal_card(card))`
- factory จะถูกเรียกเมื่อถึงคิวจริง จึงไม่มี animation ของอนาคตถูก setup ล่วงหน้า
- `Scene.play(..., run_time=allocated_duration)` ล็อกเวลาภาพตามความยาว MP3 จริง
- caption ถูกสร้างเฉพาะวลีปัจจุบัน และถูกลบทันทีเมื่อเปลี่ยนวลี

## ตอนที่มีในโปรเจกต์

- `oop_robot_factory` — OOP คืออะไร? เข้าใจด้วยโรงงานหุ่นยนต์

## ติดตั้งบน Windows PowerShell

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

## ตรวจโปรเจกต์

```powershell
# แสดงรายการ episode ที่ใช้งานได้
python cli.py list

# ตรวจโครงสร้าง, scene และเนื้อหาทั้งโปรเจกต์
python cli.py validate all

# รัน regression tests
python -m pytest
```

## สร้างเสียง

```powershell
python cli.py audio all
```

บังคับสร้างเสียงใหม่หลังแก้บทพูด:

```powershell
python cli.py audio all --force
```

ตรวจว่ามีไฟล์เสียงพร้อม render ครบหรือไม่ โดยไม่สร้างไฟล์เพิ่ม:

```powershell
python cli.py status
python cli.py status undo_redo --strict
```

`--strict` จะคืน exit code `1` หากยังมีเสียงที่ขาดอยู่ จึงใช้ตรวจใน workflow อัตโนมัติได้

## Preview

```powershell
python cli.py preview oop_robot_factory
```

Preview ใช้ 360×640 ที่ 24 FPS

Preview โดยไม่สร้างหรือใช้เสียงจริง (เหมาะสำหรับตรวจ layout และ motion):

```powershell
$env:ANIMETION_TTS = "off"
python cli.py preview oop_robot_factory
Remove-Item Env:ANIMETION_TTS
```

## Render

```powershell
# ตรวจจังหวะและ layout ที่ 540×960 ก่อน
python cli.py render oop_robot_factory --preset draft

# สร้างไฟล์ final สำหรับ TikTok ที่ 1080×1920 / 60 FPS
python cli.py render oop_robot_factory --preset final
```

Final ใช้ 1080×1920 ที่ 60 FPS

## Workflow แนะนำ

```powershell
python cli.py list
python cli.py validate all
python cli.py audio all
python cli.py status --strict
python cli.py preview oop_robot_factory
python cli.py render oop_robot_factory --preset draft
python cli.py render oop_robot_factory --preset final
```

## ล้างไฟล์ที่สร้าง

```powershell
# ลบเฉพาะไฟล์ render และ preview
python cli.py clean media

# ลบเฉพาะ narration cache
python cli.py clean narration

# ลบทั้งสองส่วน
python cli.py clean all
```

`clean` ลบไฟล์ใน `.build`, `media` และ/หรือ `.cache/narration` ตาม target ที่เลือก

## เพิ่มตอนใหม่

1. เพิ่มบทใน `content/<episode>.py`
2. เพิ่ม scene ใน `scenes/<episode>.py`
3. ลงทะเบียนใน `content/registry.py`
4. ใช้ `play_cue()` และ `beat(lambda: ...)` เท่านั้น
5. รัน `python cli.py validate all` ก่อน render

### ลงทะเบียน episode ใหม่ให้ CLI รู้จัก

ถ้าต้องการให้ episode ใหม่แสดงในคำสั่ง `list`, `preview`, `render` ต้องเพิ่มลงใน [content/registry.py](content/registry.py) โดยทำ 2 ขั้นตอน:

```python
from content.oop_robot_factory import SCRIPT as `OOP_ROBOT_FACTORY`
```

แล้วใส่ไว้ใน `EPISODES`:

```python
EPISODES = {
    episode.key: episode
    for episode in (OOP_ROBOT_FACTORY, MY_EPISODE)
}
```

หลังจากแก้แล้วให้รัน:

```powershell
python cli.py list
```

ถ้า episode ใหม่ขึ้นในรายการ แปลว่าลงทะเบียนสำเร็จแล้ว

สำหรับขั้นตอนแบบละเอียดและสิ่งที่ควรรู้ก่อนเริ่มสร้างอนิเมชั่นใหม่ ดูไฟล์ [docs/new-animation-workflow.md](docs/new-animation-workflow.md)

### สิ่งที่ควรรู้เมื่อสร้างอนิเมชั่นใหม่

- โครงสร้างหลักคือ `content/` สำหรับ narration + cue และ `scenes/` สำหรับภาพและ animation
- ภาพ UI ที่ใช้ซ้ำควรสร้างจาก `lib/components.py`
- ตำแหน่งและสีควรปรับจาก `lib/settings.py`
- อย่าใช้ animation ทั้ง section ในก้อนเดียว ให้ใช้ `beat(...)` แบบทีละช่วง
- Preview ก่อน render final เสมอ เพื่อตรวจ layout และ timing

## กฎสำคัญ

อย่าสร้าง animation ทั้ง section แล้วรวมไว้ใน `Succession` ก้อนเดียว เพราะ Manim อาจ setup target ของอนาคตล่วงหน้า ให้ส่ง animation factory ทีละ beat ผ่านระบบ v6 แทน
