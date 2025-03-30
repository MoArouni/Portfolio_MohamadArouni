<?php
require_once __DIR__ . '/../includes/db.php';
session_start();

if (!isset($_SESSION['user_id'])) {
    die("Unauthorized");
}

if (isset($_GET['comment_id'])) {
    $comment_id = $_GET['comment_id'];
    $stmt = $pdo->prepare("DELETE FROM comments WHERE id = ? AND (user_id = ? OR ? IN (SELECT user_id FROM posts WHERE id = comments.post_id))");
    $stmt->execute([$comment_id, $_SESSION['user_id'], $_SESSION['user_id']]);
    
    header("Location: " . $_SERVER['HTTP_REFERER']); // Redirect back
    exit();
}
?>