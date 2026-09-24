from dataclasses import replace
import re

import pytest

from observatory.fixtures import load_dataset
from observatory.world import WorldState, Command, TARGETS, choices, describe_world, perform


def project(state):
    return dict(location=state.location, inventory=sorted(state.inventory), flags=sorted(state.flags),
                visited=sorted(state.visited_rooms), ending=state.ending, revision=state.revision)


@pytest.mark.parametrize('case', load_dataset().cases, ids=lambda case: case.id)
def test_saved_contract_against_independent_gameplay(case):
    state = WorldState()
    for action in case.setup:
        result = perform(state, Command(action.action, action.target))
        assert result.status == 'changed'
        state = result.state
    assert project(state) == case.state.model_dump()
    if case.expected_action:
        command = case.expected_action
        result = perform(state, Command(command.action, command.target))
        assert result.status == case.expected_outcome
        assert project(result.state) == case.expected_state.model_dump()
        if result.status != 'changed':
            assert result.state is state


def run_route(actions):
    state = WorldState()
    for action in actions:
        command = Command('move', action[3:]) if action.startswith('go:') else Command(action, TARGETS[action])
        before = state
        result = perform(state, command)
        assert result.status == 'changed'
        state = result.state
        assert state.revision == before.revision + 1
        assert state.session_id == before.session_id
    return state


POWER_FIRST = ['go:workshop', 'inspect_toolbox', 'collect_fuse', 'go:generator_room',
               'install_fuse', 'start_generator', 'go:workshop', 'go:entrance_hall',
               'inspect_desk', 'collect_key', 'unlock_library', 'go:library']


@pytest.mark.parametrize('ending', ['rescued', 'sheltered'])
def test_both_endings_with_workshop_first_and_terminal_freeze(ending):
    route = POWER_FIRST + (['read_manual'] if ending == 'rescued' else []) + ['go:telescope_chamber']
    route += ['align_beacon', 'signal_rescue'] if ending == 'rescued' else ['shelter']
    state = run_route(route)
    assert state.ending == ending
    assert state.inventory == frozenset({'library_key'})
    if ending == 'sheltered':
        assert not {'manual_read', 'beacon_aligned'} & state.flags
        assert 'No rescue signal' in describe_world(state)
    assert choices(state) == ()
    for a, t in TARGETS.items():
        result = perform(state, Command(a, t))
        assert result.status == 'rejected' and result.state is state


def test_replay_restart_and_observations():
    initial = WorldState()
    inspect = Command('inspect_desk', 'desk')
    changed = perform(initial, inspect, session_id=initial.session_id, revision=0).state
    assert perform(changed, inspect, session_id=initial.session_id, revision=0).status == 'rejected'
    assert perform(changed, inspect).state is changed
    assert perform(changed, Command('look_around', 'current_room')).state is changed
    restarted = WorldState()
    assert restarted.session_id != initial.session_id and restarted.revision == 0
    assert perform(restarted, inspect, session_id=initial.session_id, revision=0).state is restarted
    assert 'key' not in describe_world(initial)
    assert not re.search(r'\bfuse\b', describe_world(replace(initial, location='workshop', visited_rooms=frozenset({'entrance_hall', 'workshop'}))))


@pytest.mark.parametrize('values', [
    {'flags': frozenset({'power_on'})},
    {'inventory': frozenset({'spare_fuse'})},
    {'flags': frozenset({'toolbox_inspected', 'fuse_installed'}), 'inventory': frozenset({'spare_fuse'})},
    {'ending': 'rescued'}, {'revision': -1}, {'inventory': set()},
])
def test_invalid_states_rejected(values):
    with pytest.raises(ValueError):
        WorldState(**values)


@pytest.mark.parametrize('command', [Command('knock', 'library_door'), Command('move', 'moon'),
                                   Command('unlock_library', 'desk'), Command('unknown', None)])
def test_wrong_commands_do_not_change_state(command):
    state = WorldState()
    assert perform(state, command).state is state


def test_all_reachable_states_have_route_to_an_ending():
    # Exhaustively explore the finite world, then propagate reachability backwards.
    initial = WorldState()
    def key(s):
        return s.location, s.inventory, s.flags, s.visited_rooms, s.ending
    found, pending, parents, wins = {key(initial)}, [initial], {}, set()
    while pending:
        state = pending.pop()
        source = key(state)
        if state.ending:
            wins.add(source)
        for command in choices(state):
            after = perform(state, command).state
            target = key(after)
            parents.setdefault(target, set()).add(source)
            if target not in found:
                found.add(target)
                pending.append(after)
    pending = list(wins)
    while pending:
        for parent in parents.get(pending.pop(), ()):
            if parent not in wins:
                wins.add(parent)
                pending.append(parent)
    assert found == wins


def test_world_cli_routes_restart_and_no_model_calls(monkeypatch, capsys):
    from observatory import __main__ as cli
    from observatory import world_cli
    requested = iter(POWER_FIRST + ['go:telescope_chamber', 'shelter'])
    available = []
    original = world_cli.choices
    def capture(state):
        available[:] = original(state)
        return tuple(available)
    post_ending = iter(['r', 'q'])
    def answer(_):
        try:
            action = next(requested)
        except StopIteration:
            return next(post_ending)
        command = Command('move', action[3:]) if action.startswith('go:') else Command(action, TARGETS[action])
        return str(available.index(command) + 1)
    monkeypatch.setattr(world_cli, 'choices', capture)
    monkeypatch.setattr('builtins.input', answer)
    monkeypatch.setattr(cli, 'Interpreter', lambda: pytest.fail('World mode invoked interpreter'))
    cli.main(['--world'])
    output = capsys.readouterr().out
    assert 'No rescue signal was sent' in output
    assert output.count('Inventory: empty') >= 2
