<?php
require_once __DIR__ . '/../includes/db.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $post_id = $_POST['post_id'];
    $content = $_POST['content'];
    
    if (isset($_SESSION['user_id'])) {
        // Logged-in user
        $stmt = $pdo->prepare("INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)");
        $stmt->execute([$post_id, $_SESSION['user_id'], $content]);
    } else {
        // Guest (store name)
        $author_name = $_POST['author_name'] ?? 'Anonymous';
        $stmt = $pdo->prepare("INSERT INTO comments (post_id, author_name, content) VALUES (?, ?, ?)");
        $stmt->execute([$post_id, $author_name, $content]);
    }
    
    header("Location: ../viewBlog.php#post-$post_id");
    exit();
}
?>