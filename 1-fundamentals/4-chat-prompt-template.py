from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

messages = [
  ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
  ("user", "{sentence}")
]

chat_prompt = ChatPromptTemplate(messages)

formatted_messages = chat_prompt.format_messages(
    input_language="Portuguese",
    output_language="English",
    sentence="Eu estou aprendendo a programar em LangChain.",
)

answer = gemini.invoke(formatted_messages)
print(answer.content)