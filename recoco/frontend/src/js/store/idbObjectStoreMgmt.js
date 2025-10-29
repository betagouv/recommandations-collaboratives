import Alpine from 'alpinejs';
import { openDB } from 'idb';

Alpine.store('idbObjectStoreMgmt', {
  async init() {
    const db = await openDB('Conversations', 2, {
      upgrade(db, oldVersion) {
        // Delete the old store if it exists
        if (db.objectStoreNames.contains('files')) {
          db.deleteObjectStore('files');
        }
        // Create the new store with autoIncrement
        const store = db.createObjectStore('files', {
          keyPath: 'id',
          autoIncrement: true,
        });
      },
    });
    const transaction = db.transaction(['files'], 'readwrite');
    this.store = transaction.objectStore('files');
  },
  async add(value) {
    return await this.store.add(value);
  },
  async getAll() {
    return await this.store.getAll();
  },
  async delete(id) {
    return await this.store.delete(id);
  },
});

export default Alpine.store('idbObjectStoreMgmt');
