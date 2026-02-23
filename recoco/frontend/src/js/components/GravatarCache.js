import Alpine from 'alpinejs';
import md5 from 'md5';
import { LocalStorageMgmt } from '../utils/localStorageMgmt';
import { generateLocalAvatar } from '../utils/avatarUtils';

// Global cache shared across all instances
let globalCache = null;
let gravatarLocalStorage = null;
const pendingChecks = new Set();

function initGlobalCache() {
  if (!gravatarLocalStorage) {
    gravatarLocalStorage = new LocalStorageMgmt({
      dataLabel: 'gravatar-map',
      expiringData: false,
      version: '0.2.0',
    });
    globalCache = gravatarLocalStorage.get() || {};
  }
}

/**
 * Checks Gravatar in background using Image preload.
 */
function checkGravatarInBackground(email, size, name, cacheKey, imgElement) {
  const hash = md5(email.toLowerCase().trim());
  const gravatarUrl = `https://www.gravatar.com/avatar/${hash}?s=${size}&d=404`;

  const testImg = new Image();

  testImg.onload = () => {
    // Gravatar exists, cache and update
    globalCache[cacheKey] = gravatarUrl;
    gravatarLocalStorage.set(globalCache);
    if (imgElement) {
      imgElement.src = gravatarUrl;
    }
    pendingChecks.delete(cacheKey);
  };

  testImg.onerror = () => {
    // No Gravatar, cache local avatar
    globalCache[cacheKey] = generateLocalAvatar(size, name);
    gravatarLocalStorage.set(globalCache);
    pendingChecks.delete(cacheKey);
  };

  testImg.src = gravatarUrl;
}

/**
 * Alpine.js component for Gravatar with local fallback.
 * Shows local avatar immediately, then loads Gravatar in background if available.
 */
Alpine.data('GravatarCache', () => ({
  init() {
    initGlobalCache();
  },

  /**
   * Returns avatar URL. Shows local avatar first, then checks Gravatar in background.
   *
   * @param {string} email - The email address.
   * @param {number} [size=50] - The size of the avatar image.
   * @param {string} [name='Inconnu'] - The name for fallback initials.
   * @returns {string} - The cached avatar URL or local avatar.
   */
  gravatarUrl(email, size = 50, name = 'Inconnu') {
    if (!name || name.trim() === '') name = 'Inconnu';

    const cacheKey = `${email}-${size}`;

    // If we have a cached value, use it immediately
    if (globalCache && globalCache[cacheKey]) {
      return globalCache[cacheKey];
    }

    // Generate local avatar immediately (no broken image)
    const localAvatar = generateLocalAvatar(size, name);

    // Check Gravatar in background (only once per cacheKey)
    if (!pendingChecks.has(cacheKey)) {
      pendingChecks.add(cacheKey);
      // Use setTimeout to avoid blocking render
      setTimeout(() => {
        checkGravatarInBackground(email, size, name, cacheKey, this.$el);
      }, 100);
    }

    return localAvatar;
  },
}));
