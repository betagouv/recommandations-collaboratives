import Alpine from "../utils/globals"

document.addEventListener('alpine:init', () => {
    Alpine.store('editor', {
        currentMessage: "",
        isEditing:false,
        isSubmitted:false,
        clearCurrentMessage() {
            this.currentMessage = ""
        },
        setIsSubmitted(isSubmitted) {
            this.isSubmitted = isSubmitted
        }
    })
})
