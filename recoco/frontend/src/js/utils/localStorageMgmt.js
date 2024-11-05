/**
 * Class representing local storage management with optional expiration.
 */
export class LocalStorageMgmt {
  /**
   * Create a LocalStorageMgmt instance.
   * @param {Object} options - The options for local storage management.
   * @param {string} [options.dataLabel='data-label'] - The label for the data.
   * @param {string|null} [options.tag=null] - An recommended tag to append to the data label (ex="Recoco_portal").
   * @param {boolean} [options.expiringData=false] - Whether the data should expire.
   * @param {number|null} [options.expiringTime=null] - The expiration time in hours.
   */
  constructor({
    dataLabel = 'data-label',
    tag = null,
    expiringData = false,
    expiringTime = null,
  }) {
    this.version = '0.1.0';
    this.fullDataLabel = `${dataLabel}${tag ? `-${tag}` : ''}`;
    this.expiringData = expiringData;
    this.expiringTime = expiringTime;
    this.data = null;
    this.expireAt = null;

    Date.prototype.addHours = function (h) {
      this.setTime(this.getTime() + h * 60 * 60 * 1000);
      return this;
    };
  }

  /**
   * Set data in local storage.
   * @param {*} data - The data to be stored.
   */
  set(data) {
    const savingObject = {
      version: this.version,
      data,
    };
    if (this.expiringData) {
      savingObject.expireAt = new Date().addHours(this.expiringTime);
    }

    localStorage.setItem(this.fullDataLabel, JSON.stringify(savingObject));
  }

  /**
   * Get data from local storage.
   * @returns {*} The stored data or null if not found or expired.
   */
  get() {
    if (this.data) {
      if (!this.expiringData) {
        return this.data;
      }
      const now = new Date().valueOf();
      if (this.expireAt <= now) {
        return null;
      }
      return this.data;
    }

    const localStorageData = localStorage.getItem(this.fullDataLabel);
    if (!localStorageData) {
      return null;
    }
    if (this.version !== JSON.parse(localStorageData).version) {
      return null;
    }
    const savedData = JSON.parse(localStorageData);
    this.data = savedData.data;

    if (!this.expiringData) {
      return this.data;
    }

    const expireAt = new Date(savedData?.expireAt).valueOf();
    const now = new Date().valueOf();
    if (expireAt <= now) {
      return null;
    }

    this.expireAt = savedData.expireAt;
    return this.data;
  }

  /**
   * Reset the stored data by removing it from local storage.
   */
  reset() {
    localStorage.removeItem(this.fullDataLabel);
    this.data = null;
  }
}
