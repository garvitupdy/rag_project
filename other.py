from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

model = init_chat_model(model = "mistral-small-2506",temperature=0.1)





prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions from a soccer coach's perspective"),
    ("human", "What skills are needed as a left winger?")
])
response = model.invoke(prompt.format_messages())

print(response.content)