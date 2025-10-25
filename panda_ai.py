from pandasai import SmartDataframe
import os
from pandasai import Agent
from pandasai.llm.openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from pandasai.responses.response_parser import ResponseParser
# ollama_llm = LocalLLM(api_base="http://localhost:11434/v1", model="gemma:latest")

# OpenAI API key placeholder - use environment variables instead
# Example: os.environ.get('OPENAI_API_KEY')

# chatgpt=OpenAI(api_token='your-openai-api-key-here')

llm = ChatGoogleGenerativeAI(google_api_key='your-google-api-key-here',model='gemini-pro',temperature=0.9)
user_defined_path=os.getcwd()


df = pd.read_excel("data.xlsx",sheet_name='Fee-Earnings') 
df.columns = df.iloc[0]
df = df[pd.to_datetime(df['Date Shipped'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna()]
df['Date Shipped'] = pd.to_datetime(df['Date Shipped'])
df['Date Shipped'] = df['Date Shipped'].dt.strftime('%Y-%m-%d')
df=df.drop("Direct Sale",axis=1)
data = df.to_dict(orient='records')



def sheet_name(f_name):
    file = pd.ExcelFile(f_name)

    dict={}
    # getting the sheetnames
    sheet_names = file.sheet_names
    for s in sheet_names:
        dict[s]=s.replace("-","_") if "-" in s else s
    # print(dict)

    new=[]
    for old in dict.values():
        new.append(old)

    ind=0
    for sheet_name in sheet_names:
        sheet = file.parse(sheet_name)
        sheet.columns=sheet.iloc[0]
        data = sheet.to_dict(orient='records')
        globals()[new[ind]] = data
        ind+=1
        
    return True

sheet_name('data.xlsx')
# print(globals().keys())
        
global Fee_Earnings,Fee_Orders, Fee_Tracking, Fee_DailyTrends, Fee_LinkType


# df=pd.read_csv('changed.csv')
# print(df.head())



# agent=Agent([Fee_Earnings,Fee_Orders, Fee_Tracking], config={"llm": llm,"save_charts": True,
#     "save_charts_path": user_defined_path, "enable_cache": False})

# try:
#     print(df.chat('mia khalifa pics if you dont find the answer leave it with some notification/'))
# except Exception as e:
#     print(f'Got an Exception as e:  {e}')
    
    
# while True:
#     x=input("Enter the input : ")
#     # x=x.lower().strip()+"If you couldn'y find the answer leave this with None as an Answer."
#     try:
#         # o1=agent.chat(x)
#         # print(f'Agent \n: {o1}')
#         out=df.chat(x)
#         print(out)
#     except Exception  as e:
#         print(f'Exception Caught in while loop :{e}')
        
        
           
        
def inp(x):
    try:
        df = SmartDataframe(Fee_Earnings, config={"llm": llm, "enable_cache": True})
        print(df)
        out=df.chat(x)
        return out
    except TypeError:
        df = SmartDataframe(Fee_Earnings, config={"llm": llm, "enable_cache": True})
        out=df.chat(x)
        return out
    except Exception as e:
        return False
        
        
        
