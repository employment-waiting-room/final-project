"""Run with python -m observatory from the project directory."""
from .engine import ACTION_LABELS, GameState, allowed_actions, apply_action, describe
from .intent import Interpreter, handle_text


def main():
    state = GameState()
    interpreter = Interpreter()
    print("The Last Observatory - entrance hall prototype")
    while True:
        print(f"\n{describe(state)}")
        print("Inventory: " + (", ".join(sorted(state.inventory)) or "empty"))
        if state.library_unlocked:
            print("Sequence complete. Exploring the library is not implemented yet.")
            return
        actions = allowed_actions(state)
        for number, action in enumerate(actions, 1):
            print(f"{number}. {ACTION_LABELS[action]}")
        try:
            answer = input("Type an action or choose a number (q to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGame closed.")
            return
        if answer.lower() == "q":
            return
        if answer not in [str(n) for n in range(1, len(actions) + 1)]:
            if not answer or answer.isdigit():
                print("Enter an action or one of the displayed numbers.")
                continue
            print("Interpreting action...")
            state, feedback = handle_text(state, answer, interpreter)
            print(feedback)
            continue
        state = apply_action(state, actions[int(answer) - 1])


if __name__ == "__main__":
    main()
