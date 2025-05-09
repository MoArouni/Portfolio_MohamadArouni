document.addEventListener('DOMContentLoaded', () => {
  document.body.addEventListener('click', handleDeleteClick);
});

function handleDeleteClick(e) {
  const deleteBtn = e.target.closest('.delete-comment');
  if (!deleteBtn) return;

  e.preventDefault();
  e.stopImmediatePropagation(); // Prevent duplicate triggering

  const postId = deleteBtn.dataset.postId;
  const commentId = deleteBtn.dataset.commentId;

  if (!postId || !commentId) {
    console.error('Missing post ID or comment ID.');
    return;
  }

  if (confirm('Delete this comment?')) {
    window.location.href = `features/delete_comment.php?post_id=${postId}&comment_id=${commentId}`;
  }
}
