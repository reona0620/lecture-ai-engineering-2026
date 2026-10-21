from types import SimpleNamespace

from app import ask


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="answer",
        usage_metadata=SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=7,
        ),
    )

    class FakeChat:
        def send_message(self, question):
            return response

    assert ask.ask(FakeChat(), "question") == "answer"
    assert capsys.readouterr().out.strip() == "[tokens] input: 12, output: 7"


def test_main_reuses_chat_for_follow_up_questions(monkeypatch):
    sent_messages = []

    class FakeChat:
        def send_message(self, question):
            sent_messages.append(question)
            return SimpleNamespace(
                text=f"answer to {question}",
                usage_metadata=SimpleNamespace(
                    prompt_token_count=12,
                    candidates_token_count=7,
                ),
            )

    chat = FakeChat()

    class FakeChats:
        def create(self, **kwargs):
            return chat

    class FakeClient:
        def __init__(self, **kwargs):
            self.chats = FakeChats()

    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "first question"])
    questions = iter(["follow-up", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask.main()

    assert sent_messages == ["first question", "follow-up"]