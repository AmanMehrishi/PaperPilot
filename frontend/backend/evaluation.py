from google import generativeai as genai
from langgraph.graph import StateGraph, Graph
from typing import Dict, Any, List
from dataclasses import dataclass
import os
from typing_extensions import TypedDict


genai.configure(api_key="KEY_HERE")

BASE_PROMPT = """
You are an assistant helping grade coding assignments. Evaluate the student's code based on the provided marking scheme.
Focus on logic and readability. If the code is incomplete but has a correct approach, assign partial marks. Provide detailed
feedback for improvement. Please provide the total score achieved by the student accross all questions at the end with the format 'Final Total: ' and then the total score achieved out of the total possible score
"""


class GradingState(TypedDict):
    question_file: str
    marking_scheme_file: str
    student_answers_folder: str
    question: str
    marking_scheme: str
    student_answers: str
    feedback: List[str]
    recheck_request: bool
    recheck_reason: str
    original_feedback: str
    student_code: str


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
        print("Starting feedback generation...")  
        folder_path = state["student_answers_folder"]
        print(f"Looking for .py files in: {folder_path}")  
        
        
        all_files = os.listdir(folder_path)
        print(f"Files found in directory: {all_files}") 
        
        feedback_results = []
        for filename in all_files:
            print(f"Checking file: {filename}")  
            if filename.endswith('.txt'):
                print(f"Processing Python file: {filename}")  
                with open(os.path.join(folder_path, filename), 'r') as file:
                    student_code = file.read()
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    feedback = model.generate_content(f"{BASE_PROMPT}\nQuestion: {state['question']}\nMarking Scheme: {state['marking_scheme']}\nStudent's Code:\n```\n{student_code}\n```")
                    feedback_text = feedback.text
                    feedback_results.append({"filename": filename, "feedback": feedback_text})
        
        print(f"Generated feedback for {len(feedback_results)} files")  
        return {"feedback": feedback_results}
    
class RecheckEvaluationAgent:
    def __call__(self, state):
        print("Evaluating recheck request...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        recheck_reason = state["recheck_reason"]
        original_feedback = state["original_feedback"]
        question = state["question"]
        marking_scheme = state["marking_scheme"]
        student_code = state["student_code"]

        prompt = f"""
        Context:
        - Question: {question}
        - Marking Scheme: {marking_scheme}
        - Original Feedback: {original_feedback}
        - Student Code: {student_code}
        - Recheck Reason: {recheck_reason}

        Task:
        - Determine if the recheck request is valid.
        - Provide a concise explanation for your decision.

        Response Format:
        - Validity: [Yes/No]
        - Reason: [Explanation]
        """

        response = model.generate_content(prompt)
        evaluation_result = response.text.strip()
        print(f"Recheck evaluation result: {evaluation_result}")
        return {"recheck_evaluation": evaluation_result}



class GradingGraph:
    def __init__(self):
        self.grading_workflow = StateGraph(state_schema=GradingState)
        self.recheck_workflow = StateGraph(state_schema=GradingState)
        
       
        self.grading_workflow.add_node("question_parser", QuestionParserAgent())
        self.grading_workflow.add_node("marking_scheme_parser", MarkingSchemeAgent())
        self.grading_workflow.add_node("feedback_generation", FeedbackGenerationAgent())
        self.recheck_workflow.add_node("evaluate_recheck", RecheckEvaluationAgent())


        self.grading_workflow.set_entry_point("question_parser")
        self.grading_workflow.add_edge("question_parser", "marking_scheme_parser")
        self.grading_workflow.add_edge("marking_scheme_parser", "feedback_generation")
        
        self.recheck_workflow.set_entry_point("evaluate_recheck")
        
        
        self.grading_graph = self.grading_workflow.compile()
        self.recheck_graph = self.recheck_workflow.compile()

    def run_grading(self, question_file, marking_scheme_file, student_answers_folder, recheck_request=False):
        print("Starting grading process...") 
        initial_state = {
            "question_file": question_file,
            "marking_scheme_file": marking_scheme_file,
            "student_answers_folder": student_answers_folder,
            "question": "",
            "marking_scheme": "",
            "student_answers": "",
            "feedback": [],
            "recheck_request": recheck_request,
            "recheck_reason": ""
        }
        
        result = self.grading_graph.invoke(initial_state)
        print("Grading process completed")  
        return result   
    
    def evaluate_recheck(self, question, marking_scheme, recheck_reason, original_feedback, student_code):
        print("Evaluating recheck request...")
        initial_state = {
            "question": question,
            "marking_scheme": marking_scheme,
            "recheck_reason": recheck_reason,
            "original_feedback": original_feedback,
            "recheck_request": True,  # Explicitly indicate this is a recheck request
            "feedback": [],
            "student_code":student_code
        }

        try:
            result = self.recheck_graph.invoke(initial_state)
            print("Recheck evaluation result:", result)
            return result
        except Exception as e:
            print(f"Error during recheck evaluation: {e}")
            raise RuntimeError(f"Recheck evaluation failed: {e}")

if __name__ == '__main__':
 
    question_file = input("Enter the path to the question paper file:\n")
    marking_scheme_file = input("Enter the path to the marking scheme file:\n")
    student_answers_folder = input("Enter the path to the folder containing student answers:\n")
    recheck_input = input("Is there a recheck request? (yes/no):\n").strip().lower()
    recheck_request = recheck_input == 'yes'


    grading_graph = GradingGraph()


    results = grading_graph.run_grading(
        question_file, marking_scheme_file, student_answers_folder, recheck_request=recheck_request
    )


    for result in results["feedback"]:
        print(f"\nFeedback for {result['filename']}:")
        print(result['feedback'])

    if recheck_request:
        original_feedback = input("Enter the original feedback:\n")
        recheck_reason = input("Enter the recheck reason:\n")
        recheck_result = grading_graph.evaluate_recheck(
            question=results["question"],
            marking_scheme=results["marking_scheme"],
            original_feedback=original_feedback,
            recheck_reason=recheck_reason
        )
        print("\nRecheck Evaluation Result:")
        print(recheck_result["recheck_evaluation"])
