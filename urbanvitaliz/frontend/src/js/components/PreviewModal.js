import Alpine from 'alpinejs'

export default function PreviewModal() {
    return {
        get taskId() {
            return this.$store.previewModal.taskId
        },
        get task() {
            return this.$store.tasksData.getTaskById(this.taskId)
        },
        get followups() {
            return this.$store.previewModal.followups
        },

        async refresh() {
            this.followupScrollToLastMessage();
        },
        
        //TODO use TaskComment()
    }
}

Alpine.data("PreviewModal", PreviewModal)
