import pytest

from observatory import __main__ as cli
from observatory.engine import GameState
from observatory.intent import Intent


@pytest.mark.parametrize("reply", ["no", "", "sure", EOFError(), KeyboardInterrupt(), "yes"])
def test_typed_action_confirmation_in_terminal(monkeypatch, capsys, reply):
    seen_states = []
    class FakeInterpreter:
        def interpret(self, text, state):
            return Intent(status="action", action="inspect_desk", target="desk")
    answers = iter(["search desk", reply, "q"])
    def read(prompt):
        if "Apply this action" in prompt:
            assert "Interpreted action: Inspect the desk (target: desk)." in capsys.readouterr().out
            assert seen_states == [GameState()]
        answer = next(answers)
        if isinstance(answer, BaseException):
            raise answer
        return answer
    original_describe = cli.describe
    def describe(state):
        seen_states.append(state)
        return original_describe(state)
    monkeypatch.setattr(cli, "Interpreter", FakeInterpreter)
    monkeypatch.setattr(cli, "describe", describe)
    monkeypatch.setattr("builtins.input", read)
    cli.main([])
    if reply == "yes":
        assert seen_states[-1].desk_inspected
    else:
        assert all(state == GameState() for state in seen_states)


def test_numbered_choices_remain_direct(monkeypatch):
    answers = iter(["1", "1", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    cli.main([])


@pytest.mark.parametrize("reply,expected_calls", [("no", 0), ("", 0), ("yes", 1)])
def test_narration_only_after_confirmed_change(monkeypatch, reply, expected_calls):
    from observatory.narrative import Scene
    calls = []
    class FakeInterpreter:
        def interpret(self, text, state):
            return Intent(status="action", action="inspect_desk", target="desk")
    class FakeNarrator:
        def render(self, state):
            assert state.desk_inspected and not state.inventory
            calls.append(state)
            return Scene("Verified scene", ("collect_key",), "entrance_hall", "fallback")
    answers = iter(["inspect desk", reply, "q"])
    monkeypatch.setattr(cli, "Interpreter", FakeInterpreter)
    monkeypatch.setattr(cli, "Narrator", FakeNarrator)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    cli.main(["--narrate"])
    assert len(calls) == expected_calls


def test_numbered_sequence_narrates_each_transition_once_including_final(monkeypatch, capsys):
    from observatory.narrative import Scene
    calls = []
    class FakeNarrator:
        def render(self, state):
            calls.append(state)
            return Scene("Final verified text" if state.library_unlocked else "Scene", (), "entrance_hall", "fallback")
    answers = iter(["1", "1", "1"])
    monkeypatch.setattr(cli, "Narrator", FakeNarrator)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    cli.main(["--narrate"])
    assert len(calls) == 3 and calls[-1].library_unlocked
    assert calls[-1].inventory == frozenset({"library_key"})
    assert "Final verified text" in capsys.readouterr().out
