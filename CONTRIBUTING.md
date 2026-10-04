<!-- TOC -->

- [Contribuindo](#contribuindo)
  - [Antes de começar](#antes-de-começar)
  - [Fluxo com fork e branch](#fluxo-com-fork-e-branch)
  - [Checklist de um pull request](#checklist-de-um-pull-request)
  - [Adicionando um novo script ou módulo](#adicionando-um-novo-script-ou-módulo)
  - [Sobre o VS Code](#sobre-o-vs-code)

<!-- TOC -->

# Contribuindo

## Antes de começar

- Prepare o ambiente com [`REQUIREMENTS.md`](REQUIREMENTS.md) (`make check`,
  `mise install`, `uv sync`).
- Leia as regras do repositório em [`CLAUDE.md`](CLAUDE.md) - valem para
  pessoas e para assistentes de IA. A principal: **não invente**. Toda API,
  parâmetro, comando, versão ou comportamento vem de uma fonte oficial
  consultada e de código executado.
- Documentação em **pt-BR**; código e comentários em **en-US**.

> Configure a autenticação SSH na sua conta do GitHub para usar o protocolo
> SSH em vez de HTTPS. Veja a
> [documentação do GitHub](https://docs.github.com/authentication/connecting-to-github-with-ssh).

## Fluxo com fork e branch

- Crie um *fork* deste repositório.
- Clone o fork:

```bash
git clone URL_DO_SEU_FORK
```

- Adicione o repositório original como `upstream`:

```bash
git remote -v
git remote add upstream git@github.com:aeciopires/learning-langchain.git
git remote -v
```

- Crie uma branch:

```bash
git checkout -b NOME_DA_BRANCH
```

- Confira que está na branch certa (ela aparece com `*`):

```bash
git branch
```

- Faça as mudanças e os testes ([checklist abaixo](#checklist-de-um-pull-request)).
- Faça commit e envie a branch:

```bash
git push --set-upstream origin NOME_DA_BRANCH
```

- Abra um *pull request* para a branch `main`
  ([como criar um PR a partir de um fork](https://docs.github.com/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)).
- Atualize o conteúdo com as sugestões da revisão, se houver.
- Depois do merge, atualize o seu clone e apague a branch:

```bash
git checkout main
git pull upstream main
git branch -d NOME_DA_BRANCH
git push origin main
git push --delete origin NOME_DA_BRANCH
```

- Para manter o fork sincronizado:

```bash
git pull upstream main
git push origin main
```

Referência: https://blog.scottlowe.org/2015/01/27/using-fork-branch-git-workflow/

## Checklist de um pull request

- [ ] `make ci` passa (ruff, mypy, pytest, gofmt, go vet, go test).
- [ ] `make coverage` continua acima de 80%.
- [ ] `make run-offline` roda todos os scripts sem erro.
- [ ] Todo script novo tem teste; você quebrou o código de propósito e viu
      o teste falhar.
- [ ] Todo fato novo na documentação (API, versão, comando, comportamento)
      tem fonte oficial nas Referências e foi executado.
- [ ] TOC atualizado e âncoras conferidas; diagramas Mermaid renderizam.
- [ ] [`CHANGELOG.md`](CHANGELOG.md) atualizado.
- [ ] Mudou uma dependência? `uv lock`, `uv sync` e `make requirements`.

## Adicionando um novo script ou módulo

1. Coloque o script no módulo a que ele pertence conceitualmente, com o
   próximo número livre (`5-...py`); um tema realmente novo ganha um novo
   diretório numerado.
2. Siga o contrato de [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#o-contrato-de-cada-script):
   `build_*(model)`, `main()`, `fake_responses` para o modo offline.
3. Escreva os testes ([`docs/TESTING.md`](docs/TESTING.md#escrevendo-um-teste-para-um-novo-script-passo-a-passo)).
4. Atualize o README do módulo, [`docs/LEARNING-PATH.md`](docs/LEARNING-PATH.md),
   o [`README.md`](README.md) e o [`CHANGELOG.md`](CHANGELOG.md).
5. Um módulo novo também entra em `MODULES` no [`Makefile`](Makefile), em
   `source` do `[tool.coverage.run]` no [`pyproject.toml`](pyproject.toml)
   e em `MODULE_DIRS` de `tests/unit/test_all_scripts_run.py`.

## Sobre o VS Code

Use o editor ou IDE que preferir; o [VS Code](https://code.visualstudio.com)
com as extensões listadas em
[`REQUIREMENTS.md`, seção 3.5](REQUIREMENTS.md#35---editor-opcional) ajuda a
pré-visualizar o Markdown, conferir a sintaxe e gerar o sumário
automaticamente.

Temas para o VS Code:

- https://vscodethemes.com/
- https://code.visualstudio.com/docs/getstarted/themes
