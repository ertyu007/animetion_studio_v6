# v6.0.0

- รื้อ timeline และ scene base ใหม่ทั้งหมด
- เพิ่ม deferred animation factories
- ล็อก cue duration ด้วยความยาว audio จริง
- เปลี่ยนดีไซน์เป็น Neon Blueprint
- ใช้ Write สำหรับข้อความทั่วไป และ typing เฉพาะโค้ด
- เขียนใหม่ 3 ตอน: print, undo/redo และ Python variables
- เพิ่ม CLI, narration cache, validation และ tests ใหม่

## Unreleased

- เพิ่ม `status` สำหรับตรวจความพร้อมของ narration cache โดยไม่สร้างเสียง
- รองรับ `status --strict` เพื่อให้ workflow ตรวจพบ cue เสียงที่ยังขาด
- แก้ `CodePanel` ที่มี prefix ว่างให้ preview ได้ตามปกติ
- แก้ vector ของ `FadeIn` ให้ทำงานกับ Manim v0.19 ได้
