# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 23:09:55 2023

@author: Sarath Babu
"""

import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

def send_mail_results(file_name,result,recipient):
    SCOPES = [
            "https://www.googleapis.com/auth/gmail.send"
        ]
    flow = InstalledAppFlow.from_client_secrets_file('../credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    service = build('gmail', 'v1', credentials=creds)
    body = f"""
    <html>
      <body>
        {result}
      </body>
    </html>
    """
    message = MIMEText('This is the body of the email')
    message = MIMEText(body, 'html')
    message['to'] = recipient
    message['subject'] = f'BIRD: {file_name} results'
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
        message = None


import streamlit as st
import pandas as pd
st.set_page_config(
    page_title="Mail Results",
    page_icon=":email:",
)


st.title(":email: Mail Results")

recipient = st.text_input("Mail to stakeholders:","example@gmail.com")

st.markdown(recipient)

file_name = pd.read_excel('session/current.xlsx')['File_Name'].values[0]

df_context = pd.read_excel('session/current.xlsx',sheet_name='Context_Provider')

context = df_context['Context'].values[0]


result = f"""<h2>BIRD: {file_name} results"""
result+= f"""<h3>{file_name}</h3>"""
result+= f"""<p>{context}</p>"""

df_context = pd.read_excel('session/current.xlsx',sheet_name='Additional_Context')

if len(df_context)>0:
    additional_context = "\n".join(df_context['Additional_Context'].values)
    
    additional_context = additional_context.split('\n')
    
    additional_context = list(dict.fromkeys(additional_context).keys())
    
    additional_context = "\n\n".join(additional_context)
    
    result+= f"""<p>{additional_context}</p>"""
    
    

    




# df_additional_context = pd.read_excel('session/current.xlsx',sheet_name='Additional_Context')

# if len(df_additional_context)>0:
#     additional_context = df_additional_context['Additional_Context'].values
    
#     additional_context = "\n\n".join(additional_context)
    
#     st.markdown(additional_context)

df_question = pd.read_excel('session/current.xlsx',sheet_name='Generate_Questions')
if len(df_question)>0:
    questions = "\n".join(df_question['Questions'].values)
    
    questions = questions.split('\n')
    
    questions = list(dict.fromkeys(questions).keys())
    
    questions = "\n\n".join([f'{i+1}. {j}' for i,j in enumerate(questions)])
    
    result+= "<h3>Questions Generated:</h3>"
    result+= "\n".join([f"<p>{i}</p>" for i in questions.split("\n\n")])
  
    
df_approaches = pd.read_excel('session/current.xlsx',sheet_name='Approach_Generation')


df_recommendation = pd.read_excel('session/current.xlsx',sheet_name='Recommendation_Generation')
if len(df_recommendation)>0:
    recommendations = "\n".join(df_recommendation['Recommendations'].values)
    
    recommendations = recommendations.split('\n')
    
    recommendations = list(dict.fromkeys(recommendations).keys())
    
    recommendations = "\n\n".join([f'{i+1}. {j}' for i,j in enumerate(recommendations)])
    
    result+= "<h3>Recommendations Generated:</h3>"
    result+= "\n".join([f"<p>{i}</p>" for i in recommendations.split("\n\n")])
    

if st.button('Send Mail'):
    send_mail_results(file_name,result,recipient)

    
st.markdown(f'File Selected: {file_name}')
st.markdown(context)
if len(df_context)>0:
    st.markdown(additional_context)

# col1, col2, col3 = st.tabs(['Questions Generated','Approaches Generated',
#                             'Recommendations Generated'])

col1, col2 = st.tabs(['Questions Generated','Recommendations Generated'])

with col1:
    if len(df_question)>0:
        questions = "\n".join(df_question['Questions'].values)
        
        questions = questions.split('\n')
        
        questions = list(dict.fromkeys(questions).keys())
        
        questions = "\n\n".join([f'{i+1}. {j}' for i,j in enumerate(questions)])
                
        st.markdown(questions)
        
# with col2:
#     if len(df_approaches)>0:
#         print('Data Present')

#         df_approaches = "\n".join(df_approaches['Approaches'].values)
        
#         df_approaches = df_approaches.split(';;;')
        
#         df_approaches = [i for i in df_approaches if i!='']
        
#         for index,insight_question_approach in enumerate(df_approaches):

#             insight_question,insight_approach = insight_question_approach.split('***')
            
#             insight_question = insight_question.lstrip()
#             insight_approach = "\n\n".join([i.lstrip() for i in insight_approach.split('\n')])
#             st.subheader(f'{index+1}. {insight_question}')
#             st.markdown(insight_approach)
    
with col2:

    if len(df_recommendation)>0:
        recommendations = "\n".join(df_recommendation['Recommendations'].values)
        
        recommendations = recommendations.split('\n')
        
        recommendations = list(dict.fromkeys(recommendations).keys())
        
        recommendations = "\n\n".join([f'{i+1}. {j}' for i,j in enumerate(recommendations)])
        
        
        st.markdown(recommendations)
