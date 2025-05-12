// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize header scroll effect
    initHeaderScroll();

    // Initialize skill tabs
    initSkillTabs();

    // Initialize project filters
    initProjectFilters();

    // Initialize project sliders
    initProjectSliders();

    // Initialize certification slider
    initCertificationSlider();

    // Initialize timeline toggle
    initTimelineToggle();

    // Initialize mobile menu
    initMobileMenu();

    // Initialize theme toggle
    initThemeToggle();

    // Initialize project modals
    initProjectModals();

    // Initialize project cards for mobile
    initProjectCards();

    // Initialize scroll indicator
    initScrollIndicator();
    
    // Ensure the hero profile image is fully visible
    adjustProfileImage();

    // Initialize skill progress bars
    initSkillProgressBars();

    // Initialize CV download modal
    initCVDownloadModal();

    // Initialize skills tabs
    initSkillsTabs();

    // Initialize timeline toggles
    initTimelineToggles();

    // Activate the first skills tab by default
    const firstTabBtn = document.querySelector('.tabs-header .tab-btn');
    if (firstTabBtn) {
        firstTabBtn.click();
    }

    // Initialize Custom Form Validations
    initCustomFormValidations();
});

// Adjust the profile image to ensure it's fully visible
function adjustProfileImage() {
    const profileImg = document.querySelector('.profile-container img');
    if (profileImg) {
        profileImg.style.objectFit = 'contain';
    }
}

// Initialize header scroll effect
function initHeaderScroll() {
    const header = document.querySelector('header');
    
    if (!header) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// Initialize skill tabs
function initSkillTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    if (tabBtns.length === 0 || tabPanels.length === 0) return;
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Show the corresponding tab panel
            const tabId = btn.getAttribute('data-tab');
            tabPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === tabId + '-tab') {
                    panel.classList.add('active');
                }
            });
        });
    });
}

// Initialize project filters
function initProjectFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const projectCards = document.querySelectorAll('.project-card');
    
    if (filterBtns.length === 0 || projectCards.length === 0) return;
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all filter buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Filter the projects
            const filter = btn.getAttribute('data-filter');
            
            projectCards.forEach(card => {
                if (filter === 'all') {
                    card.style.display = 'block';
                } else {
                    if (card.getAttribute('data-category').includes(filter)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        });
    });
}

// Initialize project sliders
function initProjectSliders() {
    const sliders = document.querySelectorAll('.project-slider');
    
    if (sliders.length === 0) return;
    
    sliders.forEach(slider => {
        const images = slider.querySelectorAll('.slider-img');
        const prevBtn = slider.querySelector('.slider-btn.prev');
        const nextBtn = slider.querySelector('.slider-btn.next');
        
        if (!images.length || !prevBtn || !nextBtn) return;
        
        let currentIndex = 0;
        
        // Show the first image by default
        images[currentIndex].classList.add('active');
        
        // Previous button click
        prevBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            images[currentIndex].classList.remove('active');
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            images[currentIndex].classList.add('active');
        });
        
        // Next button click
        nextBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            images[currentIndex].classList.remove('active');
            currentIndex = (currentIndex + 1) % images.length;
            images[currentIndex].classList.add('active');
        });
    });
}

// Initialize certification slider
function initCertificationSlider() {
    const slider = document.querySelector('.certifications-slider');
    
    if (!slider) return;
    
    const slides = slider.querySelectorAll('.certification-slide');
    const prevBtn = slider.querySelector('.slider-arrow.prev');
    const nextBtn = slider.querySelector('.slider-arrow.next');
    const dots = slider.querySelectorAll('.dot');
    
    if (slides.length === 0 || !prevBtn || !nextBtn || dots.length === 0) return;
    
    let currentIndex = 0;
    
    // Show only the first slide initially
    slides[currentIndex].classList.add('active');
    dots[currentIndex].classList.add('active');
    
    // Update slider
    function updateSlider() {
        // Hide all slides
        slides.forEach(slide => slide.classList.remove('active'));
        
        // Show only current slide
        slides[currentIndex].classList.add('active');
        
        // Update dots
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    }
    
    // Previous button click
    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        updateSlider();
    });
    
    // Next button click
    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % slides.length;
        updateSlider();
    });
    
    // Dot clicks
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentIndex = index;
            updateSlider();
        });
    });
}

// Initialize timeline toggle
function initTimelineToggle() {
    const toggleBtns = document.querySelectorAll('.timeline-toggle');
    
    if (toggleBtns.length === 0) return;
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const description = this.previousElementSibling;
            
            // Toggle the description
            description.classList.toggle('active');
            
            // Update the button text
            if (description.classList.contains('active')) {
                this.textContent = 'Read Less';
            } else {
                this.textContent = 'Read More';
            }
        });
    });
}

// Initialize mobile menu
function initMobileMenu() {
    const menuBtn = document.querySelector('.menu-btn');
    const mobileNav = document.querySelector('.mobile-nav');
    
    if (!menuBtn || !mobileNav) return;
    
    menuBtn.addEventListener('click', function() {
        this.classList.toggle('open');
        mobileNav.classList.toggle('active');
        
        // Add overlay for mobile menu
        let overlay = document.querySelector('.page-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'page-overlay';
            document.body.appendChild(overlay);
        }
        
        overlay.classList.toggle('active');
        
        // Close mobile menu when overlay is clicked
        overlay.addEventListener('click', () => {
            menuBtn.classList.remove('open');
            mobileNav.classList.remove('active');
            overlay.classList.remove('active');
        });
    });
    
    // Close menu when a mobile nav link is clicked
    const mobileNavLinks = mobileNav.querySelectorAll('a');
    
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            menuBtn.classList.remove('open');
            mobileNav.classList.remove('active');
            document.querySelector('.page-overlay')?.classList.remove('active');
        });
    });
}

// Initialize theme toggle
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (!themeToggle) return;
    
    // Check if user has previously selected a theme
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light-mode');
        themeToggle.checked = true;
    }
    
    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            document.body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
        } else {
            document.body.classList.remove('light-mode');
            localStorage.setItem('theme', 'dark');
        }
    });
}

// Initialize project modals
function initProjectModals() {
    const modal = document.getElementById('project-modal');
    const closeBtn = modal ? modal.querySelector('.close-modal') : null;
    const modalBody = modal ? modal.querySelector('.modal-body') : null;
    const detailsBtns = document.querySelectorAll('.project-details-btn');
    
    if (!modal || !closeBtn || !modalBody || detailsBtns.length === 0) return;
    
    // Close modal when clicking on X
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
    
    // Open modal when clicking on project details button
    detailsBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get project details
            const projectCard = this.closest('.project-card');
            const projectTitle = projectCard.querySelector('.project-title').textContent;
            const projectCategory = projectCard.querySelector('.project-category').textContent;
            const projectDescription = projectCard.querySelector('.project-description').innerHTML;
            const projectImage = projectCard.querySelector('.project-img img').getAttribute('src');
            
            // Populate modal
            modalBody.innerHTML = `
                <div class="modal-project-img">
                    <img src="${projectImage}" alt="${projectTitle}">
                </div>
                <h2 class="modal-project-title">${projectTitle}</h2>
                <p class="modal-project-category">${projectCategory}</p>
                <div class="modal-project-description">
                    ${projectDescription}
                </div>
            `;
            
            // Add active class to open modal
            modal.classList.add('active');
        });
    });
}

// Initialize scroll indicator
function initScrollIndicator() {
    const scrollIndicator = document.querySelector('.scroll-indicator');
    
    if (!scrollIndicator) return;
    
    scrollIndicator.addEventListener('click', () => {
        const aboutSection = document.getElementById('about');
        if (aboutSection) {
            aboutSection.scrollIntoView({ behavior: 'smooth' });
        }
    });
}

// Initialize skill progress bars
function initSkillProgressBars() {
    const skillItems = document.querySelectorAll('.skill-item');
    
    if (!skillItems.length) return; // Exit if no skill items found
    
    skillItems.forEach(item => {
        const progressBar = item.querySelector('.skill-progress');
        if (!progressBar) return; // Skip if no progress bar found
        
        // Store the original width from inline style or data attribute
        const originalWidth = progressBar.style.width || progressBar.getAttribute('data-width') || '0%';
        progressBar.setAttribute('data-width', originalWidth);
        
        // Set the width to 0 initially
        progressBar.style.width = '0%';
    });
    
    // Function to animate progress bars when visible
    function animateProgressBars() {
        const skillsSection = document.getElementById('skills');
        if (!skillsSection) return; // Exit if skills section not found
        
        const sectionTop = skillsSection.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (sectionTop < windowHeight * 0.75) {
            skillItems.forEach(item => {
                const progressBar = item.querySelector('.skill-progress');
                if (!progressBar) return; // Skip if no progress bar found
                
                // Get the original width from data attribute or default to 0%
                const originalWidth = progressBar.getAttribute('data-width') || '0%';
                
                // Add animation class and set the width
                progressBar.classList.add('animate-progress');
                progressBar.style.width = originalWidth;
            });
            
            // Remove the scroll event listener once animated
            window.removeEventListener('scroll', animateProgressBars);
        }
    }
    
    // Listen for scroll to trigger animation
    window.addEventListener('scroll', animateProgressBars);
    
    // Also check on page load
    animateProgressBars();
}

// Initialize CV download modal
function initCVDownloadModal() {
    const modal = document.getElementById('cvDownloadModal');
    if (!modal) return;
    
    const downloadBtn = document.getElementById('downloadButton');
    const closeBtn = document.querySelector('.close-modal');
    const cancelBtn = document.getElementById('cancelDownload');
    const form = document.getElementById('cvDownloadForm');
    const otherRadio = document.getElementById('other-reason');
    const otherField = document.getElementById('otherReasonField');
    
    // Open modal when download button is clicked
    downloadBtn.addEventListener('click', function() {
        modal.style.display = 'flex';
    });
    
    // Close modal when X button or Cancel is clicked
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside the modal content
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Show/hide "Other" text field based on radio selection
    document.querySelectorAll('input[name="reason"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            otherField.style.display = otherRadio.checked ? 'block' : 'none';
        });
    });
    
    // Handle form submission
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Collect form data
        const formData = new FormData(form);
        const reason = formData.get('reason');
        let finalReason = reason;
        
        // If "Other" is selected, use the text field value
        if (reason === 'Other') {
            const otherReason = formData.get('other_reason');
            if (!otherReason) {
                alert('Please specify your reason.');
                return;
            }
            finalReason = otherReason;
        }
        
        // Send the data to the server
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ reason: finalReason }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            // Create a temporary link to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'Mohamad_Arouni_CV.pdf';
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Close the modal
            modal.style.display = 'none';
            
            // Reset the form
            form.reset();
            otherField.style.display = 'none';
        })
        .catch(error => {
            console.error('Download failed:', error);
            alert('Failed to download CV. Please try again.');
        });
    });
}

// Initialize skills tabs
function initSkillsTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and panels
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Find and show the corresponding panel
            const tabId = btn.getAttribute('data-tab');
            const panel = document.getElementById(tabId + '-tab');
            if (panel) {
                panel.classList.add('active');
            }
        });
    });
}

// Initialize timeline toggles
function initTimelineToggles() {
    const toggleBtns = document.querySelectorAll('.timeline-toggle');
    
    if (toggleBtns.length === 0) return;
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const timelineContent = this.closest('.timeline-content');
            const description = timelineContent.querySelector('.timeline-description');
            
            // Toggle the active class
            description.classList.toggle('active');
            
            // Update button text
            this.textContent = description.classList.contains('active') ? 'Read Less' : 'Read More';
        });
    });
}

// Initialize Custom Form Validations
function initCustomFormValidations() {
    // Contact Form Validation
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            let isValid = true;
            const nameField = contactForm.querySelector('#contact-name');
            const emailField = contactForm.querySelector('#contact-email');
            const messageField = contactForm.querySelector('#contact-message');

            // Validate Name
            if (!validateField(nameField, 'Name is required.')) {
                isValid = false;
            }

            // Validate Email
            if (!validateField(emailField, 'A valid email is required.', value => /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(value))) {
                isValid = false;
            }

            // Validate Message
            if (!validateField(messageField, 'Message cannot be empty.')) {
                isValid = false;
            }

            if (!isValid) {
                event.preventDefault(); // Prevent submission if not valid
            } else {
                // Optional: Clear validation messages on successful submission attempt before Formspree handles it
                clearValidationMessage(nameField);
                clearValidationMessage(emailField);
                clearValidationMessage(messageField);
                // Allow form to submit to Formspree
            }
        });

        // Add real-time validation for better UX
        addRealTimeValidation(contactForm.querySelector('#contact-name'), 'Name is required.');
        addRealTimeValidation(contactForm.querySelector('#contact-email'), 'A valid email is required.', value => /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(value));
        addRealTimeValidation(contactForm.querySelector('#contact-message'), 'Message cannot be empty.');
    }

    // General field validation function
    function validateField(field, defaultMessage, customValidation = null) {
        const validationMessageSpan = field.parentElement.querySelector('.validation-message');
        let isValid = field.value.trim() !== '';
        let message = defaultMessage;

        if (isValid && customValidation) {
            isValid = customValidation(field.value.trim());
            if (!isValid) message = defaultMessage; // Keep default message for custom validation failure unless specified
        }

        if (!isValid) {
            field.classList.add('invalid');
            field.classList.remove('valid');
            if (validationMessageSpan) {
                validationMessageSpan.textContent = message;
                validationMessageSpan.style.display = 'block';
            }
        } else {
            field.classList.remove('invalid');
            field.classList.add('valid');
            if (validationMessageSpan) {
                validationMessageSpan.textContent = '';
                validationMessageSpan.style.display = 'none';
            }
        }
        return isValid;
    }

    function addRealTimeValidation(field, defaultMessage, customValidation = null) {
        if(field) {
            field.addEventListener('input', () => validateField(field, defaultMessage, customValidation));
             // Validate on blur as well, after user finishes interacting
            field.addEventListener('blur', () => validateField(field, defaultMessage, customValidation));
        }
    }

    function clearValidationMessage(field) {
        const validationMessageSpan = field.parentElement.querySelector('.validation-message');
        field.classList.remove('invalid');
        field.classList.remove('valid');
        if (validationMessageSpan) {
            validationMessageSpan.textContent = '';
            validationMessageSpan.style.display = 'none';
        }
    }
}

// Initialize project cards for mobile interaction
function initProjectCards() {
    const projectCards = document.querySelectorAll('.project-card');
    
    projectCards.forEach(card => {
        const overlay = card.querySelector('.project-overlay');
        const links = card.querySelectorAll('.project-links a');
        
        // Handle card click
        overlay.addEventListener('click', (e) => {
            // Don't toggle if clicking on a link
            if (e.target.closest('.project-links a')) {
                return;
            }
            
            // Toggle active state
            card.classList.toggle('active');
            
            // Close other cards
            projectCards.forEach(otherCard => {
                if (otherCard !== card) {
                    otherCard.classList.remove('active');
                }
            });
        });
        
        // Handle link clicks
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent card toggle when clicking links
            });
        });
        
        // Close card when clicking outside
        document.addEventListener('click', (e) => {
            if (!card.contains(e.target)) {
                card.classList.remove('active');
            }
        });
    });
}

// Note: particles.js configuration moved to separate file as requested