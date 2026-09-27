"""Deterministic five-room gameplay. No inference or evaluation dependencies."""
from dataclasses import dataclass, field, replace
from uuid import uuid4

ROOMS = ('entrance_hall', 'library', 'workshop', 'generator_room', 'telescope_chamber')
EDGES = {frozenset(pair) for pair in (
    ('entrance_hall', 'library'), ('entrance_hall', 'workshop'),
    ('workshop', 'generator_room'), ('library', 'telescope_chamber'))}
TARGETS = {
    'look_around': 'current_room', 'inspect_desk': 'desk', 'collect_key': 'library_key',
    'unlock_library': 'library_door', 'read_manual': 'manual', 'inspect_toolbox': 'toolbox',
    'collect_fuse': 'spare_fuse', 'install_fuse': 'fuse_socket', 'start_generator': 'generator',
    'align_beacon': 'beacon', 'signal_rescue': 'signalling_console', 'shelter': 'shelter_bench',
}
# action: room, prerequisite flags, prerequisite inventory, completed flag
RULES = {
    'inspect_desk': ('entrance_hall', (), (), 'desk_inspected'),
    'collect_key': ('entrance_hall', ('desk_inspected',), (), None),
    'unlock_library': ('entrance_hall', (), ('library_key',), 'library_unlocked'),
    'read_manual': ('library', (), (), 'manual_read'),
    'inspect_toolbox': ('workshop', (), (), 'toolbox_inspected'),
    'collect_fuse': ('workshop', ('toolbox_inspected',), (), None),
    'install_fuse': ('generator_room', (), ('spare_fuse',), 'fuse_installed'),
    'start_generator': ('generator_room', ('fuse_installed',), (), 'power_on'),
    'align_beacon': ('telescope_chamber', ('power_on', 'manual_read'), (), 'beacon_aligned'),
    'signal_rescue': ('telescope_chamber', ('beacon_aligned',), (), None),
    'shelter': ('telescope_chamber', ('power_on',), (), None),
}
FLAGS = frozenset(rule[3] for rule in RULES.values() if rule[3])
LABELS = {
    'look_around': 'Look around', 'inspect_desk': 'Inspect the desk',
    'collect_key': 'Collect the library key', 'unlock_library': 'Unlock the library door',
    'read_manual': 'Read the instruction manual', 'inspect_toolbox': 'Inspect the toolbox',
    'collect_fuse': 'Collect the spare fuse', 'install_fuse': 'Install the spare fuse',
    'start_generator': 'Start the generator', 'align_beacon': 'Align the beacon',
    'signal_rescue': 'Send the rescue signal', 'shelter': 'Shelter until morning',
}
OUTCOMES = {
    'inspect_desk': 'Among the dusty books on the desk, you spot a key.',
    'collect_key': 'You take the key and put it in your bag.',
    'unlock_library': 'The lock clicks. A faint scent of old books drifts through the gap beneath the library door.',
    'read_manual': 'The manual shows a generator that needs a working fuse and a beacon that must be aligned to reach the valley station. You study the alignment procedure. With power restored, the observatory can also provide shelter until morning.',
    'inspect_toolbox': 'Inside the toolbox, you find a spare fuse.',
    'collect_fuse': 'You shift tools out of the way and grab the spare fuse.',
    'install_fuse': 'The spare fuse settles into the socket and a green light flickers on.',
    'start_generator': 'The generator catches with a low rumble. Power returns to the observatory.',
    'align_beacon': "Following the manual's instructions, you ease the beacon into alignment.",
    'signal_rescue': 'The valley station receives your signal and rescue arrives after the storm.',
    'shelter': 'You shelter in the powered observatory and leave when the storm clears.',
}


@dataclass(frozen=True)
class WorldState:
    location: str = 'entrance_hall'
    inventory: frozenset[str] = frozenset()
    flags: frozenset[str] = frozenset()
    visited_rooms: frozenset[str] = frozenset({'entrance_hall'})
    ending: str | None = None
    revision: int = 0
    session_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self):
        if any(type(v) is not frozenset for v in (self.inventory, self.flags, self.visited_rooms)):
            raise ValueError('State collections must be immutable frozensets')
        f, inv = self.flags, self.inventory
        invalid_room_history = (
            self.location not in ROOMS
            or not self.visited_rooms <= set(ROOMS)
            or self.location not in self.visited_rooms
        )
        if invalid_room_history:
            raise ValueError('Invalid room history')
        if not f <= FLAGS or not inv <= {'library_key', 'spare_fuse'}:
            raise ValueError('Unknown flag or item')
        invalid_revision = type(self.revision) is not int or self.revision < 0
        invalid_session = not isinstance(self.session_id, str) or not self.session_id
        if invalid_revision or invalid_session:
            raise ValueError('Invalid revision/session')
        requirements = {'library_unlocked': {'desk_inspected'}, 'fuse_installed': {'toolbox_inspected'},
                        'power_on': {'fuse_installed'}, 'beacon_aligned': {'power_on', 'manual_read'}}
        if any(flag in f and not required <= f for flag, required in requirements.items()):
            raise ValueError('Missing prerequisite flags')
        key_without_discovery = 'library_key' in inv and 'desk_inspected' not in f
        unlocked_without_key = 'library_unlocked' in f and 'library_key' not in inv
        if key_without_discovery or unlocked_without_key:
            raise ValueError('Invalid key state')
        if 'spare_fuse' in inv and ('toolbox_inspected' not in f or 'fuse_installed' in f):
            raise ValueError('Invalid fuse state')
        if self.ending not in (None, 'rescued', 'sheltered'):
            raise ValueError('Invalid ending')
        if self.ending and (self.location != 'telescope_chamber' or 'power_on' not in f):
            raise ValueError('Ending requires chamber and power')
        if self.ending == 'rescued' and 'beacon_aligned' not in f:
            raise ValueError('Rescue requires alignment')


@dataclass(frozen=True)
class Command:
    action: str
    target: str


@dataclass(frozen=True)
class Result:
    state: WorldState
    status: str
    message: str


def perform(state, command, *, session_id=None, revision=None):
    """Optional request identity prevents applying stale/replayed UI requests."""
    def unchanged(status, message):
        return Result(state, status, message)
    wrong_session = session_id is not None and session_id != state.session_id
    wrong_revision = revision is not None and revision != state.revision
    if wrong_session or wrong_revision:
        return unchanged('rejected', 'This request is out of date. Choose an action again.')
    a, t = command.action, command.target
    if not isinstance(a, str) or not isinstance(t, str):
        return unchanged('rejected', 'That action and target are not supported.')
    if a == 'move':
        supported_pair = t in ROOMS
    else:
        supported_pair = a in TARGETS and TARGETS[a] == t
    if not supported_pair:
        return unchanged('rejected', 'That action and target are not supported.')
    if state.ending:
        return unchanged('rejected', 'The adventure has ended. Restart to play again.')
    if a == 'look_around':
        return unchanged('observed', describe_world(state))
    if a == 'move':
        edge = frozenset((state.location, t))
        if edge not in EDGES or t == state.location:
            return unchanged('rejected', 'There is no passage to that room from here.')
        library_passage = edge == frozenset(('entrance_hall', 'library'))
        if library_passage and 'library_unlocked' not in state.flags:
            return unchanged('rejected', 'The library door is locked.')
        after = replace(state, location=t, visited_rooms=state.visited_rooms | {t}, revision=state.revision + 1)
        return Result(after, 'changed', describe_world(after))
    room, flags, items, effect = RULES[a]
    if state.location != room:
        return unchanged('rejected', 'You cannot do that from this location.')
    key_collected = a == 'collect_key' and 'library_key' in state.inventory
    fuse_collected = a == 'collect_fuse' and (
        'spare_fuse' in state.inventory or 'fuse_installed' in state.flags
    )
    if effect in state.flags or key_collected or fuse_collected:
        return unchanged('unchanged', 'Already completed. ' + describe_world(state))
    missing_flags = not set(flags) <= state.flags
    missing_items = not set(items) <= state.inventory
    if missing_flags or missing_items:
        return unchanged('rejected', {
            'collect_key': 'There is no discovered key to collect.',
            'unlock_library': 'You do not have the key needed to unlock this door.',
            'collect_fuse': 'There is no discovered fuse to collect.',
            'install_fuse': 'You do not carry a spare fuse.',
            'start_generator': 'The generator needs an installed fuse.',
            'align_beacon': 'Alignment requires power and the manual procedure.',
            'signal_rescue': 'The beacon must be aligned before signalling.',
            'shelter': 'Safe shelter requires restored power.',
        }.get(a, 'The prerequisites are not met.'))
    inv = state.inventory
    if a == 'collect_key':
        inv = inv | {'library_key'}
    if a == 'collect_fuse':
        inv = inv | {'spare_fuse'}
    if a == 'install_fuse':
        inv = inv - {'spare_fuse'}
    ending = {'signal_rescue': 'rescued', 'shelter': 'sheltered'}.get(a)
    after = replace(state, inventory=inv, flags=state.flags | ({effect} if effect else set()),
                    ending=ending, revision=state.revision + 1)
    return Result(after, 'changed', OUTCOMES[a])


def choices(state):
    if state.ending:
        return ()
    candidates = [Command(a, t) for a, t in TARGETS.items() if a != 'look_around']
    candidates += [Command('move', room) for room in ROOMS]
    return tuple(c for c in candidates if perform(state, c).status == 'changed') + (Command('look_around', 'current_room'),)


def label(command):
    return 'Go to ' + command.target.replace('_', ' ') if command.action == 'move' else LABELS[command.action]


def describe_world(state):
    f = state.flags
    if state.ending:
        return OUTCOMES['signal_rescue' if state.ending == 'rescued' else 'shelter']
    descriptions = {
        'entrance_hall': 'Dust covers the desk beside the closed library door. A passage leads to the workshop.',
        'library': 'Between the bookshelves, an open instruction manual rests on a reading stand. Stairs lead to the telescope chamber.',
        'workshop': 'On the workbench sits a toolbox. A doorway leads to the generator room.',
        'generator_room': 'Wall conduits run from the generator. A fuse socket and start switch sit on its casing.',
        'telescope_chamber': 'Beneath the enclosed dome stands a telescope with a beacon attachment and alignment control. Nearby are a signalling console and a bench.',
    }
    text = f"You are in the {state.location.replace('_', ' ')}. " + descriptions[state.location]
    if state.location == 'entrance_hall':
        text += ' The library door is closed, but its lock has been released.' if 'library_unlocked' in f else ' The library door is held shut by its lock.'
        if 'desk_inspected' in f and 'library_key' not in state.inventory:
            text += ' A key lies on the desk.'
    if state.location == 'workshop' and 'toolbox_inspected' in f and 'spare_fuse' not in state.inventory and 'fuse_installed' not in f:
        text += ' There is a spare fuse inside the toolbox.'
    if state.location == 'generator_room':
        text += ' The replacement fuse sits snugly in its socket.' if 'fuse_installed' in f else ' The fuse socket sits empty in the casing.'
        text += ' The generator rumbles steadily.' if 'power_on' in f else ' The generator stands silent.'
    if state.location == 'telescope_chamber':
        text += ' The beacon holds the alignment described in the manual.' if 'beacon_aligned' in f else ' The beacon has yet to be aligned.'
    daylight = {
        'entrance_hall': 'Grey daylight filters through the window, illuminating the room.',
        'library': 'Grey light filters through the frosted glazing and falls across the open pages.',
        'workshop': 'Muted daylight washes over the workbench, reflecting off the metal surfaces.',
        'generator_room': 'Pale light from the high glazing picks out the wall conduits.',
        'telescope_chamber': 'Filtered daylight softens the outlines of the telescope beneath the dome.',
    }
    powered = {
        'entrance_hall': 'Beyond the hall, the restored generator supplies power to the observatory.',
        'library': 'Grey light filters through the frosted glazing and falls across the open pages.',
        'workshop': 'From the generator room comes the steady rumble as the generator churns.',
        'generator_room': 'Power flows from the running machine to the rest of the observatory.',
        'telescope_chamber': 'The restored generator supplies the beacon equipment with power.',
    }
    text += ' ' + (powered if 'power_on' in f else daylight)[state.location]
    return text
