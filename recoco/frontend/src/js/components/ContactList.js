import Alpine from 'alpinejs'

function ContactList() {
    return {
        currentHash:null,
        init() {
            const currentUrl = new URL(location.href);
            this.handleChangeCurrentHash(currentUrl)

            window.addEventListener("hashchange", (event) => {
                this.handleChangeCurrentHash(new URL(event.newURL))
            });
        },
        handleChangeCurrentHash(currentUrl) {
            if (currentUrl.hash) {
                this.currentHash = currentUrl.hash
            }
        }
    }
}

Alpine.data("ContactList", ContactList)
