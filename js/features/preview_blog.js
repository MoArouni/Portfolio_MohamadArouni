document.getElementById('previewBtn').addEventListener('click', function() {
    const title = document.getElementById('title').value.trim();
    const content = document.getElementById('content').value.trim();
    
    if (!title || !content) {
        alert('Please fill in both title and content before previewing');
        return;
    }
    
    // Update preview elements
    document.getElementById('previewTitle').textContent = title;
    
    // Process content with proper line breaks
    const previewContent = document.getElementById('previewContent');
    previewContent.innerHTML = '';
    
    const paragraphs = content.split('\n');
    paragraphs.forEach(para => {
        if (para.trim() === '') return;
        
        const p = document.createElement('p');
        p.textContent = para;
        previewContent.appendChild(p);
    });
    
    // Set current time
    const now = new Date();
    document.getElementById('previewDate').textContent = 
        now.toLocaleString('en-US', { 
            month: 'long', 
            day: 'numeric', 
            year: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    
    // Store values in data attributes instead of hidden inputs
    document.getElementById('publishBtn').dataset.title = title;
    document.getElementById('publishBtn').dataset.content = content;
    
    // Toggle visibility
    document.querySelector('form').style.display = 'none';
    document.getElementById('previewContainer').style.display = 'block';
});

document.getElementById('editBtn').addEventListener('click', function() {
    document.getElementById('previewContainer').style.display = 'none';
    document.querySelector('form').style.display = 'block';
});

// New publish button functionality
document.getElementById('publishBtn').addEventListener('click', function() {
    const title = this.dataset.title;
    const content = this.dataset.content;
    
    // Create a virtual form
    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    
    // Submit the data
    fetch('addPost.php', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(() => {
        // Redirect if not already redirected
        window.location.href = 'viewBlog.php';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error submitting your post. Please try again.');
    });
});