# Makefile for learning-langchain.
#
# Every target is a *shortcut* for commands documented step by step in
# REQUIREMENTS.md, docs/TESTING.md and each module's README. Learn the long
# form first (`uv run python 1-fundamentals/1-hello-world.py`, `uv run pytest`,
# `go test ./...`), then use these once you know what they run.
# `make` (or `make help`) lists every target.

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Python example modules, in learning order.
MODULES := 1-fundamentals 2-chains-and-process 3-tools-and-agents 4-rag
# The Go module (5-golang-for-devops) and where `make go-build` writes binaries.
GO_DIR := 5-golang-for-devops
GO_BIN := $(GO_DIR)/bin
# Platforms built by `make go-cross` (GOOS/GOARCH pairs).
GO_PLATFORMS := linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64

# run: one script, e.g. make run SCRIPT=1-fundamentals/1-hello-world.py
SCRIPT ?=
# run-module: one module directory, e.g. make run-module MODULE=4-rag
MODULE ?=
# SKIP_COVERAGE_CHECK=1 makes `make coverage` report without failing below 80%.
SKIP_COVERAGE_CHECK ?=

# Scripts run in numeric order (`sort -n`: 2-... before 10-..., on GNU and BSD/macOS).
# Scripts get no stdin (< /dev/null), so every interactive question takes its
# default answer - the "ENTER = default" pattern - and nothing waits for you.
define run_script
	echo ""; echo "===== $(1) ====="; uv run python "$(1)" < /dev/null
endef

.PHONY: help check sync requirements test coverage lint format typecheck ci \
	run run-module run-all run-offline \
	go-fmt go-vet go-test go-build go-cross go-clean clean

help: ## Show this list of targets
	@echo "Targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-14s %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make run SCRIPT=1-fundamentals/1-hello-world.py   make run-module MODULE=4-rag"
	@echo "  make run-offline                                  LLM_PROVIDER=openai make run-all"

check: ## Check your OS and every required/recommended tool (REQUIREMENTS.md, section 3)
	@bash scripts/check-deps.sh

sync: ## Create .venv and install the Python dependencies from uv.lock
	uv sync

requirements: ## Regenerate requirements.txt (for pip users) from uv.lock
	uv export --format requirements.txt --no-hashes --no-dev -o requirements.txt

# --- Python: quality -----------------------------------------------------------

test: ## Run every Python unit test offline (no API key needed)
	uv run pytest -q

coverage: ## Run the tests with a coverage report (fails below 80%; SKIP_COVERAGE_CHECK=1 to only report)
	uv run pytest --cov --cov-report=term-missing --cov-report=html \
		$(if $(SKIP_COVERAGE_CHECK),--cov-fail-under=0)

lint: ## Lint and check the formatting of every Python file with ruff
	uv run ruff check .
	uv run ruff format --check .

format: ## Format every Python file with ruff (changes files)
	uv run ruff check --fix .
	uv run ruff format .

# Module directories ("1-fundamentals") and scripts ("1-hello-world.py") are
# not valid Python package names, so each script is type-checked on its own.
typecheck: ## Type-check learning_langchain/, tests/ and every example script with mypy
	uv run mypy learning_langchain tests
	@set -e; for module in $(MODULES); do for file in $$module/*.py; do \
		echo "mypy $$file"; uv run mypy --no-error-summary "$$file"; \
	done; done

ci: lint typecheck test go-fmt go-vet go-test ## Everything a pull request must pass (Python and Go)

# --- Python: running the examples ----------------------------------------------

run: ## Run one script: make run SCRIPT=1-fundamentals/1-hello-world.py
	@if [ -z "$(SCRIPT)" ]; then echo "Pick a script: make run SCRIPT=1-fundamentals/1-hello-world.py" >&2; exit 1; fi
	uv run python "$(SCRIPT)"

run-module: ## Run every script of one module, in order: make run-module MODULE=2-chains-and-process
	@if [ -z "$(MODULE)" ]; then echo "Pick a module: make run-module MODULE=1-fundamentals ($(MODULES))" >&2; exit 1; fi
	@set -e; for name in $$(cd $(MODULE) && ls *.py | sort -n); do $(call run_script,$(MODULE)/$$name); done

run-all: ## Run every script of every Python module, in order (uses your .env provider; costs API calls)
	@set -e; for module in $(MODULES); do \
		for name in $$(cd $$module && ls *.py | sort -n); do $(call run_script,$$module/$$name); done; \
	done

run-offline: ## Run every script with LLM_PROVIDER=fake: no API key, no cost, canned answers
	@LLM_PROVIDER=fake $(MAKE) --no-print-directory run-all

# --- Go (5-golang-for-devops) ----------------------------------------------------

go-fmt: ## Fail if any Go file is not gofmt-formatted
	@unformatted="$$(cd $(GO_DIR) && gofmt -l .)"; \
	if [ -n "$$unformatted" ]; then echo "Run 'gofmt -w .' in $(GO_DIR) for:"; echo "$$unformatted"; exit 1; fi

go-vet: ## Run go vet (static analysis shipped with Go)
	cd $(GO_DIR) && go vet ./...

go-test: ## Run every Go test with the race detector and coverage
	cd $(GO_DIR) && go test -race -cover ./...

go-build: ## Build every Go command into 5-golang-for-devops/bin/
	cd $(GO_DIR) && go build -o bin/ ./cmd/...

go-cross: ## Cross-compile every Go command for Linux, macOS and Windows (amd64/arm64)
	@set -e; for platform in $(GO_PLATFORMS); do \
		os=$${platform%/*}; arch=$${platform#*/}; \
		echo "building $$os/$$arch"; \
		(cd $(GO_DIR) && CGO_ENABLED=0 GOOS=$$os GOARCH=$$arch go build -o bin/$$os-$$arch/ ./cmd/...); \
	done

go-clean: ## Delete the Go binaries in 5-golang-for-devops/bin/
	rm -rf $(GO_BIN)

clean: go-clean ## Delete caches and reports (keeps .venv)
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	find . -name __pycache__ -type d -not -path "./.venv/*" -prune -exec rm -rf {} +
