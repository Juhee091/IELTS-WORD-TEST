import streamlit as st
import pandas as pd
import random
import datetime

# Load vocabulary CSV (같은 디렉토리에 IELTS_vocab_extracted.csv 있어야 함)
df = pd.read_csv("IELTS_vocab_extracted.csv")

# 앱 제목
st.title("📘 IELTS Vocabulary Daily Quiz")
st.markdown("Practice 50 words a day from NGSL-based IELTS vocabulary!")

# 사용자 닉네임 입력
nickname = st.text_input("Enter your nickname:")

# 퀴즈 날짜 선택
quiz_date = st.date_input("Select a date for your quiz", datetime.date.today())

# 날짜 기반 시드로 문제 셔플
random.seed(str(quiz_date))

# 50개 랜덤 단어 추출
quiz_words = df.sample(n=50, random_state=random.randint(0, 100000))

# 점수 초기화
score = 0

# 퀴즈 시작 조건: 닉네임이 입력된 경우
if nickname:
    st.write(f"👤 Nickname: **{nickname}**")
    st.write("---")

    for idx, row in quiz_words.iterrows():
        # 의미 → 단어 또는 단어 → 의미 문제 랜덤 생성
        if random.random() < 0.5:
            # 의미 → 단어
            question = row['Meaning']
            answer = row['Word']
            choices = df['Word'].sample(4).tolist() + [answer]
            random.shuffle(choices)
            user_choice = st.radio(
                f"📌 Q{idx+1}: What is the English word for '{question}'?",
                choices,
                key=f"q{idx}"
            )
            if user_choice == answer:
                score += 1
        else:
            # 단어 → 의미
            question = row['Word']
            answer = row['Meaning']
            choices = df['Meaning'].sample(4).tolist() + [answer]
            random.shuffle(choices)
            user_choice = st.radio(
                f"📌 Q{idx+1}: What is the meaning of '{question}'?",
                choices,
                key=f"q{idx}"
            )
            if user_choice == answer:
                score += 1

    st.write("---")
    st.success(f"🎉 You got {score} out of 50 correct!")
else:
    st.warning("Please enter your nickname to begin the quiz.")

# 퀴즈 리셋 버튼
if st.button("🔄 Reload Quiz"):
    st.experimental_rerun()
