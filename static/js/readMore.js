document.querySelectorAll('.read-more').forEach(button => {
    button.addEventListener('click', function() {
        const description = this.closest('.project-text').querySelector('.project-description');
        const isHidden = description.style.display === 'none';
        
        description.style.display = isHidden ? 'block' : 'none';
        this.textContent = isHidden ? 'Read Less -' : 'Read More +';
    });
});

// Add functionality for timeline toggles
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.timeline-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const timelineContent = this.closest('.timeline-content');
            const timelineDescription = timelineContent.querySelector('.timeline-description');
            
            // Toggle the expanded class to show/hide detailed content
            timelineContent.classList.toggle('expanded');
            
            // Update button text
            if (timelineContent.classList.contains('expanded')) {
                this.textContent = 'Read Less';
                timelineDescription.style.maxHeight = timelineDescription.scrollHeight + 'px';
            } else {
                this.textContent = 'Read More';
                timelineDescription.style.maxHeight = '80px';
            }
        });
    });
    
    // Set initial state for timeline descriptions
    document.querySelectorAll('.timeline-description').forEach(desc => {
        desc.style.maxHeight = '80px';
        desc.style.overflow = 'hidden';
        desc.style.transition = 'max-height 0.3s ease';
    });
});