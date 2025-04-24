import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

class StoryProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def clean_text(self, text):
        """Clean and preprocess the input text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def split_into_chunks(self, text):
        """Split the text into manageable chunks."""
        return self.text_splitter.split_text(text)
    
    def process(self, text):
        """Process the input text."""
        cleaned_text = self.clean_text(text)
        chunks = self.split_into_chunks(cleaned_text)
        return {
            "full_text": cleaned_text,
            "chunks": chunks
        }