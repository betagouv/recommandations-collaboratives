import Alpine from 'alpinejs';
import api, { followupsUrl, taskNotificationsUrl } from '../utils/api';
import { Modal } from 'bootstrap';

document.addEventListener('alpine:init', () => {
  Alpine.store('previewModal', {
    taskId: null,
    handle: null,
    followups: null,

    isPaginated: false,
    index: null,
    scrollY: null,

    get projectId() {
      return Alpine.store('djangoData').projectId;
    },

    get newTasks() {
      return Alpine.store('tasksData').newTasks;
    },

    async init() {
      const element = document.getElementById('task-modal');
      const body = document.querySelector('body');
      this.handle = new Modal(element);

      const cleanup = async () => {
        location.hash = '';
        await this.setTaskIsVisited();

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
        this.open(parseInt(urlFromHash[1], 10));
      }
    },
    open(taskId) {
      this.isPaginated = false;
      this.setLocation(taskId);
      this.handle.show();
    },

    openWithPagination() {
      this.isPaginated = true;
      this.index = 0;
      this.setLocation(this.newTasks[this.index].id);
      this.handle.show();
    },

    next() {
      if (this.index + 1 < this.newTasks.length) {
        this.index++;
        this.setLocation(this.newTasks[this.index].id);
      }
    },

    previous() {
      if (this.index > 0) {
        this.index--;
        this.setLocation(this.newTasks[this.index].id);
      }
    },

    setLocation(taskId) {
      location.hash = `#action-${taskId}`;
    },
    async loadFollowups() {
      const { data } = await api.get(followupsUrl(this.projectId, this.taskId));
      Alpine.store('tasksData').markAllAsRead(this.taskId);
      await Alpine.store('tasksView').updateView();
      this.followups = data;
    },
    async loadNotifications() {
      const { data } = await api.get(
        taskNotificationsUrl(this.projectId, this.taskId)
      );
      this.notifications = data;
    },
    async setTaskIsVisited() {
      if (!Alpine.store('djangoData').isAdvisor) {
        await Alpine.store('tasksData').patchTask(this.taskId, {
          visited: true,
        });
        await Alpine.store('tasksView').updateView();
      }
    },
  });
});

export default Alpine.store('previewModal');
