<?php
// Start session for potential authentication checks
session_start();

// Redirect based on your preferred default view:
header('Location: blog/home.php');// Redirect to your portfolio homepage
// OR if you want the blog as default:

exit(); // Always exit after header redirect
?>