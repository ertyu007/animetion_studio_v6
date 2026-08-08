"""บทบรรยายและ cue สำหรับตอน Pointer คืออะไร ทำไมต้องใช้."""

from __future__ import annotations

from content.models import Episode
from lib.narration import NarrationCue


SCRIPT = Episode(
    key="pointer_deref",
    title="Pointer คืออะไร ทำไมต้องใช้",
    scene_file="scenes/pointer_deref_scene.py",
    scene_class="PointerDerefV1",
    tags=('#CProgramming', '#พอยน์เตอร์', '#เขียนโปรแกรม'),
    cues=(
        NarrationCue(
            key="hook",
            text='ทำไมต้องใช้พอยน์เตอร์ใน C',
            subtitle_beats=('เขียน C ไม่รู้พอยน์เตอร์ ติดขัดแน่', 'เรียนต่อไม่ต้องใช้พอยน์เตอร์'),
        ),
        NarrationCue(
            key="concept",
            text='พอยน์เตอร์คือที่จัดเก็บที่อยู่ของข้อมูล',
            subtitle_beats=('พอยน์เตอร์คือที่อยู่ของข้อมูล', 'ช่วยจัดการข้อมูลได้ดีขึ้น'),
        ),
        NarrationCue(
            key="example",
            text='สั่งซื้อของออนไลน์ ใช้พอยน์เตอร์บอกที่อยู่ของสินค้า',
            subtitle_beats=('สั่งของออนไลน์ ใช้พอยน์เตอร์บอกที่อ', 'จัดการข้อมูลได้เร็วขึ้น'),
        ),
        NarrationCue(
            key="summary",
            text='พอยน์เตอร์ช่วยจัดการข้อมูลได้ดีขึ้น',
            subtitle_beats=('พอยน์เตอร์ช่วยจัดการข้อมูลได้ดี', 'เรียน C ต้องรู้พอยน์เตอร์'),
        ),
        NarrationCue(
            key="cta",
            text='กดติดตามดูตอนต่อไป',
            subtitle_beats=('กดติดตามดูตอนต่อไป', 'เรียน C ไม่ติดขัด'),
        ),
    ),
)
