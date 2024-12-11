# PaperPilot

## Overview

This project is an AI-powered grading system designed to automate the evaluation of coding assignments. It uses advanced language models (LLMs) to provide detailed feedback, assign grades based on a marking scheme, and handle recheck requests efficiently.

<iframe width="935" height="526" src="https://www.youtube.com/embed/DuxVzKifhvw" title="PaperPilot" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

---

## Features
- **Automated Grading**: Evaluates coding assignments using a predefined marking scheme.
- **Detailed Feedback**: Generates constructive feedback highlighting areas of improvement.
- **Partial Grading**: Awards partial marks for incomplete but correct approaches.
- **Recheck Workflow**: Processes recheck requests with detailed validation reasoning.
- **Scalable Architecture**: Built with LangGraph for modular processing and easy debugging.
- **Interactive Frontend**: A user-friendly interface to upload assignments and view results.

---

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Virtual environment (recommended)
- Git

### Clone the Repository
```bash
git clone https://github.com/AmanMehrishi/PaperPilot.git
cd PaperPilot
```

### Install dependencies:
```bash
pip install -r requirements.txt
```
### Add your LLM API key (Gemini) in the configuration:
- Update evaluation.py or .env file with your API key.

### Run the backend:
```bash
python grading_app.py
```

---

## Frontend Setup

### Navigate to the frontend folder:
```bash
cd frontend
```
### Install dependencies:
```bash
npm install
```
### Start the development server:
```bash
npm run dev
```

---

## Usage

1. Access the frontend at http://localhost:5173.
2. Upload:
     - Question Paper(.txt)
     - Marking Scheme (.txt)
     - Student Answer Files (multiple .txt files can be uploaded)
3. View detailed feedback and grades for each submission.
4. Submit recheck requests directly through the UI.

---

## Testing
We tested the system with 10 diverse coding questions, evaluating its performance in:
-Accuracy of grading.
-Quality of feedback.
-Efficiency in handling rechecks.

### Results
Accuracy: 95% match with manual grading.
Feedback Quality: Rated highly detailed and actionable.
Time Efficiency: Graded 10 submissions in under 2 minutes.

---

## System Design

### Backend
- LangGraph: Modular state graph for task orchestration.
- Agents:
    - Question Parsing
    - Marking Scheme Parsing
    - Feedback Generation
    - Recheck Evaluation

### Frontend
- Built with TypeScript and SCSS for an interactive and responsive user interface.
- Features:
    - Upload multiple files simultaneously.
    - Feedback display with expandable cards.
    - Recheck request modal.
