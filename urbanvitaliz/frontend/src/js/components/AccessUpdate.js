import Alpine from 'alpinejs'
import appStore from '../store/app'

function AccessUpdate(url) {
    return {
        url: url,
        isCopied: false,
        selectText: function () {
            this.$refs.input.select();
            appStore.notification.message = "L'adresse de la page a bien été copiée"
            appStore.notification.isOpen = true
        },
        clipboardCopy: function() {
            navigator.clipboard.writeText(url).then(function () {
                this.isCopied = true;
                this.$refs.button.blur();
                this.selectText();
                
            }.bind(this));
        }
    }
}

Alpine.data("AccessUpdate", AccessUpdate)
