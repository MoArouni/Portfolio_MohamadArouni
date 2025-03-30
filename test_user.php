<?php
try {
    // New password to hash
    $new_password = "9276463"; // Change this
    $hashed_password = password_hash($new_password, PASSWORD_BCRYPT);

    // Database connection
    $pdo = new PDO("mysql:host=localhost;dbname=portfolio_blog_db;charset=utf8mb4", "root", "");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Update query with parameter binding for security
    $sql = "UPDATE users SET password = :password WHERE email = :email";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([
        ':password' => $hashed_password,
        ':email' => "mohamadarouni5@gmail.com" // Change this if needed
    ]);

    echo "Password updated successfully!";
} catch (PDOException $e) {
    die("Error: " . $e->getMessage()); // Debugging info (remove in production)
}
?>
