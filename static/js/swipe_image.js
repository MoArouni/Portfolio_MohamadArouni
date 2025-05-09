document.addEventListener('DOMContentLoaded', function() {
    const image = this.getElementById("Gallery")
    const imageSources = [
        '/static/images/about/projects/website_before.png',
        '/static/images/about/projects/website_after.png',
    ]
    let currentIndex = 0;

    document.getElementById("next").addEventListener("click", function() {
        currentIndex = (currentIndex + 1) % imageSources.length;
        image.src = imageSources[currentIndex];
    });

    document.getElementById("previous").addEventListener("click", function() {
        currentIndex = (currentIndex - 1 + imageSources.length) % imageSources.length;
        image.src = imageSources[currentIndex];
    });
});