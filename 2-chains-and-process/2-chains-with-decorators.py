from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import chain
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@chain
def square(input: dict) -> dict:
    x = input["x"]
    return {"square_result": x * x}

question_template = PromptTemplate(
    input_variables=["square_result"],
    template="Tell me about the number {square_result}",
)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

chain = square | question_template | model

result = chain.invoke({"x": 25})
print(result)
