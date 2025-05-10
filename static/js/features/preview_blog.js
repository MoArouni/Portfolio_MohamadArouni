/**
 * Blog Preview Functionality
 * 
 * This script handles the preview functionality for both adding and editing blog posts.
 * It shows a live preview of the post as it will appear when published.
 */

document.addEventListener('DOMContentLoaded', function() {
    const previewBtn = document.getElementById('previewBtn');
    const previewContainer = document.getElementById('previewContainer');
    const previewTitle = document.getElementById('previewTitle');
    const previewContent = document.getElementById('previewContent');
    const form = document.querySelector('form');
    
    // Only run if we're on a page with the preview button
    if (previewBtn && previewContainer) {
        // Initially hide the preview using a class
        previewContainer.classList.remove('active');
        
        // Preview button click handler
        previewBtn.addEventListener('click', function() {
            // Get form inputs
            const titleInput = document.getElementById('title');
            const contentInput = document.getElementById('content');
            
            // Validate inputs
            if (!titleInput.value.trim() || !contentInput.value.trim()) {
                alert('Please enter both title and content to preview.');
                return;
            }
            
            // Set preview content
            previewTitle.textContent = titleInput.value.trim();
            previewContent.innerHTML = contentInput.value.replace(/\n/g, '<br>');
            
            // Toggle visibility using classes rather than directly manipulating style
            if (!form.classList.contains('hidden')) {
                // Show preview, hide form
                form.classList.add('hidden');
                previewContainer.classList.add('active');
                previewBtn.innerHTML = '<i class="fas fa-edit"></i> Edit';
            } else {
                // Show form, hide preview
                form.classList.remove('hidden');
                previewContainer.classList.remove('active');
                previewBtn.innerHTML = '<i class="fas fa-eye"></i> Preview';
            }
        });
        
        // Edit button click handler
        const editBtn = document.getElementById('editBtn');
        if (editBtn) {
            editBtn.addEventListener('click', function() {
                form.classList.remove('hidden');
                previewContainer.classList.remove('active');
                previewBtn.innerHTML = '<i class="fas fa-eye"></i> Preview';
            });
        }
        
        // If coming back from a failed form submission, restore form visibility
        if (document.querySelector('.error-message')) {
            form.classList.remove('hidden');
            previewContainer.classList.remove('active');
        }
    }
}); 