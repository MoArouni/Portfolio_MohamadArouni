<?php
require_once __DIR__ . '/includes/db.php';
session_start();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mohamad Arouni Webpage</title>
    <link rel="stylesheet" href="../css/reset.css">
    <link rel="stylesheet" href="../css/home.css">
    <link rel="stylesheet" href="../css/mobile.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Ovo&display=swap" rel="stylesheet">
    <script src = "../js/text_appear.js"></script>

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
            <li><a href="#about">Home</a></li>
            <li><a href="#portfolio">Portfolio</a></li>
            <li><a href="#contact">Contact Me</a></li>
            <li><a href="viewBlog.php">Blog</a></li>
            <?php if (isset($_SESSION['user_id'])): ?>
                <li><a href="logout.php">Logout</a></li>
            <?php else: ?>
                <li><a href="login.php">Login</a></li>
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
                <li><a href="#about">About Me</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="/home/#hobbies">Hobbies</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#cv">Download CV</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#education">Education</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#projects">Projects</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#skills">Skills</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#certifications">Certifications</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="#contact">Contact Me</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <li><a href="viewBlog.php">Blog</a></li>
                <div class="underline2" style="width: 90%;"></div>
                <?php if (isset($_SESSION['user_id'])): ?>
                    <li><a href="logout.php">Logout</a></li>
                <?php else: ?>
                    <li><a href="login.php">Login</a></li>
                <?php endif; ?>
                <div class="underline2" style="width: 90%;"></div>

            </ul>
        </div>
        <script src="../js/anti-scroll-menu.js"></script>
    </nav>

    <section id="hero">
        <div class="hero-container">
            <!-- Left Section: Mission and Languages -->
            <div class="hero-left">
                <div class="section-box social-media links">
                    <section class="footer" id="social-media">
                        <a id = "facebook" href="https://www.facebook.com/mo.arouni/" 
                        class = "social-media-link" target="_blank">Facebook
                        </a>

                        <a id = "instagram" href="https://www.instagram.com/mohamad_arouni/" 
                        class = "social-media-link" target="_blank">Instagram
                        </a>
                        <a id = "linkedin" href="https://www.linkedin.com/in/mohamad-arouni-578168293/" 
                        class = "social-media-link" target="_blank">Linkedin
                        </a>
                        <a id = "github" href="https://github.com/MoArouni" 
                        class = "social-media-link" target="_blank">Github
                        </a>
                    </section>
                </div>  
                <div class="section-box languages">
                    <div class="skill-container">
                        <label for="skill">English</label>
                        <div class="skill-bar">
                            <div id = "languages" class="skill-progress" style="width: 100%;"></div> <!-- Fluent -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">French</label>
                        <div class="skill-bar">
                            <div id = "languages" class="skill-progress" style="width: 100%;"></div> <!-- Fluent -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Arabic</label>
                        <div class="skill-bar">
                            <div id = "languages" class="skill-progress" style="width: 100%;"></div> <!-- Fluent -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Spanish</label>
                        <div class="skill-bar">
                            <div id = "languages" class="skill-progress" style="width: 60%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                </div>
            </div>
    
            <!-- Middle Section: Profile Picture and About Me -->
            <div id = "about" class="hero-middle">
                <div class="section-box hero-text">
                    <h1 style="text-align: left;">About</h1>
                    <div class="underline" style="width: 4rem;"></div>
                    <p><em>I'm not here to impress, I'm here to improve.</em></p>
                    <div class="hero-image">
                        <img src="/Project/images/about/me/tyre-pic.jpg" alt="Your Profile">
                        <figcaption>Aspiring Computer Scientist</figcaption>
                    </div>
                </div>
            </div>
    
            <!-- Right Section: "Currently Doing..." -->
            <div class="hero-right">
                <div class="section-box mission">
                    <h1>My Mission</h1>
                    <div class="underline" style="width: 6.8rem;"></div> <!-- Small line under the title -->
                    <p style="font-size: 1.1rem;">My mission is to harness the power of technology to create innovative solutions 
                        that solve real-world problems. My career aspirations include seeking work experience, 
                        finishing my project on my Flask application, starting a machine learning project,
                            and working in tech after graduating with a first. I aim to become a software engineer, 
                            delve into artificial intelligence, data analytics, and machine learning, or venture into cybersecurity.</p>
                </div>
            </div>
        </div>
    </section>   

    <section id="portfolio" class="intro-section">
        <h1 style="font-size: 4rem; text-align: center; margin-right: 5rem;">Portfolio</h1>
    </section>

    
    <div id="portfolio">
        <div class="cv-container">
            <div class="cv-text">
                <p>If you wish to download my CV, you can do so here.</p>
            </div>
            <div id = "cv" class="cv-img">
                <script src="../js/cv_authorise.js"></script>
                <a id="downloadButton" href="javascript:void(0);" download>
                    <img src="/Project/images/about/me/cv.png" alt="Basic Info">
                </a>
            </div>
        </div>
    </div>

    <div id="education" class="intro-section">
        <h1 style="font-size: 2rem; text-align: center;">Education</h1>
    </div>  

    <section id="education" class="hero-container2">
        <!-- Education Items Grid -->
        <div class="grid">
            <!-- Lycee International -->
            <div class="section-box project-container">
                <!-- Image Division -->
                <div class="project-image">
                    <img src="/Project/images/about/work/school.webp" alt="School">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division -->
                    <div class="project-title">
                        <h3>Lycée International De Londres Winston Churchill</h3>
                        <div class="read-more">Read More +</div>
                    </div>
                    
                    <!-- Info Division -->
                    <div class="project-info">
                        <span>Graduated: 2023</span>
                    </div>
                    
                    <!-- Hidden Description -->
                    <div class="project-description" style="display: none;">
                        <p>Graduated with <strong>Highest Honours with Committee Praise</strong> in the French Baccalaureate.</p>
                        <ul>
                            <li>A* in Mathematics</li>
                            <li>A* in Physics & Chemistry</li>
                            <li>A* in Computer Science</li>
                            <li>A* in Further Mathematics</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Queen Mary University -->
            <div class="section-box project-container">
                <!-- Image Division -->
                <div class="project-image">
                    <img src="/Project/images/about/work/university.png" alt="University">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division -->
                    <div class="project-title">
                        <h3>Queen Mary University of London</h3>
                        <h4>EECS (Electronic Engineering and Computer Science)</h4>
                        <div class="read-more">Read More +</div>
                    </div>
                    
                    <!-- Info Division -->
                    <div class="project-info">
                        <span>2023 - Present</span>
                    </div>
                    
                    <!-- Hidden Description -->
                    <div class="project-description" style="display: none;">
                        <p><strong>Bachelor of Computer Science with Industrial Placement</strong></p>
                        <p>Currently in my <strong>1st year</strong>, expected to graduate with <strong>First-Class Honours</strong>.</p>
                        <p>Relevant Courses:</p>
                        <ul>
                            <li>Procedural & Object-Oriented Programming</li>
                            <li>Systems & Networks (Computing Context)</li>
                            <li>Software Engineering Principles</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </section>


    <div class="intro-section">
        <h1 style="font-size: 2rem; text-align: center;">Projects</h1>
    </div>


    <section id="projects" class="hero-container2">  
        <!-- Title Section -->      
        <div class = "grid">
            <!-- Tetris Project -->
            <div class="section-box project-container">
                <!-- Image Division (70% height, 100% width) -->
                <div class="project-image">
                    <img src="/Project/images/about/work/tetris.png" alt="Tetris">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division with Read More -->
                    <div class="project-title">
                        <h3>Tetris Enhancement: Open Source Project</h3>
                        <div class="read-more">Read More +</div>
                    </div>
                    <!-- Info Division (GitHub link/date) -->
                    <div class="project-info">
                        <a href="https://github.com/MoArouni/Tetris-project" target="_blank"><small>GitHub Repository</small></a> /
                        <span>December 2024</span>
                    </div>
                    
                    <!-- Hidden Description (revealed on click) -->
                    <div class="project-description" style="display: none;">
                        <p>Transformed a basic Tetris implementation by introducing a feature-rich menu system and refining gameplay functionalities.</p>
                        <ul>
                            <li>Enhanced user experience with an improved interface and upgraded visuals.</li>
                            <li>Implemented <strong>Object-Oriented Programming</strong> principles for scalability and maintainability.</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Data Tools Project -->
            <div class="section-box project-container">
                <!-- Image Division -->
                <div class="project-image">
                    <img src="/Project/images/about/work/data-tools.png" alt="Data-tools">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division with Read More -->
                    <div class="project-title">
                        <h3>Flask Application: Data Tools</h3>
                        <div class="read-more">Read More +</div>
                    </div>
                    <!-- Info Division -->
                    <div class="project-info">
                        <a href="https://github.com/MoArouni/Data_analysis_tools" target="_blank"><small>GitHub Repository</small></a> /
                        <span>December 2024-Present</span>
                    </div>
                    
                    <!-- Hidden Description -->
                    <div class="project-description" style="display: none;">
                        <p>Developed a <strong>Flask-based web application</strong> for structured data analysis and management.</p>
                        <ul>
                            <li><strong>Automated Data Processing:</strong> Utilized Pandas for data cleaning and analysis.</li>
                            <li><strong>Dynamic Frontend Rendering:</strong> Implemented Jinja2 for real-time content updates.</li>
                            <li><strong>Secure & Scalable Backend:</strong> Used Object-Oriented Programming for maintainability.</li>
                            <li><strong>Real-Time Data Updates:</strong> Integrated Google Apps Script for automated database management.</li>
                            <li><strong>Local Deployment:</strong> Used ngrok and Render to host the website locally.</li>
                        </ul>
                        <p><em>Currently refining authentication and SQL storage for enhanced security.</em></p>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <script src = "../js/readMore.js"></script>


    <div id="skills" class="intro-section">
        <h1 style="font-size: 2rem; text-align: center;">Skills</h1>
    </div> 

    <section id = "skills"> 
        <div class="hero-container2">
            <div class="skills">
                <div class="section-box">
                    <h1>Technical Skills</h1>
                    <br>
                    <div class="skill-container">
                        <label for="skill">Python</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 90%;"></div> <!-- Fluent -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Java</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 90%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">HTML5</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 100%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">CSS3</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 90%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">JavaScript</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 80%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">SQL</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 80%;"></div> <!-- Intermediate -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Abstract Thinking</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 100%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Data and Statistical Analysis</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 70%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">PHP</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 60%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                </div>
            
                <div class="section-box">
                    <h1>Soft Skills</h1>
                    <br>
                    <div class="skill-container">
                        <label for="skill">Collaboration</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 90%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Communication</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 100%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Problem Solving</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 100%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Time management</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 80%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Adaptability</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 90%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                </div>
            
                <div class="section-box">
                    <h1>Libraries and Frameworks</h1>
                    <br>
                    <div class="skill-container">
                        <label for="skill">Pandas</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 80%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Matplotlib</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 70%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Seaborn</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 70%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Flask</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 100%;"></div> <!-- Proficient -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Pygame</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 80%;"></div> <!-- Intermediate -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Java Swing</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 10%;"></div> <!-- Intermediate -->
                        </div>
                    </div>
                    <div class="skill-container">
                        <label for="skill">Scikit Learn</label>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: 20%;"></div> <!-- Intermediate -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <div id="certifications" class="intro-section">
        <h1 style="font-size: 2rem; text-align: center;">Certifications</h1>
    </div>
    

    <section id="certifications">
        <div class = "hero-container2">
            <div class="certification-grid">
                <div class="certification-card">
                    <img src="/Project/images/about/work/data-certificate.png" alt="Data Analysis with Python">
                    <h3>Data Analysis with Python</h3>
                    <p>Issued by: edX</p>
                    <p>Year: July-August 2023</p>
                </div>
                <div class="certification-card">
                    <img src="/Project/images/about/work/web-certificate.png" alt="Introduction to Web Development with HTML5, CSS3, JavaScript">
                    <h3>Introduction to Web Development with HTML5, CSS3, JavaScript</h3>
                    <p>Issued by: edX</p>
                    <p>Year: August 2023</p>
                </div>
                <div class="certification-card">
                    <img src="/Project/images/about/work/ai-certificate.png" alt="AI for Everyone: Master the Basics">
                    <h3>AI for Everyone: Master the Basics</h3>
                    <p>Issued by: edX</p>
                    <p>Year: August 2023</p>
                </div>
                <!-- Repeat for other certifications -->
            </div>        
        </div>
    </section>

    <section id="hobbies" class="hero-container2">
        <!-- Title Section -->
        <div class="intro-section">
            <h1 style="font-size: 2rem; text-align: center;">Hobbies</h1>
        </div>
        
        <!-- Hobbies Grid -->
        <div class="grid">
            <!-- Chess -->
            <div class="section-box project-container">
                <!-- Image Division -->
                <div class="project-image">
                    <img src="/Project/images/about/hobbies/chess.jpg" alt="Chess">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division -->
                    <div class="project-title">
                        <h3>Chess</h3>
                        <div class="read-more">Read More +</div>
                    </div>
                    
                    <!-- Info Division -->
                    <div class="project-info">
                        <span>Chess Regionals Victory round 1</span>
                    </div>
                    
                    <!-- Hidden Description -->
                    <div class="project-description" style="display: none;">
                        <p>Chess was a casual pastime for me as a kid, but as I grew older, 
                        I started playing for hours every day and became advanced in the game.</p>
                        <ul>
                            <li>1700 rating</li>
                            <li>Developed strategic thinking skills</li>
                            <li>Provides life perspectives through game analogies</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Football -->
            <div class="section-box project-container">
                <!-- Image Division -->
                <div class="project-image">
                    <img src="/Project/images/about/hobbies/football.jpg" alt="Football">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division -->
                    <div class="project-title">
                        <h3>Football</h3>
                        <div class="read-more">Read More +</div>
                    </div>
                    
                    <!-- Info Division -->
                    <div class="project-info">
                        <span>Hampstead FC Player</span>
                    </div>
                    
                    <!-- Hidden Description -->
                    <div class="project-description" style="display: none;">
                        <p>Football has always been a major part of my life. I played in a Sunday league with a football club.</p>
                        <ul>
                            <li>Scored winning goal for team promotion</li>
                            <li>Developed teamwork and leadership skills</li>
                            <li>Playing since 3 years old</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Swimming -->
            <div class="section-box project-container">
                <!-- Image Division -->
                <div class="project-image">
                    <img src="/Project/images/about/hobbies/swimming.jpg" alt="Swimming">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division -->
                    <div class="project-title">
                        <h3>Swimming</h3>
                        <div class="read-more">Read More +</div>
                    </div>
                    
                    <!-- Info Division -->
                    <div class="project-info">
                        <span>National Level Competitor</span>
                    </div>
                    
                    <!-- Hidden Description -->
                    <div class="project-description" style="display: none;">
                        <p>Competed at national level three times, starting at age five. Trained internationally with twice-daily sessions.</p>
                        <ul>
                            <li>Competed in Lebanon, UK, and Saudi Arabia</li>
                            <li>Developed amazing discipline</li>
                            <li>Primary sport for 10+ years</li>
                        </ul>
                        <figcaption>Nationals 6 and Under In Aramco, Riyadh</figcaption>
                    </div>
                </div>
            </div>

            <!-- Piano -->
            <div class="section-box project-container">
                <!-- Image Division -->
                <div class="project-image">
                    <img src="/Project/images/about/hobbies/piano.jpg" alt="Piano">
                </div>
                
                <!-- Text Division -->
                <div class="project-text">
                    <!-- Title Division -->
                    <div class="project-title">
                        <h3>Piano</h3>
                        <div class="read-more">Read More +</div>
                    </div>
                    
                    <!-- Info Division -->
                    <div class="project-info">
                        <span>Grade 8 ABRSM</span> 
                    </div>
                    
                    <!-- Hidden Description -->
                    <div class="project-description" style="display: none;">
                        <p>With over 10 years of practice, achieved distinction in grade 8 ABRSM piano performance exam.</p>
                        <ul>
                            <li>Provides creative outlet</li>
                            <li>Develops focus and patience</li>
                            <li>Helps balance sedentary work life</li>
                        </ul>
                        <figcaption>ABRSM grade 8 piano performance</figcaption>
                    </div>
                </div>
            </div>
        </div>
    </section>


    
    <!-- Contact Section -->
    <section id="contact">
        <form action="https://formspree.io/f/mldgykon" method="POST">
            <h1 style = "font-size: 3rem; text-align: center;">Contact Me</h1>
            <br> 
            <br>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>

            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>

            <label for="message">Message:</label>
            <textarea id="message" name="message" required ></textarea>

            <div style="text-align: center;">
                <button class="cta-button" type="submit">Send</button>
            </div>
        </form>
        <script src="js/contact-form.js"></script>
    </section>



    <footer>
        <i>&copy; 2025 Mohamad Arouni. All rights reserved.</i>
    </footer>
</body>
</html>
