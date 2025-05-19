# chatbot_engine.py
from fuzzywuzzy import fuzz
from utils.nlp_utils import correct_spelling

class TherapyChatbot:
    def __init__(self, questions):
        self.questions = questions

    def get_question(self, session_number, question_index):
        session_key = f"session_{session_number}"
        if session_key in self.questions and question_index < len(self.questions[session_key]):
            return self.questions[session_key][question_index]
        return None

    def analyze_response(self, user_input):
        corrected = correct_spelling(user_input)
        if any(word in corrected.lower() for word in ["sad", "depressed", "hopeless"]):
            sentiment = "negative"
        elif any(word in corrected.lower() for word in ["happy", "hopeful", "better"]):
            sentiment = "positive"
        else:
            sentiment = "neutral"
        return {
            "original": user_input,
            "corrected": corrected,
            "sentiment": sentiment
        }
