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
LABELS = dict(zip(TARGETS, (
    'Look around', 'Inspect the desk', 'Collect the library key', 'Unlock the library door',
    'Read the instruction manual', 'Inspect the toolbox', 'Collect the spare fuse',
    'Install the spare fuse', 'Start the generator', 'Align the beacon',
    'Send the rescue signal', 'Shelter until morning')))
OUTCOMES = {
    'inspect_desk': 'You discover a library key on the desk. It is not yet collected.',
    'collect_key': 'You pick up the library key.',
    'unlock_library': 'You unlock the library door. It remains closed.',
    'read_manual': 'The manual explains: install the fuse, start the generator, align the beacon, then signal for rescue. Powered shelter is another option.',
    'inspect_toolbox': 'You discover a spare fuse in the toolbox and close the lid again.',
    'collect_fuse': 'You collect the spare fuse and close the toolbox.',
    'install_fuse': 'You install the spare fuse in the socket. It is no longer in your inventory.',
    'start_generator': 'You start the generator. Observatory power is restored.',
    'align_beacon': 'You align the beacon using the manual procedure.',
    'signal_rescue': 'The valley station receives your signal. Rescue arrives after the storm.',
    'shelter': 'You shelter in the powered observatory and leave when the storm clears. No rescue signal was sent.',
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
        if self.location not in ROOMS or not self.visited_rooms <= set(ROOMS) or self.location not in self.visited_rooms:
            raise ValueError('Invalid room history')
        if not f <= FLAGS or not inv <= {'library_key', 'spare_fuse'}:
            raise ValueError('Unknown flag or item')
        if type(self.revision) is not int or self.revision < 0 or not isinstance(self.session_id, str) or not self.session_id:
            raise ValueError('Invalid revision/session')
        requirements = {'library_unlocked': {'desk_inspected'}, 'fuse_installed': {'toolbox_inspected'},
                        'power_on': {'fuse_installed'}, 'beacon_aligned': {'power_on', 'manual_read'}}
        if any(flag in f and not required <= f for flag, required in requirements.items()):
            raise ValueError('Missing prerequisite flags')
        if ('library_key' in inv and 'desk_inspected' not in f) or ('library_unlocked' in f and 'library_key' not in inv):
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
    if (session_id is not None and session_id != state.session_id) or (revision is not None and revision != state.revision):
        return unchanged('rejected', 'This request is out of date. Choose an action again.')
    a, t = command.action, command.target
    if not isinstance(a, str) or not isinstance(t, str) or (a == 'move' and t not in ROOMS) or (a != 'move' and (a not in TARGETS or TARGETS[a] != t)):
        return unchanged('rejected', 'That action and target are not supported.')
    if state.ending:
        return unchanged('rejected', 'The adventure has ended. Restart to play again.')
    if a == 'look_around':
        return unchanged('observed', describe_world(state))
    if a == 'move':
        edge = frozenset((state.location, t))
        if edge not in EDGES or t == state.location:
            return unchanged('rejected', 'There is no passage to that room from here.')
        if edge == frozenset(('entrance_hall', 'library')) and 'library_unlocked' not in state.flags:
            return unchanged('rejected', 'The library door is locked.')
        after = replace(state, location=t, visited_rooms=state.visited_rooms | {t}, revision=state.revision + 1)
        return Result(after, 'changed', describe_world(after))
    room, flags, items, effect = RULES[a]
    if state.location != room:
        return unchanged('rejected', 'You cannot do that from this location.')
    if effect in state.flags or (a == 'collect_key' and 'library_key' in state.inventory) or (a == 'collect_fuse' and ('spare_fuse' in state.inventory or 'fuse_installed' in state.flags)):
        return unchanged('unchanged', 'Already completed. ' + describe_world(state))
    if not set(flags) <= state.flags or not set(items) <= state.inventory:
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
    if a == 'collect_key': inv = inv | {'library_key'}
    if a == 'collect_fuse': inv = inv | {'spare_fuse'}
    if a == 'install_fuse': inv = inv - {'spare_fuse'}
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
        'entrance_hall': 'A dusty desk stands beside the closed library door. A passage leads to the workshop.',
        'library': 'Bookshelves line the room. An instruction manual rests on a reading stand. Stairs lead to the telescope chamber.',
        'workshop': 'A closed toolbox rests on the workbench. A doorway leads to the generator room.',
        'generator_room': 'The generator has a fuse socket and a start switch.',
        'telescope_chamber': 'The telescope carries a beacon attachment. There is an alignment control, a signalling console and a shelter bench.',
    }
    text = f"You are in the {state.location.replace('_', ' ')}. " + descriptions[state.location]
    if state.location == 'entrance_hall':
        text += ' The library door is ' + ('unlocked.' if 'library_unlocked' in f else 'locked.')
        if 'desk_inspected' in f and 'library_key' not in state.inventory:
            text += ' The discovered library key remains on the desk.'
    if state.location == 'workshop' and 'toolbox_inspected' in f and 'spare_fuse' not in state.inventory and 'fuse_installed' not in f:
        text += ' The discovered spare fuse remains inside the toolbox.'
    if state.location == 'generator_room':
        text += ' The fuse is installed.' if 'fuse_installed' in f else ' The fuse socket is empty.'
        text += ' The generator is running.' if 'power_on' in f else ' The generator is stopped.'
    if state.location == 'telescope_chamber':
        text += ' The beacon is aligned.' if 'beacon_aligned' in f else ' The beacon is not aligned.'
    text += ' Observatory power is on.' if 'power_on' in f else ' Diffuse daylight provides visibility; electrical power is off.'
    return text
