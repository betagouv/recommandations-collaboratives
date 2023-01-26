import Alpine from 'alpinejs'
import axios from 'axios'

Alpine.data("Consent", Consent)

function Consent() {
    return {
        userHasSelectedCookies: false,
        init() {
            this.userHasSelectedCookies = document.cookie.includes('cookie_consent')
        },
        async handleAcceptAllCookies(url) {
            try {
                await axios.post(url)
                location.reload()
            } catch (err) {
                console.error('Something went wrong : ', err)
            }
        },
        async handleRejectAllCookies(url) {
            try {
                await axios.post(url)
                location.reload()
            } catch (err) {
                console.error('Something went wrong : ', err)
            }
        },
        handleSetCookiesPreferences() {
            console.log('lol');
        }
    }
}
