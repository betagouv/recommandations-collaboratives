//TODO edit a task comment component
import Alpine from 'alpinejs'

export default function TaskComment() {
    return {
        isEditing: false,
        async handleEditComment(comment, task) {
            this.isEditing = true
            task.isLoading = true
            await this.$store.tasksData.patchTask(task.id, { content: comment })
            await this.$store.tasksView.updateViewWithTask(task.id)
            task.isLoading = false
            this.isEditing = false
        }
    }
}

Alpine.data("TaskComment", TaskComment)
