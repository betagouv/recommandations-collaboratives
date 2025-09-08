import Alpine from 'alpinejs';
import _ from 'lodash';

document.addEventListener('alpine:init', () => {
  Alpine.store('tasksView', {
    displayedTasks: [],
    currentView: 'inline',
    async init() {
      try {
        const tasksLoaded = await Alpine.store('tasksData').loadTasks();
        for (const task of tasksLoaded) {
          console.log('tasksLoaded in tasksView init:', task);
          if (task.status != 0) {
           this.currentView = 'kanban';
          }
        }
      } catch (error) {
        throw new Error('Error loading tasks while view initialization : ' + error);
      }
    },
    async updateViewWithTask(taskId) {
      try {
        const updatedTasks = await Alpine.store('tasksData').loadTasks();
        const updatedTask = updatedTasks.find((task) => task.id === taskId);
        this.displayedTasks = this.displayedTasks.map((task) =>
          task.id === taskId ? updatedTask : task
        );
      } catch (error) {
        throw new Error('Error loading tasks while view update : ' + error);
      }
    },
    async updateView() {
      try {
        const tasksLoaded = await Alpine.store('tasksData').loadTasks();
        this.displayedTasks = _.orderBy(tasksLoaded, ['order'], ['asc']);
      } catch (error) {
        throw new Error('Error loading tasks while view update : ' + error);
      }
    },
    findById(taskId) {
      return this.displayedTasks.find((task) => task.id === taskId);
    },
    findLast() {
      return this.displayedTasks.slice(-1)[0];
    },
    findFirst() {
      return this.displayedTasks[0];
    },
    switchView() {
      this.currentView === 'inline'
        ? (this.currentView = 'kanban')
        : (this.currentView = 'inline');
    },
  });

  Alpine.store('taskModal', {
    currentTask: null,

    previewModalHandle: null,
    deleteModalHandle: null,
    feedbackModalHandle: null,
    feedbackModalStatus: null,

    onPreviewClick(task) {
      this.currentTask = task;
      this.previewModalHandle.show();
    },
    onDeleteClick(task) {
      this.currentTask = task;
      this.deleteModalHandle.show();
    },
    onFeedbackClick(task, status) {
      this.currentTask = task;
      this.feedbackModalStatus = status;
      this.feedbackModalHandle.show();
    },
  });
});

export default Alpine.store('tasksView');
