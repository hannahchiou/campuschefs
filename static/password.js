document.addEventListener("DOMContentLoaded", function () {
    // Using the eye slash icons from Bootstrap Icons
    const togglePasswordIcons = document.querySelectorAll(".bi-eye-slash, .bi-eye");
    
    togglePasswordIcons.forEach(icon => {
        icon.addEventListener("click", function () {
            const passwordField = this.previousElementSibling;

            if (passwordField && passwordField.type === "password") {
                // Switch to text input
                passwordField.type = "text";
                this.classList.remove("bi-eye-slash");
                this.classList.add("bi-eye");
            } else if (passwordField) {
                // Switch back to password input
                passwordField.type = "password";
                this.classList.remove("bi-eye");
                this.classList.add("bi-eye-slash");
            }
        });
    });
});
