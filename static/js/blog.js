document.addEventListener('DOMContentLoaded', function() {
    // Post like buttons
    const likeButtons = document.querySelectorAll('.like-button');
    const isLoggedIn = document.querySelector('.blog-container')?.dataset.loggedIn === "1";
    
    // Create or get anonymous user identifier
    let anonymousId = localStorage.getItem('anonymous_user_id');
    if (!anonymousId && !isLoggedIn) {
        anonymousId = 'anon_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('anonymous_user_id', anonymousId);
    }
    
    // Track posts liked by anonymous users
    let anonymousLikes = JSON.parse(localStorage.getItem('anonymous_likes') || '[]');
    
    // Apply anonymous likes from localStorage on page load
    if (!isLoggedIn) {
        likeButtons.forEach(button => {
            const postId = button.getAttribute('data-post-id');
            if (anonymousLikes.includes(parseInt(postId))) {
                toggleLikeUI(button, true);
            }
        });
    }
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = parseInt(this.getAttribute('data-post-id'));
            const liked = this.classList.contains('liked');
            const likeCountElement = this.querySelector('.like-count');
            
            if (isLoggedIn) {
                // Logged in user like/unlike handling
                handleLikeAction(this, postId, liked, likeCountElement);
            } else {
                // Anonymous user handling
                if (liked) {
                    // Can't unlike as anonymous user
                    alert('Anonymous users cannot remove their likes');
                } else if (!anonymousLikes.includes(postId)) {
                    // Skip prompt, use 'Anonymous' as default username
                    handleAnonymousLike(this, postId, 'Anonymous', likeCountElement);
                } else {
                    alert('You have already liked this post');
                }
            }
        });
    });
    
    // Function to handle regular like/unlike actions
    function handleLikeAction(button, postId, liked, likeCountElement) {
        // First call the API
        const url = liked ? `/post/unlike/${postId}` : `/post/like/${postId}`;
        
        console.log(`Making ${liked ? 'unlike' : 'like'} request to ${url} for post ${postId}`);
        
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            console.log('API response:', data);
            if (data.success) {
                // Only update UI after successful API response
                toggleLikeUI(button, !liked);
                likeCountElement.textContent = data.like_count;
                console.log(`Updated like count to: ${data.like_count}`);
            } else {
                // Error - but update count if provided
                console.error('Error with like action:', data.error);
                if (data.like_count !== undefined) {
                    likeCountElement.textContent = data.like_count;
                    console.log(`Updated like count from error response to: ${data.like_count}`);
                }
                if (data.error === 'Already liked') {
                    // If already liked but UI doesn't show it, update UI
                    if (!liked) toggleLikeUI(button, true);
                }
            }
        })
        .catch(error => {
            console.error('Network error with like action:', error);
        });
    }
    
    // Helper function to toggle like UI state
    function toggleLikeUI(button, isLiked) {
        if (isLiked) {
            button.classList.add('liked');
            button.querySelector('i').classList.replace('far', 'fas');
        } else {
            button.classList.remove('liked');
            button.querySelector('i').classList.replace('fas', 'far');
        }
    }
    
    // Function to handle anonymous likes
    function handleAnonymousLike(button, postId, username, likeCountElement) {
        // First call the API
        fetch(`/post/anonymous_like/${postId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                username: username,
                anonymous_id: anonymousId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Only update UI after successful API response
                toggleLikeUI(button, true);
                likeCountElement.textContent = data.like_count;
                
                // Store like in localStorage
                anonymousLikes.push(postId);
                localStorage.setItem('anonymous_likes', JSON.stringify(anonymousLikes));
            } else {
                // Error - but update count if provided
                console.error('Error with anonymous like:', data.error);
                if (data.like_count !== undefined) {
                    likeCountElement.textContent = data.like_count;
                }
                if (data.error === 'Already liked') {
                    // If already liked but not in localStorage, add it
                    if (!anonymousLikes.includes(postId)) {
                        anonymousLikes.push(postId);
                        localStorage.setItem('anonymous_likes', JSON.stringify(anonymousLikes));
                        toggleLikeUI(button, true);
                    }
                }
            }
        })
        .catch(error => {
            console.error('Network error with anonymous like:', error);
        });
    }
    
    // Comment like buttons
    const commentLikeButtons = document.querySelectorAll('.comment-like-button:not([disabled])');
    commentLikeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const liked = this.classList.contains('liked');
            const likeCountElement = this.querySelector('.comment-like-count');
            
            // First call the API
            const url = liked ? `/comment/unlike/${commentId}` : `/comment/like/${commentId}`;
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Only update UI after successful API response
                    toggleLikeUI(this, !liked);
                    likeCountElement.textContent = data.like_count;
                } else {
                    // Error - but update count if provided
                    console.error('Error with comment like action:', data.error);
                    if (data.like_count !== undefined) {
                        likeCountElement.textContent = data.like_count;
                    }
                }
            })
            .catch(error => {
                console.error('Network error with comment like action:', error);
            });
        });
    });
    
    // Author like buttons (admin only)
    const authorLikeButtons = document.querySelectorAll('.author-like-button');
    authorLikeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            
            // API call
            fetch(`/comment/author-like/${commentId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI based on response
                    if (data.liked_by_author) {
                        this.classList.add('active');
                        addAuthorLikeBadge(this);
                    } else {
                        this.classList.remove('active');
                        removeAuthorLikeBadge(this);
                    }
                }
            });
        });
    });
    
    // Helper function to add author like badge
    function addAuthorLikeBadge(button) {
        const commentAuthor = button.closest('.comment').querySelector('.comment-author');
        if (!commentAuthor.querySelector('.author-liked')) {
            const badge = document.createElement('span');
            badge.classList.add('author-liked');
            badge.setAttribute('title', 'Liked by author');
            badge.innerHTML = '<i class="fas fa-check-circle"></i>';
            commentAuthor.appendChild(badge);
        }
    }
    
    // Helper function to remove author like badge
    function removeAuthorLikeBadge(button) {
        const badge = button.closest('.comment').querySelector('.author-liked');
        if (badge) {
            badge.remove();
        }
    }
}); 