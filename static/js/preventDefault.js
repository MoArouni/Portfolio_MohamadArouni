// Form validation script
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('blogForm');
    const title = document.getElementById('title');
    const content = document.getElementById('content');
    const titleError = document.getElementById('titleError');
    const contentError = document.getElementById('contentError');
    
    // Function to validate a field
    function validateField(field, errorElement, errorMessage) {
        if (field.value.trim() === '') {
            field.classList.add('error-field');
            errorElement.textContent = errorMessage;
            return false;
        } else {
            field.classList.remove('error-field');
            errorElement.textContent = '';
            return true;
        }
    }
    
    // Form submission handler
    form.addEventListener('submit', function(event) {
        const isTitleValid = validateField(title, titleError, 'Title is required');
        const isContentValid = validateField(content, contentError, 'Content is required');
        
        if (!isTitleValid || !isContentValid) {
            event.preventDefault();
            // Focus the first invalid field
            if (!isTitleValid) {
                title.focus();
            } else if (!isContentValid) {
                content.focus();
            }
        }
    });
    
    // Real-time validation for better user experience
    title.addEventListener('blur', function() {
        validateField(title, titleError, 'Title is required');
    });
    
    content.addEventListener('blur', function() {
        validateField(content, contentError, 'Content is required');
    });
    
    // Clear error when user starts typing
    title.addEventListener('input', function() {
        if (title.value.trim() !== '') {
            title.classList.remove('error-field');
            titleError.textContent = '';
        }
    });
    
    content.addEventListener('input', function() {
        if (content.value.trim() !== '') {
            content.classList.remove('error-field');
            contentError.textContent = '';
        }
    });
    
    // Preview button should also validate
    document.getElementById('previewBtn').addEventListener('click', function() {
        const isTitleValid = validateField(title, titleError, 'Title is required');
        const isContentValid = validateField(content, contentError, 'Content is required');
        
        if (!isTitleValid || !isContentValid) {
            if (!isTitleValid) {
                title.focus();
            } else if (!isContentValid) {
                content.focus();
            }
        }
        // If valid, the existing preview code will run
    });
});