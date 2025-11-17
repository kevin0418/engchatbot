#
# Gemini 주제별  챗봇 Streamlit 앱
#

import streamlit as st
# from google import genai
import os
import google.generativeai as genai
from datetime import datetime

api_key = st.secrets["gemini_api_key"]  
# 페이지 설정
st.set_page_config(
    page_title=" 주제 별  챗봇 by Kevin",
    page_icon="🤖",
    layout="wide"
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic" not in st.session_state:
    st.session_state.topic = ""


# --- 텍스트 파일 저장 함수 추가 ---
def save_chat_to_text(messages, topic):
    # 대화 내용을 텍스트로 포맷팅
    chat_content = f"--- 챗봇 대화 기록 ({topic}) ---\n\n"
    for message in messages:
        role_name = "User" if message["role"] == "user" else "Assistant"
        chat_content += f"[{role_name}]\n{message['content']}\n\n"
    chat_content += f"--- 기록 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n"
 
    return chat_content

# 사이드바 - 설정
with st.sidebar:
    # st.title("챗봇 설정")
    
    # API 키 입력
    # api_key = os.getenv("gemini_api_key")
    # st_secrets["gemini_api_key"] = "YOUR_GEMINI_API
    # 모델 정보
    # st.info("사용 모델: gemini-2.5-flash")
    
    # 주제 선택
    st.sidebar.subheader("주제 선택")
    topic = st.selectbox("",
          ["종교 (성경해설)", "심리학 (고민상담)", "의학 (질병)", "영어 (회화, 해설)", "기타"]
    )
    
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.topic = topic
        st.rerun()

# 주제별 시스템 프롬프트 생성 함수
def get_system_prompt(topic):
    system_prompts = {
        "종교 (성경해설)": """
        당신은 기독교 성경 전문 해설가입니다. 사용자의 질문에 대해 성경 구절을 인용하고,
        그 의미를 현대적 관점에서 쉽게 설명해주세요. 
        답변은 항상 사랑과 긍정의 메시지를 담아야 합니다.
        
        답변 형식:
        1. 관련 성경 구절 인용 (장:절)
        2. 구절의 역사적/문화적 배경 설명
        3. 현대 생활에 적용할 수 있는 교훈
        4. 격려의 말씀
        
        항상 한국어로 답변해주세요.
        """,
        
        "심리학 (고민상담)": """
        당신은 전문 상담 심리학자입니다. 사용자의 고민에 공감하며,
        과학적으로 입증된 심리학적 지식을 바탕으로 조언을 제공해주세요.
        위기 상황에서는 전문가 상담을 권유해야 합니다.
        
        답변 형식:
        1. 공감과 이해 표현
        2. 관련 심리학 개념 설명
        3. 실용적인 조언과 해결책 제시
        4. 필요한 경우 전문가 상담 권유
        
        항상 한국어로 답변해주세요.
        """,
        
        "의학 (질병)": """
        당신은 의학 정보를 제공하는 조수입니다. 사용자의 건강 관련 질문에 대해
        일반적인 정보를 제공하되, 진단이나 치료법을 제시하지는 마세요.
        항상 전문 의료진의 상담을 받을 것을 강조하세요.
        
        답변 형식:
        1. 질문에 대한 일반적인 의학 정보 제공
        2. 가능한 원인과 증상 설명
        3. 예방법이나 관리 팁
        4. 반드시 전문 의료진 상담 권고
        
        항상 한국어로 답변해주세요.
        """,
        
        "영어 (회화, 해설)": """
        당신은 영어 교육 전문가입니다. 사용자의 영어 관련 질문에 대해
        문법, 표현, 발음 등 다양한 측면에서 설명해주세요.
        한국어와 영어를 적절히 혼용하여 설명하되, 예문은 반드시 영어로 제공하세요.
        
        답변 형식:
        1. 질문의 핵심 개념 설명 (한국어)
        2. 관련 문법/표현 상세 설명
        3. 예문 제시 (영어 + 한국어 해석)
        4. 실전 활용 팁
        
        기본 설명은 한국어로 제공해주세요.
        """,
        
        "기타": """
        사용자의 질문에 대해 전문적이고 정확한 정보를 제공해주세요.
        특정 주제에 속하지 않는 일반적인 질문에도 친절하게 답변해주세요.
        항상 한국어로 답변해주세요.
        """
    }
    
    return system_prompts.get(topic, system_prompts["기타"])

# Gemini API 호출 함수
def call_gemini(messages, system_prompt, api_key):
    if not api_key:
        return "🚨 Gemini API 키가 설정되지 않았습니다."
    try:
             
        genai.configure(api_key= api_key, transport='rest') # 이 옵션을 추가 
        # 모델 설정
        model = genai.GenerativeModel(
            'models/gemini-2.5-flash',
            system_instruction=system_prompt
        )
        # 대화 기록을 단일 프롬프트로 변환
        conversation_text = ""
        for msg in messages[-6:]:  # 최근 6개 메시지만 사용 (컨텍스트 제한)
            role = "사용자" if msg["role"] == "user" else "어시스턴트"
            conversation_text += f"{role}: {msg['content']}\n"
        
        # 마지막 사용자 메시지
        last_user_message = messages[-1]["content"] if messages else ""
        
        # 프롬프트 생성
        prompt = f"""대화 기록:
{conversation_text}

현재 질문: {last_user_message}

위 대화 기록을 참고하여 현재 질문에 답변해주세요:"""
        
        # 응답 생성
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Gemini API 호출 중 오류 발생: {str(e)}"

# 메인 화면
st.title("🤖 주제별 챗봇  by  Kevin ")
st.markdown(f"현재 선택된 주제: **{topic}**")

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("질문을 입력하세요..."):
    # if not gemini_api_key:
    #     st.error("🚨 Gemini API 키를 입력해주세요!")
    #     st.stop()
    
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 시스템 프롬프트 생성
    system_prompt = get_system_prompt(topic)
    
    # 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("Gemini가 답변을 생성 중..."):
            # response = call_gemini(st.session_state.messages, system_prompt, gemini_api_key)
            response = call_gemini(st.session_state.messages, system_prompt, api_key)
            st.markdown(response)
    
    # 어시스턴트 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": response})

# 주제별 설명
st.sidebar.markdown("---")
st.sidebar.subheader("주제 설명")

topic_descriptions = {
    "종교 (성경해설)": "성경 구절 해석과 기독교 교리 관련 질문",
    "심리학 (고민상담)": "심리적 고민과 일상 문제 상담",
    "의학 (질병)": "질병 증상과 건강 관리 일반 정보",
    "영어 (회화, 해설)": "영어 학습과 회화 관련 질문",
    "기타": "기타 다양한 주제의 질문"
}

st.sidebar.info(topic_descriptions[topic])

# 사용 통계
if st.session_state.messages:
    st.sidebar.markdown("---")
    st.sidebar.subheader("대화 통계")
    st.sidebar.write(f"총 메시지 수: {len(st.session_state.messages)}")
    user_messages = [msg for msg in st.session_state.messages if msg['role'] == 'user']
    st.sidebar.write(f"사용자 질문: {len(user_messages)}")


    # ⬇️ 텍스트 파일 저장 버튼 추가
    chat_content = save_chat_to_text(st.session_state.messages, topic)
    filename = f"chat_{topic.replace(' ', '_').replace('(', '').replace(')', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    st.sidebar.download_button(
        label="💾 대화 내용 텍스트로 저장",
        data=chat_content,
        file_name=filename,
        mime="text/plain"
   )


# 주의사항
st.sidebar.markdown("---")
st.sidebar.caption("""
**주의사항:**
- 의학/심리학 상담은 전문가 상담을 대체하지 않습니다
- 중요한 결정은 여러 정보원을 참고하세요
- API 키는 안전하게 관리해주세요
- Gemini 모델: gemini-1.5-flash 사용
""")

