import Alpine from 'alpinejs';
import api, {
  tasksUrl,
  taskUrl,
  moveTaskUrl,
  followupsUrl,
  followupUrl,
  taskNotificationsUrl,
  markTaskNotificationsAsReadUrl,
} from '../utils/api';
import { generateUUID } from '../utils/uuid';
import { NO_TOPICS } from '../config/tasks';

document.addEventListener('alpine:init', () => {
  Alpine.store('tasksData', {
    get projectId() {
      return Alpine.store('djangoData').projectId;
    },

    tasks: [],
    draftTasks: [],
    validatedTasks: [],
    topics: [],
    async init() {
      await this.loadTasks();
      Alpine.store('tasksView').displayedTasks = this.tasks;
      // NOTE : rollback tasks topic display
      // this.extractTopicFromTasks();
    },
    get newTasks() {
      return this.tasks.filter((task) => task.visited === false && task.public);
    },
    extractTopicFromTasks() {
      let topics = [];

      this.tasks.forEach((task) => {
        if (task.topic) {
          if (!topics.find((topic) => topic === task.topic.name)) {
            topics.push(task.topic.name);
          }
        }
      });

      topics.push(NO_TOPICS);

      this.topics = topics;
    },
    async loadTasks() {
      const json = await api.get(tasksUrl(this.projectId));

      const data = json.data.results.map((d) =>
        Object.assign(d, {
          // TODO: Virer les UUID
          uuid: generateUUID(),
        })
      );

      this.tasks = data.map((task) => ({ ...task, isLoading: false }));
      this.draftTasks = this.tasks.filter((task) => task.public === false);
      this.validatedTasks = this.tasks.filter((task) => task.public === true);

      return this.tasks;
    },
    getTaskById(id) {
      return this.tasks.find((task) => task.id == id);
    },
    async moveTask(taskId, otherTaskId, below) {
      const params = new URLSearchParams(
        `${below ? 'below' : 'above'}=${otherTaskId}`
      );
      await api.post(moveTaskUrl(this.projectId, taskId), params, {
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
      });
    },
    // Movement Buttons
    async moveAbove(task, otherTask) {
      await this.moveTask(task.id, otherTask.id);
    },
    async moveBelow(task, otherTask) {
      await this.moveTask(task.id, otherTask.id, true);
    },
    async patchTask(taskId, patch) {
      await api.patch(taskUrl(this.projectId, taskId), patch);
      await this.loadTasks();
    },

    // TODO : Plus tard
    async loadFollowups(taskId) {
      const { data } = await api.get(followupsUrl(this.projectId, taskId));
      return data;
    },
    async loadNotifications(taskId) {
      const { data } = await api.get(
        taskNotificationsUrl(this.projectId, taskId)
      );
      return data;
    },
    async issueFollowup(task, status, comment = '') {
      const body = { comment, status };

      if (body.status === task.status && body.comment === '') return;

      await api.post(followupsUrl(this.projectId, task.id), body);
    },
    async editComment(taskId, followupId, comment) {
      await api.patch(followupUrl(this.projectId, taskId, followupId), {
        comment,
      });
    },
    async markAllAsRead(taskId) {
      await api.post(
        markTaskNotificationsAsReadUrl(this.projectId, taskId),
        {}
      );
    },
  });
});

export default Alpine.store('tasksData');
