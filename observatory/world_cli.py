"""Full-world terminal with optional typed interpretation and direct choices."""
from .world import WorldState, choices, describe_world, label, perform
from .world_intent import WorldInterpreter, handle_world_text


def confirm(proposal):
    print(proposal)
    return input('Apply this action? Type y/yes to confirm; anything else cancels: ')


def main():
    state = WorldState()
    interpreter = None
    print('The Last Observatory - full world (typed actions or numbered choices)')
    print(describe_world(state))
    while True:
        print('Inventory: ' + (', '.join(sorted(state.inventory)) or 'empty'))
        commands = choices(state)
        for number, command in enumerate(commands, 1):
            print(f'{number}. {label(command)}')
        try:
            answer = input('Type an action or choose a number (r to restart, q to quit): ').strip()
        except (EOFError, KeyboardInterrupt):
            return
        if answer.lower() == 'q':
            return
        if answer.lower() == 'r':
            state = WorldState()
            print(describe_world(state))
            continue
        if answer and not answer.isdecimal():
            interpreter = interpreter or WorldInterpreter()
            print('Interpreting action...')
            result = handle_world_text(state, answer, interpreter, confirm)
            state = result.state
            print(result.message)
            continue
        if not answer or len(answer) > 6 or not 1 <= int(answer) <= len(commands):
            print('Choose a displayed number or type an action.')
            continue
        result = perform(state, commands[int(answer) - 1], session_id=state.session_id, revision=state.revision)
        state = result.state
        print(result.message)
