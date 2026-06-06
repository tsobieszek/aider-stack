#!/usr/bin/env python3
import json
import os
import re
import sys

# Prefix ai-watch prepends to every dispatch it submits to Claude.
DISPATCH_MARKER = "aider-stack: "
FILE_KEYS = ("file_path", "TargetFile", "path", "target_file", "filepath", "notebook_path")


def log_err(msg):
    print(msg, file=sys.stderr)


def load_payload():
    try:
        return json.loads(sys.stdin.read())
    except Exception as e:
        log_err(f"Failed to parse stdin payload: {e}")
        sys.exit(0)  # Safe default: allow


def target_from_input(tool_input):
    """Best-effort path the tool intends to edit, or None."""
    for key in FILE_KEYS:
        val = tool_input.get(key)
        if isinstance(val, str):
            return val
    for val in tool_input.values():
        if isinstance(val, str) and (val.startswith("/") or val.startswith(".")):
            return val
    return None


def message_text(entry):
    """Plain text of a transcript 'user' entry; '' for tool-result-only messages."""
    if entry.get("type") != "user":
        return ""
    content = entry.get("message", {}).get("content", "")
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content
                        if isinstance(c, dict) and c.get("type") == "text")
    return str(content)


def last_user_prompt(transcript_path):
    """Most recent genuine user text, skipping tool-result messages.

    Walks the transcript from the end so a multi-edit turn keeps seeing the
    dispatch instead of an intervening (empty) tool-result message.
    """
    if not (transcript_path and os.path.exists(transcript_path)):
        return ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        log_err(f"Error reading transcript: {e}")
        return ""
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            text = message_text(json.loads(line))
        except Exception:
            continue
        if text.strip():
            return text
    return ""


def is_dispatch(prompt):
    """True only for ai-watch dispatches: they begin with the dispatch marker."""
    return prompt.lstrip().startswith(DISPATCH_MARKER)


def is_listed(prompt, abs_target):
    """True if abs_target is explicitly listed after an EDIT: marker."""
    rel_path = os.path.relpath(abs_target, os.getcwd())
    pattern = (r"EDIT:\s*(?:\./)?(?:" + re.escape(abs_target) + r"|"
               + re.escape(rel_path) + r")(?=[\r\n\s]|$)")
    return re.search(pattern, prompt) is not None


def block_unlisted(target_file):
    """Block the edit (exit 2); stderr is relayed to Claude for the user to act on."""
    log_err(f"[aider-stack] Edit to {target_file} blocked: this file is not listed "
            f"in the current ai-watch dispatch (no matching EDIT: marker). "
            f"Reply to approve it, or add it to the dispatch.")
    sys.exit(2)


def main():
    payload = load_payload()
    target_file = target_from_input(payload.get("tool_input", {}))
    if not target_file:
        sys.exit(0)

    prompt = last_user_prompt(payload.get("transcript_path", ""))
    if not is_dispatch(prompt):
        sys.exit(0)  # Not an ai-watch dispatch: do not interfere.

    if is_listed(prompt, os.path.abspath(target_file)):
        sys.exit(0)

    block_unlisted(target_file)


if __name__ == "__main__":
    main()
