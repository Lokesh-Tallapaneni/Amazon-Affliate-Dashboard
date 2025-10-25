import os
from langchain_experimental.agents import create_csv_agent
from langchain_openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["OPENAI_API_KEY"] = ""


def load(file_name):
    agent = create_csv_agent(OpenAI(temperature=0.9), "data.csv", verbose=True)
    # agent=create_csv_agent(ChatGoogleGenerativeAI(google_api_key='',model='gemini-pro',temperature=0.9),"data.csv",verbose=True)
    if agent:
        return agent
    else:
        return False


def chat(agent, prompt):
    response = agent.run(prompt)
    if response:
        return response
    else:
        return False
