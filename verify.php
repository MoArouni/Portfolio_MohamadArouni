<?php
require_once 'blog/includes/db.php';

// Check if test user exists
$stmt = $pdo->query("SELECT * FROM users WHERE email = 'mohamadarouni5@gmail.com'");
$user = $stmt->fetch();

if ($user) {
    echo "User exists!<br>";
    echo "Password hash: " . $user['password'];
} else {
    echo "User not found! Create one with:";
    echo "<pre>
    INSERT INTO users (email, password) 
    VALUES ('mohamadarouni5@gmail.com', '" . password_hash('lol', PASSWORD_DEFAULT) . "')
    </pre>";
}
?>