import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

# Load dataset
df = pd.read_csv('dataset/mood_dataset.csv')

# Split data
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['mood'], test_size=0.2, random_state=42)

# Create a pipeline
model = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', MultinomialNB())
])

# Train model
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'model/mood_classifier.pkl')

print("Model trained and saved successfully.")
