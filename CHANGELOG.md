<!-- TOC -->

- [Changelog](#changelog)
  - [\[0.2.0\] - 2026-10-04](#020---2026-10-04)
    - [Adicionado](#adicionado)
    - [Alterado](#alterado)
    - [Removido](#removido)
  - [\[0.1.0\] - versão inicial](#010---versão-inicial)

<!-- TOC -->

# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.
O formato segue, de forma simplificada, o
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [0.2.0] - 2026-10-04

### Adicionado

- Gerenciamento de ferramentas e dependências com **mise** (`mise.toml`:
  Python 3.14, uv 0.12, Go 1.27) e **uv** (`pyproject.toml`, `uv.lock`,
  `.python-version`), com versões fixadas: `langchain==1.4.3`,
  `langchain-core==1.6.6`, `langchain-google-genai==4.4.0`,
  `langchain-openai==1.6.7`, `langchain-text-splitters==1.1.3`,
  `numpy==2.5.3`, `python-dotenv==1.2.4`; grupo `dev` com pytest,
  pytest-cov, ruff e mypy.
- `Makefile` com atalhos para rodar scripts em massa (`run`, `run-module`,
  `run-all`, `run-offline`), testes, cobertura, lint, typecheck, `ci` e o
  módulo Go (`go-test`, `go-vet`, `go-fmt`, `go-build`, `go-cross`).
- `scripts/check-deps.sh` (`make check`): confere SO (Ubuntu 22.04/24.04/26.04,
  macOS 13+, WSL2), ferramentas e `.env`.
- Pacote `learning_langchain/`: `config.py` (variáveis `LLM_*` validadas),
  `models.py` (`get_chat_model()` com `init_chat_model()`, `get_embeddings()`,
  `FakeToolCallingModel`), `cli.py` (padrão "ENTER = padrão" também sem
  `stdin`), `rag.py`.
- **Modo offline** `LLM_PROVIDER=fake`: todos os scripts rodam sem chave de
  API e sem custo, com o modelo falso do LangChain.
- Novos scripts: `1-fundamentals/5-messages.py`, `6-streaming-and-batch.py`;
  `2-chains-and-process/6-output-parsers.py`, `7-structured-output.py`,
  `8-runnable-parallel.py`; `3-tools-and-agents/1-first-tool.py`,
  `2-simple-agent.py`, `3-agent-with-memory.py`.
- Novo módulo `4-rag/` (documentos, splitters, embeddings, vector store,
  RAG como chain e como agente) com runbooks fictícios como base de
  conhecimento.
- Novo módulo `5-golang-for-devops/` (Go 1.27, só biblioteca padrão):
  `healthcheck`, `portcheck`, `certcheck`, `logstats`, `envcheck`, com testes
  *table-driven*, `httptest` e detector de *race conditions*.
- Testes Python em `tests/` (pytest, offline), incluindo um *smoke test* que
  roda o `main()` de todos os scripts; cobertura mínima de 80%.
- Documentação em pt-BR, com analogias e diagramas Mermaid: README de cada
  módulo, `REQUIREMENTS.md`, `docs/LEARNING-PATH.md`, `docs/CONCEPTS.md`,
  `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `docs/TROUBLESHOOTING.md`.
- `CHANGELOG.md`.

### Alterado

- `README.md`, `CONTRIBUTING.md` e `CLAUDE.md` reescritos em pt-BR, com as
  regras do repositório (não inventar, fontes oficiais, testes, formatação).
- Scripts existentes reorganizados em funções `build_*()` + `main()` para
  serem testáveis, usando `get_chat_model()` e `message.text` (no lugar da
  função `extract_text()` própria).
- Modelo padrão do Gemini: `gemini-2.5-flash` -> `gemini-3.7-flash`
  (configurável com `LLM_MODEL`).
- `3-tools-and-agents/1-agent-review.py` renomeado para `4-agent-review.py`.
- `requirements.txt` agora é gerado a partir do `uv.lock` (`make requirements`).
- `.gitignore` e `.env.example` simplificados e atualizados.

### Removido

- `INSTALL_SOFTWARES.md` (conteúdo incorporado ao `REQUIREMENTS.md`).
- Dependências não usadas pelos scripts: `beautifulsoup4` e `pypdf`.

## [0.1.0] - versão inicial

- Scripts dos módulos `1-fundamentals/`, `2-chains-and-process/` e
  `3-tools-and-agents/` (agente revisor de código), `requirements.txt`,
  `INSTALL_SOFTWARES.md`, `CONTRIBUTING.md` e `CLAUDE.md`.
