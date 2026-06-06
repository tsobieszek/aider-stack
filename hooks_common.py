#!/usr/bin/env python3
"""Shared helpers for the install/uninstall hook scripts.

Used only at install time (run from the project tree); the runtime hook
``aider-stack-confirm.py`` does not depend on this module.
"""
import json
import os

MATCHER = 'Edit|Write|MultiEdit|NotebookEdit'
DEFAULT_HOOK = '~/.claude/hooks/aider-stack-confirm.py'
DEFAULT_SETTINGS = '~/.claude/settings.json'


def resolve(argv):
    """(hook_command, settings_path) from argv, honouring CLAUDE_DIR overrides."""
    hook = argv[1] if len(argv) > 1 else DEFAULT_HOOK
    settings = argv[2] if len(argv) > 2 else DEFAULT_SETTINGS
    return os.path.abspath(os.path.expanduser(hook)), os.path.expanduser(settings)


def load_settings(path):
    """Parsed settings.json, or an empty config when the file is absent."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_settings(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
