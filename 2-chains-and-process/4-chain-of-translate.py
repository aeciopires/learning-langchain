from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda, chain
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# RunnableLambda: wraps a plain function to normalize/validate the raw input
# before it reaches the prompt template. Both input and output languages are
# dynamic (received at invoke time), not hardcoded, so we just clean them up
# here (e.g. removing extra spaces).
def prepare_input(input: dict) -> dict:
    return {
        "input_language": input["input_language"].strip(),
        "output_language": input["output_language"].strip(),
        "sentence": input["sentence"].strip(),
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

# Chat model responsible for actually performing the translation.
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)


# @chain decorator: an alternative, more concise way (compared to
# RunnableLambda) to turn a plain function into a Runnable. Here it is used
# to post-process the model's response, keeping only the translated text.
@chain
def extract_translation(response) -> str:
    return response.content.strip()


# Chain execution order:
# 1) prepare_input_runnable: cleans up the raw dict received on invoke()
# 2) translation_template: builds the translation prompt using both dynamic languages
# 3) model: generates the translated sentence
# 4) extract_translation: extracts and trims the final text from the model's response
chain = prepare_input_runnable | translation_template | model | extract_translation

result = chain.invoke(
    {
        "input_language": "English",
        "output_language": "Portuguese",
        "sentence": "The weather is beautiful today.",
    }
)
print(result)

# Same chain reused with different dynamic languages, proving both are flexible.
result2 = chain.invoke(
    {
        "input_language": "Portuguese",
        "output_language": "Spanish",
        "sentence": "Eu adoro aprender novas tecnologias.",
    }
)
print(result2)
