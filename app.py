import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_questions(story, question_type):
    prompt_map = {
        "listening": "Generate 2 questions that check careful reading/listening. Answers should be obvious. Provide ONLY the questions, no answers.",
        "memory": "Generate 2 questions requiring memory of specific details. Provide ONLY the questions, no answers.", 
        "reasoning": "Generate 2 questions requiring reasoning or moral judgment. Provide ONLY the questions, no answers."
    }
    prompt = f"Story:\n{story}\n\n{prompt_map[question_type]}\nFormat: One question per line, no numbering."
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    questions = []
    for line in response.choices[0].message.content.split("\n"):
        clean_line = line.strip().split(". ", 1)[-1].replace('"', '').strip()
        if clean_line and clean_line[-1] == "?":
            questions.append(clean_line)
    return questions[:2]

def evaluate_answer(story, question, user_answer):
    prompt = f"""Story:
{story}

Question: {question}
User's Answer: {user_answer}

Evaluate correctness, completeness, and clarity. Give percentage score (0-100) and brief explanation. Do NOT ask follow-up questions."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

st.title("🧠 Story Comprehension Question Pipeline")
story = st.text_area("Paste your story here:", height=400)

if story:
    if "stage" not in st.session_state:
        st.session_state.stage = 1
        st.session_state.show_next_button = False

    stage = st.session_state.stage
    questions_key = f"questions_{stage}"
    answers_key = f"answers_{stage}"

    if questions_key not in st.session_state:
        question_types = ["listening", "memory", "reasoning"]
        generated_questions = generate_questions(story, question_types[stage-1])
        st.session_state[questions_key] = generated_questions
        st.session_state[answers_key] = [""] * len(generated_questions)

    st.subheader(f"{['Listening', 'Memory', 'Reasoning'][stage-1]} Questions")
    
    for i, q in enumerate(st.session_state[questions_key]):
        st.write(f"**Q{i+1}:** {q}")
        st.session_state[answers_key][i] = st.text_input(f"Your Answer {i+1}", key=f"ans_{stage}_{i}")

    if st.button("Submit Answers"):
        st.session_state.show_next_button = False
        all_pass = True
        for i, ans in enumerate(st.session_state[answers_key]):
            feedback = evaluate_answer(story, st.session_state[questions_key][i], ans)
            st.markdown(f"**Feedback Q{i+1}:**\n{feedback}")
            
            score = 0
            if "%" in feedback:
                score = int(''.join(filter(str.isdigit, feedback.split("%")[0])))
            if score < 60:
                all_pass = False
        
        if all_pass:
            if stage < 3:
                st.session_state.show_next_button = True
            else:
                st.success("🎉 All levels completed!")
        else:
            st.warning("❗ Some answers need improvement. Try again!")

    if st.session_state.get('show_next_button') and stage < 3:
        if st.button("Next Stage →"):
            st.session_state.stage += 1
            st.session_state.show_next_button = False
            st.rerun()