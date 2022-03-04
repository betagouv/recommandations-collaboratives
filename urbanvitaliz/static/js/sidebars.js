/* should be moved to global js */
(function () {
    'use strict'
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl)
    })
})();

/* for sidebar toggling */
(function mainScript() {
    "use strict";

    const offcanvasToggle = document.querySelector(
        '[data-bs-toggle="offcanvas"]'
    );
    const offcanvasCollapse = document.querySelector(".offcanvas-collapse");

    offcanvasToggle.addEventListener("click", function () {
        offcanvasCollapse.classList.toggle("open");
    });
})();
