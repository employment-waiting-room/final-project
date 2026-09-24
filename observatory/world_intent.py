"""Full-world typed interpretation and confirmation, separate from model scoring."""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

import httpx
from pydantic import BaseModel, ConfigDict, model_validator

from .evaluate_intent import PROMPTS
from .world import Command, Result, ROOMS, TARGETS, describe_world, label, perform


class WorldIntent(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    status: Literal['action', 'clarify', 'unsupported']
    action: str | None
    target: str | None

    @model_validator(mode='after')
    def pair(self):
        if self.status == 'action':
            valid = self.target in ROOMS if self.action == 'move' else self.action in TARGETS and TARGETS[self.action] == self.target
            if not valid:
                raise ValueError('Unknown action/target pair')
        elif self.action is not None or self.target is not None:
            raise ValueError('Non-action must have null action and target')
        return self


class WorldInterpreter:
    def __init__(self, client=None, log_dir=None):
        self.client = client
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).resolve().parents[1] / 'generated/world-intent-logs'

    def save(self, record):
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            path = self.log_dir / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex + '.json')
            path.write_text(json.dumps(record, indent=2), encoding='utf-8')
        except OSError:
            print('Warning: could not save typed-action log.')

    def interpret(self, text, state):
        # Explicitly select the measured JSON configuration, never runner defaults.
        version, prompt = PROMPTS['v1-json']
        record = {'kind': 'interpretation', 'policy': 'world-gameplay-guards-v1',
                  'session_id': state.session_id, 'revision': state.revision, 'input': text,
                  'prompt_version': version, 'source': 'local_guard'}
        started = time.perf_counter()
        try:
            if not text.strip() or len(text) > 500:
                raise ValueError('Enter an action of 1-500 characters.')
            status = None
            if re.search(r'\b(knock|knocking|break|breaking|drop|dropping)\b|\b(ignore|override|bypass)\b.*\b(rules|instructions)\b', text, re.I):
                status = 'unsupported'
            elif re.search(r'\b(it|that|this|them|those|these|and|then|also|or)\b|[;&]', text, re.I) or re.fullmatch(r'\s*(use (the )?key|finish)[.!?]?\s*', text, re.I):
                status = 'clarify'
            if status:
                intent = WorldIntent(status=status, action=None, target=None)
            else:
                request = {'model': 'qwen3:4b', 'stream': False, 'think': False,
                           'format': WorldIntent.model_json_schema(),
                           'options': {'temperature': 0, 'seed': 42, 'num_ctx': 4096, 'num_predict': 180},
                           'messages': [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': json.dumps({
                               'scene': describe_world(state), 'inventory': sorted(state.inventory),
                               'known_flags': sorted(state.flags), 'player_request': text})}]}
                record.update(source='model', request=request)
                if self.client is None:
                    with httpx.Client(timeout=30, trust_env=False) as client:
                        response = client.post('http://127.0.0.1:11434/api/chat', json=request)
                else:
                    response = self.client.post('http://127.0.0.1:11434/api/chat', json=request)
                record['raw_response'] = response.text
                response.raise_for_status()
                body = response.json()
                if not isinstance(body, dict) or body.get('done') is not True or body.get('done_reason') == 'length':
                    raise ValueError('Incomplete intent response')
                intent = WorldIntent.model_validate_json(body['message']['content'])
            record['interpretation'] = intent.model_dump()
            return intent
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
            raise ValueError('Could not interpret that action. Try again or choose a number.') from exc
        finally:
            record['seconds'] = time.perf_counter() - started
            self.save(record)


def handle_world_text(state, text, interpreter, confirm=None):
    """Only an explicitly approved, engine-validated proposal becomes live state."""
    record = {'kind': 'decision', 'session_id': state.session_id, 'revision': state.revision, 'input': text}
    result = Result(state, 'cancelled', 'Action cancelled; state unchanged.')
    try:
        if state.ending:
            result = Result(state, 'rejected', 'The adventure has ended. Restart to play again.')
            return result
        intent = interpreter.interpret(text, state)
        record['interpretation'] = intent.model_dump()
        if intent.status != 'action':
            result = Result(state, intent.status, 'Name one action and its object.' if intent.status == 'clarify' else 'That action is not supported in this adventure.')
            return result
        command = Command(intent.action, intent.target)
        preview = perform(state, command, session_id=state.session_id, revision=state.revision)
        if preview.status != 'changed':
            result = preview
            return result
        proposal = f'Interpreted action: {label(command)} (action: {command.action}, target: {command.target}).'
        reply = confirm(proposal) if confirm else None
        record['confirmed'] = isinstance(reply, str) and reply.strip().lower() in ('y', 'yes')
        if record['confirmed']:
            # Immutable preview already contains exactly one validated transition.
            result = preview
        return result
    except (EOFError, KeyboardInterrupt):
        return result
    except ValueError as exc:
        result = Result(state, 'error', str(exc))
        return result
    finally:
        record.update(status=result.status, resulting_revision=result.state.revision)
        interpreter.save(record)
