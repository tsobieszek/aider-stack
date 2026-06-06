PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
CLAUDE_DIR ?= $(HOME)/.claude
CLAUDE_SKILLS_DIR = $(CLAUDE_DIR)/skills
CLAUDE_HOOKS_DIR = $(CLAUDE_DIR)/hooks

.PHONY: all install uninstall

all:
	@echo "ai-watch is a shell script stack. Run 'make install' to install to $(BINDIR)."

install:
	mkdir -p $(BINDIR)
	install -m 755 ai-watch $(BINDIR)/ai-watch
	install -m 755 ai-watch-toggle $(BINDIR)/ai-watch-toggle
	# Install global Claude Code skill
	mkdir -p $(CLAUDE_SKILLS_DIR)/aider-stack
	install -m 644 SKILL.md $(CLAUDE_SKILLS_DIR)/aider-stack/SKILL.md
	# Install global Claude Code hook
	mkdir -p $(CLAUDE_HOOKS_DIR)
	install -m 755 aider-stack-confirm.py $(CLAUDE_HOOKS_DIR)/aider-stack-confirm.py
	python3 install-hooks.py "$(CLAUDE_HOOKS_DIR)/aider-stack-confirm.py" "$(CLAUDE_DIR)/settings.json"

uninstall:
	rm -f $(BINDIR)/ai-watch
	rm -f $(BINDIR)/ai-watch-toggle
	# Uninstall global Claude Code skill
	rm -f $(CLAUDE_SKILLS_DIR)/aider-stack/SKILL.md
	rmdir $(CLAUDE_SKILLS_DIR)/aider-stack 2>/dev/null || true
	# Uninstall global Claude Code hook
	rm -f $(CLAUDE_HOOKS_DIR)/aider-stack-confirm.py
	python3 uninstall-hooks.py "$(CLAUDE_HOOKS_DIR)/aider-stack-confirm.py" "$(CLAUDE_DIR)/settings.json"

