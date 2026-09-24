"""Model-free full-world terminal; the AI/media prototype remains separate."""
from .world import WorldState, choices, describe_world, label, perform


def main():
    state = WorldState()
    print('The Last Observatory - full-world rules mode (numbered actions)')
    print(describe_world(state))
    while True:
        print('Inventory: ' + (', '.join(sorted(state.inventory)) or 'empty'))
        commands = choices(state)
        for number, command in enumerate(commands, 1):
            print(f'{number}. {label(command)}')
        try:
            answer = input('Choose a number (r to restart, q to quit): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            return
        if answer == 'q':
            return
        if answer == 'r':
            state = WorldState()
            print(describe_world(state))
            continue
        if not answer.isdecimal() or not 1 <= int(answer) <= len(commands):
            print('Choose a displayed number. Typed model actions are not connected in this mode yet.')
            continue
        result = perform(state, commands[int(answer) - 1], session_id=state.session_id, revision=state.revision)
        state = result.state
        print(result.message)
