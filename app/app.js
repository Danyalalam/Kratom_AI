document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const progressBar = document.getElementById('progress');
    const progressSteps = document.querySelectorAll('.progress-step');
    const steps = document.querySelectorAll('.step');
    const currentStepText = document.getElementById('current-step');
    const nextButtons = document.querySelectorAll('.next-btn');
    const backButtons = document.querySelectorAll('.back-btn');
    const submitButton = document.getElementById('submit-btn');
    const restartButton = document.getElementById('restart-btn');
    const saveButton = document.getElementById('save-btn');
    const painLevels = document.querySelectorAll('.pain-level');
    const painLevelInput = document.getElementById('pain-level');
    const loadingOverlay = document.getElementById('loading-overlay');
    const questionnaireContainer = document.querySelector('.questionnaire-container');
    const resultsContainer = document.querySelector('.results-container');

    // Error message elements
    const ageError = document.getElementById('age-error');
    const heightError = document.getElementById('height-error');
    const weightError = document.getElementById('weight-error');
    const bodyTypeError = document.getElementById('body-type-error');
    const painLevelError = document.getElementById('pain-level-error');
    const emailError = document.getElementById('email-error');

    // Form data
    const formData = {};

    // Initialize the progress bar
    function updateProgress(currentStep) {
        const totalSteps = progressSteps.length;
        const percent = ((currentStep - 1) / (totalSteps - 1)) * 100;
        progressBar.style.width = percent + '%';
        
        // Update progress steps
        progressSteps.forEach((step, idx) => {
            if (idx + 1 < currentStep) {
                step.classList.add('complete');
                step.classList.remove('active');
            } else if (idx + 1 === currentStep) {
                step.classList.add('active');
                step.classList.remove('complete');
            } else {
                step.classList.remove('active', 'complete');
            }
        });
        
        // Update step text
        currentStepText.textContent = currentStep;
    }

    // Show specific step
    function showStep(stepNumber) {
        steps.forEach(step => {
            step.classList.remove('active');
        });
        document.querySelector(`.step[data-step="${stepNumber}"]`).classList.add('active');
        updateProgress(stepNumber);
    }

    // Validate step before proceeding
    function validateStep(stepNumber) {
        let isValid = true;
        
        switch (stepNumber) {
            case 1:
                const age = document.getElementById('age').value;
                if (!age || age < 18) {
                    ageError.textContent = 'Please enter a valid age (18 or older)';
                    isValid = false;
                } else {
                    ageError.textContent = '';
                    formData.age = parseInt(age);
                }
                break;
                
            case 2:
                const feet = document.getElementById('height-feet').value;
                const inches = document.getElementById('height-inches').value;
                if (!feet || feet < 3 || feet > 8) {
                    heightError.textContent = 'Please enter a valid height';
                    isValid = false;
                } else if (inches === '' || inches < 0 || inches > 11) {
                    heightError.textContent = 'Please enter valid inches (0-11)';
                    isValid = false;
                } else {
                    heightError.textContent = '';
                    formData.height = {
                        feet: parseInt(feet),
                        inches: parseInt(inches)
                    };
                    formData.heightCm = (parseInt(feet) * 30.48) + (parseInt(inches) * 2.54);
                }
                break;
                
            case 3:
                const weight = document.getElementById('weight').value;
                if (!weight || weight < 70 || weight > 500) {
                    weightError.textContent = 'Please enter a valid weight (70-500 lbs)';
                    isValid = false;
                } else {
                    weightError.textContent = '';
                    formData.weight = parseInt(weight);
                    // Convert lbs to kg for API
                    formData.weightKg = parseInt(weight) * 0.45359237;
                }
                break;
                
            case 4:
                const bodyType = document.querySelector('input[name="body-type"]:checked');
                if (!bodyType) {
                    bodyTypeError.textContent = 'Please select your body type';
                    isValid = false;
                } else {
                    bodyTypeError.textContent = '';
                    formData.bodyType = bodyType.value;
                }
                break;
                
            case 5:
                const bloodType = document.querySelector('input[name="blood-type"]:checked');
                if (bloodType) {
                    formData.bloodType = bloodType.value;
                } else {
                    formData.bloodType = 'unknown';
                }
                isValid = true; // Blood type is optional
                break;
                
            case 6:
                if (!painLevelInput.value) {
                    painLevelError.textContent = 'Please select your pain level';
                    isValid = false;
                } else {
                    painLevelError.textContent = '';
                    formData.painLevel = parseInt(painLevelInput.value);
                }
                break;
                
            case 7:
                const email = document.getElementById('email').value;
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!email || !emailRegex.test(email)) {
                    emailError.textContent = 'Please enter a valid email address';
                    isValid = false;
                } else {
                    emailError.textContent = '';
                    formData.email = email;
                    formData.newsletter = document.getElementById('newsletter').checked;
                }
                break;
        }
        
        return isValid;
    }

    // Next button handler
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            const currentStep = parseInt(button.closest('.step').dataset.step);
            if (validateStep(currentStep)) {
                const nextStep = parseInt(button.dataset.next);
                showStep(nextStep);
            }
        });
    });

    // Back button handler
    backButtons.forEach(button => {
        button.addEventListener('click', () => {
            const prevStep = parseInt(button.dataset.prev);
            showStep(prevStep);
        });
    });

    // Pain level selection
    painLevels.forEach(level => {
        level.addEventListener('click', () => {
            painLevels.forEach(l => l.classList.remove('selected'));
            level.classList.add('selected');
            painLevelInput.value = level.dataset.value;
        });
    });

    // Submit form
    submitButton.addEventListener('click', async () => {
        if (validateStep(7)) {
            // Show loading overlay
            loadingOverlay.style.display = 'flex';
            
            try {
                // Prepare data for API
                const apiData = {
                    age: formData.age,
                    weight: formData.weightKg, // Already converted to kg
                    pain_level: formData.painLevel,
                    body_type: formData.bodyType
                };
                
                // Call API
                const response = await fetch('http://localhost:8000/recommend', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(apiData),
                });
                
                if (!response.ok) {
                    throw new Error('API request failed');
                }
                
                const result = await response.json();
                
                // Hide loading and show results
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                    questionnaireContainer.style.display = 'none';
                    resultsContainer.style.display = 'block';
                    
                    // Update results
                    document.getElementById('dosage-result').textContent = result.dosage;
                    document.getElementById('additional-info').textContent = result.additional_info || 'No additional information available.';
                    document.getElementById('ai-insights').textContent = result.ai_insights || 'No AI insights available.';
                }, 1500); // Delay for user experience
                
            } catch (error) {
                console.error('Error:', error);
                loadingOverlay.style.display = 'none';
                alert('Something went wrong. Please try again.');
            }
        }
    });

    // Restart button handler
    restartButton.addEventListener('click', () => {
        // Reset form
        document.querySelectorAll('input').forEach(input => {
            if (input.type === 'radio' || input.type === 'checkbox') {
                input.checked = false;
            } else if (input.id !== 'newsletter') {
                input.value = '';
            }
        });
        
        // Reset pain levels
        painLevels.forEach(level => level.classList.remove('selected'));
        painLevelInput.value = '';
        
        // Reset error messages
        document.querySelectorAll('.error-message').forEach(error => {
            error.textContent = '';
        });
        
        // Show questionnaire
        resultsContainer.style.display = 'none';
        questionnaireContainer.style.display = 'block';
        showStep(1);
    });

    // Save results button handler
    saveButton.addEventListener('click', () => {
        const dosage = document.getElementById('dosage-result').textContent;
        const additionalInfo = document.getElementById('additional-info').textContent;
        const aiInsights = document.getElementById('ai-insights').textContent;
        
        const content = `
Kratom AI Recommendation Results
===============================

Personal Information:
- Age: ${formData.age}
- Height: ${formData.height.feet}'${formData.height.inches}"
- Weight: ${formData.weight} lbs
- Body Type: ${formData.bodyType}
- Blood Type: ${formData.bloodType}
- Pain Level: ${formData.painLevel}/10

Your Recommendation:
${dosage}

Additional Information:
${additionalInfo}

AI Insights:
${aiInsights}

IMPORTANT DISCLAIMER:
These recommendations are not medical advice. Kratom is not FDA-approved for any medical use.
Always consult with a healthcare professional before using any new supplement.
`;
        
        // Create a download link
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
        element.setAttribute('download', 'kratom_ai_recommendation.txt');
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });

    // Initialize first step
    showStep(1);
});