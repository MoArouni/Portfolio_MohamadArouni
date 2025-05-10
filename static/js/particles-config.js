// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize particles.js
    if (document.getElementById('particles-js')) {
        console.log("Initializing particles.js");
        
        // Check if in dark mode (light theme)
        const isDarkMode = document.body.classList.contains('dark-mode');
        
        // Adjust opacity and number of particles based on theme
        const particleValue = isDarkMode ? 80 : 100;
        const opacityValue = isDarkMode ? 0.3 : 0.4;
        
        particlesJS('particles-js', {
            "particles": {
                "number": {
                    "value": particleValue,
                    "density": {
                        "enable": true,
                        "value_area": 800
                    }
                },
                "color": {
                    "value": "#6e00ff"
                },
                "shape": {
                    "type": "circle",
                    "stroke": {
                        "width": 0,
                        "color": "#000000"
                    },
                    "polygon": {
                        "nb_sides": 5
                    }
                },
                "opacity": {
                    "value": opacityValue,
                    "random": true,
                    "anim": {
                        "enable": true,
                        "speed": 1,
                        "opacity_min": 0.1,
                        "sync": false
                    }
                },
                "size": {
                    "value": 3,
                    "random": true,
                    "anim": {
                        "enable": true,
                        "speed": 2,
                        "size_min": 0.1,
                        "sync": false
                    }
                },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#6e00ff",
                    "opacity": 0.3,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 1.5,
                    "direction": "none",
                    "random": true,
                    "straight": false,
                    "out_mode": "out",
                    "bounce": false,
                    "attract": {
                        "enable": false,
                        "rotateX": 600,
                        "rotateY": 1200
                    }
                }
            },
            "interactivity": {
                "detect_on": "window",
                "events": {
                    "onhover": {
                        "enable": true,
                        "mode": "grab"
                    },
                    "onclick": {
                        "enable": true,
                        "mode": "push"
                    },
                    "resize": true
                },
                "modes": {
                    "grab": {
                        "distance": 140,
                        "line_linked": {
                            "opacity": 0.8
                        }
                    },
                    "bubble": {
                        "distance": 400,
                        "size": 40,
                        "duration": 2,
                        "opacity": 8,
                        "speed": 3
                    },
                    "repulse": {
                        "distance": 200,
                        "duration": 0.4
                    },
                    "push": {
                        "particles_nb": 4
                    },
                    "remove": {
                        "particles_nb": 2
                    }
                }
            },
            "retina_detect": true
        });
        
        // Re-initialize on theme change
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('change', function() {
                setTimeout(function() {
                    // Clear previous particles
                    pJSDom[0].pJS.particles.array = [];
                    
                    // Reinitialize with adjusted values based on new theme
                    const isNowDarkMode = document.body.classList.contains('dark-mode');
                    pJSDom[0].pJS.particles.number.value = isNowDarkMode ? 80 : 100;
                    pJSDom[0].pJS.particles.opacity.value = isNowDarkMode ? 0.3 : 0.4;
                    
                    // Redraw particles
                    pJSDom[0].pJS.fn.particlesRefresh();
                }, 100);
            });
        }
    } else {
        console.error("Particles container not found");
    }
}); 