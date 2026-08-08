"""บทบรรยายและ cue สำหรับตอน C++ Hello World ภาษาแรกของใครหลายคน.

วางไฟล์นี้ที่:
    content/cpp_hello_world.py

หมายเหตุ:
- ใช้ model มาตรฐานของโปรเจกต์: Episode (content.models) และ NarrationCue (lib.narration)
- SCRIPT.cue("ชื่อ_cue") ใช้งานได้ทันที
"""

from __future__ import annotations

from content.models import Episode
from lib.narration import NarrationCue


SCRIPT = Episode(
    key="cpp_hello_world",
    title="ภาษา C++ เริ่มต้น เขียน Hello World ตัวแรก",
    scene_file="scenes/cpp_hello_world_scene.py",
    scene_class="CppHelloWorldV1",
    tags=(
        "#C++",
        "#เริ่มเรียนเขียนโปรแกรม",
        "#CodingThailand",
        "#โปรแกรมมิ่ง",
        "#เรียนเขียนโค้ด",
    ),
    cues=(
        NarrationCue(
            key="hook",
            text=(
                "ขอต้อนรับสู่ภาษา ซีพลัสพลัส โปรแกรมแรกคือการแสดงคำว่า สวัสดีชาวโลก "
                "แล้วรันให้มันทำงานออกมาบนหน้าจอ"
            ),
            subtitle_beats=(
                "ภาษา C++ ภาษาแรก",
                "พิมพ์โค้ดสั้นๆ ชุดนี้",
                "รันแล้วเห็น สวัสดีชาวโลก!",
            ),
        ),
        NarrationCue(
            key="include",
            text=(
                "บรรทัดแรกคือการรวมไลบรารี ไอโอสตรีม "
                "ซึ่งจัดการข้อมูลเข้าและแสดงผลออกทางหน้าจอ"
            ),
            subtitle_beats=(
                "นำเข้าไลบรารี iostream",
                "จัดการข้อมูลเข้า-ออก",
            ),
        ),
        NarrationCue(
            key="namespace",
            text=(
                "บรรทัดต่อมาคือ เนมสเปซ เอสทีดี "
                "เพื่อให้ใช้คำสั่งได้โดยไม่ต้องเขียนคำนำหน้าซ้ำทุกครั้ง"
            ),
            subtitle_beats=(
                "ใช้ namespace std",
                "พิมพ์คำสั่งได้สั้นลง",
            ),
        ),
        NarrationCue(
            key="main",
            text=(
                "ฟังก์ชันหลักชื่อ เมน คือจุดเริ่มต้นของโปรแกรม "
                "โค้ดที่อยู่ภายในปีกกาจะทำงานตามลำดับเมื่อรัน"
            ),
            subtitle_beats=(
                "int main() จุดเริ่มต้น",
                "โค้ดในปีกกาทำงานตามลำดับ",
            ),
        ),
        NarrationCue(
            key="cout",
            text=(
                "คำสั่ง ซีเอ้าท์ ใช้แสดงข้อความออกทางหน้าจอ "
                "โดยใช้เครื่องหมายสองอันชี้ไปยังข้อความที่ต้องการ"
            ),
            subtitle_beats=(
                "cout แสดงข้อความออกจอ",
                "<< ชี้ไปที่ข้อความ",
            ),
        ),
        NarrationCue(
            key="return_cue",
            text=(
                "คำสั่ง รีเทิร์น ศูนย์ คือการคืนค่าให้ระบบ "
                "บอกว่าโปรแกรมจบการทำงานอย่างปกติ"
            ),
            subtitle_beats=(
                "return 0 จบปกติ",
                "คืนค่า 0 = สำเร็จ",
            ),
        ),
        NarrationCue(
            key="compile",
            text=(
                "ขั้นต่อไปต้องแปลงโค้ดให้เป็นภาษาเครื่อง "
                "เรียกว่าการคอมไพล์ แล้วค่อยรันดูผลลัพธ์บนหน้าจอ"
            ),
            subtitle_beats=(
                "คอมไพล์โค้ดก่อน",
                "รันไฟล์โปรแกรม",
                "เห็น Hello World! บนจอ",
            ),
        ),
        NarrationCue(
            key="summary",
            text=(
                "สรุปโปรแกรมนี้ประกอบด้วย การรวมไลบรารี ฟังก์ชันหลัก "
                "คำสั่งแสดงผล และการคืนค่าให้ระบบ"
            ),
            subtitle_beats=(
                "รวมไลบรารี",
                "ฟังก์ชัน main()",
                "cout แสดงผล",
                "return 0 จบงาน",
            ),
        ),
        NarrationCue(
            key="question",
            text=(
                "คำถามทิ้งท้าย คำสั่งใดที่ทำให้ข้อความปรากฏบนหน้าจอ "
                "รู้แล้วตอบได้เลย"
            ),
            subtitle_beats=(
                "ข้อความโผล่จอเพราะอะไร?",
                "cout, return หรือ main",
            ),
        ),
    ),
)
