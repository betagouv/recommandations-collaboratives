import Alpine from 'alpinejs';

import { renderMarkdown } from '../utils/markdown';
import { truncate } from '../utils/taskStatus';

export default function Task(currentTask) {
  return {
    currentTask: null,
    renderMarkdown,
    truncate,
    init() {
      this.currentTask = currentTask;
    },
    getTaskColor(task) {
      if (!task.public && task.content === '') {
        return '-orange';
      } else if (!task.public) {
        return '-yellow';
      } else {
        return '-grey-light';
      }
    },
  };
}

Alpine.data('Task', Task);
