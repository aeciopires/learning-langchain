<!-- TOC -->

- [Ubuntu](#ubuntu)
  - [Requirements](#requirements)
  - [LangChaing](#langchaing)
  - [Configure the Google AI Studio API Key](#configure-the-google-ai-studio-api-key)
  - [Configure the OpenAI API Key](#configure-the-openai-api-key)
  - [Configure the .env file](#configure-the-env-file)
  - [Run the applications](#run-the-applications)

<!-- TOC -->

# Ubuntu

## Requirements

Run the following commands on Ubuntu 24.04/22.02:

```bash
sudo apt install -y git curl wget openssl net-tools python3 python3-pip python3-venv jq make
```

With Python "3.10.*", run the following command to create the symbolic link:

```bash
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
```

With Python "3.12.*", run the following command to create the symbolic link:

```bash
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
```

Install the following softwares:

- Google Chrome
- WPS: https://br.wps.com/download/
- Visual Code: https://code.visualstudio.com
  - Ubuntu: https://code.visualstudio.com/docs/setup/linux
  - Plugins:
  - Export/import of the plugins: https://stackoverflow.com/questions/35773299/how-can-you-export-the-visual-studio-code-extension-list
  - gitlens: https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens (Requer instalação do comando git mostrado na seção a anterior).
  - Markdown-all-in-one: https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one
  - Markdown-lint: https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint
  - Markdown-toc: https://marketplace.visualstudio.com/items?itemName=CharlesWan.markdown-toc
  - python: https://marketplace.visualstudio.com/items?itemName=ms-python.python 
  - YAML: https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml
  - Count lines number: https://marketplace.visualstudio.com/items?itemName=gurumukhi.selected-lines-count
  - Theme for VSCode:
    - https://code.visualstudio.com/docs/getstarted/themes
    - https://dev.to/thegeoffstevens/50-vs-code-themes-for-2020-45cc
    - https://vscodethemes.com/

## LangChaing

Creating the VirtualEnvironment and install requirements:

```bash
# Access repository directory
cd learning-langchain/

# Creating the virtual environment
python -m venv venv

# Activating the virtual environment
source venv/bin/activate

# Install first requirements
pip install langchain langchain-openai langchain-google-genai python-dotenv beautifulsoup4 pypdf

# Save the requirements list
pip freeze > requirements.txt
```

## Configure the Google AI Studio API Key

Follow the instructions of the page: https://ai.google.dev/gemini-api/docs/get-started

## Configure the OpenAI API Key

Follow the instructions of the page: https://developers.openai.com/api/docs/quickstart

## Configure the .env file

Copy the `.env.example` file to `.env` and fill in the values of the API keys:

```bash
cp .env.example .env
```

## Run the applications

Run the following command to run the applications:

```bash
python APP_DIR/APP_NAME.py
```
