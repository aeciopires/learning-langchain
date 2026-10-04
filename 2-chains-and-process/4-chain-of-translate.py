"""A reusable translation chain with dynamic source and target languages.

Run: uv run python 2-chains-and-process/4-chain-of-translate.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, chain

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


# RunnableLambda: wraps a plain function to normalize/validate the raw input
# before it reaches the prompt template. Both input and output languages are
# dynamic (received at invoke time), not hardcoded, so we just clean them up
# here (e.g. removing extra spaces).
def prepare_input(data: dict) -> dict:
    return {
        "input_language": data["input_language"].strip(),
        "output_language": data["output_language"].strip(),
        "sentence": data["sentence"].strip(),
    }


prepare_input_runnable = RunnableLambda(prepare_input)

# Prompt template with three dynamic placeholders: the source language, the
# target language and the sentence to be translated.
translation_template = PromptTemplate(
    input_variables=["input_language", "output_language", "sentence"],
    template=(
        "Translate the following sentence from {input_language} to "
        "{output_language}.\nSentence: {sentence}\nTranslation:"
    ),
)


# @chain decorator: an alternative, more concise way (compared to
# RunnableLambda) to turn a plain function into a Runnable. Here it is used
# to post-process the model's response, keeping only the translated text.
@chain
def extract_translation(response) -> str:
    return response.text.strip()


def build_chain(model: BaseChatModel) -> Runnable:
    """Chain execution order:
    1) prepare_input_runnable: cleans up the raw dict received on invoke()
    2) translation_template: builds the translation prompt using both dynamic languages
    3) model: generates the translated sentence
    4) extract_translation: extracts and trims the final text from the model's response
    """
    return prepare_input_runnable | translation_template | model | extract_translation


def main() -> None:
    model = get_chat_model(
        fake_responses=["O tempo está lindo hoje.", "Me encanta aprender nuevas tecnologías."]
    )
    translate = build_chain(model)

    print(
        translate.invoke(
            {
                "input_language": "English",
                "output_language": "Portuguese",
                "sentence": "The weather is beautiful today.",
            }
        )
    )
    # Same chain reused with different dynamic languages, proving both are flexible.
    print(
        translate.invoke(
            {
                "input_language": "Portuguese",
                "output_language": "Spanish",
                "sentence": "Eu adoro aprender novas tecnologias.",
            }
        )
    )


if __name__ == "__main__":
    main()
