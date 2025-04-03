//TODO edit a task comment component
import Alpine from 'alpinejs';

export default function TaskComment() {
  return {
    comment: {
      text: '',
    },
    isEditing: false,

    async handleEditComment(task) {
      this.isEditing = true;
      task.isLoading = true;
      await this.$store.tasksData.patchTask(task.id, {
        content: this.comment.text,
      });
      await this.$store.tasksView.updateViewWithTask(task.id);
      task.isLoading = false;
      this.isEditing = false;
    },
  };
}

Alpine.data('TaskComment', TaskComment);
