import Alpine from 'alpinejs'
import axios from 'axios'

Alpine.data("Consent", Consent)

function Consent() {
    return {
        userHasSelectedCookies: false,
        init() {
            console.log('consent');
            this.userHasSelectedCookies = document.cookie.includes('cookie_consent')
            console.log('this.user', this.userHasSelectedCookies)
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
        }
    }
}
