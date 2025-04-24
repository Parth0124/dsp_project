# Contents of answer_evaluator.py
from openai import OpenAI
import json

class AnswerEvaluator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
    
    def evaluate_answer(self, question, reference_answer, user_answer, question_type):
        """Evaluate the user's answer compared to the reference answer."""
        prompt = f"""
        Evaluate the accuracy of the user's answer compared to the reference answer for the following question.
        Provide a percentage score (0-100) based on correctness and completeness.

        Question: {question}
        Question Type: {question_type}
        Reference Answer: {reference_answer}
        User Answer: {user_answer}

        For listening and memory questions, evaluate based on factual accuracy.
        For reasoning questions, evaluate based on validity of reasoning, depth of insight, and relevance.

        Format your response as a JSON object with 'score' (number), 'explanation' (string), and 'feedback' (string) fields.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a fair and consistent evaluator of reading comprehension answers."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
