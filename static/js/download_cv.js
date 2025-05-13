document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('cvDownloadModal');
    const downloadBtn = document.getElementById('downloadButton');
    const closeBtn = modal.querySelector('.close-modal');
    const cancelBtn = document.getElementById('cancelDownload');
    const downloadOptions = document.querySelectorAll('.download-option');
    const otherReasonForm = document.getElementById('otherReasonForm');
    const otherReasonInput = document.getElementById('other-reason-text');
    const emailInput = document.getElementById('cv-email');
    const emailValidationMessage = document.querySelector('.email-input-container .validation-message');

    if (!modal || !downloadBtn) return;

    // Open modal when download button is clicked
    downloadBtn.addEventListener('click', function() {
        modal.classList.add('active');
    });

    // Close modal when X button or Cancel is clicked
    closeBtn.addEventListener('click', function() {
        modal.classList.remove('active');
        resetForm();
    });

    cancelBtn.addEventListener('click', function() {
        modal.classList.remove('active');
        resetForm();
    });

    // Close modal when clicking outside the modal content
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.classList.remove('active');
            resetForm();
        }
    });

    // Validate email input
    emailInput.addEventListener('input', function() {
        validateEmail();
    });

    // Handle download option clicks
    downloadOptions.forEach(option => {
        option.addEventListener('click', function() {
            const reason = this.getAttribute('data-reason');
            if (validateEmail()) {
                downloadCV(reason, emailInput.value);
            }
        });
    });

    // Handle other reason form submission
    otherReasonForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const reason = otherReasonInput.value.trim();
        
        if (!validateEmail()) {
            return;
        }
        
        if (reason) {
            downloadCV(reason, emailInput.value);
        } else {
            showMessage('Please specify a reason for downloading', 'error');
        }
    });

    // Function to validate email
    function validateEmail() {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            emailInput.classList.add('invalid');
            emailValidationMessage.textContent = 'Email address is required';
            return false;
        } else if (!emailRegex.test(email)) {
            emailInput.classList.add('invalid');
            emailValidationMessage.textContent = 'Please enter a valid email address';
            return false;
        } else {
            emailInput.classList.remove('invalid');
            emailInput.classList.add('valid');
            emailValidationMessage.textContent = '';
            return true;
        }
    }

    // Function to reset form
    function resetForm() {
        emailInput.value = '';
        otherReasonInput.value = '';
        emailInput.classList.remove('invalid', 'valid');
        emailValidationMessage.textContent = '';
    }

    // Function to handle CV download
    function downloadCV(reason, email) {
        // Show loading message
        const loadingMessage = showMessage('Preparing download...', 'info');

        // Send download request to server
        fetch('/download_cv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                reason: reason,
                email: email
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            // Create a temporary link to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'Mohamad_Arouni_CV.pdf';
            document.body.appendChild(a);
            a.click();

            // Clean up
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Close the modal
            modal.classList.remove('active');
            
            // Reset the form
            resetForm();

            // Show success message
            showMessage('CV downloaded successfully!', 'success');

            // Remove loading message
            if (loadingMessage && loadingMessage.parentNode) {
                loadingMessage.parentNode.removeChild(loadingMessage);
            }
        })
        .catch(error => {
            console.error('Download failed:', error);
            showMessage('Failed to download CV. Please try again.', 'error');

            // Remove loading message
            if (loadingMessage && loadingMessage.parentNode) {
                loadingMessage.parentNode.removeChild(loadingMessage);
            }
        });
    }

    // Function to show a message to the user
    function showMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messageElement.className = `message-toast ${type}`;
        document.body.appendChild(messageElement);
        
        // Show the message
        setTimeout(() => {
            messageElement.classList.add('visible');
        }, 100);
        
        // Hide and remove after 3 seconds (except for loading messages)
        if (type !== 'info') {
            setTimeout(() => {
                messageElement.classList.remove('visible');
                setTimeout(() => {
                    if (messageElement.parentNode) {
                        document.body.removeChild(messageElement);
                    }
                }, 300);
            }, 3000);
        }
        
        return messageElement;
    }
}); 