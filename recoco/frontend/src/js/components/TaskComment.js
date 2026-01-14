//TODO edit a task comment component
import Alpine from 'alpinejs';
import { ToastType } from '../models/toastType';

export default function TaskComment() {
  return {
    comment: {
      text: '',
    },
    isEditing: false,

    async handleEditComment(task) {
      this.isEditing = true;
      task.isLoading = true;
      try {
        await this.$store.tasksData.patchTask(task.id, {
          content: this.comment.text,
        });
        await this.$store.tasksView.updateViewWithTask(task.id);
        task.isLoading = false;
        this.isEditing = false;
      } catch (error) {
        console.error(error);
        this.$store.app.displayToastMessage({
          message: `Erreur lors de la modification du commentaire`,
          timeout: 5000,
          type: ToastType.error,
        });
        task.isLoading = false;
        this.isEditing = false;
      }
    },
  };
}

Alpine.data('TaskComment', TaskComment);
