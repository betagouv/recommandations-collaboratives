import Alpine from 'alpinejs';
import md5 from 'md5';
import { LocalStorageMgmt } from '../utils/localStorageMgmt';

/**
 * Alpine.js component for caching Gravatar URLs in local storage.
 *
 * @param {string} currentSiteName - The name of the current site, used as a tag for local storage.
 * @returns {object} - The Alpine.js component object.
 *
 * @property {object|null} cache - The cache object for storing Gravatar URLs.
 * @property {string} currentSiteName - The sanitized name of the current site.
 * @property {object|null} gravatarLocalStorage - The local storage management object.
 *
 */
Alpine.data('GravatarCache', (currentSiteName) => ({
  cache: null,
  currentSiteName: currentSiteName.replaceAll(' ', '_'),
  gravatarLocalStorage: null,
  init() {
    this.initLocalStorage();
    this.cache = this.gravatarLocalStorage.get();
  },

  initLocalStorage() {
    this.gravatarLocalStorage = new LocalStorageMgmt({
      dataLabel: 'gravatar-map',
      tag: this.currentSiteName,
      expiringData: false,
    });
  },

  /**
   * Generates a Gravatar URL for the given email and caches it.
   *
   * @param {string} email - The email address to generate the Gravatar for.
   * @param {number} [size=50] - The size of the Gravatar image.
   * @param {string} [name='Inconnu'] - The fallback name to use if the email does not have a Gravatar.
   * @returns {string} - The generated Gravatar URL.
   */
  gravatarUrl(email, size = 50, name = 'Inconnu') {
    if (!this.cache) {
      this.cache = {};
    }
    if (this.cache[email]) {
      return this.cache[email];
    }
    if (name.trim() == '') name = 'Inconnu';

    const hash = md5(email);
    const encoded_fallback_uri = encodeURIComponent(
      `https://ui-avatars.com/api/${name}/${size}`
    );

    this.cache[email] =
      `https://www.gravatar.com/avatar/${hash}?s=50&d=${encoded_fallback_uri}`;

    this.gravatarLocalStorage.set(this.cache);

    return this.cache[email];
  },
}));
