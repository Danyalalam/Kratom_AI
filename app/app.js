document.addEventListener('DOMContentLoaded', function() {
    // Add hamburger menu functionality and overlay
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;

    // Create overlay element
    const overlay = document.createElement('div');
    overlay.className = 'menu-overlay';
    body.appendChild(overlay);

    // Toggle menu
    hamburgerMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        navMenu.classList.toggle('active');
        overlay.classList.toggle('active');
        body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
    });

    // Close menu when clicking overlay
    overlay.addEventListener('click', () => {
        navMenu.classList.remove('active');
        overlay.classList.remove('active');
        body.style.overflow = '';
    });

    // Handle menu item clicks
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            overlay.classList.remove('active');
            body.style.overflow = '';
        });
    });

    // Initialize page-specific functionality
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    // Blog page specific functionality
    if (currentPage === 'blogs.html') {
        const blogContainer = document.getElementById('blog-container');
        if (blogContainer) {
            // Declare fetchKratomNews inside this scope so it has access to blogContainer
            async function fetchKratomNews() {
                try {
                    const response = await fetch('https://kratom-ai.onrender.com/news');
                    const data = await response.json();
                    
                    if (data.articles && data.articles.length > 0) {
                        blogContainer.innerHTML = data.articles.slice(0, 6).map(article => `
                            <div class="blog-card">
                                <img src="${article.urlToImage || 'https://via.placeholder.com/300x200'}" alt="${article.title}" class="blog-image">
                                <div class="blog-content">
                                    <div class="blog-date">${new Date(article.publishedAt).toLocaleDateString()}</div>
                                    <h3 class="blog-title">${article.title}</h3>
                                    <p class="blog-description">${article.description || 'No description available.'}</p>
                                    <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="blog-link">
                                        Read More <i class="fas fa-arrow-right"></i>
                                    </a>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        blogContainer.innerHTML = '<p>No articles found.</p>';
                    }
                } catch (error) {
                    console.error('Error fetching news:', error);
                    blogContainer.innerHTML = '<p>Error loading articles. Please try again later.</p>';
                }
            }
            fetchKratomNews();
        }
    }

    // Home page specific functionality
    if (currentPage === 'index.html' || currentPage === '') {
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
        const sexTypeError = document.getElementById('sex-type-error');
        const painLevelError = document.getElementById('pain-level-error');
        const emailError = document.getElementById('email-error');

        // Form data
        const formData = {};

        // IP Location
        async function getLocation(){
            try{
                const response = await fetch('https://ipapi.co/json/');
                const data = await response.json();
                return {
                    ip: data.ip,
                    city: data.city,
                    region: data.region,
                    country: data.country_name
                }
            }
            catch(error){
                console.error('Error fetching location data:', error);
                return null;
            }
            
        }

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
                    const sexType = document.querySelector('input[name="sex-type"]:checked');
                    if (!sexType) {
                        sexTypeError.textContent = 'Please select your sex';
                        isValid = false;
                    } else {
                        sexTypeError.textContent = '';
                        formData.sexType = sexType.value;
                    }
                    break;
                    
                case 3:
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
                    
                case 4:
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
                    
                case 5:
                    const bodyType = document.querySelector('input[name="body-type"]:checked');
                    if (!bodyType) {
                        bodyTypeError.textContent = 'Please select your body type';
                        isValid = false;
                    } else {
                        bodyTypeError.textContent = '';
                        formData.bodyType = bodyType.value;
                    }
                    break;
                    
                case 6:
                    const bloodType = document.querySelector('input[name="blood-type"]:checked');
                    if (bloodType) {
                        formData.bloodType = bloodType.value;
                    } else {
                        formData.bloodType = 'unknown';
                    }
                    isValid = true; // Blood type is optional
                    break;
                    
                case 7:
                    if (!painLevelInput.value) {
                        painLevelError.textContent = 'Please select your pain level';
                        isValid = false;
                    } else {
                        painLevelError.textContent = '';
                        formData.painLevel = parseInt(painLevelInput.value);
                    }
                    break;
                    
                case 8:
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
            if (validateStep(8)) {
                // Show loading overlay
                loadingOverlay.style.display = 'flex';
                
                try {
                    const locationData = await getLocation();

                    const apiData = {
                        age: formData.age,
                        weight: formData.weightKg,
                        height: formData.height,
                        pain_level: formData.painLevel,
                        body_type: formData.bodyType,
                        blood_type: formData.bloodType || 'unknown',
                        sex: formData.sexType,
                        email: formData.email,
                        newsletter: formData.newsletter,
                        location_data: locationData
                    };

                    console.log("api request data:", apiData);
                    
                    // Call API
                    const response = await fetch('https://kratom-ai.onrender.com/recommend', {
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
                        
                        // Handle sponsored vendor information
                        const sponsoredVendorSection = document.getElementById('sponsored-vendor');
                        if (result.sponsored_info) {
                            document.getElementById('vendor-name').textContent = result.sponsored_info.vendor;
                            document.getElementById('vendor-description').textContent = result.sponsored_info.description;
                            document.getElementById('vendor-link').href = result.sponsored_info.url;
                            sponsoredVendorSection.style.display = 'block';
                        } else {
                            sponsoredVendorSection.style.display = 'none';
                        }
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
- Sex: ${formData.sexType}
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
    }
});