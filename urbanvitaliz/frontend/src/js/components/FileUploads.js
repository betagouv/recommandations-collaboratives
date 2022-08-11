import Alpine from 'alpinejs'
import { createPopper } from '@popperjs/core';
import { getString } from '../utils/getString'

Alpine.data('FileUpload', (type) => ({
    getString,
    type,
    // Popover
    popper: null,
    isOpening: false,

    init() {
        const popper = createPopper(this.$refs.button, this.$refs.popover, {
            placement: 'bottom',
            modifiers: [
                { name: 'arrow', options: { element: this.$refs.arrow } },
                { name: 'offset', options: { offset: [0, 12] } }
            ]
        })

        this.$refs.popover.style.display = 'none'
        this.popper = popper
    },

    async show() {
        this.$refs.popover.style.display = 'block'
        await this.popper.update()
    },

    hide() {
        this.reset()
        this.$refs.popover.style.display = 'none'
    },

    async onButtonClick() {
        await this.show()
        this.isOpening = true
    },

    onOutsideClick() {
        if (this.isOpening) {
            this.isOpening = false
        } else {
            this.hide()
        }
    },

    // API
    pendingFile: null,
    pendingTitle: null,

    reset() {
        this.pendingFile = null,
            this.pendingTitle = null
    }
}))

Alpine.start();
