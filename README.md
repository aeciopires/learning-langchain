<!-- TOC -->

- [learning-langchain](#learning-langchain)
  - [Setup and running scripts](#setup-and-running-scripts)
  - [Contributing](#contributing)
  - [Repository structure](#repository-structure)
  - [Resource to learn LangChain](#resource-to-learn-langchain)
  - [Developer](#developer)
  - [License](#license)

<!-- TOC -->

# learning-langchain

A personal learning repository for LangChain in Python. It is not a package or service — it's a collection of small, standalone, runnable scripts organized progressively by topic. There is no test suite, linter config, or build system.

## Setup and running scripts

See [INSTALL_SOFTWARES.md](INSTALL_SOFTWARES.md) for instructions on installing dependencies and running the scripts.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute to this repository.

## Repository structure

Directories are numbered learning modules; files within each are numbered in the order they should be read/run, each building on concepts from the previous one.

```
.
├── 1-fundamentals/            # Basic model initialization and prompt templates
│   ├── 1-hello-world.py
│   ├── 2-init-chat-model.py
│   ├── 3-prompt-template.py
│   └── 4-chat-prompt-template.py
├── 2-chains-and-process/       # LCEL chains, RunnableLambda, @chain decorator, map-reduce pipeline
│   ├── 1-starting-chain.py
│   ├── 2-chains-with-decorators.py
│   ├── 3-runnable-lambda.py
│   ├── 4-chain-of-translate.py
│   └── 5-sumarization-map-reduce-pipeline.py
├── 3-tools-and-agents/         # Tool-calling agents built with langchain.agents.create_agent
│   └── 1-agent-review.py
├── requirements.txt            # Python dependencies
├── .env.example                 # Template for API key configuration (copy to .env)
├── CLAUDE.md                    # Guidance for Claude Code when working in this repository
├── CONTRIBUTING.md              # How to contribute to this repository
├── INSTALL_SOFTWARES.md         # Environment setup and how to run the scripts
└── README.md
```

## Resource to learn LangChain

Github repos: 

- https://github.com/langchain-ai/langchain
- https://github.com/Nasiko-Labs/nasiko 


Site/Blogs:

- https://docs.langchain.com/oss/python/langchain/quickstart
- https://smith.langchain.com/hub/search?organizationId=dda3b4b9-812c-4344-837c-8f72d2e9661d
- https://www.langchain.com/
- https://docs.smith.langchain.com/
- https://docs.langchain.com/oss/python/langchain/overview
- https://www.youtube.com/watch?v=J7j5tCB_y4w 
- https://pythonacademy.com.br/blog/o-que-e-e-como-funciona-o-langchain
- https://www.udemy.com/course/langchain-desenvolva-agentes-e-aplicacoes-ia-com-llms
- https://docs.langchain.com/oss/python/learn
- https://blog.jetbrains.com/pycharm/2026/02/langchain-tutorial-2026/
- https://academy.langchain.com/courses/foundation-introduction-to-langchain-python
- https://latenode.com/blog/ai-frameworks-technical-infrastructure/langchain-setup-tools-agents-memory/langchain-python-tutorial-complete-beginners-guide-to-getting-started
- https://academy.langchain.com/courses/langchain-essentials-python
- https://ricardo-reis.medium.com/langchain-guia-de-in%C3%ADcio-r%C3%A1pido-138284ec8681
- https://www.datacamp.com/tutorial/building-langchain-agents-to-automate-tasks-in-python
- https://academy.langchain.com/courses/intro-to-langgraph 

AI Tools and Agents:

- https://www.promptingguide.ai/ 
- https://docs.anthropic.com/en/docs/claude-code/skills
- https://docs.anthropic.com/en/docs/claude-code/overview
- https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
- https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills
- https://www.skills.sh/ 
- https://mcpserverhub.com/
- https://mcp-catalog.com/
- https://hub.docker.com/mcp 

## Developer

Aecio dos Santos Pires
- Linkedin: https://www.linkedin.com/in/aeciopires/
- Site: http://aeciopires.com/

## License

GNU General Public License v3.0
