function enterDashboard() {

    const button = document.querySelector(".enter-btn");

    button.disabled = true;

    button.style.transform = "scale(0.96)";

    setTimeout(() => {

        window.location.href = "/dashboard";

    }, 350);

}