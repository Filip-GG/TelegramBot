import config as cfg
import os

from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory

llm = GoogleGenerativeAI(
    model='gemini-pro',
    google_api_key= cfg.GOOGLE_API
)

def query(text, instruct = None, memory_save = None):
    
    memory = ConversationSummaryBufferMemory(llm=llm)

    if memory_save != None:
        memory = memory_save
    else: 
        if instruct != None:
            memory.save_context(
                {'input':instruct}, 
                {'outputs':'Хорошо'}
            )
    
    chat = ConversationChain(
        llm=llm,
        memory = memory
    )
    out = chat.invoke(text)
    return [out['response'], memory]


'''
llm = GoogleGenerativeAI(
    model='gemini-pro',
    google_api_key= cfg.GOOGLE_API
)

from langchain_core.prompts import ChatPromptTemplate

def query(text, system = None):
    tample = ChatPromptTemplate.from_messages([
        ("system", '{system}'),
        ("user", "{query}")
    ])
    out = llm.invoke(
        tample.invoke({
            'system':system,
            'query':text
        })
    )
    return out

'''

'''
import google.generativeai as genai

def get_text(out):
    txt = out.to_dict()
    return txt['candidates'][0]['content']['parts'][0]['text']
    
def query(promt):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cfg.GOOGLE_JSON
    os.environ['GOOGLE_API_KEY']=cfg.GOOGLE_API

    model = genai.GenerativeModel(
        model_name='gemini-pro'
        )
    out = model.generate_content(promt)
    return get_text(out)
'''