import streamlit as sts
import pandas as pd
import random
import datetime

# CSV 파일 경로
df = pd.read_csv("IELTS_vocab_extracted.csv")
all_words = df.to_dict("records")

# 세션 상태 초기화
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "wrong_questions" not in st.session_state:
    st.session_state.wrong_questions = []
if "retry_mode" not in st.session_state:
    st.session_state.retry_mode = False

# 닉네임 입력
if not st.session_state.nickname:
    nickname = st.text_input("Enter your nickname to start:")
    if nickname:
        st.session_state.nickname = nickname
        st.experimental_rerun()
    st.stop()

# 퀴즈 생성 함수
def generate_quiz(data, num=50, exclude=[]):
    sample = random.sample([w for w in data if w["Word"] not in exclude], num)
    quiz_data = []
    for item in sample:
        correct = item["Meaning"]
        others = random.sample([w["Meaning"] for w in data if w["Meaning"] != correct], 4)
        options = random.sample(others + [correct], 4)
        quiz_data.append({
            "question": item["Word"],
            "answer": correct,
            "choices": options,
            "type": "word_to_meaning"
        })
    return quiz_data

# 퀴즈 초기화
if not st.session_state.quiz and not st.session_state.retry_mode:
    st.session_state.quiz = generate_quiz(all_words)

st.title("📝 IELTS Word Quiz")
st.markdown(f"**👤 Nickname:** {st.session_state.nickname}")

# 문제 출력
for idx, item in enumerate(st.session_state.quiz):
    st.markdown(f"**Q{idx+1}.** What does **{item['question']}** mean?")
    st.session_state.answers[idx] = st.radio(
        f"Q{idx+1}",
        item["choices"],
        index=None,
        key=f"radio_{idx}"
    )

# 제출 버튼
if not st.session_state.submitted:
    if st.button("✅ Submit Answers"):
        score = 0
        wrong = []
        for idx, item in enumerate(st.session_state.quiz):
            selected = st.session_state.answers.get(idx)
            if selected == item["answer"]:
                score += 1
            else:
                wrong.append(item)
        st.session_state.score = score
        st.session_state.wrong_questions = wrong
        st.session_state.submitted = True

        # 기록 저장
        result_row = {
            "nickname": st.session_state.nickname,
            "score": score,
            "date": datetime.datetime.today().strftime("%Y-%m-%d")
        }
        try:
            result_df = pd.read_csv("quiz_ranking.csv")
        except FileNotFoundError:
            result_df = pd.DataFrame(columns=["nickname", "score", "date"])
        result_df = pd.concat([result_df, pd.DataFrame([result_row])], ignore_index=True)
        result_df.to_csv("quiz_ranking.csv", index=False)
        st.experimental_rerun()

# 결과 출력
if st.session_state.submitted:
    st.subheader("🎉 Result")
    st.markdown(f"**Score: {st.session_state.score} / {len(st.session_state.quiz)}**")

    if st.session_state.wrong_questions:
        st.subheader("❌ Incorrect Answers")
        for item in st.session_state.wrong_questions:
            st.markdown(f"- **{item['question']}** → {item['answer']}")

        if st.button("🔁 Retry Wrong Questions"):
            st.session_state.quiz = st.session_state.wrong_questions
            st.session_state.answers = {}
            st.session_state.submitted = False
            st.session_state.retry_mode = True
            st.experimental_rerun()

    st.subheader("🏆 Ranking")
    try:
        ranking_df = pd.read_csv("quiz_ranking.csv")
        st.dataframe(ranking_df.sort_values(by="score", ascending=False).reset_index(drop=True))
    except FileNotFoundError:
        st.warning("No rankings recorded yet.")

    if st.button("🔄 New Quiz"):
        st.session_state.quiz = []
        st.session_state.answers = {}
        st.session_state.submitted = False
        st.session_state.retry_mode = False
        st.experimental_rerun()
