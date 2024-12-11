from flask import Flask, request, jsonify
from flask_cors import CORS
from evaluation import GradingGraph
import os
import shutil

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File upload folder configuration with the full path
UPLOAD_FOLDER = 'D:/PaperPilot/frontend/uploads'

@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        # Clear the entire uploads folder before saving new files
        if os.path.exists(UPLOAD_FOLDER):
            try:
                shutil.rmtree(UPLOAD_FOLDER)  # Delete the entire uploads folder
                print(f"Deleted folder: {UPLOAD_FOLDER}")
            except Exception as e:
                print(f"Error deleting folder {UPLOAD_FOLDER}: {e}")
                return jsonify({"error": f"Could not clear uploads folder: {e}"}), 500

        # Recreate the uploads folder
        try:
            os.makedirs(UPLOAD_FOLDER)
            print(f"Created folder: {UPLOAD_FOLDER}")
        except Exception as e:
            print(f"Error creating folder {UPLOAD_FOLDER}: {e}")
            return jsonify({"error": f"Could not create uploads folder: {e}"}), 500

        # Define paths for question paper, marking scheme, and student answers
        question_path = os.path.join(UPLOAD_FOLDER, 'question_paper.txt')
        marking_scheme_path = os.path.join(UPLOAD_FOLDER, 'marking_scheme.txt')
        student_answers_folder = os.path.join(UPLOAD_FOLDER, 'student_answers')

        # Recreate student answers folder
        try:
            os.makedirs(student_answers_folder)
            print(f"Created folder: {student_answers_folder}")
        except Exception as e:
            print(f"Error creating folder {student_answers_folder}: {e}")
            return jsonify({"error": f"Could not create student answers folder: {e}"}), 500

        # Get files from the form
        question_file = request.files['question_file']
        marking_scheme_file = request.files['marking_scheme_file']
        student_answers_files = request.files.getlist('student_answers_files')

        # Save individual files
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

        # Run grading using GradingGraph
        try:
            grading_graph = GradingGraph()
            feedback_results = grading_graph.run_grading(question_path, marking_scheme_path, student_answers_folder)
        except Exception as e:
            print(f"Error running grading: {e}")
            return jsonify({"error": f"Grading process failed: {e}"}), 500

        # Prepare the results in JSON-serializable format
        feedback_serializable = []
        for feedback in feedback_results.get('feedback', []):
            feedback_serializable.append({
                "filename": feedback['filename'],
                "feedback": feedback['feedback']
            })

        return jsonify({"feedback": feedback_serializable})

if __name__ == '__main__':
    app.run(debug=True)
