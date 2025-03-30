document.addEventListener('DOMContentLoaded', () => {
    // Use { once: true } to prevent duplicate listeners
    document.body.addEventListener('click', handleDeleteClick, { once: true });
});

function handleDeleteClick(e) {
    const deleteBtn = e.target.closest('.delete-post');
    if (!deleteBtn) return;

    e.preventDefault();
    e.stopImmediatePropagation(); // Crucial fix
    
    const postId = deleteBtn.dataset.postId;
    
    if (confirm('Delete this post?')) {
        window.location.href = `features/delete_post.php?post_id=${postId}`;
    }
}