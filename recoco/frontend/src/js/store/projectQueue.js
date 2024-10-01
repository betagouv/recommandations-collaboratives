import Alpine from 'alpinejs';

/**
 * Alpine.js store for managing a project queue.
 *
 * @store projectQueue
 * @property {Array} queue - The array holding the project IDs in the queue.
 * @property {number} maxQueueSize - The maximum size of the queue.
 *
 * @method init - Initializes the queue from localStorage if available, otherwise sets it to an empty array.
 * @method addCurrentProjectId - Adds a project ID to the front of the queue, ensuring no duplicates and maintaining the max queue size.
 * @param {string} projectId - The ID of the project to add to the queue.
 *
 * @method pop - Removes the last project ID from the queue.
 *
 * @method get - Returns the current queue.
 */
Alpine.store('projectQueue', {
  queue: new Array(),
  maxQueueSize: 4,
  init() {
    const projectQueue = localStorage.getItem('projectQueue');
    if (projectQueue) {
      this.queue = JSON.parse(projectQueue);
    } else {
      this.queue = new Array();
    }
  },

  addCurrentProjectId(projectId) {
    this.queue.unshift(projectId);
    this.queue = [...new Set(this.queue)];
    if (this.queue.length > this.maxQueueSize) {
      this.pop();
    }
    localStorage.setItem('projectQueue', JSON.stringify(this.queue));
  },

  pop() {
    this.queue.pop();
    localStorage.setItem('projectQueue', JSON.stringify(this.queue));
  },

  get() {
    return this.queue;
  },
});

export default Alpine.store('projectQueue');
