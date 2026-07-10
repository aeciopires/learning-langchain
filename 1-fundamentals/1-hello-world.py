from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

model = ChatOpenAI(model_name="gpt-5-nano", temperature=0.5)
message = "Hello, how are you?"
response = model.invoke(message)
print(response)
