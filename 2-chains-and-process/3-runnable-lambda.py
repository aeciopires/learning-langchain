from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# RunnableLambda wraps a plain Python function so it behaves like any other
# LangChain "Runnable". This lets us plug arbitrary Python logic into a chain
# using the "|" pipe operator, just like prompts and models.
def square(input: dict) -> dict:
    x = input["x"]
    return {"square_result": x * x}


square_runnable = RunnableLambda(square)

# Prompt template that consumes the output produced by the RunnableLambda above.
question_template = PromptTemplate(
    input_variables=["square_result"],
    template="Tell me about the number {square_result}",
)

# Chat model that will answer the question built from the prompt template.
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)


# A second RunnableLambda used to post-process the model's response, keeping
# only the text content instead of the full AIMessage object.
def extract_content(response) -> str:
    return response.content


to_text = RunnableLambda(extract_content)

# Chain execution order:
# 1) square_runnable: {"x": 25} -> {"square_result": 625}
# 2) question_template: builds the prompt text using "square_result"
# 3) model: generates the answer for the prompt
# 4) to_text: extracts only the text content from the model's response
chain = square_runnable | question_template | model | to_text

result = chain.invoke({"x": 25})
print(result)
