"""Full-world terminal with optional typed interpretation and direct choices."""
from .world import WorldState, choices, describe_world, label, perform
from .world_intent import WorldInterpreter, handle_world_text
from .world_media import WorldPresentation


def confirm(proposal):
    print(proposal)
    return input('Apply this action? Type y/yes to confirm; anything else cancels: ')


def main(narrate=False, illustrate=False, speak=False):
    state = WorldState()
    presentation = WorldPresentation(narrate, illustrate, speak)
    interpreter = None
    print('The Last Observatory - full world (typed actions or numbered choices)')
    presentation.present(state, describe_world(state), scene_mode=True)
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
            presentation.present(state, describe_world(state), scene_mode=True)
            continue
        if answer and not answer.isdecimal():
            interpreter = interpreter or WorldInterpreter()
            print('Interpreting action...')
            previous = state
            result = handle_world_text(state, answer, interpreter, confirm)
            state = result.state
            if result.status in ('changed', 'observed'):
                presentation.present(state, result.message, scene_mode=result.status == 'observed' or previous.location != state.location)
            else:
                print(result.message)
            continue
        if not answer or len(answer) > 6 or not 1 <= int(answer) <= len(commands):
            print('Choose a displayed number or type an action.')
            continue
        previous = state
        result = perform(state, commands[int(answer) - 1], session_id=state.session_id, revision=state.revision)
        state = result.state
        if result.status in ('changed', 'observed'):
            presentation.present(state, result.message, scene_mode=result.status == 'observed' or previous.location != state.location)
        else:
            print(result.message)
