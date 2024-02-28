import Alpine from 'alpinejs'

Alpine.store('app', {
    isLoading: false,
    notification: {
        isOpen: false,
        message: ''
    }
})

export default Alpine.store('app')
