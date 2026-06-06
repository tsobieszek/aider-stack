#!/usr/bin/env python3
import os
import sys

from hooks_common import load_settings, resolve, save_settings


def prune(pre_tool_use, hook_cmd):
    """PreToolUse list with hook_cmd removed; matcher entries left empty are dropped.

    Entries without a 'hooks' key are unrelated/foreign and left untouched.
    """
    out = []
    for entry in pre_tool_use:
        hooks = entry.get('hooks')
        if hooks is None:
            out.append(entry)
            continue
        kept = [h for h in hooks if h.get('command') != hook_cmd]
        if kept:
            out.append({**entry, 'hooks': kept})
    return out


def drop_empty(data):
    """Remove now-empty PreToolUse / hooks containers."""
    if not data['hooks'].get('PreToolUse'):
        data['hooks'].pop('PreToolUse', None)
    if not data['hooks']:
        del data['hooks']


def main():
    hook_cmd, settings_path = resolve(sys.argv)
    if not os.path.exists(settings_path):
        return

    data = load_settings(settings_path)
    pre = data.get('hooks', {}).get('PreToolUse')
    if not pre:
        return

    new_pre = prune(pre, hook_cmd)
    if new_pre == pre:
        return

    data['hooks']['PreToolUse'] = new_pre
    drop_empty(data)
    save_settings(settings_path, data)
    print("Successfully unregistered PreToolUse hook from settings.json.")


if __name__ == '__main__':
    main()
