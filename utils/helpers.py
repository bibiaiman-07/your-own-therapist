# utils/helpers.py

import random

def generate_bot_reaction(user_message, sentiment):
    """
    Return a dynamic bot reaction message based on user input and sentiment.
    """
    if sentiment == 'positive':
        responses = [
            "That's wonderful to hear! 😊",
            "I'm glad you're feeling that way!",
            "Keep up the great mindset! 👍"
        ]
    elif sentiment == 'negative':
        responses = [
            "I'm sorry you're feeling like that. I'm here for you. 💙",
            "That sounds tough. Would you like to talk more about it?",
            "It's okay to feel this way sometimes. You're not alone."
        ]
    else:
        responses = [
            "Thanks for sharing that.",
            "I see. Could you tell me more?",
            "I'm listening."
        ]
    
    return random.choice(responses)
