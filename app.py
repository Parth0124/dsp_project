
import streamlit as st
import os
from utils import load_environment
from story_processor import StoryProcessor
from question_generator import QuestionGenerator
from answer_evaluator import AnswerEvaluator

# Initialize environment
try:
    env = load_environment()
    OPENAI_API_KEY = env["openai_api_key"]
except Exception as e:
    st.error(f"Error loading environment: {e}")
    OPENAI_API_KEY = None

# Initialize components
story_processor = StoryProcessor()
question_generator = QuestionGenerator(OPENAI_API_KEY)
answer_evaluator = AnswerEvaluator(OPENAI_API_KEY)

# Set up session state
if 'story' not in st.session_state:
    st.session_state.story = None
if 'current_question_type' not in st.session_state:
    st.session_state.current_question_type = "listening"
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'questions' not in st.session_state:
    st.session_state.questions = {
        "listening": [],
        "memory": [],
        "reasoning": []
    }
if 'scores' not in st.session_state:
    st.session_state.scores = {
        "listening": [],
        "memory": [],
        "reasoning": []
    }
if 'completed_types' not in st.session_state:
    st.session_state.completed_types = set()

def reset_session():
    """Reset the session state."""
    st.session_state.story = None
    st.session_state.current_question_type = "listening"
    st.session_state.current_question_index = 0
    st.session_state.questions = {
        "listening": [],
        "memory": [],
        "reasoning": []
    }
    st.session_state.scores = {
        "listening": [],
        "memory": [],
        "reasoning": []
    }
    st.session_state.completed_types = set()

def generate_questions(story):
    """Generate all types of questions for the story."""
    with st.spinner("Generating questions..."):
        listening_questions = question_generator.generate_listening_questions(story)
        memory_questions = question_generator.generate_memory_questions(story)
        reasoning_questions = question_generator.generate_reasoning_questions(story)
        
        st.session_state.questions = {
            "listening": listening_questions,
            "memory": memory_questions,
            "reasoning": reasoning_questions
        }

def submit_answer(user_answer):
    """Process the user's answer."""
    question_type = st.session_state.current_question_type
    question_index = st.session_state.current_question_index
    current_question = st.session_state.questions[question_type][question_index]
    
    with st.spinner("Evaluating your answer..."):
        evaluation = answer_evaluator.evaluate_answer(
            current_question["question"],
            current_question["answer"],
            user_answer,
            question_type
        )
    
    st.session_state.scores[question_type].append(evaluation["score"])
    
    # Display evaluation
    st.success(f"Evaluation: {evaluation['score']}% accuracy")
    st.info(f"Feedback: {evaluation['feedback']}")
    
    # Move to next question or question type
    if question_index < len(st.session_state.questions[question_type]) - 1:
        st.session_state.current_question_index += 1
    else:
        # Completed all questions of current type
        st.session_state.completed_types.add(question_type)
        avg_score = sum(st.session_state.scores[question_type]) / len(st.session_state.scores[question_type])
        st.success(f"Completed all {question_type} questions with average score: {avg_score:.1f}%")
        
        # Move to next question type
        if question_type == "listening" and "listening" in st.session_state.completed_types:
            st.session_state.current_question_type = "memory"
            st.session_state.current_question_index = 0
        elif question_type == "memory" and "memory" in st.session_state.completed_types:
            st.session_state.current_question_type = "reasoning"
            st.session_state.current_question_index = 0
        elif question_type == "reasoning" and "reasoning" in st.session_state.completed_types:
            st.success("Congratulations! You've completed all questions.")
            st.balloons()
            
            # Calculate final score
            total_score = 0
            total_questions = 0
            for q_type in ["listening", "memory", "reasoning"]:
                if st.session_state.scores[q_type]:
                    total_score += sum(st.session_state.scores[q_type])
                    total_questions += len(st.session_state.scores[q_type])
            
            final_score = total_score / total_questions if total_questions > 0 else 0
            st.success(f"Final score: {final_score:.1f}%")

# Main application
st.title("Story Comprehension Assessment")
st.write("Enter a story, and we'll generate questions to test your comprehension.")

# Story input
story_text = st.text_area("Enter your story here:", height=300)

if st.button("Process Story"):
    if story_text.strip():
        with st.spinner("Processing story..."):
            processed_story = story_processor.process(story_text)
            st.session_state.story = processed_story["full_text"]
            generate_questions(processed_story["full_text"])
            st.success("Story processed! Let's start with the questions.")
            # Reset progress
            st.session_state.current_question_type = "listening"
            st.session_state.current_question_index = 0
            st.session_state.scores = {"listening": [], "memory": [], "reasoning": []}
            st.session_state.completed_types = set()
    else:
        st.error("Please enter a story.")

# Display questions and collect answers
if st.session_state.story and st.session_state.questions:
    question_type = st.session_state.current_question_type
    question_index = st.session_state.current_question_index
    
    if question_type in st.session_state.completed_types and "reasoning" in st.session_state.completed_types:
        st.success("All questions completed!")
        
        # Display final scores
        st.subheader("Final Scores")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            listening_avg = sum(st.session_state.scores["listening"]) / len(st.session_state.scores["listening"]) if st.session_state.scores["listening"] else 0
            st.metric("Listening", f"{listening_avg:.1f}%")
        
        with col2:
            memory_avg = sum(st.session_state.scores["memory"]) / len(st.session_state.scores["memory"]) if st.session_state.scores["memory"] else 0
            st.metric("Memory", f"{memory_avg:.1f}%")
        
        with col3:
            reasoning_avg = sum(st.session_state.scores["reasoning"]) / len(st.session_state.scores["reasoning"]) if st.session_state.scores["reasoning"] else 0
            st.metric("Reasoning", f"{reasoning_avg:.1f}%")
        
        total_avg = (listening_avg + memory_avg + reasoning_avg) / 3
        st.metric("Overall", f"{total_avg:.1f}%")
        
        if st.button("Start Over"):
            reset_session()
            st.experimental_rerun()
    else:
        if question_type == "listening":
            st.subheader("Listening Comprehension Question")
            st.info("These questions test if you've read the story attentively.")
        elif question_type == "memory":
            st.subheader("Memory Question")
            st.info("These questions test your memory of specific details from the story.")
        elif question_type == "reasoning":
            st.subheader("Reasoning Question")
            st.info("These questions require critical thinking beyond what's directly stated in the story.")
        
        if question_index < len(st.session_state.questions[question_type]):
            current_question = st.session_state.questions[question_type][question_index]
            st.write(f"**Question {question_index + 1}:** {current_question['question']}")
            
            user_answer = st.text_area("Your answer:", key=f"{question_type}_{question_index}")
            
            if st.button("Submit Answer"):
                if user_answer.strip():
                    submit_answer(user_answer)
                    st.experimental_rerun()
                else:
                    st.error("Please enter an answer.")