#!/usr/bin/env python3
import sys

from hooks_common import MATCHER, load_settings, resolve, save_settings


def matcher_entry(pre_tool_use):
    """The PreToolUse entry for our matcher, or None."""
    return next((e for e in pre_tool_use if e.get('matcher') == MATCHER), None)


def already_registered(pre_tool_use, hook_cmd):
    entry = matcher_entry(pre_tool_use)
    return bool(entry) and any(h.get('command') == hook_cmd for h in entry.get('hooks', []))


def register(pre_tool_use, hook_cmd):
    entry = matcher_entry(pre_tool_use)
    if entry is None:
        entry = {'matcher': MATCHER, 'hooks': []}
        pre_tool_use.append(entry)
    entry.setdefault('hooks', []).append({'type': 'command', 'command': hook_cmd})


def main():
    hook_cmd, settings_path = resolve(sys.argv)
    data = load_settings(settings_path)
    pre = data.setdefault('hooks', {}).setdefault('PreToolUse', [])

    if already_registered(pre, hook_cmd):
        print("Aider-Stack hook is already registered in settings.json.")
        return

    register(pre, hook_cmd)
    save_settings(settings_path, data)
    print("Successfully registered PreToolUse hook in settings.json.")


if __name__ == '__main__':
    main()
