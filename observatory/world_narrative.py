"""State-grounded full-world presentation, never gameplay transitions."""
import json
import re
import time
from pathlib import Path

from .gameplay_io import post_chat, save_record
from .narrative import GeneratedText, Scene
from .world import choices, describe_world, label

PROMPT = '''Return only JSON with a description string. Describe the verified scene
or completed outcome in second person. Copy every required sentence exactly once.
For scene mode use at most 140 words. For outcome mode use at most 70 words and
do not recap the room. You may add one brief atmospheric sentence grounded in
the provided facts, but never invent entities, discoveries, actions or effects.
Do not move the player, open doors, change inventory, power or endings. Suggestions
are application-owned. Context is for consistency, not additional events.'''


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s.strip()]


def validate(text, required, mode):
    parts = sentences(text)
    reasons = []
    if any(parts.count(sentence) != 1 for sentence in required):
        reasons.append('missing_or_repeated_fact')
    if len(text.split()) > (140 if mode == 'scene' else 70) or len(parts) > len(required) + 1:
        reasons.append('too_long')
    extra = ' '.join(p for p in parts if p not in required).lower()
    # Deliberately conservative known-claim filter, not semantic proof.
    if re.search(r'\b(key|fuse|manual|toolbox|door|open|opens|opened|enter|leave|carry|inventory|collect|take|pick|unlock|lock|generator|power|electricity|beacon|signal|rescue|shelter|person|stranger|lantern|candle|torch|map|portal|i|we)\b', extra):
        reasons.append('unsupported_claim')
    if mode == 'outcome' and re.search(r'\b(room|hall|daylight|storm|weather|glazing)\b', extra):
        reasons.append('scene_recap')
    return reasons


class WorldNarrator:
    def __init__(self, client=None, log_dir=None):
        self.client = client
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).resolve().parents[1] / 'generated/world-narratives'

    def render(self, state, outcome=None, scene_mode=True):
        mode = 'scene' if scene_mode else 'outcome'
        fallback = describe_world(state) if scene_mode else outcome
        required = sentences(fallback)
        facts = {'mode': mode, 'required_sentences': required,
                 'inventory': sorted(state.inventory), 'known_flags': sorted(state.flags)}
        request = {'model': 'qwen3:4b', 'stream': False, 'think': False,
                   'format': GeneratedText.model_json_schema(),
                   'options': {'temperature': 0.3, 'seed': 42, 'num_ctx': 4096, 'num_predict': 600},
                   'messages': [{'role': 'system', 'content': PROMPT}, {'role': 'user', 'content': json.dumps(facts)}]}
        record = {'prompt_version': 'world-gameplay-narrative-v1', 'policy_version': 'world-gameplay-guards-v1',
                  'session_id': state.session_id, 'revision': state.revision, 'location': state.location,
                  'mode': mode, 'request': request, 'source': 'fallback', 'validation_reasons': []}
        text = fallback
        started = time.perf_counter()
        try:
            response = post_chat(request, self.client)
            record['raw_response'] = response.text
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, dict) or body.get('done') is not True or body.get('done_reason') == 'length':
                raise ValueError('Incomplete response')
            generated = GeneratedText.model_validate_json(body['message']['content'])
            record['validation_reasons'] = validate(generated.description, required, mode)
            if not record['validation_reasons']:
                text = generated.description
                record['source'] = 'model'
        except (Exception, KeyboardInterrupt) as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
            record['validation_reasons'] = ['generation_failure']
        record.update(accepted_text=text, seconds=time.perf_counter() - started)
        save_record(self.log_dir, record, 'Warning: could not save narration log.')
        return Scene(text, tuple(label(c) for c in choices(state)), state.location, record['source'], tuple(record['validation_reasons']))
