document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Send form data to Formspree
        const formData = new FormData(form);
        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                alert('Thank you for your message!');
                // Clear all input fields
                const inputs = form.querySelectorAll('input');
                inputs.forEach(input => input.value = '');

                // Clear all textarea fields
                const textareas = form.querySelectorAll('textarea');
                textareas.forEach(textarea => textarea.value = '');
            } else {
                alert('Oops! There was a problem submitting your form');
            }
        }).catch(error => {
            alert('Oops! There was a problem submitting your form');
        });
    });
});