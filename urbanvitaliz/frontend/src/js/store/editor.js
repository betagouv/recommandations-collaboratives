import Alpine from "../utils/globals"

document.addEventListener('alpine:init', () => {
    Alpine.store('editor', {
        currentMessage: "",
        isEditing:false,
        clearCurrentMessage() {
            this.currentMessage = ""
        }
    })
})
