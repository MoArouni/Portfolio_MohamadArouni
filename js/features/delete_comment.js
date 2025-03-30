document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', (e) => {
      const deleteBtn = e.target.closest('.delete-comment');
      if (!deleteBtn) return;
  
      e.preventDefault();
      const commentId = deleteBtn.dataset.commentId;
      
      if (confirm('Delete this comment?')) {
        window.location.href = `features/delete_comment.php?comment_id=${commentId}`;
      }
    });
  });