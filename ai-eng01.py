# Streamlit 챗봇 코드 예시

import streamlit as st
import openai
import os
api_key = st.secrets["api_keys"]["my_api_key"]
openai.api_key = api_key

# llm = openai(api_key=api_key)

def generate_english_answer(user_input):
# Prompt 생성: 상황 설명, 답변, 해설, 오류 체크 포함
    prompt = f"""
    You are an English conversation chatbot.
    - If the user's input is Korean, translate it to English and answer in English.
    - For every answer, provide:
    1. The English answer.
    2. A simple explanation of the answer in English.
    3. A description of the situation/scenario related to the conversation.
    4. If the answer is wrong or inappropriate, point out and explain the mistake in Korean.
    User input: {user_input}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 또는 최신 모델 사용
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    output = response['choices'][0]['message']['content']
    return output

#st.title("English Chatbot by Kevin")
st.markdown('<span style="font-size:20px;">English Chatbot by Kevin</span>', unsafe_allow_html=True)

user_input = st.text_input("Ask your question:")
if st.button("질문하기") and user_input: 
    result = generate_english_answer(user_input)

    st.markdown("---")
    st.markdown(result)

