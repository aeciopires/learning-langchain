<!-- TOC -->

- [CLAUDE.md](#claudemd)
  - [1. Sobre este repositório](#1-sobre-este-repositório)
  - [2. Estrutura de diretórios e arquivos](#2-estrutura-de-diretórios-e-arquivos)
  - [3. O contrato de cada script e de cada módulo](#3-o-contrato-de-cada-script-e-de-cada-módulo)
  - [4. Não invente: o guardrail principal](#4-não-invente-o-guardrail-principal)
  - [5. Idiomas](#5-idiomas)
  - [6. Configuração e segredos (inegociável)](#6-configuração-e-segredos-inegociável)
  - [7. Fatos da biblioteca específicos deste repositório](#7-fatos-da-biblioteca-específicos-deste-repositório)
  - [8. Convenções de Markdown](#8-convenções-de-markdown)
  - [9. Convenções de Python](#9-convenções-de-python)
  - [10. Convenções de Go](#10-convenções-de-go)
  - [11. Fluxo ao adicionar ou alterar conteúdo](#11-fluxo-ao-adicionar-ou-alterar-conteúdo)
  - [12. O que não fazer](#12-o-que-não-fazer)
  - [13. Notas de ambiente](#13-notas-de-ambiente)

<!-- TOC -->

# CLAUDE.md

Guia para quem mantém ou amplia este repositório - pessoas ou assistentes
de IA como o Claude Code. Leia antes de adicionar ou editar conteúdo.

## 1. Sobre este repositório

`learning-langchain` é uma trilha de estudo **pública e para iniciantes** de
LangChain com Python - do primeiro `invoke()` a agentes e RAG - mais um
módulo de Go para o dia a dia de DevOps/Cloud. Não é um pacote nem um
serviço: são scripts pequenos, numerados, executáveis e testados, cada um
ensinando um conceito, com README por módulo (explicação, analogias,
diagramas, exemplos, testes, erros comuns, referências oficiais).

Ferramentas: [uv](https://docs.astral.sh/uv/) (dependências Python),
[mise](https://mise.jdx.dev) (versões de Python, uv e Go), `Makefile`
(atalhos). Todo script roda **offline** com `LLM_PROVIDER=fake`.

Licença GPL-3.0. Não altere o `LICENSE` sem pedido explícito.

## 2. Estrutura de diretórios e arquivos

```
.
├── README.md / REQUIREMENTS.md / CONTRIBUTING.md / CHANGELOG.md / CLAUDE.md / LICENSE
├── pyproject.toml          # pinned dependencies, dev group, ruff/mypy/pytest/coverage config
├── uv.lock                 # exact versions - regenerate with `uv lock`
├── requirements.txt        # GENERATED from uv.lock (`make requirements`) - never edit by hand
├── .python-version         # 3.14
├── mise.toml               # python 3.14, uv 0.12, go 1.27
├── Makefile                # shortcuts - REQUIREMENTS.md section 6
├── .env.example            # every LLM_* variable and API key slot
├── scripts/check-deps.sh   # `make check`
├── learning_langchain/     # config.py, models.py, cli.py, rag.py (installed by uv sync)
├── 1-fundamentals/ 2-chains-and-process/ 3-tools-and-agents/ 4-rag/   # numbered scripts + README.md
├── 5-golang-for-devops/    # Go module: cmd/<tool>/main.go + internal/<pkg>/ + tests
├── docs/                   # LEARNING-PATH, CONCEPTS, ARCHITECTURE, TESTING, TROUBLESHOOTING
└── tests/                  # conftest.py, _helpers.py, unit/test_*.py
```

Diretórios são módulos numerados; arquivos dentro deles são numerados na
ordem de leitura. Um script novo vai para o módulo a que pertence
conceitualmente, com o próximo número livre; um tema realmente novo ganha
um novo diretório numerado. **Nunca renumere** o que já existe.

## 3. O contrato de cada script e de cada módulo

Cada script Python (veja [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#o-contrato-de-cada-script)):

1. Docstring do módulo com o objetivo e o comando `uv run python ...`.
2. `from dotenv import load_dotenv` + `load_dotenv()` logo após os imports,
   quando usa um modelo.
3. O modelo vem de `learning_langchain.models.get_chat_model(fake_responses=[...])`
   (embeddings: `get_embeddings()`), nunca de uma classe de provedor fixa -
   exceto em `1-fundamentals/2-init-chat-model.py`, que ensina exatamente isso.
4. `fake_responses` reproduz o caminho de um modelo real (inclusive
   `AIMessage` com `tool_calls` em agentes e saída estruturada).
5. Funções `build_*(model)` que os testes usam; a parte interativa e os
   `print` ficam em `main()`, protegido por `if __name__ == "__main__":`.
6. Perguntas interativas com `learning_langchain.cli.ask()`/`ask_yes_no()`
   (ENTER ou falta de `stdin` = padrão documentado).
7. Comentários explicam o **objetivo** de cada etapa (o que um prompt,
   `RunnableLambda` ou ferramenta faz e por quê) - é material didático.
8. Um teste em `tests/unit/test_N_<modulo>.py`; o *smoke test*
   `test_all_scripts_run.py` roda o `main()` automaticamente.

Cada README de módulo tem, nesta ordem: Visão geral, O que você vai
aprender, Arquitetura (Mermaid + versão em texto em `<details>`), Conceitos
com analogias, Os scripts, Como executar, Exemplos de código, Testes, Erros
comuns, Referências (só fontes oficiais).

**Cobertura: nunca abaixo de 80%** (`make coverage`); hoje está perto de 97%.

## 4. Não invente: o guardrail principal

1. **Toda classe, função, parâmetro, comando, nome de modelo, versão e
   comportamento vem de uma fonte consultada** - a documentação oficial do
   LangChain ([docs.langchain.com](https://docs.langchain.com), cujo fonte é
   [langchain-ai/docs](https://github.com/langchain-ai/docs)), a
   [referência da API](https://reference.langchain.com/python/), o código
   dos pacotes instalados em `.venv/`, a documentação do provedor (Google,
   OpenAI), do Go ([go.dev](https://go.dev), [pkg.go.dev](https://pkg.go.dev)),
   do uv e do mise. Não da memória.
2. **Verifique executando.** Um exemplo de código ou uma saída só entra em
   um README depois de rodar (com `LLM_PROVIDER=fake` ou um provedor real);
   saídas de exemplo são copiadas da execução, não escritas à mão.
3. **Números e versões são o conteúdo mais arriscado** (versões de pacotes,
   nomes de modelos, preços, limites, contagens): confira a fonte atual,
   cite a data ("outubro de 2026") e diga que podem mudar.
4. **Comportamento observado, não presumido**: quando uma biblioteca aceita
   algo mas não faz (ex.: `set_verbose` em LCEL, `temperature` em `gpt-5`),
   diga isso e cite onde foi observado.
5. Conteúdo de terceiros (blogs, cursos) pode usar APIs anteriores ao
   LangChain 1.0 - nunca copie código de lá sem conferir na fonte oficial.
6. Se uma página não carrega, tente outra URL oficial (ou o repositório de
   origem no GitHub); se algo continuar sem verificação, deixe de fora ou
   diga explicitamente que não foi verificado.
7. Dados de exemplo (runbooks, logs, inventário de serviços) são
   **fictícios** e dizem isso; não use nomes de empresas reais.

## 5. Idiomas

- **Documentação** (READMEs, `docs/`, `REQUIREMENTS.md`, `CONTRIBUTING.md`,
  `CHANGELOG.md`, este arquivo): **pt-BR**.
- **Código, comentários, docstrings, mensagens impressas pelos scripts,
  nomes de testes e mensagens de commit**: **en-US**.
- Termos técnicos consagrados ficam em inglês, em itálico na primeira vez
  quando ajudar (*chunk*, *embeddings*, *rate limit*).

## 6. Configuração e segredos (inegociável)

- Tudo configurável é variável de ambiente com padrão, lida e validada em
  `learning_langchain/config.py` com uma mensagem que cita a variável
  (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_EMBEDDING_MODEL`, `LLM_TEMPERATURE`).
  Variável nova: `.env.example`, `config.py`, teste em `test_config.py` e a
  tabela de [`REQUIREMENTS.md`, seção 5.1](REQUIREMENTS.md#51---variáveis-de-configuração).
- Nunca faça commit de chaves; o `.env` está no `.gitignore`.
- Testes nunca chamam um provedor real: a fixture automática em
  `tests/conftest.py` força `LLM_PROVIDER=fake`.

## 7. Fatos da biblioteca específicos deste repositório

A pilha instalada é **LangChain 1.x** (`langchain==1.4.3`,
`langchain-core==1.6.6`). Não presuma que APIs de tutoriais anteriores ao
1.0 funcionam:

- `langchain.chains` (classes legadas como `load_summarize_chain`) **não
  existe**. Use LCEL (`prompt | model`, `RunnableLambda`, `@chain`) - veja
  `2-chains-and-process/5-sumarization-map-reduce-pipeline.py`.
- Agentes: `langchain.agents.create_agent(model, tools, system_prompt=...)`
  devolve um grafo compilado do LangGraph. Invoque com
  `agent.invoke({"messages": [...]})`; a resposta é `result["messages"][-1]`.
  Memória: `checkpointer=InMemorySaver()` + `config={"configurable": {"thread_id": ...}}`.
- `langchain_core.globals.set_verbose(True)` **não tem efeito visível** em
  LCEL/agentes. Use `set_debug(True)` - é o que "modo verbose" significa
  neste repositório.
- `AIMessage.content` pode ser `str` ou uma lista de *content blocks*
  (Gemini). Use a propriedade **`message.text`** (só o texto; `.text()` como
  método está depreciado desde o `langchain-core` 1.0).
- `GenericFakeChatModel` não implementa `bind_tools()`; para `create_agent` e
  `with_structured_output()` offline use `FakeToolCallingModel`
  (`learning_langchain/models.py`).
- `StrOutputParser` devolve um `TextAccessor` (subclasse de `str`).
- `InMemoryVectorStore` e `DeterministicFakeEmbedding` precisam de `numpy`.
- `langchain-openai`: modelos `gpt-5` (exceto `gpt-5-chat`) só aceitam
  `temperature=1`; outro valor é descartado.
- Para listar modelos Gemini: `from google import genai;
  genai.Client().models.list()`, filtrando `"generateContent" in
  model.supported_actions` (`3-tools-and-agents/4-agent-review.py`).
- `init_chat_model("provedor:modelo", **kwargs)`; padrões:
  `google_genai:gemini-3.7-flash` e `openai:gpt-5-nano` (configuráveis).

## 8. Convenções de Markdown

- TOC manual entre marcadores `<!-- TOC -->` no topo de todo arquivo com
  mais de ~3 seções, uma entrada por título `##`/`###`.
- Âncoras seguem a regra do GitHub: minúsculas; remove tudo exceto letras
  (inclusive acentuadas), dígitos, espaços, `-` e `_`; espaços viram `-`.
  Confira toda âncora depois de renomear um título.
- Só links relativos dentro do repositório.
- Tabelas para comparações; todo README termina com `## Referências`
  (só fontes oficiais).
- **Diagramas em Mermaid** (blocos ` ```mermaid `, que o GitHub renderiza) -
  sem arquivos de imagem para manter sincronizados. Só `flowchart` e
  `sequenceDiagram`; rótulos entre aspas duplas, `<br/>` para quebra de
  linha, e nenhum id de nó que seja palavra reservada do Mermaid (`end`,
  `call`, `click`, `class`, `style`, ...). Renderize antes do commit (por
  exemplo `npx -p @mermaid-js/mermaid-cli mmdc -i diagrama.mmd -o diagrama.svg`).
- O diagrama de "Arquitetura" de um módulo é seguido da versão em texto em
  `<details><summary>Versão em texto</summary>` - mantenha os dois iguais.
- Todo conceito difícil ganha uma **analogia** em um bloco `> **Analogia:**`.
- Comandos copiáveis, com a saída esperada quando ajudar (copiada de uma
  execução real).

## 9. Convenções de Python

- `from __future__ import annotations` e anotações de tipo no pacote
  `learning_langchain/`; `make typecheck` (mypy) precisa passar.
- `make lint` (ruff: lint + formatação, linha de até 110 caracteres).
- Tudo roda via `uv run`; dependências novas com versão fixada em
  `pyproject.toml`, depois `uv lock`, `uv sync`, `make requirements`.

## 10. Convenções de Go

- Só biblioteca padrão, a menos que haja um motivo forte (e uma biblioteca
  oficial do fornecedor).
- `cmd/<ferramenta>/main.go` só lê *flags*, imprime e define o código de
  saída (0 ok, 1 falha de checagem, 2 uso incorreto); a lógica fica em
  `internal/<pacote>/` com testes *table-driven*.
- `make go-fmt go-vet go-test` precisam passar (`go test -race`).
- A versão do Go fica igual em `mise.toml` e no `go.mod` (`go` + `toolchain`).

## 11. Fluxo ao adicionar ou alterar conteúdo

1. Leia o README do módulo e um script vizinho.
2. Consulte a fonte oficial de cada API que vai usar (seção 4).
3. Escreva o script seguindo o contrato (seção 3); rode com
   `LLM_PROVIDER=fake` e, se possível, com um provedor real.
4. Escreva os testes; `uv run pytest tests/unit/test_N_<modulo>.py -v`;
   quebre o código de propósito e confirme que o teste falha.
5. Atualize o README do módulo (copie as saídas reais), `docs/LEARNING-PATH.md`,
   `README.md` e `CHANGELOG.md`; `docs/TROUBLESHOOTING.md` quando houver um
   novo modo de falha.
6. `make ci` e `make coverage`.
7. Git: branch padrão `main`; **não faça commit nem push sem pedido explícito**.

## 12. O que não fazer

- Não invente classe, parâmetro, comando, nome de modelo, versão, preço ou
  comportamento.
- Não use `langchain.chains` nem APIs anteriores ao LangChain 1.0.
- Não chame um provedor real nos testes; não faça commit de chaves.
- Não fixe o provedor no código dos scripts - use `get_chat_model()`.
- Não edite `requirements.txt` à mão.
- Não deixe a cobertura cair abaixo de 80%, nem âncoras quebradas ou TOC
  desatualizado.
- Não substitua um comando longo documentado por um target do `make` - os
  targets são atalhos opcionais.
- Não escreva documentação em inglês nem código/comentários em português.
- Não faça commit nem push sem ser pedido.

## 13. Notas de ambiente

Não há pipeline de CI configurado; `make ci` reúne as checagens. O primeiro
`uv sync` precisa de acesso ao PyPI; `mise install` baixa Python, uv e Go
da internet; os scripts com provedor real precisam de acesso à API do
Google ou da OpenAI. Testes e `make run-offline` não usam a rede.

Scripts interativos rodam sem terminal com `< /dev/null` (todas as
perguntas recebem o padrão), por exemplo:
`LLM_PROVIDER=fake uv run python 3-tools-and-agents/4-agent-review.py < /dev/null`.
