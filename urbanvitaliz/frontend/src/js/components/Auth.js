import Alpine from 'alpinejs'
import { escapeHtml } from '../utils/escapeHTML'

function Auth() {
    return {
        initLogin() {
            const loginInput = document.getElementById("id_login");
            const forgotPasswordButton = document.getElementById("forgot-password");

            loginInput.addEventListener("change", e => {

                const newUrlwithHash = forgotPasswordButton.href + "#" + e.target.value;

                forgotPasswordButton.addEventListener("click", e => {
                    e.preventDefault();

                    location.href = escapeHtml(newUrlwithHash)
                })
            })
        },
        initResetPassword() {
            console.log("lol");
            const url = new URL(window.location.href);

            console.log(url);
            const urlHash = url.hash.replace('#', '');

            const loginInput = document.getElementById("id_email");

            if (urlHash && urlHash.length > 0) loginInput.value = urlHash
        }
    }
}

Alpine.data("Auth", Auth)
