// TOGGLE IMAGE WHERE IS THE BUS STOP ID
document.addEventListener("DOMContentLoaded", function() {
    // Get elements
    const toggleLink = document.querySelector(".toggle_help_finding_stop_id");
    const helpDiv = document.getElementById("help_finding_stop_id");
    const closeButton = helpDiv.querySelector("button");

    // Toggle help div on link click/touch
    toggleLink.addEventListener("click", function() {
        const computed = window.getComputedStyle(helpDiv).display;
        if (computed === "none") {
            helpDiv.style.display = "block";
        } else {
            helpDiv.style.display = "none";
        }
    });

    // Close button hides the help div
    closeButton.addEventListener("click", function() {
        helpDiv.style.display = "none";
    });
});