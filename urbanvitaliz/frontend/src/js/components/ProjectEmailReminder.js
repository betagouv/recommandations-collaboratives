import Alpine from 'alpinejs'
import { createPopper } from '@popperjs/core';

function ProjectEmailReminder() {
    return {
        popper: null,
        isOpening: false,
        get isLoading() {
            return this.$store.app.isLoading
        },
        init() {
            const popper = createPopper(this.$refs.emailReminderButton, this.$refs.emailReminderTooltip, {
                placement: 'bottom-end',
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
            this.$refs.emailReminderTooltip.setAttribute('data-show', '');
            await this.popper.update()
        },

        hide() {
            this.$refs.emailReminderTooltip.removeAttribute('data-show');
        },
        async onEmailReminderButtonClick() {
            await this.show()
            this.isOpening = true
        },

        onOutsideEmailReminderButtonClick() {
            if (this.isOpening) {
                this.isOpening = false
            } else {
                this.hide()
            }
        },
    }
}

Alpine.data("ProjectEmailReminder", ProjectEmailReminder)
