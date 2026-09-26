"""Full-world typed interpretation and confirmation, separate from model scoring."""
import json
import re
import time
from pathlib import Path
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, model_validator

from .evaluate_intent import PROMPTS
from .gameplay_io import post_chat, save_record
from .world import Command, Result, ROOMS, TARGETS, describe_world, label, perform

GAMEPLAY_PROMPT_VERSION = 'world-gameplay-intent-v2'
CANONICAL_TARGETS = {action: [target] for action, target in TARGETS.items()}
CANONICAL_TARGETS['move'] = list(ROOMS)
GAMEPLAY_PROMPT = PROMPTS['v1-json'][1] + '''
Action and target are separate fields. Never put an action/target pair such as
"look_around/current_room" in the action field. Use exactly the canonical IDs
below, including underscores. Players use normal language and do not need IDs.
Checking a named desk means inspecting that desk, not looking around the room.
"check the desk" -> {"status":"action","action":"inspect_desk","target":"desk"}
"go to the telescope chamber" -> {"status":"action","action":"move","target":"telescope_chamber"}
"go to telescope room" means the same destination, telescope_chamber.
Interpret explicit requests even when a route or prerequisite is unavailable;
the engine will check feasibility. Preserve clarification for compound requests.
Canonical action to target mapping:
''' + json.dumps(CANONICAL_TARGETS, sort_keys=True)


class WorldIntent(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    status: Literal['action', 'clarify', 'unsupported']
    action: Literal['look_around', 'inspect_desk', 'collect_key', 'unlock_library',
                    'move', 'read_manual', 'inspect_toolbox', 'collect_fuse',
                    'install_fuse', 'start_generator', 'align_beacon', 'signal_rescue', 'shelter'] | None
    target: Literal['current_room', 'desk', 'library_key', 'library_door', 'manual',
                    'toolbox', 'spare_fuse', 'fuse_socket', 'generator', 'beacon',
                    'signalling_console', 'shelter_bench', 'entrance_hall', 'library',
                    'workshop', 'generator_room', 'telescope_chamber'] | None

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
        save_record(self.log_dir, record, 'Warning: could not save typed-action log.')

    def interpret(self, text, state):
        # Gameplay revision based on V1-JSON; frozen evaluation stays unchanged.
        version, prompt = GAMEPLAY_PROMPT_VERSION, GAMEPLAY_PROMPT
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
                response = post_chat(request, self.client)
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
