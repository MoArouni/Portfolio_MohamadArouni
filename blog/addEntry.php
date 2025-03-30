<?php
require_once __DIR__ . '/includes/db.php';
session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: ../login.html');
    exit();
}

// Redirect to your styled HTML form
header('Location: addPost.php');
exit();
?>