"""第1回: 会話履歴を保ったままLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    # 回答後も続けて質問できる。終了するときは exit を入力する

ツールは使わず、会話履歴を保ったままモデルとやり取りする。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat, question: str) -> str:
    response = chat.send_message(question)

    usage = response.usage_metadata
    if usage is None:
        print("[tokens] input: unavailable, output: unavailable")
    else:
        print(
            f"[tokens] input: {usage.prompt_token_count}, "
            f"output: {usage.candidates_token_count}"
        )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保ってLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    print(f"[model] {MODEL}")
    question = args.question
    while True:
        print(f"[質問] {question}\n")
        try:
            print(ask(chat, question))
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            raise SystemExit(1)

        while True:
            try:
                question = input("\n続けて質問できます（終了: exit）> ").strip()
            except EOFError:
                return
            if question.lower() in {"exit", "quit", "q", "/exit"}:
                return
            if question:
                break


if __name__ == "__main__":
    main()
