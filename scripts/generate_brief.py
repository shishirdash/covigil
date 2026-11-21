"""Starter: one model call that turns the three sources into a brief with flags.

Untested: written without an API key. Run from the repo root:
    python scripts/generate_brief.py > out.json
"""
import base64
import json
import pathlib
import re
import sys

import anthropic

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "claude-fable-5-2"


def system_prompt() -> str:
    text = (ROOT / "prompts" / "brief_prompt.md").read_text()
    start = text.index("## System prompt") + len("## System prompt")
    end = text.index("## Second pass")
    return text[start:end].strip()


def main() -> None:
    pdf = base64.standard_b64encode((ROOT / "data" / "outside_records_fax.pdf").read_bytes()).decode()
    fills = (ROOT / "data" / "pharmacy_fills.csv").read_text()
    intake = (ROOT / "data" / "intake_form.md").read_text()

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    message = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=system_prompt(),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {"type": "base64", "media_type": "application/pdf", "data": pdf},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"<pharmacy_fills>\n{fills}\n</pharmacy_fills>\n\n"
                            f"<intake_form>\n{intake}\n</intake_form>\n\n"
                            "The visit is on 2026-11-23. Write the pre-visit brief as JSON."
                        ),
                    },
                ],
            }
        ],
    )
    raw = "".join(block.text for block in message.content if block.type == "text")
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        sys.exit("No JSON in the model reply:\n" + raw)
    print(json.dumps(json.loads(match.group(0)), indent=2))


if __name__ == "__main__":
    main()
