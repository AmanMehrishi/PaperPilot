import './style.scss'

interface FeedbackResult {
    filename: string;
    feedback: string;
}

interface GradingResponse {
    feedback: FeedbackResult[];
}

// Interactive bubble animation and form initialization
document.addEventListener('DOMContentLoaded', () => {
    // Interactive bubble movement
    const interBubble = document.querySelector<HTMLDivElement>('.interactive')!;
    let curX = 0;
    let curY = 0;
    let tgX = 0;
    let tgY = 0;

    function move() {
        curX += (tgX - curX) / 20;
        curY += (tgY - curY) / 20;
        interBubble.style.transform = `translate(${Math.round(curX)}px, ${Math.round(curY)}px)`;
        requestAnimationFrame(() => move());
    }

    window.addEventListener('mousemove', (event) => {
        tgX = event.clientX;
        tgY = event.clientY;
    });

    move();

    // File upload handling
    const uploadForm = document.getElementById('uploadForm') as HTMLFormElement | null;
    if (!uploadForm) {
        console.error('Upload form not found.');
        return;
    }
    
    const submitBtn = uploadForm.querySelector<HTMLButtonElement>('.submit-btn')!;
    const resultsContainer = document.getElementById('results-container') as HTMLDivElement | null;

    const buttonText = submitBtn.querySelector<HTMLSpanElement>('.button-text')!;
    

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        let buttonText = submitBtn.querySelector<HTMLSpanElement>('.button-text');
        if (buttonText) {
            submitBtn.removeChild(buttonText);
        }

        let spinner = document.createElement('span');
        spinner.classList.add('spinner');
        submitBtn.appendChild(spinner);


        submitBtn.disabled = true;

        const formData = new FormData(uploadForm);

        try {
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: GradingResponse = await response.json();
            displayResults(data.feedback);

            // Scroll to results if the container exists
            if (resultsContainer) {
                resultsContainer.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Error uploading files. Please try again.');
        } finally {
            // Reset loading state
            // Re-enable the submit button
            
            submitBtn.removeChild(spinner);

            // Add button text back
            if (!buttonText) {
                buttonText = document.createElement('span');
                buttonText.classList.add('button-text');
                buttonText.textContent = 'Submit'; // Replace with your button text
            }
            submitBtn.appendChild(buttonText);

            // Re-enable the button
            submitBtn.disabled = false;
        }       
    });

    function displayResults(feedbackResults: FeedbackResult[]) {
        const resultsContainer = document.getElementById('results-container') as HTMLDivElement | null;
        if (!resultsContainer) {
            console.error('Results container not found.');
            return;
        }
    
        const resultsGrid = resultsContainer.querySelector<HTMLDivElement>('.results-grid');
        if (!resultsGrid) {
            console.error('Results grid not found.');
            return;
        }
    
        // Clear any existing results
        resultsGrid.innerHTML = '';
    
        // Check if feedbackResults has data
        if (feedbackResults.length === 0) {
            console.log('No feedback to display.');
            resultsContainer.style.display = 'none'; // Hide container if no results
            return;
        }
    
        feedbackResults.forEach((result) => {
            const feedbackCard = document.createElement('div');
            feedbackCard.className = 'feedback-card';
    
            // Extract score from feedback if available
            const scoreMatch = result.feedback.match(/Final Total:\s*(\d+\/\d+)/);
            const score = scoreMatch ? scoreMatch[1] : 'Score not available';
    
            let cleanedFeedback = result.feedback.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            cleanedFeedback = cleanedFeedback.replace(/##/g, ''); // Remove ##
            cleanedFeedback = cleanedFeedback.replace(/\n/g, '<br>'); // Convert newlines to <br> for better formatting
    
            cleanedFeedback = cleanedFeedback.replace(/```python([\s\S]*?)```/g, (_, code) => {
                return `<pre><code class="python">${code.trim()}</code></pre>`;
            });
    
            feedbackCard.innerHTML = `
                <h4>${result.filename}</h4>
                <div class="toggle-icon">
                    <img src="/src/assets/plus.svg" alt="Expand" class="icon-plus visible" />
                    <img src="/src/assets/minus.svg" alt="Collapse" class="icon-minus" />
                </div>
                <div class="feedback-content">${cleanedFeedback}</div>
                <div class="score"><strong>Score:</strong> ${score}</div>
                <button class="recheck-btn">Request Recheck</button>
            `;
    
            resultsGrid.appendChild(feedbackCard);
    
            // Add click event listener for toggling feedback visibility
            const feedbackContent = feedbackCard.querySelector<HTMLDivElement>('.feedback-content');
            const recheckButton = feedbackCard.querySelector<HTMLButtonElement>('.recheck-btn')!;
            
            if (feedbackContent) {
                feedbackCard.addEventListener('click', () => {
                    const isVisible = feedbackContent.classList.toggle('visible');
                    feedbackContent.style.display = isVisible ? 'block' : 'none';

                    const plusIcon = feedbackCard.querySelector<HTMLImageElement>('.icon-plus');
                    const minusIcon = feedbackCard.querySelector<HTMLImageElement>('.icon-minus');

                    if (plusIcon && minusIcon) {
                        // Toggle icons
                        plusIcon.classList.toggle('visible', !isVisible);
                        minusIcon.classList.toggle('visible', isVisible);
                    }
                    feedbackCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                });
            }
    
            // Add click event listener for recheck requests
            recheckButton.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent card click event from firing
                handleRecheckRequest(result);
            });
        });
    
        resultsContainer.style.display = 'block';
        setTimeout(() => {
            resultsContainer.classList.add('visible');
        }, 100);
    }
    

    function handleRecheckRequest(result: FeedbackResult) {
        // Create a form for the student to fill in why they are requesting a recheck
        const modal = document.createElement('div');
        modal.className = 'recheck-modal';
    
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-btn">&times;</span>
                <h2>Request Recheck for: ${result.filename}</h2>
                <textarea id="recheck-reason" rows="5" placeholder="Please describe why you believe this feedback should be reconsidered..."></textarea>
                <button id="submit-recheck">Submit Recheck Request</button>
            </div>
        `;
    
        document.body.appendChild(modal);
    
        const closeBtn = modal.querySelector('.close-btn') as HTMLSpanElement;
        const submitRecheckBtn = modal.querySelector('#submit-recheck') as HTMLButtonElement;
    
        // Close modal
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    
        // Handle recheck submission
        submitRecheckBtn.addEventListener('click', async () => {
            const reason = (modal.querySelector('#recheck-reason') as HTMLTextAreaElement).value;
    
            if (reason.trim() === '') {
                alert('Please provide a reason for your recheck request.');
                return;
            }
    
            // Send recheck request to the backend
            try {
                const response = await fetch('http://localhost:5000/recheck', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        filename: result.filename,
                        reason: reason.trim(),
                        original_feedback: result.feedback,
                    }),
                });
    
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
    
                const responseData = await response.json();
                alert(`Recheck request submitted successfully: ${responseData.evaluation}`);
            } catch (error) {
                console.error('Error submitting recheck request:', error);
                alert(`Failed to submit recheck request. Details: ${error}`);
            } finally {
                document.body.removeChild(modal);
            }
        });
    }
    
    
    const fileInputs = uploadForm.querySelectorAll<HTMLInputElement>('.file-input');
    fileInputs.forEach((input) => {
        input.addEventListener('change', (event) => {
            const target = event.target as HTMLInputElement;
            const label = uploadForm.querySelector<HTMLLabelElement>(`label[for="${target.id}"]`);

            if (label) {
                if (target.files?.length) {
                    if (target.multiple) {
                        label.textContent = `${target.files.length} files selected`;
                    } else {
                        label.textContent = target.files[0].name;
                    }
                } else {
                    label.textContent = 'Choose File';
                }
            }
        });
    });
});
