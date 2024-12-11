from flask import Flask, request, jsonify
from flask_cors import CORS
from evaluation import GradingGraph
import os
import shutil
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
CORS(app)  

UPLOAD_FOLDER = 'D:/PaperPilot/frontend/uploads'

@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
       
        if os.path.exists(UPLOAD_FOLDER):
            try:
                shutil.rmtree(UPLOAD_FOLDER)  
                print(f"Deleted folder: {UPLOAD_FOLDER}")
            except Exception as e:
                print(f"Error deleting folder {UPLOAD_FOLDER}: {e}")
                return jsonify({"error": f"Could not clear uploads folder: {e}"}), 500

       
        try:
            os.makedirs(UPLOAD_FOLDER)
            print(f"Created folder: {UPLOAD_FOLDER}")
        except Exception as e:
            print(f"Error creating folder {UPLOAD_FOLDER}: {e}")
            return jsonify({"error": f"Could not create uploads folder: {e}"}), 500

        question_path = os.path.join(UPLOAD_FOLDER, 'question_paper.txt')
        marking_scheme_path = os.path.join(UPLOAD_FOLDER, 'marking_scheme.txt')
        student_answers_folder = os.path.join(UPLOAD_FOLDER, 'student_answers')


        try:
            os.makedirs(student_answers_folder)
            print(f"Created folder: {student_answers_folder}")
        except Exception as e:
            print(f"Error creating folder {student_answers_folder}: {e}")
            return jsonify({"error": f"Could not create student answers folder: {e}"}), 500

      
        question_file = request.files['question_file']
        marking_scheme_file = request.files['marking_scheme_file']
        student_answers_files = request.files.getlist('student_answers_files')


        recheck_request = False  
        recheck_reason = ''
        if 'recheck_reason' in request.form:
            recheck_reason = request.form['recheck_reason'].strip()
            recheck_request = recheck_reason != ''

       
        try:
            question_file.save(question_path)
            print(f"Saved question paper to: {question_path}")

            marking_scheme_file.save(marking_scheme_path)
            print(f"Saved marking scheme to: {marking_scheme_path}")

            for student_file in student_answers_files:
                save_path = os.path.join(student_answers_folder, student_file.filename)
                student_file.save(save_path)
                print(f"Saved student answer to: {save_path}")
        except Exception as e:
            print(f"Error saving files: {e}")
            return jsonify({"error": f"Could not save uploaded files: {e}"}), 500

       

        try:
            grading_graph = GradingGraph()
            feedback_results = grading_graph.run_grading(question_path, marking_scheme_path, student_answers_folder,recheck_request=recheck_request)
            print("Feedback results from grading:", feedback_results)  
            
        except Exception as e:
            print(f"Error running grading: {e}")
            return jsonify({"error": f"Grading process failed: {e}"}), 500

        
        feedback_serializable = []
        for feedback in feedback_results.get('feedback', []):
            print("Processing feedback:", feedback)  
            feedback_content = feedback.get('feedback',"no feedback generated")

            
            feedback_serializable.append({
                "filename": feedback.get('filename', 'Unknown File'),
                "feedback": feedback_content
            })

        print("Final feedback serializable:", feedback_serializable)  
        return jsonify({"feedback": feedback_serializable})

@app.route('/recheck', methods=['POST'])
def recheck():
    try:
        data = request.get_json()
        filename = data.get("filename", "")
        reason = data.get("reason", "")

        # Ensure required fields are provided
        if not filename or not reason:
            return jsonify({"error": "Missing filename or reason"}), 400

        # Paths to question paper and marking scheme
        question_path = os.path.join(UPLOAD_FOLDER, 'question_paper.txt')
        marking_scheme_path = os.path.join(UPLOAD_FOLDER, 'marking_scheme.txt')
        student_file_path = os.path.join(UPLOAD_FOLDER, "student_answers", filename)
        if not os.path.exists(student_file_path):
            return jsonify({"error": f"File not found: {filename}"}), 404
        
        with open(student_file_path, 'r') as f:
            student_code = f.read()

        # Read content of question paper and marking scheme
        try:
            with open(question_path, 'r') as q_file:
                question = q_file.read()
            with open(marking_scheme_path, 'r') as m_file:
                marking_scheme = m_file.read()
        except FileNotFoundError as e:
            return jsonify({"error": f"File not found: {e}"}), 404
        except Exception as e:
            return jsonify({"error": f"Error reading files: {e}"}), 500

        # Original feedback could be included as part of the request
        original_feedback = data.get("original_feedback", "")

        # Call GradingGraph to evaluate the recheck
        grading_graph = GradingGraph()
        recheck_result = grading_graph.evaluate_recheck(
            question=question,
            marking_scheme=marking_scheme,
            original_feedback=original_feedback,
            recheck_reason=reason,
            student_code = student_code
        )

        return jsonify({"evaluation": recheck_result.get("recheck_evaluation", "No evaluation result")})
    except Exception as e:
        print(f"Error during recheck evaluation: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
