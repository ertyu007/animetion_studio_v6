"""Narration-synced scene base with deferred, sequential animation beats."""

from __future__ import annotations

import logging
from typing import Iterable, Optional

from manim import FadeOut, Mobject, MovingCameraScene, UL, VGroup, LEFT, RIGHT, DOWN

from lib.components import BlueprintBackground, BrandBar, Caption
from lib.narration import EdgeTTSRenderer, NarrationCue, RenderedNarration
from lib.settings import SETTINGS, ProjectSettings
from lib.sync import make_schedule
from lib.timeline import CueBeat


LOGGER = logging.getLogger("animetion.v6")


class CaptionController:
    def __init__(self, scene: MovingCameraScene, settings: ProjectSettings = SETTINGS) -> None:
        self.scene = scene
        self.settings = settings
        self.current: Optional[VGroup] = None
        self.current_text = ""

    def show(self, phrase: str) -> None:
        if phrase == self.current_text:
            return
        self.clear()
        if not phrase:
            return
        caption = Caption(phrase, self.settings)
        caption.move_to([0, self.settings.layout.caption_y, 0])
        caption.set_z_index(500, family=True)
        self.scene.add_foreground_mobjects(caption)
        self.current = caption
        self.current_text = phrase

    def clear(self) -> None:
        if self.current is not None:
            self.scene.remove_foreground_mobjects(self.current)
            self.scene.remove(self.current)
        self.current = None
        self.current_text = ""


class NarratedPortraitScene(MovingCameraScene):
    """Base scene that guarantees a cue cannot outlive its narration."""

    def setup(self) -> None:
        super().setup()
        self.settings = SETTINGS
        self.narration = EdgeTTSRenderer()
        self.caption = CaptionController(self, self.settings)
        self._background: Optional[BlueprintBackground] = None
        self._brand: Optional[BrandBar] = None

    def build_stage(self) -> None:
        self._background = BlueprintBackground(self.settings)
        self.add(self._background)
        self._brand = BrandBar(self.settings)
        self._brand.scale(0.86)
        self._brand.to_corner(UL, buff=0.42)
        self._brand.set_z_index(300, family=True)
        self.add_foreground_mobjects(self._brand)
        credit = self.add_credit_text()
        self.add_foreground_mobjects(credit)

    def add_credit_text(self):
        from lib.components import ThaiText

        credit = ThaiText("@ertyu0075", 16, self.settings.palette.muted, mono=True)
        credit.to_corner(DOWN + LEFT, buff=0.28)
        credit.set_z_index(300, family=True)
        return credit

    def play_cue(
        self,
        cue: NarrationCue,
        beats: Iterable[CueBeat],
        *,
        cleanup: Optional[Mobject] = None,
    ) -> RenderedNarration:
        """Play factories one by one within the exact narration duration.

        No future beat is constructed or passed to Manim. ``Scene.play`` receives
        one current animation only, so nested setup cannot reveal future objects.
        Cue timing comes only from the measured narration duration.
        """

        steps = tuple(beats)
        result = self.narration.render(cue)
        if result.error:
            LOGGER.warning("Narration %s: %s", cue.key, result.error)
        target = max(cue.min_duration, result.duration)
        schedule = make_schedule(
            [step.weight for step in steps],
            target,
            lead=self.settings.timing.cue_lead,
            exit=self.settings.timing.section_exit,
            tail=self.settings.timing.cue_tail,
            minimum_beat=self.settings.timing.minimum_beat,
            has_cleanup=cleanup is not None,
        )

        if result.media_path is not None:
            # Bypass Scene.add_sound: it silently drops audio when
            # renderer.skip_animations is still True (leftover from cached
            # partial movies), which would keep only the first cue's sound.
            self.renderer.file_writer.add_sound(str(result.media_path), self.time, None)

        if schedule.lead > 0:
            self.wait(schedule.lead)

        for step, duration in zip(steps, schedule.beats):
            if step.caption:
                self.caption.show(step.caption)
            animation = step.build()
            if animation is None:
                self.wait(duration)
            else:
                # Explicit run_time is the only source of cue timing.
                self.play(animation, run_time=duration)

        self.caption.clear()
        if cleanup is not None and schedule.exit > 0:
            self.play(FadeOut(cleanup), run_time=schedule.exit)
        if schedule.tail > 0:
            self.wait(schedule.tail)
        return result


NarratedScene = NarratedPortraitScene
