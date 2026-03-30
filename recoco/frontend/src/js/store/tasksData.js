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
    _subscribers: [],
    _state: {
      tasks: [],
    },
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
    _subscribe(callback) {
      this._subscribers.push(callback);
      return () => {
        this._subscribers = this._subscribers.filter((cb) => cb !== callback);
      };
    },
    setState(newState) {
      this._state = { ...this._state, ...newState };
      this._subscribers.forEach((callback) => callback(this._state));
    },
    _unsubscribe(callback) {
      this._subscribers = this._subscribers.filter((cb) => cb !== callback);
    },
    _notify() {
      this._subscribers.forEach((callback) => callback());
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

      const data = json.data.map((d) =>
        Object.assign(d, {
          // TODO: Virer les UUID
          uuid: generateUUID(),
        })
      );

      this.tasks = data.map((task) => ({ ...task, isLoading: false }));
      this.draftTasks = this.tasks.filter((task) => task.public === false);
      this.validatedTasks = this.tasks.filter((task) => task.public === true);
      this.setState({ tasks: this.tasks });
      return this.tasks;
    },
    getTaskById(id) {
      return this.tasks.find((task) => task.id == id);
    },
    async moveTask(taskId, otherTaskId, { direction }) {
      const params = new URLSearchParams(`${direction}=${otherTaskId}`);
      await api.post(moveTaskUrl(this.projectId, taskId), params, {
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
      });
    },
    async moveTaskFast(taskId, { direction }) {
      const params = new URLSearchParams(`${direction}=true`);
      await api.post(moveTaskUrl(this.projectId, taskId), params, {
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
      });
    },
    // Movement Buttons
    async moveAbove(task, otherTask) {
      await this.moveTask(task.id, otherTask.id, { direction: 'above' });
    },
    async moveBelow(task, otherTask) {
      await this.moveTask(task.id, otherTask.id, { direction: 'below' });
    },
    async moveTop(task) {
      await this.moveTaskFast(task.id, { direction: 'top' });
    },
    async moveBottom(task) {
      await this.moveTaskFast(task.id, { direction: 'bottom' });
    },
    async patchTask(taskId, patch) {
      await api.patch(taskUrl(this.projectId, taskId), patch);
      await this.loadTasks();
    },

    // TODO : To remove ?
    async loadFollowups(taskId) {
      const { data } = await api.get(followupsUrl(this.projectId, taskId));
      return data;
    },
    // TODO : To remove ?
    async loadNotifications(taskId) {
      const { data } = await api.get(
        taskNotificationsUrl(this.projectId, taskId)
      );
      return data;
    },
    async issueFollowup(task, status, comment = '', contact = null) {
      const body = { comment, status };
      if (contact) {
        body.contact = contact.id;
      }

      if (body.status === task.status && body.comment === '') return;

      return await api.post(followupsUrl(this.projectId, task.id), body);
    },
    async editComment(taskId, followupId, { comment, contact }) {
      await api.patch(followupUrl(this.projectId, taskId, followupId), {
        comment,
        contact: contact ? contact.id : null,
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
