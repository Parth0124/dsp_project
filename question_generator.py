# Contents of question_generator.py
from openai import OpenAI
import json

class QuestionGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
    
    def generate_listening_questions(self, story):
        """Generate questions that test basic listening/reading comprehension."""
        prompt = f"""
        Generate 2 questions that test basic reading comprehension for the following story. 
        These questions should be directly answerable from the text and test if the reader has read the story attentively.
        
        Story: {story}
        
        Format your response as a JSON array with each question object having 'question', 'answer', and 'explanation' fields.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant that generates reading comprehension questions."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.choices[0].message.content)["questions"]
        except:
            # Fallback parsing method
            content = response.choices[0].message.content
            # Extract JSON array using regex or other methods
            # This is a simplification, proper error handling would be needed
            return json.loads(content)["questions"]
    
    def generate_memory_questions(self, story):
        """Generate questions that test memory of details from the story."""
        prompt = f"""
        Generate 2 questions that test memory of specific details from the following story.
        These questions should require recalling specific details that are mentioned in the story but might not be the main focus.
        
        Story: {story}
        
        Format your response as a JSON array with each question object having 'question', 'answer', and 'explanation' fields.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant that generates memory-based questions."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.choices[0].message.content)["questions"]
        except:
            content = response.choices[0].message.content
            return json.loads(content)["questions"]
    
    def generate_reasoning_questions(self, story):
        """Generate questions that require reasoning beyond the text."""
        prompt = f"""
        Generate 2 questions about the following story that require reasoning, critical thinking, or applying common sense.
        These questions should not be directly answerable from the text but require understanding themes, morals, character motivations, or drawing inferences.
        Examples include questions about the moral of the story, values learned, or character analysis.
        
        Story: {story}
        
        Format your response as a JSON array with each question object having 'question', 'answer', and 'explanation' fields.
        The 'answer' should be a model answer that captures key points a good response would contain.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant that generates critical thinking questions."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.choices[0].message.content)["questions"]
        except:
            content = response.choices[0].message.content
            return json.loads(content)["questions"]