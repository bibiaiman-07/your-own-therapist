import joblib
import os

model_path = os.path.join('model', 'mood_classifier.pkl')
model = joblib.load(model_path)

def predict_mood(text):
    return model.predict([text])[0]

