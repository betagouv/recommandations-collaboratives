import Alpine from 'alpinejs'
import { createPopper } from '@popperjs/core';

Alpine.data("User", User)

function User() {
    return {
        popper: null,
        init() {
            console.log('user component ready : ');

            // const popper = createPopper(this.$refs.user, this.$refs.userTooltip)

            console.log(this.$refs.user);

            // this.$refs.userTooltip.style.display = 'none'
            // this.popper = popper
        },

        async show() {
            this.$refs.userTooltip.style.display = 'block'
            await this.popper.update()
        },
    
        hide() {
            this.$refs.userTooltip.style.display = 'none'
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
    }
}
