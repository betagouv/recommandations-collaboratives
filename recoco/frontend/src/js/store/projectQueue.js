import Alpine from 'alpinejs';

/**
 * Alpine.js store for managing a project queue.
 *
 * @store projectQueue
 * @property {Array} queue - The array holding the project IDs in the queue.
 * @property {number} maxQueueSize - The maximum size of the queue.
 * @property {number} queueVersion - Version of the queue (in case of invalidation).
 *
 * @param {number} projectId - The ID of the project to add to the queue.
 * @param {string} projectName - Project name to add to the queue.
 * @param {string} communeName - Project commune name to add to the queue.
 * @param {string} communeInsee - Project commune INSEE to add to the queue.
 *
 * @method init - Initializes the queue from localStorage if available, otherwise sets it to an empty array.
 * @method addCurrentProjectId - Adds a project ID to the front of the queue, ensuring no duplicates and maintaining the max queue size.
 * @method pop - Removes the last project ID from the queue.
 * @method refreshQueue - Refresh the queue in localstorage.
 * @method get - Returns the current queue.
 *
 */
Alpine.store('projectQueue', {
  queue: new Array(),
  maxQueueSize: 5,
  queueVersion: 0.1,
  init() {
    const { projectQueue, version } = JSON.parse(
      localStorage.getItem('projectQueue') || '{}'
    );
    if (projectQueue) {
      this.queue = projectQueue;
      if (version !== this.queueVersion) {
        this.queue = new Array();
        this.refreshQueue();
      }
    } else {
      this.queue = new Array();
    }
  },

  addCurrentProjectId(projectId, projectName, communeName, communeInsee, orgName) {
    this.queue = this.queue.filter((project) => project.id !== projectId);
    this.queue.unshift({
      id: projectId,
      name: projectName,
      org_name: orgName,
      commune: {
        name: communeName,
        insee: communeInsee,
      },
    });
    if (this.queue.length > this.maxQueueSize) {
      this.pop();
    }
    this.refreshQueue();
  },

  pop() {
    this.queue.pop();
    this.refreshQueue();
  },
  refreshQueue() {
    localStorage.setItem(
      'projectQueue',
      JSON.stringify({ projectQueue: this.queue, version: this.queueVersion })
    );
  },

  get() {
    return this.queue;
  },
});

export default Alpine.store('projectQueue');
