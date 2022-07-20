import Alpine from 'alpinejs'

function Spinner() {
    return {
        get isLoading() {
            return this.$store.app.isLoading
        }
    }
}

Alpine.data("Spinner", Spinner)
