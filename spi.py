from flask import Flask, request, jsonify, render_template
import re
from textblob import TextBlob
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import os

app = Flask(__name__)
load_dotenv()
CORS(app, origins=["https://app.rework.club"])
# Define the rubric with corrected weights
rubric = {
    "Excellent": {
        "min_score": 90,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Good": {
        "min_score": 75,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Satisfactory": {
        "min_score": 55,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Fair": {
        "min_score": 40,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Poor": {
        "min_score": 0,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    }
}

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')

    prompt = f"""
Imagine you are conducting a professional interview and your task is to evaluate the candidate's response to a specific question. The question posed to the candidate is: "{question}". 

In this evaluation, you will consider several key aspects of the candidate's response:
Accuracy: The response should be factually correct, demonstrating a solid understanding of the topic.
Completeness: Assess if the response covers all essential aspects of the question with relevant details, balancing conciseness and comprehensiveness.
Relevance: Evaluate how directly the response addresses the question and aligns with the role's requirements.
Clarity: Look for clear, concise language appropriate for a professional setting, avoiding ambiguity.
Depth: Evaluate if the response shows a deep understanding of the topic, providing insightful analysis beyond surface-level explanations.
Organization: Check for a well-organized structure with logical flow and clear transitions between ideas, reflecting effective communication skills.
Use of Evidence: Note if the response uses appropriate evidence like statistics, research findings, or personal experiences to support claims.
Grammar and Spelling: Consider grammatical accuracy and spelling, which enhance readability and professionalism.
Sentiment: Assess the overall tone and emotion conveyed—looking for professionalism, confidence, and positivity.

After evaluating each aspect of the candidate's response thoroughly, assign a score (ranging from 0 to 100) and justify your assessments with specific examples from the Candidate's Response, highlighting strengths and areas for improvement.

Candidate's Response: "{answer}"
"""

    genai.configure(api_key=os.getenv("gemini_api_key"))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    evaluation = response.text.strip()
    scores = [float(value) for value in re.findall(r'-?\d+', evaluation)]

    breakdown_percentage = {criterion: min(score * rubric["Excellent"]["criteria"][criterion]["weight"], 100) for criterion, score in zip(rubric["Excellent"]["criteria"].keys(), scores)}

    # Calculate the final score
    final_score = min(sum(breakdown_percentage.values()), 100)

    sentiment = TextBlob(answer).sentiment.polarity

    grade = None
    for level, level_criteria in rubric.items():
        if final_score >= level_criteria["min_score"]:
            grade = level
            break

    return jsonify({
        "final_score": final_score,
        "grade": grade,
        "breakdown": breakdown_percentage,
        "sentiment": sentiment
    })

@app.route('/')
def index():
    return render_template('spi.html')

if __name__ == '__main__':
    app.run(debug=True)
