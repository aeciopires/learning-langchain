from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

gemini = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai", temperature=0.5)

answer = gemini.invoke("Hello, how are you?")
print(answer)