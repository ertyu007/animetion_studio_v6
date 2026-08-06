# v6.0.0

- รื้อ timeline และ scene base ใหม่ทั้งหมด
- เพิ่ม deferred animation factories
- ล็อก cue duration ด้วยความยาว audio จริง
- เปลี่ยนดีไซน์เป็น Neon Blueprint
- ใช้ Write สำหรับข้อความทั่วไป และ typing เฉพาะโค้ด
- ตอนปัจจุบัน: `oop_robot_factory` และ `c_led_blink`
- เพิ่ม CLI, narration cache, validation และ tests ใหม่

## Unreleased

- เพิ่ม `status` สำหรับตรวจความพร้อมของ narration cache โดยไม่สร้างเสียง
- รองรับ `status --strict` เพื่อให้ workflow ตรวจพบ cue เสียงที่ยังขาด
- แก้ `CodePanel` ที่มี prefix ว่างให้ preview ได้ตามปกติ
- แก้ vector ของ `FadeIn` ให้ทำงานกับ Manim v0.19 ได้
- ลบ `ProgressDots` และ `set_progress()` ออกจาก scene base (`build_stage()` ไม่รับ argument)
- เพิ่ม validation: บทบรรยายไม่เกิน 120 ตัวอักษร และห้ามศัพท์ eng ≥ 4 ตัวโดยไม่มีคำอ่านไทย
- เพิ่มตอน `c_led_blink` — C ควบคุม LED เริ่มต้น
- เพิ่มตอน `c_variables` — ตัวแปรและชนิดข้อมูล ภาษา C พื้นฐาน
