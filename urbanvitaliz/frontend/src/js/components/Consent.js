import Alpine from 'alpinejs'
import axios from 'axios'

Alpine.data("Consent", Consent)

function Consent() {
    return {
        init() {
            console.log('consent');
        },
        async handleAcceptAllCookies(url) {
            console.log('url ?', url);
            let response = await axios.post(url)


            console.log('response : ', response);

        },
        handleRejectAllCookies() {

        }
    }
}

// const instance = axios.create({
//     cache: "no-cache",
//     mode: "same-origin",
//     credentials: "same-origin",
//     headers: {
//         "Content-Type": "application/json",
//         "X-CSRFToken": Cookies.get("csrftoken"),
//     },
// })
