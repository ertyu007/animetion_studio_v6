# v6 Architecture

## 1. Deferred beats

Scene ประกาศ beat แบบนี้:

```python
beat(lambda: reveal_card(card), weight=1.0, caption="แสดง [[การ์ด]]")
```

`lambda` ยังไม่สร้าง Animation จนกว่า `play_cue()` จะเดินมาถึง beat นั้น จึงไม่มี future object เข้า Manim setup ก่อนเวลา

## 2. Audio-owned timing

`EdgeTTSRenderer` อ่านความยาว MP3 จริงผ่าน Mutagen แล้วส่งเวลาให้ `make_schedule()`

เวลารวมของ cue คือ:

```text
lead + sum(beat durations) + cleanup + tail = narration duration
```

`play_cue()` ส่ง `run_time` ให้ `Scene.play()` โดยตรง ไม่อ่าน natural runtime จาก animation และไม่แตะ internals ของ `_AnimationBuilder`

## 3. Caption lifecycle

CaptionController มี caption ปัจจุบันเพียงหนึ่งชุด:

- ลบ caption เก่า
- สร้าง caption ของวลีปัจจุบัน
- เพิ่มเป็น foreground
- ไม่สร้างวลีในอนาคตไว้ล่วงหน้า

- Stroke & Contrast: `ThaiText` ใช้ `stroke_width=0.8` และ `stroke_color` เพื่ออ่านง่ายไม่กลืนกับพื้นหลัง
- TikTok Safe-Zone & Credit: `caption_y` ตั้งไว้ที่ `-3.20` เพื่อหลบ TikTok UI และมีเครดิต `@ertyu0075` มุมขวาของจอ
- Motion: `.animate.move_to(...)` ถูกส่งตรงเข้า `Scene.play()` ตอนถึงคิว

## 5. Static validation

Validator ตรวจ:

- scene path ต้องอยู่ใน project root
- scene file ต้อง parse ได้
- scene class ต้องมีจริง
- cue key ห้ามซ้ำ
- highlight markup ต้องสมดุล
- ห้ามใช้ legacy timing/spoiler APIs ใน scene
