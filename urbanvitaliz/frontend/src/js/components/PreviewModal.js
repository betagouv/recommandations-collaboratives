import Alpine from 'alpinejs'

export default function PreviewModal() {
    return {
        get task() {
            return this.$store.previewModal.task
        },
        get followups() {
            return this.$store.previewModal.followups
        },

        async init() {
            await this.$store.tasksData.markAllAsRead(task.id);

            this.followupScrollToLastMessage();
        },
        //TODO use TaskComment()
    }
}

Alpine.data("PreviewModal", PreviewModal)
