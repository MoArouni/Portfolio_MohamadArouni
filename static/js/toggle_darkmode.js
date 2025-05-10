document.addEventListener("DOMContentLoaded", () => {
    const toggleButton = document.getElementById("dark-mode-toggle");
    const sunIcon = toggleButton.querySelector('.sun');
    const moonIcon = toggleButton.querySelector('.moon');
    const body = document.body;

    // Debugging
    console.log("Initial darkMode value:", localStorage.getItem("darkMode"));
    
    // Check local storage for dark mode preference
    if (localStorage.getItem("darkMode") === "enabled") {
        body.classList.remove("light-mode");
        console.log("Applied dark mode on load");
    } else {
        body.classList.add("light-mode");
        console.log("Applied light mode on load");
    }

    toggleButton.addEventListener("click", () => {
        if (body.classList.contains("light-mode")) {
            body.classList.remove("light-mode");
            localStorage.setItem("darkMode", "enabled");
            console.log("Switched to dark mode");
        } else {
            body.classList.add("light-mode");
            localStorage.setItem("darkMode", "disabled");
            console.log("Switched to light mode");
        }
        
        // Debugging
        console.log("Current darkMode value:", localStorage.getItem("darkMode"));
        console.log("Body has light-mode class:", body.classList.contains("light-mode"));
    });
});