# ielts_quiz.py
import streamlit as st
import pandas as pd
import random, datetime, os, json

# ──────────────────────────────────────────────────────────────
# 1. 데이터 로드
# ──────────────────────────────────────────────────────────────
CSV_FILE  = "IELTS_vocab_extracted.csv"     # 단어·뜻 CSV
RANK_FILE = "quiz_ranking.csv"              # 랭킹 CSV

if not os.path.exists(CSV_FILE):
    st.error(f"❌ '{CSV_FILE}' 파일이 앱과 같은 폴더에 있어야 합니다.")
    st.stop()

df = pd.read_csv(CSV_FILE).dropna().drop_duplicates()
records = df.to_dict("records")

# ──────────────────────────────────────────────────────────────
# 2. 세션 상태 초기화
# ──────────────────────────────────────────────────────────────
defaults = {
    "nickname"     : "",
    "quiz_data"    : [],
    "answers"      : {},
    "submitted"    : False,
    "score"        : 0,
    "incorrect"    : [],
    "retry_mode"   : False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────
# 3. 닉네임 & 날짜 입력
# ──────────────────────────────────────────────────────────────
st.title("📘 IELTS Vocabulary Quiz")

if not st.session_state.nickname:
    name = st.text_input("Enter your nickname to start:")
    if name:
        st.session_state.nickname = name
        st.experimental_rerun()
        st.stop()
    st.stop()

quiz_date = st.date_input("Quiz date", datetime.date.today())
seed_key  = f"{st.session_state.nickname}-{quiz_date}"

# ──────────────────────────────────────────────────────────────
# 4. 퀴즈 생성 함수
# ──────────────────────────────────────────────────────────────
def make_quiz(source, n=50):
    random.seed(seed_key if not st.session_state.retry_mode else None)
    sample = random.sample(source, k=min(n, len(source)))
    quiz = []
    for item in sample:
        word, meaning = item["Word"], item["Meaning"]
        # 방향 결정
        if random.random() < 0.5:
            prompt = meaning               # 뜻 → 단어
            answer = word
            pool   = [r["Word"] for r in records if r["Word"] != answer]
        else:
            prompt = word                  # 단어 → 뜻
            answer = meaning
            pool   = [r["Meaning"] for r in records if r["Meaning"] != answer]

        # 보기 4개
        choices = random.sample(pool, 3) + [answer]
        random.shuffle(choices)

        quiz.append({
            "prompt" : prompt,
            "answer" : answer,
            "choices": choices,
            "direction": "KR→EN" if prompt == meaning else "EN→KR"
        })
    return quiz

# ──────────────────────────────────────────────────────────────
# 5. 퀴즈 데이터 준비
# ──────────────────────────────────────────────────────────────
if not st.session_state.quiz_data:
    st.session_state.quiz_data  = make_quiz(records, 50)
    st.session_state.answers    = {}
    st.session_state.submitted  = False
    st.session_state.incorrect  = []
    st.session_state.score      = 0

st.markdown(f"👤 **{st.session_state.nickname}** | 🗓 **{quiz_date}**")
st.divider()

# ──────────────────────────────────────────────────────────────
# 6. 문제 표시
# ──────────────────────────────────────────────────────────────
for idx, q in enumerate(st.session_state.quiz_data):
    st.session_state.answers[idx] = st.radio(
        f"**Q{idx+1}.** {q['prompt']}",
        q["choices"],
        key=f"q_{idx}",
       index = q['choices'].index(st.session_state.answers.get(idx)) if st.session_state.answers.get(idx) else 0
    )

# ──────────────────────────────────────────────────────────────
# 7. 제출 버튼
# ──────────────────────────────────────────────────────────────
if not st.session_state.submitted and st.button("✅ Submit All"):
    score, wrong = 0, []
    for idx, q in enumerate(st.session_state.quiz_data):
        user = st.session_state.answers.get(idx)
        correct = q["answer"]
        if user == correct:
            score += 1
        else:
            wrong.append({**q, "your": user})
    # 상태 업데이트
    st.session_state.score     = score
    st.session_state.incorrect = wrong
    st.session_state.submitted = True

    # 랭킹 저장
    entry = {
        "nickname"      : st.session_state.nickname,
        "date"          : str(quiz_date),
        "score"         : score,
        "wrong_count"   : len(wrong),
        "total_q"       : len(st.session_state.quiz_data)
    }
    if os.path.exists(RANK_FILE):
        rank_df = pd.read_csv(RANK_FILE)
    else:
        rank_df = pd.DataFrame(columns=entry.keys())
    rank_df = pd.concat([rank_df, pd.DataFrame([entry])], ignore_index=True)
    rank_df.to_csv(RANK_FILE, index=False)
    st.rerun()

# ──────────────────────────────────────────────────────────────
# 8. 결과 & 오답 & 재시험
# ──────────────────────────────────────────────────────────────
if st.session_state.submitted:
    st.success(f"🎉 Score: **{st.session_state.score} / {len(st.session_state.quiz_data)}**")
    if st.session_state.incorrect:
        st.subheader("❌ Incorrect Answers")
        for w in st.session_state.incorrect:
            st.write(f"- **{w['prompt']}**")
            st.write(f"  Your answer: `{w['your']}` | Correct: ✅ `{w['answer']}`")

        if st.button("🔁 Retry Wrong Questions"):
            st.session_state.retry_mode   = True
            st.session_state.quiz_data    = st.session_state.incorrect
            st.session_state.answers      = {}
            st.session_state.submitted    = False
            st.session_state.incorrect    = []
            st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 9. 랭킹판
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("🏆 Leaderboard (Top 20)")

if os.path.exists(RANK_FILE):
    rank = pd.read_csv(RANK_FILE)
    rank = rank.sort_values(by=["score", "wrong_count"], ascending=[False, True]).head(20)
    rank.index = range(1, len(rank)+1)
    st.table(rank[["nickname", "score", "wrong_count", "date"]])
else:
    st.info("No rankings saved yet.")

# ──────────────────────────────────────────────────────────────
# 10. 새 퀴즈
# ──────────────────────────────────────────────────────────────
if st.button("🔄 New Quiz"):
    for k in ["quiz_data", "answers", "submitted", "incorrect", "score", "retry_mode"]:
        st.session_state[k] = defaults[k]
    st.experimental_rerun()
