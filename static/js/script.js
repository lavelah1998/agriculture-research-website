
// Wait until the webpage is fully loaded
document.addEventListener("DOMContentLoaded", function () {

    // Display current year in the footer if an element exists
    const yearElement = document.getElementById("current-year");

    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }

    // Highlight navigation links when clicked
    const navigationLinks = document.querySelectorAll(".nav-links a");

    navigationLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            navigationLinks.forEach(function (item) {
                item.classList.remove("active");
            });

            link.classList.add("active");
        });
    });

});


/* ADMIN DASHBOARD */

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 35px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.dashboard-card {
    background: #ffffff;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #e5eee8;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
}

.dashboard-card h3 {
    color: #315b43;
    margin-bottom: 12px;
}

.dashboard-number {
    font-size: 36px;
    font-weight: bold;
    color: #176b3a;
    margin: 10px 0;
}

.dashboard-card span {
    color: #777777;
    font-size: 14px;
}

.dashboard-welcome {
    margin-top: 35px;
    padding: 25px;
    background: #f1f7f2;
    border-radius: 12px;
}
