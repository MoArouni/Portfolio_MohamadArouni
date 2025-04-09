<?php
require_once __DIR__ . '/includes/db.php';
session_start();

// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $email = $_POST['email'];
    $password = $_POST['password'];
    
    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch();
    
    if ($user && password_verify($password, $user['password'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        
        // Redirect based on role
        if ($user['role'] === 'admin') {
            header('Location: addEntry.php');
        } else {
            header('Location: viewBlog.php');
        }
        exit();
    } else {
        $login_error = "Invalid credentials. Please try again.";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="../css/reset.css">
    <link rel="stylesheet" href="../css/home.css">
    <link rel="stylesheet" href="../css/mobile.css">
    <link rel="stylesheet" href="../css/login.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Ovo&display=swap" rel="stylesheet">
</head>
<body>
    <nav>
        <script src="../js/toggle_darkmode.js"></script>
        <div class="dark-mode-toggle">
            <button id="dark-mode-toggle" aria-label="Toggle dark mode">
                <svg class="sun" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>
                <svg class="moon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
            </button>
        </div>
        
        <ul class="nav-links">
            <li><a href="home.php">Home</a></li>
            <li><a href="home.php#portfolio">Portfolio</a></li>
            <li><a href="home.php#contact">Contact Me</a></li>
            <li><a href="viewBlog.php">Blog</a></li>
        </ul>

        <script src="../js/hamburger_menu.js"></script>
        <button style="background : none;" class="hamburger" id="hamburger">
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
                <li><a href="#cv">Download CV</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#skills">Skills</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#contact">Contact Me</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="viewBlog.php">Blog</a></li>
                <div class="underline2" style="width: 90%;"></div>
            </ul>
        </div>
        <script src="../js/anti-scroll-menu.js"></script>
    </nav>
    
    <section>
        <form action="login.php" method="POST">
            <h1 style="font-size: 3rem; text-align: center;">Login</h1>
            <br><br>
            
            <?php if (isset($login_error)): ?>
                <div class="error-message"><?= htmlspecialchars($login_error) ?></div>
            <?php endif; ?>
            
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
            
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>

            <input type="hidden" name="login" value="1">
            
            <div class="button">
                <button type="submit">Login</button>
            </div>
            
            <div class="register-link">
                <p>Don't have an account? <a href="register.php">Register here</a></p>
            </div>
        </form>
    </section>
    <p id="statusMessage"></p>
</body>
</html>