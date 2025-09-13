#
# 영어 공부 챗봇 by Kevin
#

import streamlit as st
import openai
import re

# 페이지 설정
st.set_page_config(
    page_title="영어 공부 챗봇 by Kevin",
    page_icon="💬",
    layout="wide"
)

# API 키 설정 (Streamlit Secrets에서 관리 권장)
# openai.api_key = st.secrets["OPENAI_API_KEY"]
YOUR_API_KEY = st.secrets["api_keys"]["my_api_key"]
openai.api_key = YOUR_API_KEY

# 시스템 프롬프트 - 챗봇의 역할 정의
system_prompt = """
You are an English tutor. Your role is:
1. Respond in English to any question, even if it's asked in Korean
2. If the user's English contains errors, politely point them out and explain the correct usage
3. Provide context and situational explanations for your responses
4. Be encouraging and supportive in your teaching style
5. If there is an inportent keyword, please explain it separately, if you use it, ethmology, etc
Always structure your response as:
- First, provide your natural English response to the user's input
- Then, if there are errors, explain them clearly with examples
- Finally, provide additional context or alternative expressions when relevant
"""

# OpenAI 클라이언트 객체 생성
client = openai.OpenAI(api_key=YOUR_API_KEY)

def correct_english(text):
    """영어 문장을 교정하는 함수"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an English grammar expert. Correct any errors in the following text and explain the mistakes briefly."},
                {"role": "user", "content": f"Correct this: {text}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in correction: {str(e)}"

def generate_response(user_input):
    """챗봇 응답 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# UI 구성
st.title("💬 영어 챗봇  by Kevin")
st.markdown("""
영어 에 대해 뭐든지 물어보세요 영어로 답변해 드립니다.
- 💡 영어 실력을 향상시키고 싶으세요?
- 🗣️ 자연스러운 표현을 배우고 싶으세요?

지금 바로 물어 해보세요!
""")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
user_input = st.chat_input("영어나 한국어로 질문하세요...")

if user_input:
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변을 생성 중입니다..."):
            # 영어 문장인지 확인하고 교정 필요시 교정
            if re.search(r'[a-zA-Z]', user_input) and len(user_input.split()) > 2:
                with st.expander("문법 검사 결과"):
                    correction = correct_english(user_input)
                    st.write(correction)
            
            # 챗봇 응답 생성
            response = generate_response(user_input)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# 사이드바에 추가 정보
with st.sidebar:
    st.header("사용법 안내")
    st.markdown("""
    ### 💡 학습 팁
    1. **대화 내용**:  다른말로도 표현 해춰
    2. **문법 질문**:  수동태로 바꿔질물해줘
    3. **표문 표현**:  문장을 다른 3개료 표현해줘
    4. **교정 요청**:  문장을 입력하고 교정해줘  
        
    """)
    
    # ### 🎯 예시 질문
    # - "What's the difference between 'make' and 'do'?"
    # - "회의에 늦을 것 같다고 말하는 방법 알려줘"
    # - "I has a apple" (문법 오류 자동 교정)
    # - "How to order coffee in English?"
    # st.divider()
    
    # st.subheader("주의사항")
    # st.info(
    #     "이 챗봇은 AI를 기반으로 하므로 완벽하지 않을 수 있습니다. "
    #     "중요한 내용은 추가로 확인하시기 바랍니다."
    # )


## 실행 방법

# 1. 필요한 패키지 설치:
# ```
# pip install streamlit openai
# ```

# 2. API 키 설정:
#    - Streamlit Cloud를 사용하는 경우: Secrets 관리에 `OPENAI_API_KEY` 설정
#    - 로컬에서 실행하는 경우: `.streamlit/secrets.toml` 파일에 API 키 추가

# 3. 애플리케이션 실행:
# ```
# streamlit run chatbot.py
# ```

# ## 주요 기능

# 1. **다국어 지원**: 한국어 질문에도 영어로 답변
# 2. **자동 문법 검사**: 영어 입력 시 오류 자동 교정
# 3. **상황별 표현**: 맥락에 맞는 자연스러운 영어 표현 제시
# 4. **교육적 설명**: 문법 규칙과 사용법 상세 설명

# 이 코드는 OpenAI의 GPT 모델을 사용하여 영어 회화 연습을 도와주는 챗봇을 구현합니다.
