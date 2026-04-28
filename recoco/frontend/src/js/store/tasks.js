import Alpine from 'alpinejs';
import _ from 'lodash';

document.addEventListener('alpine:init', () => {
  Alpine.store('tasksView', {
    displayedTasks: [],
    async init() {
      try {
        await Alpine.store('tasksData').loadTasks();
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
  });

  Alpine.store('taskModal', {
    deleteModalHandle: null,
    onDeleteClick(task) {
      this.currentTask = task;
      this.deleteModalHandle.show();
    },
  });
});

export default Alpine.store('tasksView');
