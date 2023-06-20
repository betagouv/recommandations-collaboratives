import Alpine from 'alpinejs'
import { createPopper } from '@popperjs/core';
import appStore from '../store/app'
import { gravatar_url } from '../utils/gravatar';

Alpine.data("User", User)

function User() {
    return {
        popper: null,
        isOpening: false,
        gravatar_url,
        init() {
            const popper = createPopper(this.$refs.user, this.$refs.userTooltip, {
                placement: 'top-start',
                modifiers: [
                    {
                        name: 'offset',
                        options: {
                            offset: [0, 10],
                        },
                    },
                ],
            })

            this.popper = popper
        },

        async show() {
            this.$refs.userTooltip.setAttribute('data-show', '');
            await this.popper.update()
        },

        hide() {
            this.$refs.userTooltip.removeAttribute('data-show');
        },

        async onUserClick() {
            await this.show()
            this.isOpening = true
        },

        onOutsideUserClick() {
            if (this.isOpening) {
                this.isOpening = false
            } else {
                this.hide()
            }
        },
        clipboardCopy(type, text) {
            navigator.clipboard.writeText(text).then(function () {
                this.selectText(type);
            }.bind(this));
        },
        selectText: function (text) {
            appStore.notification.message = `${text} a bien été copiée`
            appStore.notification.isOpen = true
        },
    }
}
