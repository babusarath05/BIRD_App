# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 13:57:45 2023

@author: Sarath Babu
"""

import glob
import pandas as pd
import streamlit as st
import sqlite3
import warnings
warnings.filterwarnings('ignore')
# from langchain.llms import CTransformers
# from langchain.callbacks.manager import CallbackManager
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import google.generativeai as genai

# callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])

# config_sql = {'max_new_tokens': 512, 'repetition_penalty': 1.1,'temperature':0,'stop':[';']}

st.set_page_config(
    page_title="Chat with your data",
    page_icon=":speech_balloon:",
)


st.title(":speech_balloon: Chat with your data")

# from pysqldf import SQLDF
# sqldf = SQLDF(globals())

def clean_sql_query(query_result):
    if query_result.find('SELECT')!=-1:
        query_result = query_result[query_result.find('SELECT'):]
    elif query_result.find('Select')!=-1:
        query_result = query_result[query_result.find('Select'):]
    else:
        query_result = 'No Select Statement Found'
        
    return query_result


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
  
session_files=glob.glob("session/*")



file_name = pd.read_excel('session/current.xlsx')['File_Name'].values[0]

@st.cache_data(show_spinner=f"Fetching data from {file_name}")
def read_files(file_name):
    #st.session_state.messages.append({"role": "file_selected", "content": file_selected})
    if 'xlsx' in file_name:
        df1=pd.read_excel(file_name,nrows=10000)
    elif 'csv' in file_name:
        df1=pd.read_csv(file_name,nrows=10000)  
    return df1


df=read_files(file_name)
columns = df.columns.values
columns = [i.replace(" ","_") for i in columns]
df.columns=columns

# =============================================================================
file = "BIRD.db"
try: 
    conn = sqlite3.connect(file) 
    print(f"Database {file} formed.") 
except: 
    print(f"Database {file} not formed.")

with sqlite3.connect(file) as conn:
    try:
        df.to_sql('df',conn,if_exists='replace',index=False)
        print('df table created')
    except:
        print('df table not created')
        
con = sqlite3.connect("BIRD.db")
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
# =============================================================================



st.markdown(f'File Selected: {file_name}')

file_name = file_name.split(".")[0]

file_name = file_name.replace(" ","_")

df_context = pd.read_excel('session/current.xlsx',sheet_name='Context_Provider')

context = df_context['Context'].values[0]
    
st.markdown(context)

context = context.replace(file_name,'df')

df_context = pd.read_excel('session/current.xlsx',sheet_name='Additional_Context')

if len(df_context)>0:
    additional_context = "\n".join(df_context['Additional_Context'].values)
    
    additional_context = additional_context.split('\n')
    
    additional_context = list(dict.fromkeys(additional_context).keys())
    
    additional_context = "\n\n".join(additional_context)
    
    context = context + additional_context
    
    st.markdown(additional_context)
    
print(df.shape)

st.write(df)

@st.cache_resource(show_spinner="Generating answers from prompt.....")
def generate_sql_query(question):
    genai.configure(api_key='')
    model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest") 

    prompt = f"""{context}
    Question: Generate a sql query and enclose within ``` for the question '{question}'
    Answer:"""

    # llm = CTransformers(model="TheBloke/OpenOrca-Platypus2-13B-GGUF", 
    #                     model_file="openorca-platypus2-13b.q4_K_M.gguf", 
    #                     model_type="llama", 
    #                     config=config_sql,callback_manager=callback_manager)
    
    # # llm = CTransformers(model='openorca-platypus2-13b.Q4_K_M.gguf', 
    # #             config=config_sql,
    # #             callback_manager=callback_manager)
    # return llm(prompt)

    response = model.generate_content(prompt)

    response = response.candidates[0].content.parts[0].text
    
    response = response.replace('```','').replace('sql','')
    
    response = response.strip()
    
    return response

for message in st.session_state.messages:
    if message['role']=='user':
        st.chat_message('user').markdown(message['content'])
    elif message['role']=='query':
       st.chat_message('assistant').code(message['content'])
    elif message['role']=='dataframe':
       st.write(pd.DataFrame(message['content']))
       


# Accept user input
if prompt := st.chat_input("Enter your query here"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        print(prompt)
        
    query_result = generate_sql_query(prompt)
    # query_result = clean_sql_query(query_result)+';'
    
    df_result = pd.DataFrame(zip(['No Result']),columns=['Empty Column'])
    try:
        # df_result = sqldf.execute(query_result)
        with sqlite3.connect(file) as conn:
            df_result = pd.read_sql_query(query_result, conn)
    except:
        pass

    with st.chat_message('assistant'):
        st.code(query_result)
    st.write(df_result)
    
    # df_chart = df_result.copy()
    # if len(df_chart.columns.values)>1:
    #     index_col= df_chart.columns.values[0]
    #     df_chart = df_chart.set_index(index_col)
    #     st.bar_chart(df_chart,width=0,height=0)
    
    # if options := st.multiselect(
    # 'Select Columns',
    # df_chart.columns.values):

    #     st.write('You selected:', options)
        
    st.session_state.messages.append({"role": "query", "content": query_result})
    st.session_state.messages.append({"role": "dataframe", "content": df_result.to_dict('records')})
    st.rerun()