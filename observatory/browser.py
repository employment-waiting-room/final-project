"""Local single-player browser application. Run python -m observatory.browser."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import secrets
from threading import RLock
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .world import WorldState, Command, choices, label, describe_world, perform
from .world_intent import WorldInterpreter
from .world_narrative import WorldNarrator
from .illustration import Illustrator
from .speech import Speaker

ROOT = Path(__file__).resolve().parent


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid')
    session: str
    revision: int
    text: str = Field(default='', max_length=500)
    action: str = ''
    target: str = ''
    proposal: str = ''


class Game:
    def __init__(self, media=True, executor=None):
        self.lock = RLock()
        self.executor = executor or ThreadPoolExecutor(max_workers=1)
        self.media = media
        self.interpreter = WorldInterpreter()
        self.narrator = WorldNarrator() if media else None
        self.speaker = Speaker(player=None) if media else None
        self.briefs = json.loads((ROOT / 'world_image_briefs.json').read_text(encoding='utf-8'))
        self.assets = {}
        self.reset()

    def reset(self):
        self.state = WorldState()
        self.text = describe_world(self.state)
        self.message = 'Ready to explore.'
        self.pending = None
        self.busy = False
        self.job = uuid4().hex
        self.images = {}
        self.image = self.audio = None
        self.started = False

    def snapshot(self):
        with self.lock:
            return {'session': self.state.session_id, 'revision': self.state.revision,
                    'location': self.state.location.replace('_', ' '), 'inventory': sorted(self.state.inventory),
                    'ending': self.state.ending, 'text': self.text, 'message': self.message,
                    'busy': self.busy, 'proposal': self.pending and {'id': self.pending[0], 'label': label(self.pending[1]),
                        'action': self.pending[1].action, 'target': self.pending[1].target},
                    'choices': [{'action': c.action, 'target': c.target, 'label': label(c)} for c in choices(self.state)],
                    'image': self.image, 'audio': self.audio}

    def check(self, data):
        if data.session != self.state.session_id or data.revision != self.state.revision:
            raise HTTPException(409, 'This request is out of date.')

    def asset(self, path):
        key = uuid4().hex
        self.assets[key] = Path(path)
        return '/asset/' + key

    def valid(self, job):
        return self.job == job

    def publish_media(self, job, state, text, scene_mode):
        try:
            with self.lock:
                if not self.valid(job): return
            if self.narrator:
                text = self.narrator.render(state, outcome=text, scene_mode=scene_mode).description
            with self.lock:
                if not self.valid(job): return
                self.text = text
                self.message = 'Preparing illustration and audio...' if self.media else 'Ready.'
                cached = self.images.get(state.location)
                attempted = state.location in self.images
            if self.media and not attempted:
                adapter = Illustrator(location=state.location, prompt=self.briefs[state.location], viewer=lambda _: None)
                path = adapter.show(state.location)
                with self.lock:
                    if not self.valid(job): return
                    cached = self.asset(path) if path else None
                    self.images[state.location] = cached
            with self.lock:
                if not self.valid(job): return
                self.image = cached
            audio = self.speaker.speak(text) if self.speaker else None
            with self.lock:
                if not self.valid(job): return
                self.audio = self.asset(audio['audio_path']) if audio and audio.get('success') else None
                self.message = 'Ready.' if not self.media or (cached and self.audio) else 'Some media is unavailable; text gameplay remains available.'
        except Exception:
            with self.lock:
                if self.valid(job): self.message = 'Media unavailable; continue with the displayed text.'
        finally:
            with self.lock:
                if self.valid(job): self.busy = False

    def schedule(self, text, scene_mode):
        self.job = uuid4().hex
        self.busy = True
        self.text = text  # Immediate verified fallback, before generation finishes.
        self.audio = None
        self.image = self.images.get(self.state.location)
        self.message = 'Preparing scene...'
        self.executor.submit(self.publish_media, self.job, self.state, text, scene_mode)

    def apply(self, command):
        before = self.state
        result = perform(before, command)
        self.state = result.state
        self.message = result.message
        if result.status in ('changed', 'observed'):
            self.schedule(result.message, result.status == 'observed' or before.location != self.state.location)

    def interpret(self, job, state, text):
        try:
            intent = self.interpreter.interpret(text, state)
            with self.lock:
                if not self.valid(job): return
                if intent.status != 'action':
                    self.message = 'Name one action and its object.' if intent.status == 'clarify' else 'That action is not supported.'
                else:
                    command = Command(intent.action, intent.target)
                    result = perform(state, command)
                    if result.status == 'changed':
                        self.pending = (uuid4().hex, command)
                        self.message = 'Confirm the interpreted action before applying it.'
                    elif result.status == 'observed':
                        self.apply(command)
                        return
                    else:
                        self.message = result.message
                self.busy = False
        except Exception:
            with self.lock:
                if self.valid(job):
                    self.message = 'Could not interpret that action. Try a numbered suggestion.'
                    self.busy = False

    def request(self, operation, data):
        with self.lock:
            self.check(data)
            if operation in ('start', 'restart'):
                if operation == 'restart':
                    self.reset()
                if not self.started:
                    self.started = True
                    self.schedule(describe_world(self.state), True)
                return
            if self.busy:
                raise HTTPException(409, 'Please wait for the current response.')
            if operation in ('confirm', 'cancel'):
                if not self.pending or self.pending[0] != data.proposal:
                    raise HTTPException(409, 'That proposal is no longer available.')
                command = self.pending[1]
                self.pending = None  # Consume before applying; cannot confirm twice.
                self.interpreter.save({'kind': 'browser_decision', 'session_id': self.state.session_id,
                                       'revision': self.state.revision, 'action': command.action,
                                       'target': command.target, 'confirmed': operation == 'confirm'})
                if operation == 'confirm': self.apply(command)
                else: self.message = 'Action cancelled; state unchanged.'
                return
            if self.pending:
                raise HTTPException(409, 'Confirm or cancel the pending action first.')
            if self.state.ending:
                raise HTTPException(409, 'Restart to play again.')
            if operation == 'choose':
                command = Command(data.action, data.target)
                if command not in choices(self.state):
                    raise HTTPException(400, 'Choose an available action.')
                self.apply(command)
            elif operation == 'type':
                if not data.text.strip(): raise HTTPException(400, 'Enter an action.')
                self.job = uuid4().hex
                self.busy = True
                self.message = 'Interpreting action...'
                self.executor.submit(self.interpret, self.job, self.state, data.text)
            else:
                raise HTTPException(404)


def create_app(game=None):
    app = FastAPI()
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost'])
    game = game or Game()
    token = secrets.token_urlsafe(32)

    @app.get('/')
    def index(): return FileResponse(ROOT / 'browser.html')

    @app.get('/state')
    def state(): return dict(game.snapshot(), token=token)

    @app.post('/api/{operation}')
    def action(operation: str, data: Input, request: Request):
        if request.headers.get('x-game-token') != token:
            raise HTTPException(403, 'Invalid local session token.')
        game.request(operation, data)
        return game.snapshot()

    @app.get('/asset/{key}')
    def asset(key: str):
        with game.lock: path = game.assets.get(key)
        if path is None or not path.is_file(): raise HTTPException(404)
        return FileResponse(path)

    return app


def main():
    import uvicorn
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-media', action='store_true', help='Skip generated narration, images and speech; typed requests still use Ollama')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    print(f'Open http://127.0.0.1:{args.port} in your browser. Ctrl+C stops the server.')
    uvicorn.run(create_app(Game(media=not args.no_media)), host='127.0.0.1', port=args.port)


if __name__ == '__main__': main()
