from google import generativeai as genai
from langgraph.graph import StateGraph, Graph
from typing import Dict, Any, List
from flask import Flask, request, jsonify
import os
from typing_extensions import TypedDict

# Configure the API key for the Generative AI model
genai.configure(api_key="AIzaSyBamCfjQfvXxgYRmOngc6yWwVeQIULspZ8")

# Define the base prompt for evaluating code based on a marking scheme
BASE_PROMPT = """
You are an assistant helping grade coding assignments. Evaluate the student's code based on the provided marking scheme.
Focus on logic and readability. If the code is incomplete but has a correct approach, assign partial marks. Provide detailed
feedback for improvement.
"""

# Define the state schema using TypedDict
class GradingState(TypedDict):
    question_file: str
    marking_scheme_file: str
    student_answers_folder: str
    question: str
    marking_scheme: str
    student_answers: str
    feedback: List[str]

# Modify the agents to be callable classes
class QuestionParserAgent:
    def __call__(self, state):
        with open(state["question_file"], 'r') as file:
            return {"question": file.read()}

class MarkingSchemeAgent:
    def __call__(self, state):
        with open(state["marking_scheme_file"], 'r') as file:
            return {"marking_scheme": file.read()}

class FeedbackGenerationAgent:
    def __call__(self, state):
        folder_path = state["student_answers_folder"]
        feedback_results = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):  # Adjust for your file extensions
                with open(os.path.join(folder_path, filename), 'r') as file:
                    student_code = file.read()
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    feedback = model.generate_content(f"{BASE_PROMPT}\nQuestion: {state['question']}\nMarking Scheme: {state['marking_scheme']}\nStudent's Code:\n```\n{student_code}\n```")
                    feedback_results.append({
                        "filename": filename,
                        "feedback": self.serialize_response(feedback)  # Serialize response before storing
                    })
        return {"feedback": feedback_results}
    
    @staticmethod
    def serialize_response(response):
        """Custom serialization to convert response object into JSON-compatible format"""
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'content'):
            return response.content
        else:
            return str(response)

# Define the graph and agents
class GradingGraph:
    def __init__(self):
        self.workflow = StateGraph(state_schema=GradingState)
        
        # Add nodes and their configs
        self.workflow.add_node("question_parser", QuestionParserAgent())
        self.workflow.add_node("marking_scheme_parser", MarkingSchemeAgent())
        self.workflow.add_node("feedback_generation", FeedbackGenerationAgent())
        
        # Define the flow
        self.workflow.set_entry_point("question_parser")
        self.workflow.add_edge("question_parser", "marking_scheme_parser")
        self.workflow.add_edge("marking_scheme_parser", "feedback_generation")
        
        # Build the graph
        self.graph = self.workflow.compile()

    def run_grading(self, question_file, marking_scheme_file, student_answers_folder):
        print("Starting grading process...")  # Debug print
        initial_state = {
            "question_file": question_file,
            "marking_scheme_file": marking_scheme_file,
            "student_answers_folder": student_answers_folder,
            "question": "",
            "marking_scheme": "",
            "student_answers": "",
            "feedback": []
        }
        
        result = self.graph.invoke(initial_state)
        print("Grading process completed")  # Debug print
        return result

if __name__ == '__main__':
    # File paths input by the user
    question_file = input("Enter the path to the question paper file:\n")
    marking_scheme_file = input("Enter the path to the marking scheme file:\n")
    student_answers_folder = input("Enter the path to the folder containing student answers:\n")

    # Initialize the LangGraph Grading system
    grading_graph = GradingGraph()

    # Run the grading process and get feedback
    results = grading_graph.run_grading(question_file, marking_scheme_file, student_answers_folder)

    # Output the feedback for each student
    for result in results["feedback"]:
        print(f"\nFeedback for {result['filename']}:")
        print(result['feedback'])
