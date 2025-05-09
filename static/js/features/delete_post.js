document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', handleDeletePostClick);
  });
  
  function handleDeletePostClick(e) {
    const deleteBtn = e.target.closest('.delete-post');
    if (!deleteBtn) return;
  
    e.preventDefault();
    e.stopImmediatePropagation();
  
    const postId = deleteBtn.dataset.postId;
  
    if (!postId) {
      console.error('Missing post ID.');
      return;
    }
  
    if (confirm('Delete this post?')) {
      window.location.href = `features/delete_post.php?post_id=${postId}`;
    }
  }
  