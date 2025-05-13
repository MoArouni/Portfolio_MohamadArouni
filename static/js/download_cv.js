document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('cvDownloadModal');
    const downloadBtn = document.getElementById('downloadButton');
    const closeBtn = modal.querySelector('.close-modal');
    const cancelBtn = document.getElementById('cancelDownload');
    const downloadOptions = document.querySelectorAll('.download-option');
    const emailInput = document.getElementById('cv-email');
    const emailValidationMessage = document.querySelector('.email-input-container .validation-message');
    const sendVerificationBtn = document.getElementById('sendVerificationBtn');
    const verificationMessage = document.querySelector('.verification-message');
    const verificationStep = document.getElementById('verification-step');

    // Tracks the currently selected reason
    let selectedReason = '';

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

    // Add click event to download options to select them
    downloadOptions.forEach(option => {
        option.addEventListener('click', function() {
            // First remove selected class from all options
            downloadOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to this option
            this.classList.add('selected');
            
            // Save the reason
            selectedReason = this.getAttribute('data-reason');
            
            // Show the verification step
            verificationStep.classList.add('visible');
        });
    });

    // Handle verification link button click
    if (sendVerificationBtn) {
        sendVerificationBtn.addEventListener('click', function() {
            // Validate email
            if (!validateEmail()) {
                return;
            }
            
            // Ensure a reason was selected
            if (!selectedReason) {
                showMessage('Please select a reason for downloading', 'error');
                return;
            }
            
            // Show loading message
            sendVerificationBtn.disabled = true;
            sendVerificationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            verificationMessage.textContent = '';
            
            // Send verification link request
            sendVerificationLink(emailInput.value, selectedReason);
        });
    }

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
        emailInput.classList.remove('invalid', 'valid');
        emailValidationMessage.textContent = '';
        verificationMessage.textContent = '';
        downloadOptions.forEach(opt => opt.classList.remove('selected'));
        sendVerificationBtn.disabled = false;
        sendVerificationBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Verification Link';
        verificationStep.classList.remove('visible');
        selectedReason = '';
    }

    // Function to send verification link
    function sendVerificationLink(email, reason) {
        fetch('/send-verification-link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email: email,
                reason: reason
            })
        })
        .then(response => response.json())
        .then(data => {
            sendVerificationBtn.disabled = false;
            sendVerificationBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Verification Link';
            
            if (data.success) {
                // Show success message on the modal
                verificationMessage.textContent = data.message;
                verificationMessage.classList.add('success');
                verificationMessage.classList.remove('error');
                
                // Show toast message
                showMessage(data.message, 'success');
            } else {
                // Show error message
                verificationMessage.textContent = data.message || 'Failed to send verification link';
                verificationMessage.classList.add('error');
                verificationMessage.classList.remove('success');
                
                // Show toast message
                showMessage(data.message || 'Failed to send verification link', 'error');
            }
        })
        .catch(error => {
            console.error('Error sending verification link:', error);
            sendVerificationBtn.disabled = false;
            sendVerificationBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Verification Link';
            
            // Show error message
            verificationMessage.textContent = 'Unable to send verification email. Please check your email address and try again later.';
            verificationMessage.classList.add('error');
            verificationMessage.classList.remove('success');
            
            // Show toast message
            showMessage('Unable to send verification email. The server might be temporarily unavailable.', 'error');
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