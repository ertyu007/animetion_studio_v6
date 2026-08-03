"""Scene สำหรับตอน OOP เข้าใจง่ายด้วยโรงงานหุ่นยนต์

วางไฟล์นี้ที่:
    scenes/oop_robot_factory.py

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
    Circle,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    GREEN,
    GrowFromCenter,
    LEFT,
    Line,
    ORANGE,
    RED,
    RIGHT,
    RoundedRectangle,
    Square,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
    YELLOW,
)

from content.oop_robot_factory import SCRIPT
from lib.scene_base import NarratedScene
from lib.timeline import beat


class OOPRobotFactoryV1(NarratedScene):
    """อธิบาย OOP ด้วยภาพโรงงานผลิตหุ่นยนต์"""

    def construct(self) -> None:
        self.build_stage(11)

        self.show_hook()
        self.show_oop_intro()
        self.show_class()
        self.show_object()
        self.show_attribute()
        self.show_method()
        self.show_encapsulation()
        self.show_inheritance()
        self.show_polymorphism()
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

    def make_code(self, code: str, *, size: int = 28) -> Text:
        return Text(
            code,
            font="Consolas",
            font_size=size,
            color=WHITE,
            line_spacing=0.9,
        )

    def make_panel(
        self,
        width: float = 6.4,
        height: float = 4.2,
        *,
        title: str | None = None,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            stroke_width=2.5,
            color=BLUE,
            fill_opacity=0.08,
        )
        group = VGroup(box)

        if title:
            header = self.make_text(title, size=26, color=BLUE, weight="BOLD")
            header.next_to(box.get_top(), DOWN, buff=0.22)
            group.add(header)

        return group

    def make_robot(
        self,
        name: str,
        *,
        battery: int = 100,
        scale: float = 1.0,
    ) -> VGroup:
        head = RoundedRectangle(
            width=1.45,
            height=1.05,
            corner_radius=0.18,
            color=BLUE,
            fill_opacity=0.16,
        )
        left_eye = Circle(radius=0.08, color=GREEN, fill_opacity=1)
        right_eye = left_eye.copy()
        eyes = VGroup(left_eye, right_eye).arrange(RIGHT, buff=0.35)
        eyes.move_to(head)

        mouth = Line(LEFT * 0.24, RIGHT * 0.24, color=WHITE)
        mouth.next_to(eyes, DOWN, buff=0.18)

        body = RoundedRectangle(
            width=1.7,
            height=1.45,
            corner_radius=0.15,
            color=BLUE,
            fill_opacity=0.12,
        )
        body.next_to(head, DOWN, buff=0.12)

        battery_box = RoundedRectangle(
            width=1.15,
            height=0.36,
            corner_radius=0.08,
            color=GREEN if battery >= 50 else ORANGE,
            fill_opacity=0.18,
        )
        battery_text = self.make_text(f"{battery}%", size=20)
        battery_group = VGroup(battery_box, battery_text)
        battery_text.move_to(battery_box)
        battery_group.move_to(body)

        antenna = Line(head.get_top(), head.get_top() + UP * 0.38, color=BLUE)
        antenna_tip = Circle(radius=0.08, color=YELLOW, fill_opacity=1)
        antenna_tip.move_to(antenna.get_end())

        left_arm = Line(body.get_left(), body.get_left() + LEFT * 0.55, color=BLUE)
        right_arm = Line(body.get_right(), body.get_right() + RIGHT * 0.55, color=BLUE)

        left_leg = Line(
            body.get_bottom() + LEFT * 0.42,
            body.get_bottom() + LEFT * 0.42 + DOWN * 0.5,
            color=BLUE,
        )
        right_leg = Line(
            body.get_bottom() + RIGHT * 0.42,
            body.get_bottom() + RIGHT * 0.42 + DOWN * 0.5,
            color=BLUE,
        )

        label = self.make_text(name, size=24, color=YELLOW, weight="BOLD")
        label.next_to(body, DOWN, buff=0.66)

        robot = VGroup(
            head,
            eyes,
            mouth,
            body,
            battery_group,
            antenna,
            antenna_tip,
            left_arm,
            right_arm,
            left_leg,
            right_leg,
            label,
        )
        robot.scale(scale)
        return robot

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

    def place_title(self, title, *, buff: float = 2.7) -> Text:
        title.to_edge(UP, buff=buff)
        return title

    # ------------------------------------------------------------------
    # Cues
    # ------------------------------------------------------------------

    def show_hook(self) -> None:
        cue = SCRIPT.cue("hook")

        title = self.make_text(
            "ถ้าเกมมีหุ่นยนต์ 100 ตัว?",
            size=46,
            color=YELLOW,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        code = self.make_code(
            'robot1_name = "บี๊บ"\n'
            "robot1_battery = 100\n"
            'robot2_name = "บ๊อบ"\n'
            "robot2_battery = 80\n"
            'robot3_name = "บูม"\n'
            "robot3_battery = 60",
            size=25,
        )
        panel = self.make_panel(title="ตัวแปรที่เพิ่มขึ้นเรื่อย ๆ")
        code.move_to(panel[0]).shift(DOWN * 0.2)
        code_group = VGroup(panel, code)
        code_group.next_to(title, DOWN, buff=0.5)

        warning = self.make_text(
            "โค้ดยาว • แก้ยาก • ผิดพลาดง่าย",
            size=31,
            color=RED,
            weight="BOLD",
        )
        warning.next_to(code_group, DOWN, buff=0.45)

        group = VGroup(title, code_group, warning)

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
                        FadeIn(panel, shift=UP * 0.15),
                        AddTextLetterByLetter(code),
                        lag_ratio=0.15,
                    ),
                    weight=1.5,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: Write(warning),
                    weight=0.9,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_oop_intro(self) -> None:
        cue = SCRIPT.cue("oop_intro")

        oop = self.make_text("OOP", size=92, color=BLUE, weight="BOLD")
        full = self.make_text(
            "Object-Oriented Programming",
            size=27,
            color=WHITE,
        )
        full.next_to(oop, DOWN, buff=0.22)

        object_card = self.make_badge("OBJECT", color=GREEN)
        data_card = self.make_badge("DATA", color=YELLOW)
        action_card = self.make_badge("ACTION", color=ORANGE)
        cards = VGroup(object_card, data_card, action_card).arrange(
            DOWN,
            buff=0.28,
        )
        cards.next_to(full, DOWN, buff=0.65)

        group = VGroup(oop, full, cards)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: Write(oop),
                    weight=0.8,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: Write(full),
                    weight=0.7,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AnimationGroup(
                        *(GrowFromCenter(card) for card in cards),
                        lag_ratio=0.25,
                    ),
                    weight=1.1,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_class(self) -> None:
        cue = SCRIPT.cue("class")

        title = self.make_text(
            "CLASS = พิมพ์เขียว",
            size=45,
            color=BLUE,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        blueprint = self.make_panel(
            width=6.3,
            height=5.0,
            title="class Robot",
        )
        robot_outline = self.make_robot("ต้นแบบ", battery=100, scale=0.82)
        robot_outline.move_to(blueprint[0]).shift(LEFT * 1.35 + DOWN * 0.2)

        specs = self.make_code(
            "name\nbattery\n\nwalk()\ncharge()",
            size=29,
        )
        specs.move_to(blueprint[0]).shift(RIGHT * 1.45 + DOWN * 0.18)

        divider = Line(
            blueprint[0].get_top() + DOWN * 0.75,
            blueprint[0].get_bottom() + UP * 0.35,
            color=BLUE,
        )

        blueprint_group = VGroup(blueprint, robot_outline, specs, divider)
        blueprint_group.next_to(title, DOWN, buff=0.45)

        group = VGroup(title, blueprint_group)

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
                        FadeIn(blueprint),
                        Create(divider),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AnimationGroup(
                        GrowFromCenter(robot_outline),
                        AddTextLetterByLetter(specs),
                        lag_ratio=0.25,
                    ),
                    weight=1.3,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_object(self) -> None:
        cue = SCRIPT.cue("object")

        title = self.make_text(
            "OBJECT = หุ่นยนต์ที่สร้างจริง",
            size=42,
            color=GREEN,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        factory = self.make_badge("class Robot", color=BLUE)
        factory.next_to(title, DOWN, buff=0.55)

        robot_a = self.make_robot("บี๊บ", battery=100, scale=0.72)
        robot_b = self.make_robot("บ๊อบ", battery=60, scale=0.72)
        robots = VGroup(robot_a, robot_b).arrange(RIGHT, buff=1.05)
        robots.next_to(factory, DOWN, buff=0.65)

        arrow_a = Arrow(
            factory.get_bottom(),
            robot_a.get_top(),
            buff=0.18,
            color=BLUE,
        )
        arrow_b = Arrow(
            factory.get_bottom(),
            robot_b.get_top(),
            buff=0.18,
            color=BLUE,
        )

        code = self.make_code(
            'robot_a = Robot("บี๊บ", 100)\n'
            'robot_b = Robot("บ๊อบ", 60)',
            size=24,
        )
        code.next_to(robots, DOWN, buff=0.5)

        group = VGroup(title, factory, robots, arrow_a, arrow_b, code)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        GrowFromCenter(factory),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(arrow_a),
                        Create(arrow_b),
                        GrowFromCenter(robot_a),
                        GrowFromCenter(robot_b),
                        lag_ratio=0.18,
                    ),
                    weight=1.25,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AddTextLetterByLetter(code),
                    weight=1.0,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_attribute(self) -> None:
        cue = SCRIPT.cue("attribute")

        title = self.make_text(
            "ATTRIBUTE = ข้อมูลของ Object",
            size=41,
            color=YELLOW,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        robot = self.make_robot("บี๊บ", battery=100, scale=0.78)
        robot.shift(LEFT * 1.55 + DOWN * 0.2)

        name_box = self.make_badge('name = "บี๊บ"', color=YELLOW)
        battery_box = self.make_badge("battery = 100", color=GREEN)
        attrs = VGroup(name_box, battery_box).arrange(DOWN, buff=0.35)
        attrs.shift(RIGHT * 1.55 + DOWN * 0.15)

        name_arrow = Arrow(
            robot.get_right(),
            name_box.get_left(),
            buff=0.15,
            color=YELLOW,
        )
        battery_arrow = Arrow(
            robot.get_right() + DOWN * 0.7,
            battery_box.get_left(),
            buff=0.15,
            color=GREEN,
        )

        group = VGroup(
            title,
            robot,
            attrs,
            name_arrow,
            battery_arrow,
        )

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        GrowFromCenter(robot),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(name_arrow),
                        GrowFromCenter(name_box),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(battery_arrow),
                        GrowFromCenter(battery_box),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_method(self) -> None:
        cue = SCRIPT.cue("method")

        title = self.make_text(
            "METHOD = สิ่งที่ Object ทำได้",
            size=41,
            color=ORANGE,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        code = self.make_code("robot_a.walk()", size=34)
        code.next_to(title, DOWN, buff=0.48)

        robot = self.make_robot("บี๊บ", battery=100, scale=0.8)
        robot.next_to(code, DOWN, buff=0.5).shift(LEFT * 1.4)

        destination = Square(
            side_length=0.72,
            color=GREEN,
            fill_opacity=0.15,
        )
        destination.shift(RIGHT * 2.2 + DOWN * 1.4)

        path = Line(
            robot.get_right(),
            destination.get_left(),
            color=ORANGE,
            stroke_width=4,
        )

        output = self.make_text(
            "บี๊บ กำลังเดิน",
            size=29,
            color=GREEN,
            weight="BOLD",
        )
        output.next_to(destination, DOWN, buff=0.35)

        group = VGroup(title, code, robot, destination, path, output)

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
                        AddTextLetterByLetter(code),
                        GrowFromCenter(robot),
                        lag_ratio=0.25,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(path),
                        robot.animate.shift(RIGHT * 2.5),
                        GrowFromCenter(destination),
                        Write(output),
                        lag_ratio=0.18,
                    ),
                    weight=1.35,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_encapsulation(self) -> None:
        cue = SCRIPT.cue("encapsulation")

        title = self.make_text(
            "ENCAPSULATION = ป้องกันข้อมูล",
            size=39,
            color=GREEN,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        robot = self.make_robot("บี๊บ", battery=100, scale=0.72)
        robot.shift(LEFT * 1.65 + DOWN * 0.25)

        bad_code = self.make_code("robot.__battery = -500", size=25)
        bad_code.shift(RIGHT * 1.25 + UP * 0.3)

        cross_a = Line(
            bad_code.get_corner(LEFT + UP),
            bad_code.get_corner(RIGHT + DOWN),
            color=RED,
            stroke_width=6,
        )
        cross_b = Line(
            bad_code.get_corner(RIGHT + UP),
            bad_code.get_corner(LEFT + DOWN),
            color=RED,
            stroke_width=6,
        )

        shield = Circle(
            radius=1.2,
            color=GREEN,
            stroke_width=7,
            fill_opacity=0.08,
        )
        shield.move_to(robot).shift(UP * 0.15)

        safe_code = self.make_code(
            "robot.charge(20)\n# Method ตรวจสอบค่าก่อน",
            size=24,
        )
        safe_code.shift(RIGHT * 1.3 + DOWN * 1.1)

        group = VGroup(
            title,
            robot,
            bad_code,
            cross_a,
            cross_b,
            shield,
            safe_code,
        )

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        GrowFromCenter(robot),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        AddTextLetterByLetter(bad_code),
                        Create(cross_a),
                        Create(cross_b),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(shield),
                        AddTextLetterByLetter(safe_code),
                        lag_ratio=0.22,
                    ),
                    weight=1.15,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_inheritance(self) -> None:
        cue = SCRIPT.cue("inheritance")

        title = self.make_text(
            "INHERITANCE = นำของเดิมมาต่อยอด",
            size=38,
            color=BLUE,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        parent = self.make_badge("Robot", color=BLUE, width=2.5, font_size=24)
        child_a = self.make_badge("CleaningRobot", color=GREEN, width=3.7, font_size=24)
        child_b = self.make_badge("GuardRobot", color=ORANGE, width=3.3, font_size=24)

        parent.next_to(title, DOWN, buff=0.72)

        children = VGroup(child_a, child_b).arrange(RIGHT, buff=0.85)
        children.next_to(parent, DOWN, buff=1.15)

        line_a = Arrow(
            parent.get_bottom() + LEFT * 0.35,
            child_a.get_top() + UP * 0.02,
            buff=0.14,
            color=BLUE,
            stroke_width=5,
        )
        line_b = Arrow(
            parent.get_bottom() + RIGHT * 0.35,
            child_b.get_top() + UP * 0.02,
            buff=0.14,
            color=BLUE,
            stroke_width=5,
        )

        inherited = self.make_text(
            "รับ name • battery • walk()",
            size=27,
            color=WHITE,
        )
        extra = self.make_text(
            "เพิ่ม clean() หรือ patrol()",
            size=29,
            color=YELLOW,
            weight="BOLD",
        )

        info = VGroup(inherited, extra).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        info.next_to(children, DOWN, buff=0.6)
        info.align_to(children, LEFT)
        info.shift(RIGHT * 0.25)

        content = VGroup(parent, children, line_a, line_b, info)
        content.shift(DOWN * 0.22)

        group = VGroup(title, content)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        GrowFromCenter(parent),
                        lag_ratio=0.2,
                    ),
                    weight=0.9,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Create(line_a),
                        Create(line_b),
                        GrowFromCenter(child_a),
                        GrowFromCenter(child_b),
                        lag_ratio=0.18,
                    ),
                    weight=1.2,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AnimationGroup(
                        Write(inherited),
                        Write(extra),
                        lag_ratio=0.25,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_polymorphism(self) -> None:
        cue = SCRIPT.cue("polymorphism")

        title = self.make_text(
            "POLYMORPHISM",
            size=48,
            color=YELLOW,
            weight="BOLD",
        )
        subtitle = self.make_text(
            "คำสั่งเดียว แต่ผลลัพธ์ต่างกัน",
            size=30,
            color=WHITE,
        )
        subtitle.next_to(title, DOWN, buff=0.18)
        heading = VGroup(title, subtitle)
        self.place_title(heading, buff=2.1)

        command = self.make_code("robot.work()", size=34)
        command.next_to(heading, DOWN, buff=0.48)

        clean_robot = self.make_robot("Cleaner", battery=90, scale=0.58)
        guard_robot = self.make_robot("Guard", battery=90, scale=0.58)
        robots = VGroup(clean_robot, guard_robot).arrange(RIGHT, buff=1.05)
        robots.next_to(command, DOWN, buff=0.5)

        clean_result = self.make_text(
            "กวาดพื้น",
            size=27,
            color=GREEN,
            weight="BOLD",
        )
        guard_result = self.make_text(
            "ตรวจตรา",
            size=27,
            color=ORANGE,
            weight="BOLD",
        )
        clean_result.next_to(clean_robot, DOWN, buff=0.35)
        guard_result.next_to(guard_robot, DOWN, buff=0.35)

        arrow_a = Arrow(
            command.get_bottom(),
            clean_robot.get_top(),
            buff=0.15,
            color=YELLOW,
        )
        arrow_b = Arrow(
            command.get_bottom(),
            guard_robot.get_top(),
            buff=0.15,
            color=YELLOW,
        )

        group = VGroup(
            heading,
            command,
            robots,
            clean_result,
            guard_result,
            arrow_a,
            arrow_b,
        )

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        Write(subtitle),
                        lag_ratio=0.2,
                    ),
                    weight=0.85,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        AddTextLetterByLetter(command),
                        Create(arrow_a),
                        Create(arrow_b),
                        lag_ratio=0.2,
                    ),
                    weight=1.0,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: AnimationGroup(
                        GrowFromCenter(clean_robot),
                        GrowFromCenter(guard_robot),
                        Write(clean_result),
                        Write(guard_result),
                        lag_ratio=0.18,
                    ),
                    weight=1.25,
                    caption=cue.subtitle_beats[2],
                ),
            ),
            cleanup=group,
        )

    def show_summary(self) -> None:
        cue = SCRIPT.cue("summary")

        title = self.make_text(
            "จำ OOP ให้ได้ใน 4 คำ",
            size=46,
            color=YELLOW,
            weight="BOLD",
        )
        self.place_title(title, buff=2.2)

        class_card = self.make_badge("Class = แม่พิมพ์", color=BLUE)
        object_card = self.make_badge("Object = ของจริง", color=GREEN)
        attr_card = self.make_badge("Attribute = ข้อมูล", color=YELLOW)
        method_card = self.make_badge("Method = ความสามารถ", color=ORANGE)

        cards = VGroup(
            class_card,
            object_card,
            attr_card,
            method_card,
        ).arrange(DOWN, buff=0.32)
        cards.next_to(title, DOWN, buff=0.55)

        group = VGroup(title, cards)

        self.play_cue(
            cue,
            (
                beat(
                    lambda: AnimationGroup(
                        Write(title),
                        GrowFromCenter(class_card),
                        lag_ratio=0.2,
                    ),
                    weight=0.8,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: GrowFromCenter(object_card),
                    weight=0.65,
                    caption=cue.subtitle_beats[1],
                ),
                beat(
                    lambda: GrowFromCenter(attr_card),
                    weight=0.65,
                    caption=cue.subtitle_beats[2],
                ),
                beat(
                    lambda: GrowFromCenter(method_card),
                    weight=0.65,
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
        self.place_title(title, buff=2.3)

        code = self.make_code(
            'robot_a = Robot("บี๊บ", 100)',
            size=29,
        )
        panel = self.make_panel(width=6.5, height=1.45)
        code.move_to(panel[0])
        code_group = VGroup(panel, code)
        code_group.next_to(title, DOWN, buff=0.62)

        question = self.make_text(
            "robot_a คืออะไร?",
            size=42,
            color=WHITE,
            weight="BOLD",
        )
        question.next_to(code_group, DOWN, buff=0.55)

        choices = VGroup(
            self.make_badge("A. Class", color=BLUE),
            self.make_badge("B. Object", color=GREEN),
            self.make_badge("C. Method", color=ORANGE),
        ).arrange(DOWN, buff=0.25)
        choices.next_to(question, DOWN, buff=0.45)

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
                    weight=1.05,
                    caption=cue.subtitle_beats[0],
                ),
                beat(
                    lambda: AnimationGroup(
                        Write(question),
                        *(GrowFromCenter(choice) for choice in choices),
                        lag_ratio=0.18,
                    ),
                    weight=1.25,
                    caption=cue.subtitle_beats[1],
                ),
            ),
            cleanup=group,
        )
