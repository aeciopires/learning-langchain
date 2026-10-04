"""Two ways to create a chat model: init_chat_model() and the provider class.

Run: uv run python 1-fundamentals/2-init-chat-model.py
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from learning_langchain.config import LLMSettings, load_settings
from learning_langchain.models import build_fake_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


def build_with_init_chat_model(settings: LLMSettings) -> BaseChatModel:
    """Option 1: init_chat_model("provider:model") - one function for every
    provider; switching providers means changing a string, not the import."""
    return init_chat_model(f"{settings.provider}:{settings.model}", temperature=settings.temperature)


def build_with_provider_class(settings: LLMSettings) -> BaseChatModel:
    """Option 2: import the provider's own class. More explicit, and exposes
    provider-specific parameters, but ties the code to one provider."""
    if settings.provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=settings.model, temperature=settings.temperature)
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(model=settings.model, temperature=settings.temperature)


def main() -> None:
    settings = load_settings()
    print(f"Provider: {settings.provider} | model: {settings.model} | temperature: {settings.temperature}")

    models: dict[str, BaseChatModel]
    if settings.provider == "fake":
        # Offline mode: both options need a real provider, so we use the fake
        # model to show the same invoke() call works with any chat model.
        models = {"fake model": build_fake_chat_model(["Hi from the fake model!"])}
    else:
        models = {
            "init_chat_model()": build_with_init_chat_model(settings),
            "provider class": build_with_provider_class(settings),
        }

    for label, model in models.items():
        # Every chat model shares the same interface (invoke, stream, batch),
        # which is why the rest of the code never cares which one it got.
        answer = model.invoke("Say hello in one short sentence.")
        print(f"[{label}] {type(model).__name__}: {answer.content}")


if __name__ == "__main__":
    main()
