# V6 Validation Report

วันที่ตรวจ: 2026-08-03

## ผ่าน

- Python compile ทั้งโปรเจกต์
- Pytest: 28/28
- Registry: 3 episodes (`oop_robot_factory`, `c_led_blink`, `c_variables`)
- Scene class และ scene path ถูกต้อง
- Subtitle highlight markup ถูกต้อง
- ไม่มี `VisualPlan`
- ไม่มี manual animation runtime introspection
- ไม่มี opacity pre-hide workaround
- ไม่มี legacy `narration_beats`
- Scene ทุกตอนไปผ่าน `play_cue()` และ deferred `beat(lambda: ...)`
- `validate all` ไม่พบ issues (รวมกฎใหม่: บทบรรยาย ≤ 120 ตัว, ไม่มีศัพท์ eng ไม่มีคำอ่าน, `build_stage()` ไม่มี argument)

## ยืนยันแล้วใน environment นี้

- การ render MP4 จริง (smoke preview 360×640 ผ่าน)
- Edge TTS audio generation จริง (narration cache ครบทุก cue)

## ยังไม่ได้ยืนยัน

- รูปทรง glyph ของฟอนต์ภาษาไทยบนเครื่องผู้ใช้ (ตรวจ final render บนเครื่องจริงก่อนเผยแพร่)
