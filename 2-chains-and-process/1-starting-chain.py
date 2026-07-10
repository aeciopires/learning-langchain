from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

question_template = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?",
)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

chain = question_template | model

result = chain.invoke({"product": "colorful socks"})
print(result)
