"""Run with python -m observatory from the project directory."""
import argparse
from .engine import ACTION_LABELS, GameState, allowed_actions, apply_action, describe
from .intent import Interpreter, handle_text
from .narrative import Narrator
from .speech import Speaker


def confirm_action(proposal):
    print(proposal)
    return input("Apply this action? Type y/yes to confirm; anything else cancels: ")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--narrate", action="store_true", help="Generate guarded narration after accepted actions")
    parser.add_argument("--speak", action="store_true", help="Speak displayed scene text with local Kokoro after accepted changes")
    args = parser.parse_args(argv)
    state = GameState()
    interpreter = Interpreter()
    narrator = Narrator() if args.narrate else None
    scene = None
    speaker = Speaker() if args.speak else None
    speech_pending = False
    print("The Last Observatory - entrance hall prototype")
    while True:
        print(f"\n{scene.description if scene else describe(state)}")
        print("Inventory: " + (", ".join(sorted(state.inventory)) or "empty"))
        if speech_pending:
            speech_pending = False
            print("Speaking scene...")
            speaker.speak(scene.description if scene else describe(state))
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
            previous = state
            try:
                state, feedback = handle_text(state, answer, interpreter, confirm_action)
            except (EOFError, KeyboardInterrupt):
                print("\nAction cancelled; state unchanged. Game closed.")
                return
            print(feedback)
            speech_pending = speaker is not None and state is not previous
            if narrator and state is not previous:
                print("Generating scene description...")
                scene = narrator.render(state)
                if scene.source == "fallback":
                    print("Using the factual scene description.")
            continue
        state = apply_action(state, actions[int(answer) - 1])
        speech_pending = speaker is not None
        if narrator:
            print("Generating scene description...")
            scene = narrator.render(state)
            if scene.source == "fallback":
                print("Using the factual scene description.")


if __name__ == "__main__":
    main()
