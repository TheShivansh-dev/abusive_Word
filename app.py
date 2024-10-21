from flask import Flask, request, jsonify
from better_profanity import profanity
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for the API

# Initialize the profanity filter
profanity.load_censor_words()

# Ensure that stopwords are downloaded only once
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

# Function to remove stopwords
def remove_stopwords(text):
    words = re.findall(r'\b\w+\b', text.lower())  # Tokenize text into words
    filtered_words = [word for word in words if word not in stop_words]  # Remove stopwords
    return ' '.join(filtered_words)  # Join the filtered words back into a sentence

# Function to detect and return only abusive words
def detect_abusive_words(text):
    words = re.findall(r'\b\w+\b', text.lower())  # Tokenize the text into words
    abusive_words = [word for word in words if profanity.contains_profanity(word)]  # Find abusive words
    return abusive_words

# Function to check for basic grammar mistakes (e.g., missing punctuation, repeated words)
def check_basic_grammar(text):
    errors = []
    # Check if the text ends with proper punctuation
    if text.strip()[-1] not in '.!?':
        errors.append("The sentence does not end with proper punctuation (e.g., '.', '!', '?').")
    
    # Simple check for consecutive repeated words
    words = re.findall(r'\b\w+\b', text.lower())  # Tokenize the text into words
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            errors.append(f"Word repetition detected: '{words[i]}' is repeated consecutively.")
    
    return errors

# Function to detect repetitive words based on a threshold (default is 2)
def detect_repetitive_words(text, threshold=2):
    words = re.findall(r'\b\w+\b', text.lower())  # Tokenize text into words
    word_counts = Counter(words)  # Count the occurrence of each word
    repetitive_words = [word for word, count in word_counts.items() if count >= threshold]
    return repetitive_words

# API route to process the text
@app.route('/process_text', methods=['POST'])
def process_text():
    # Expecting JSON input with a 'text' field
    data = request.json
    user_input = data.get('text', '')
    
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    # Remove stopwords from the input text
    filtered_input = remove_stopwords(user_input)

    # Detect abusive words
    abusive_detected = detect_abusive_words(filtered_input)

    # Check for basic grammar mistakes
    grammar_errors = check_basic_grammar(filtered_input)

    # Detect repetitive words (words that appear more than twice, for example)
    repetitive_words = detect_repetitive_words(filtered_input)

    # Prepare the result in a dictionary format
    result = {
        "filtered_text": filtered_input,
        "abusive_words": abusive_detected,
        "grammar_errors": grammar_errors,
        "repetitive_words": repetitive_words
    }

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
