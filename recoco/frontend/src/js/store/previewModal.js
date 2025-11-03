import Alpine from 'alpinejs';
import api, {
  markTaskNotificationAsVisited,
  taskNotificationsUrl,
} from '../utils/api';
import { Modal } from 'bootstrap';

document.addEventListener('alpine:init', () => {
  Alpine.store('previewModal', {
    taskId: null,
    currentTask: null,
    handle: null,

    isPaginated: false,
    index: null,
    scrollY: null,

    notifications: [],

    contact: null,

    get projectId() {
      return Alpine.store('djangoData').projectId;
    },

    get newTasks() {
      return Alpine.store('tasksData').newTasks;
    },

    async init() {
      const element = document.getElementById('task-modal');
      if (!element) return;

      const body = document.querySelector('body');
      this.handle = new Modal(element);

      const cleanup = () => {
        location.hash = '';
        Alpine.store('tasksView').updateView();
        // Restore scroll position
        window.scrollTo(0, this.scrollY);
      };
      element.addEventListener('show.bs.modal', () => {
        // Save scroll position
        if (body) {
          this.scrollY = window.scrollY;
        }
      });

      element.addEventListener('hidePrevented.bs.modal', cleanup);
      element.addEventListener('hidden.bs.modal', cleanup);

      window.addEventListener('hashchange', () => {
        if (location.hash === '') {
          this.handle.hide();
          this.taskId = null;
        } else {
          const urlFromHash = location.hash.match(/^#action-(\d+)/);
          if (urlFromHash) {
            this.taskId = parseInt(urlFromHash[1], 10);
          }
        }
      });
      const urlFromHash = location.hash.match(/^#action-(\d+)/);
      if (urlFromHash) {
        this.taskId = parseInt(urlFromHash[1], 10);
        if (this.newTasks.length === 0) {
          const tasks = await Alpine.store('tasksData').loadTasks();
          this.open(
            tasks
              .filter((task) => task.public)
              .find((task) => task.id === this.taskId)
          );
        } else {
          this.open(this.newTasks.find((task) => task.id === this.taskId));
        }
      }
    },
    open(task) {
      if (!task) {
        throw new Error('Error while open task modal - task not found');
      }
      this.isPaginated = false;
      this.setLocation(task.id);
      this.visitTask(task);
      this.handle.show();
    },

    openWithPagination() {
      this.isPaginated = true;
      this.index = 0;
      this.setLocation(this.newTasks[this.index].id);
      this.visitTask(this.newTasks[this.index]);
      this.handle.show();
    },

    next() {
      if (this.index + 1 < this.newTasks.length) {
        this.index++;
        this.setLocation(this.newTasks[this.index].id);
        this.visitTask(this.newTasks[this.index]);
      }
    },

    previous() {
      if (this.index > 0) {
        this.index--;
        this.setLocation(this.newTasks[this.index].id);
        this.visitTask(this.newTasks[this.index]);
      }
    },
    visitTask(task) {
      this.currentTask = task;
      this.taskId = task.id;

      if (!this.currentTask.visited) {
        this.setTaskIsVisited();
      }
    },

    setLocation(taskId) {
      location.hash = `#action-${taskId}`;
    },
    async loadNotifications() {
      const { data } = await api.get(
        taskNotificationsUrl(this.projectId, this.taskId)
      );
      this.notifications = data;
    },
    async setTaskIsVisited() {
      if (!Alpine.store('djangoData').isAdvisor) {
        await api.post(
          markTaskNotificationAsVisited(this.projectId, this.taskId)
        );
      }
    },
  });
});

export default Alpine.store('previewModal');
