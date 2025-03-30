<?php
require_once __DIR__ . '/includes/db.php';
session_start();

// 1. Fetch all posts (unsorted)
try {
    $stmt = $pdo->query("SELECT * FROM posts");
    $posts = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    if (empty($posts)) {
        // No changes needed here - your empty state handling remains perfect
    }
} catch (PDOException $e) {
    die("Database error: " . $e->getMessage());
}

// 2. Implement Merge Sort algorithm
function mergeSortPosts(array &$posts) {
    $length = count($posts);
    if ($length <= 1) return;
    
    $mid = (int)($length / 2);
    $left = array_slice($posts, 0, $mid);
    $right = array_slice($posts, $mid);
    
    mergeSortPosts($left);
    mergeSortPosts($right);
    
    $posts = merge($left, $right);
}

function merge(array $left, array $right) {
    $result = [];
    $leftIdx = $rightIdx = 0;
    
    while ($leftIdx < count($left) && $rightIdx < count($right)) {
        if ($left[$leftIdx]['created_at'] >= $right[$rightIdx]['created_at']) {
            $result[] = $left[$leftIdx++];
        } else {
            $result[] = $right[$rightIdx++];
        }
    }
    return array_merge($result, array_slice($left, $leftIdx), array_slice($right, $rightIdx));
}

// 3. Sort the posts (newest first)
mergeSortPosts($posts);

?>

<!DOCTYPE html>
<html>
<head>
    <title>Blog Posts</title>
    <link rel="stylesheet" href="../css/reset.css">
    <link rel="stylesheet" href="../css/blog.css">
    <link rel="stylesheet" href="../css/mobile.css">
</head>

<body>
    <nav>
        <script src="../js/toggle_darkmode.js"></script>
        <div class="dark-mode-toggle">
            <input type="checkbox" id="dark-mode-toggle">
            <label for="dark-mode-toggle"></label>
        </div>
        
        <ul class="nav-links">
            <li><a href="home.php">Home</a></li>
            <li><a href="home.php#portfolio">Portfolio</a></li>
            <li><a href="home.php#contact">Contact Me</a></li>
            <?php if (isset($_SESSION['user_id'])): ?>
                <li><a href="logout.php">Logout</a></li>
            <?php else: ?>
                <li><a href="../login.html">Login</a></li>
            <?php endif; ?>
        </ul>

        <script src="../js/hamburger_menu.js"></script>
        <button class="hamburger" id="hamburger">
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
        </button>

        <div class="right-menu" id="right-menu">
            <ul>
                <li><a href="home.php">Home</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="home.php#portfolio">Portfolio</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="home.php#cv">Download CV</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#skills">Skills</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#contact">Contact Me</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <?php if (isset($_SESSION['user_id'])): ?>
                    <li><a href="logout.php">Logout</a></li>
                <?php else: ?>
                    <li><a href="../login.html">Login</a></li>
                <?php endif; ?>
                <div class="underline2" style="width: 90%;"></div>
                <?php if (isset($_SESSION['user_id'])): ?>
                    <li><a href="addPost.php">Add Post</a></li>
                <?php endif; ?>
                <div class="underline2" style="width: 90%;"></div>
            </ul>
        </div>
        
        <script src="../js/anti-scroll-menu.js"></script>
    </nav>

    <div class="blog-container">
        <?php if (empty($posts)): ?>
            <div class="comment">
                <p><em>No Posts yet.</em></p>
            </div>
        <?php else: ?>
            <?php foreach ($posts as $post): ?>
                <article class="blog-post" id="post-<?= $post['id'] ?>">
                    <small class="date">
                        <span class="time-icon">🕒</span>
                        <?= date('F j, Y g:i A', strtotime($post['created_at'])) ?>
                    </small>
                    
                    <?php if (isset($_SESSION['user_id']) && $_SESSION['user_id'] == $post['user_id']): ?>
                        <button class="delete-post" data-post-id="<?= htmlspecialchars($post['id']) ?>" title="Delete post">
                            X
                        </button>
                        <script src="../js/features/delete_post.js" defer></script>
                    <?php endif; ?>
                    
                    <h2><?= htmlspecialchars($post['title']) ?></h2>
                    <div class="underline2" style="width: 100%;"></div>
                    <p><?= nl2br(htmlspecialchars($post['content'])) ?></p>
                    <!-- Comments Section -->
                    <div class="comments">
                        <h3>Comments</h3>
                        <br>
                        <?php
                        // Fetch comments for this post
                        $stmt = $pdo->prepare("SELECT * FROM comments WHERE post_id = ? ORDER BY created_at DESC");
                        $stmt->execute([$post['id']]);
                        $comments = $stmt->fetchAll();

                        if (empty($comments)): ?>
                            <div class="comment">
                                <p><em>No comments yet.</em></p>
                            </div>
                        <?php else:
                            foreach ($comments as $comment):
                            ?>
                                <div class="comment">
                                    <strong>
                                        <?= $comment['user_id'] ? "User #{$comment['user_id']}" : htmlspecialchars($comment['author_name']) ?>
                                    </strong>
                                    <em><small><span class="time-icon">🕒</span><?= date('M j, Y', strtotime($comment['created_at'])) ?>
                                    </small></em>
                                    
                                    
                                    <?php if (isset($_SESSION['user_id']) && ($_SESSION['user_id'] == $comment['user_id'] || $_SESSION['user_id'] == $post['user_id'])): ?>
                                        <button 
                                            class="delete-comment"
                                            onclick="if(confirm('Delete this comment?')) window.location='features/delete_comment.php?comment_id=<?= $comment['id'] ?>'"
                                        >
                                            X
                                        </button>
                                    <?php endif; ?>
                                    
                                    <p><?= nl2br(htmlspecialchars($comment['content'])) ?></p>
                                </div>
                            <?php endforeach; ?>
                        <?php endif; ?>
                        <!-- Comment Form -->
                        <?php if (!isset($_SESSION['user_id'])): ?>
                            <form class = "form-comment" method="POST" action="features/add_comment.php">
                                <input type="hidden" name="post_id" value="<?= $post['id'] ?>">
                                <textarea name="content" rows = "3" placeholder="Your comment..." required></textarea>
                                
                                <div class = "form-comment-buttons">
                                    <input type="text" name="author_name" placeholder="Your name">
                                    <button type="submit">Post</button>
                                </div>
                            </form>
                                    
                        <?php endif; ?>
                        
                    </div>
                </article>
            <?php endforeach; ?>
        <?php endif; ?>
        
        <?php if (isset($_SESSION['user_id'])): ?>
            <a href="addEntry.php" class="new-post-btn">New Post</a>
        <?php endif; ?>
    </div>
</body>
</html>