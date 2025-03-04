document.getElementById("clearBtn").addEventListener("click", function() {
    if (confirm("Are you sure you want to clear the fields?")) {
        document.getElementById("email").value = "";
        document.getElementById("password").value = "";
    }
});