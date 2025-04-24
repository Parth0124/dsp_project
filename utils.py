# Contents of 
import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables."""
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }

def calculate_average_score(scores):
    """Calculate the average score."""
    if not scores:
        return 0
    return sum(scores) / len(scores)