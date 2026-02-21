// MOVE FORM UP OR DOWN
document.addEventListener("DOMContentLoaded", function() {
    const section = document.getElementById("select_by_stop_id");
    const arrow = document.getElementById("collapse_arrow");

    let collapsed = false;

    arrow.addEventListener("click", () => {
        // Get current total height of the section
        const sectionHeight = section.offsetHeight;

        if (!collapsed) {
            // Collapse: move section up by its height
            section.style.transform = `translateY(-${sectionHeight}px)`;
            arrow.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M297.4 438.6C309.9 451.1 330.2 451.1 342.7 438.6L502.7 278.6C515.2 266.1 515.2 245.8 502.7 233.3C490.2 220.8 469.9 220.8 457.4 233.3L320 370.7L182.6 233.4C170.1 220.9 149.8 220.9 137.3 233.4C124.8 245.9 124.8 266.2 137.3 278.7L297.3 438.7z"/></svg>`; // up arrow
        } else {
            // Expand: move section back down
            section.style.transform = `translateY(0px)`;
            arrow.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M297.4 201.4C309.9 188.9 330.2 188.9 342.7 201.4L502.7 361.4C515.2 373.9 515.2 394.2 502.7 406.7C490.2 419.2 469.9 419.2 457.4 406.7L320 269.3L182.6 406.6C170.1 419.1 149.8 419.1 137.3 406.6C124.8 394.1 124.8 373.8 137.3 361.3L297.3 201.3z"/></svg>`; // down arrow
        }

        collapsed = !collapsed;
    });
});