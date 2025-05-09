const toast = document.getElementById('toast');
  toast.classList.remove('hidden');
  toast.classList.add('show');

  // Redirect after 3 seconds
  setTimeout(() => {
    window.location.href = '/Project/blog/login.php';
  }, 3000);