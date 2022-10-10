import Alpine from 'alpinejs'

function Auth() {
    return {
        initLogin() {
            const loginInput = document.getElementById("id_login");
            const forgotPasswordButton = document.getElementById("forgot-password");

            loginInput.addEventListener("change", (e) => {
                forgotPasswordButton.href = forgotPasswordButton.href + `#${e.target.value}`
            })
        },
        initResetPassword() {
            const url = new URL(window.location.href);
            const urlHash = url.hash.replace('#','');

            const loginInput = document.getElementById("id_email");

            if (urlHash && urlHash.length > 0) loginInput.value = urlHash
        }
    }
}

Alpine.data("Auth", Auth)
