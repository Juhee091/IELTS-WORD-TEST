import streamlit as st
import pandas as pd
import random
import datetime

# Load vocabulary CSV
df = pd.read_csv("IELTS_vocab_extracted.csv")
df.dropna(inplace=True)

# State initialization
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "completed" not in st.session_state:
    st.session_state.completed = []

# Get today's quiz seed (ensures repeatable questions per day)
today = datetime.date.today().isoformat()
random.seed(today + st.session_state.nickname)

# UI: Nickname input
if not st.session_state.nickname:
    st.title("IELTS Vocabulary Quiz")
    nickname = st.text_input("Enter your nickname to begin:")
    if nickname:
        st.session_state.nickname = nickname
        st.experimental_rerun()
else:
    st.title(f"Welcome, {st.session_state.nickname}! ✨")
    st.write(f"📅 Today's quiz - {today}")

    # Prepare quiz questions
    quiz_pool = df.sample(frac=1, random_state=random.randint(1, 9999)).reset_index(drop=True)
    questions = quiz_pool.head(50)

    score = 0
    for idx, row in questions.iterrows():
        direction = random.choice(["en2ko", "ko2en"])
        options = [row['Word'] if direction == "ko2en" else row['Meaning']]
        while len(options) < 4:
            sample = df.sample(1).iloc[0]
            opt = sample['Word'] if direction == "ko2en" else sample['Meaning']
            if opt not in options:
                options.append(opt)
        random.shuffle(options)

        # Ask question
        st.subheader(f"Q{idx+1}")
        question = row['Meaning'] if direction == "en2ko" else row['Word']
        answer = row['Word'] if direction == "ko2en" else row['Meaning']
        user_answer = st.radio(f"What is the meaning of: **{question}**", options, key=f"q_{idx}")

        if user_answer == answer:
            score += 1

    # Show score
    st.write("---")
    st.success(f"✅ You got {score} out of 50 correct!")
    st.balloons()

    # Save user record
    if today not in st.session_state.completed:
        st.session_state.completed.append(today)
        st.session_state.score = score
        with open("quiz_log.csv", "a", encoding="utf-8") as f:
            f.write(f"{today},{st.session_state.nickname},{score}\n")

    # Show leaderboard
    st.write("## 📊 Leaderboard (Today)")
    try:
        logs = pd.read_csv("quiz_log.csv", names=["Date", "Name", "Score"])
        today_logs = logs[logs["Date"] == today].sort_values(by="Score", ascending=False)
        st.dataframe(today_logs.reset_index(drop=True))
    except Exception as e:
        st.error(f"Could not load leaderboard: {e}")
