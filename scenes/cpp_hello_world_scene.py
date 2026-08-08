"""Scene สำหรับตอน C++ Hello World ภาษาแรก

วางไฟล์นี้ที่:
    scenes/cpp_hello_world_scene.py

โค้ดนี้ใช้ API หลักตามคู่มือ Animetion Studio v6:
- NarratedScene
- self.play_cue(...)
- beat(lambda: ...)
- SCRIPT.cue(...)

ภาพประกอบสร้างด้วย Manim มาตรฐาน เพื่อลดการผูกกับ constructor
ของ component ภายในโปรเจกต์ที่อาจแตกต่างกัน
"""

from __future__ import annotations

from manim import (
    AddTextLetterByLetter,
    AnimationGroup,
    Arrow,
    BLUE,
    Create,
    DOWN,
    FadeIn,
    GREEN,
    GrowFromCenter,
    LEFT,
    ORANGE,
    PURPLE,
    RIGHT,
    RoundedRectangle,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
    YELLOW,
)

from content.cpp_hello_world import SCRIPT
from lib.scene_base import NarratedScene
from lib.timeline import beat


FULL_CODE = (
    "#include <iostream>\n"
    "using namespace std;\n"
    "\n"
    "int main() {\n"
    '  cout << "Hello World!";\n'
    "  return 0;\n"
    "}"
)

CODE_COLORS = {
    "#include": BLUE,
    "<iostream>": YELLOW,
    "using": PURPLE,
    "namespace": PURPLE,
    "std": YELLOW,
    "int": ORANGE,
    "main()": GREEN,
    "cout": BLUE,
    '"Hello World!"': GREEN,
    "return": ORANGE,
}


class CppHelloWorldV1(NarratedScene):
    """อธิบายโครงสร้างโปรแกรม C++ แรก ด้วยโค้ด Hello World"""

    def construct(self) -> None:
        self.build_stage()

        self.show_hook()
        self.show_include()
        self.show_namespace()
        self.show_main()
        self.show_cout()
        self.show_return()
        self.show_compile()
        self.show_summary()
        self.show_question()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def make_text(
        self,
        text: str,
        *,
        size: int = 42,
        color=WHITE,
        weight: str = "NORMAL",
    ) -> Text:
        return Text(
            text,
            font_size=size,
            color=color,
            weight=weight,
        )

    def make_code(self, code: str, *, size: int = 30, color_map=None) -> Text:
        return Text(
            code,
            font="Consolas",
            font_size=size,
            color=WHITE,
            line_spacing=0.9,
            t2c=color_map or CODE_COLORS,
        )

    def make_panel(
        self,
        width: float = 6.6,
        height: float = 2.0,
        *,
        title: str | None = None,
        color=BLUE,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            stroke_width=2.5,
            color=color,
            fill_opacity=0.08,
        )
        group = VGroup(box)

        if title:
            header = self.make_text(title, size=26, color=color, weight="BOLD")
            header.next_to(box.get_top(), DOWN, buff=0.2)
            group.add(header)

        return group

    def make_badge(
        self,
        text: str,
        *,
        color=BLUE,
        width: float | None = None,
        height: float = 0.82,
        font_size: int = 25,
    ) -> VGroup:
        if width is None:
            width = max(2.6, min(4.2, 1.35 + len(text) * 0.17))

        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.15,
            color=color,
            fill_opacity=0.12,
        )
        label = self.make_text(text, size=font_size, color=color, weight="BOLD")
        label.move_to(box)
        return VGroup(box, label)

    def place_title(self, title, *, buff: float = 2.2) -> Text:
        title.to_edge(UP, buff=buff)
        return title

    def explain_line(
        self,
        code_text: str,
        badge_text: str,
        *,
        badge_color,
        code_size: int = 32,
        code_color: str | None = None,
    ) -> VGroup:
        code = self.make_code(code_text, size=code_size)
        if code_color is not None:
            code.set_color(code_color)
        panel = self.make_panel(width=6.6, height=1.7)
        code.move_to(panel[0])
        code_group = VGroup(panel, code)

        badge = self.make_badge(badge_text, color=badge_color, width=6.0)
        badge.next_to(code_group, DOWN, buff=0.5)

        arrow = Arrow(
            code_group.get_bottom(),
            badge.get_top(),
            buff=0.15,
            color=badge_color,
        )
        return VGroup(code_group, badge, arrow)

    # ------------------------------------------------------------------
    # Cues
    # ------------------------------------------------------------------

    def show_hook(self) -> None:
        cue = SCRIPT.cue("hook")

        title = self.make_text(
            "โปรแกรมแรกของคุณ",
            size=46,
            color=YELLOW,
            weight="BOLD",
        )
        self.place_title(title, buff=2.0)

        code = self.make_code(FULL_CODE, size=26)
        panel = self.make_panel(width=6.8, height=3.6, title="C++")
        code.move_to(panel[0]).shift(DOWN * 0.25)
        code_group = VGroup(panel, code)
        code_group.next_to(title, DOWN, buff=0.45)

        tagline = self.make_text(
            "รันแล้วเห็น สวัสดีชาวโลก!",
            size=30,
            color=GREEN,
            weight="BOLD",
        )
        tagline.next_to(code_group, DOWN, buff=0.4)

        group = VGroup(title, code_group, tagline)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: Write(title),
                    weight=0.8,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        FadeIn(panel),
                        AddTextLetterByLetter(code),
                        lag_ratio=0.15,
                    ),
                    weight=1.5,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: Write(tagline),
                    weight=0.9,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_include(self) -> None:
        cue = SCRIPT.cue("include")

        title = self.make_text(
            "1. นำเข้าไลบรารี",
            size=42,
            color=BLUE,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        content = self.explain_line(
            "#include <iostream>",
            "ไว้จัดการข้อมูลเข้า-ออก",
            badge_color=GREEN,
        )
        content.next_to(title, DOWN, buff=0.5)

        group = VGroup(title, content)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        FadeIn(content[0]),
                        AddTextLetterByLetter(content[0][1]),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(content[2]),
                        GrowFromCenter(content[1]),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[1],
                ),
            ),
            cleanup=group,
        )

    def show_namespace(self) -> None:
        cue = SCRIPT.cue("namespace")

        title = self.make_text(
            "2. ใช้ namespace std",
            size=42,
            color=PURPLE,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        content = self.explain_line(
            "using namespace std;",
            "พิมพ์คำสั่งโดยไม่ต้องเขียน std::",
            badge_color=YELLOW,
        )
        content.next_to(title, DOWN, buff=0.5)

        group = VGroup(title, content)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        FadeIn(content[0]),
                        AddTextLetterByLetter(content[0][1]),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(content[2]),
                        GrowFromCenter(content[1]),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[1],
                ),
            ),
            cleanup=group,
        )

    def show_main(self) -> None:
        cue = SCRIPT.cue("main")

        title = self.make_text(
            "3. จุดเริ่มต้น : main()",
            size=42,
            color=GREEN,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        content = self.explain_line(
            "int main() {",
            "โค้ดในปีกกาทำงานตามลำดับ",
            badge_color=GREEN,
        )
        content.next_to(title, DOWN, buff=0.5)

        group = VGroup(title, content)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        FadeIn(content[0]),
                        AddTextLetterByLetter(content[0][1]),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(content[2]),
                        GrowFromCenter(content[1]),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[1],
                ),
            ),
            cleanup=group,
        )

    def show_cout(self) -> None:
        cue = SCRIPT.cue("cout")

        title = self.make_text(
            "4. แสดงผลด้วย cout",
            size=42,
            color=BLUE,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        content = self.explain_line(
            'cout << "Hello World!";',
            "ส่งข้อความออกทางหน้าจอ",
            badge_color=GREEN,
            code_size=29,
        )
        content.next_to(title, DOWN, buff=0.5)

        group = VGroup(title, content)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        FadeIn(content[0]),
                        AddTextLetterByLetter(content[0][1]),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(content[2]),
                        GrowFromCenter(content[1]),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[1],
                ),
            ),
            cleanup=group,
        )

    def show_return(self) -> None:
        cue = SCRIPT.cue("return_cue")

        title = self.make_text(
            "5. จบโปรแกรม : return 0",
            size=42,
            color=ORANGE,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        content = self.explain_line(
            "return 0;",
            "คืนค่า 0 = จบปกติ",
            badge_color=ORANGE,
        )
        content.next_to(title, DOWN, buff=0.5)

        group = VGroup(title, content)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        FadeIn(content[0]),
                        AddTextLetterByLetter(content[0][1]),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(content[2]),
                        GrowFromCenter(content[1]),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[1],
                ),
            ),
            cleanup=group,
        )

    def show_compile(self) -> None:
        cue = SCRIPT.cue("compile")

        title = self.make_text(
            "คอมไพล์ แล้วก็ รัน",
            size=46,
            color=YELLOW,
            weight="BOLD",
        )
        self.place_title(title, buff=2.0)

        code = self.make_code(FULL_CODE, size=19)
        code_panel = self.make_panel(width=4.4, height=3.2, title="โปรแกรม")
        code.move_to(code_panel[0]).shift(DOWN * 0.1)
        code.scale_to_fit_width(3.9)
        left = VGroup(code_panel, code)

        output = self.make_text(
            "Hello World!",
            size=30,
            color=GREEN,
            weight="BOLD",
        )
        term_panel = self.make_panel(width=4.4, height=3.2, title="ผลลัพธ์", color=GREEN)
        output.move_to(term_panel[0])
        right = VGroup(term_panel, output)

        panels = VGroup(left, right).arrange(RIGHT, buff=0.7)
        panels.next_to(title, DOWN, buff=0.6)

        arrow = Arrow(
            left.get_right(),
            right.get_left(),
            buff=0.3,
            color=YELLOW,
        )

        done = self.make_badge("สำเร็จ!", color=GREEN)
        done.next_to(panels, DOWN, buff=0.5)

        group = VGroup(title, panels, arrow, done)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        FadeIn(code_panel),
                        AddTextLetterByLetter(code),
                        lag_ratio=0.15,
                    ),
                    weight=1.1,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(arrow),
                        FadeIn(term_panel),
                        Write(output),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: GrowFromCenter(done),
                    weight=0.8,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_summary(self) -> None:
        cue = SCRIPT.cue("summary")

        title = self.make_text(
            "จำโครงสร้างให้แม่น",
            size=46,
            color=YELLOW,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        badges = VGroup(
            self.make_badge("รวมไลบรารี iostream", color=BLUE, width=5.4),
            self.make_badge("ฟังก์ชัน main()", color=GREEN, width=4.6),
            self.make_badge("cout แสดงผล", color=ORANGE, width=4.0),
            self.make_badge("return 0 จบงาน", color=PURPLE, width=4.6),
        ).arrange(DOWN, buff=0.3)
        badges.next_to(title, DOWN, buff=0.55)

        group = VGroup(title, badges)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        GrowFromCenter(badges[0]),
                        lag_ratio=0.2,
                    ),
                    weight=0.8,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: GrowFromCenter(badges[1]),
                    weight=0.6,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: GrowFromCenter(badges[2]),
                    weight=0.6,
                    caption=cue.subtitle_beats[2],
                ),
                beat(
                    lambda: GrowFromCenter(badges[3]),
                    weight=0.6,
                    caption=cue.subtitle_beats[3],
                ),
            ),
            cleanup=group,
        )

    def show_question(self) -> None:
        cue = SCRIPT.cue("question")

        title = self.make_text(
            "คำถามท้ายคลิป",
            size=48,
            color=YELLOW,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        code = self.make_code('cout << "Hello World!";', size=27)
        panel = self.make_panel(width=7.0, height=1.55)
        code.move_to(panel[0])
        code_group = VGroup(panel, code)
        code_group.next_to(title, DOWN, buff=0.55)

        question = self.make_text(
            "ทำไมข้อความถึงโผล่บนจอ?",
            size=36,
            color=WHITE,
            weight="BOLD",
        )
        question.next_to(code_group, DOWN, buff=0.45)

        choices = VGroup(
            self.make_badge("A. cout", color=GREEN),
            self.make_badge("B. return", color=ORANGE),
            self.make_badge("C. main", color=BLUE),
        ).arrange(DOWN, buff=0.25)
        choices.next_to(question, DOWN, buff=0.4)

        group = VGroup(title, code_group, question, choices)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        FadeIn(panel),
                        AddTextLetterByLetter(code),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Write(question),
                        *(GrowFromCenter(choice) for choice in choices),
                        lag_ratio=0.18,
                    ),
                    weight=1.2,
                    caption=cue.subtitle_beats[1],
                ),
            ),
            cleanup=group,
        )
