document.getElementById("clearBtn").addEventListener("click", function() {
    if (confirm("Are you sure you want to clear the fields?")) {
        document.getElementById("title").value = "";
        document.getElementById("content").value = "";
    }
});