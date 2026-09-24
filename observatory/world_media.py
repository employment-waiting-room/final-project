"""Synchronous full-world media orchestration, separate from engine mutation."""
import json
from pathlib import Path

from .illustration import Illustrator
from .speech import Speaker
from .world_narrative import WorldNarrator


class WorldPresentation:
    def __init__(self, narrate=False, illustrate=False, speak=False):
        self.narrator = WorldNarrator() if narrate else None
        self.speaker = Speaker() if speak else None
        self.illustrate = illustrate
        self.images = {}
        self.current_image = None
        self.session_id = None
        self.briefs = json.loads((Path(__file__).with_name('world_image_briefs.json')).read_text(encoding='utf-8')) if illustrate else {}

    def present(self, state, text, scene_mode=False):
        if self.session_id != state.session_id:
            self.images.clear()
            self.current_image = None
            self.session_id = state.session_id
        if self.narrator:
            print('Generating scene description...' if scene_mode else 'Generating action response...')
            scene = self.narrator.render(state, outcome=text, scene_mode=scene_mode)
            text = scene.description
            if scene.source == 'fallback':
                print('Using the factual description.')
        print(text)
        if self.illustrate and self.current_image != state.location:
            image = self.images.get(state.location)
            if image is None:
                image = Illustrator(location=state.location, prompt=self.briefs[state.location])
                self.images[state.location] = image
                image.show(state.location)
            elif image.path:
                try:
                    image.viewer(image.path)
                    print(f'Reusing room illustration: {image.path}')
                except (Exception, KeyboardInterrupt):
                    print('Could not open saved illustration; continuing with text.')
            self.current_image = state.location
        if self.speaker:
            print('Speaking scene...')
            self.speaker.speak(text)
