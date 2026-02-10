import Alpine from 'alpinejs';
import md5 from 'md5';
import { LocalStorageMgmt } from '../utils/localStorageMgmt';

// Global cache shared across all instances
let globalCache = null;
let gravatarLocalStorage = null;
const pendingChecks = new Set();

function initGlobalCache() {
  if (!gravatarLocalStorage) {
    gravatarLocalStorage = new LocalStorageMgmt({
      dataLabel: 'gravatar-map',
      expiringData: false,
    });
    globalCache = gravatarLocalStorage.get() || {};
  }
}

/**
 * Extracts initials from a name (max 2 characters).
 */
function getInitials(name) {
  if (!name || name.trim() === '') return '?';

  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Generates a local SVG avatar as a data URI.
 */
function generateLocalAvatar(size, name) {
  const initials = getInitials(name);
  const bgColor = '#DDDDDD';
  const textColor = '#000000';
  const fontSize = size * 0.4;

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><rect width="100%" height="100%" fill="${bgColor}"/><text x="50%" y="50%" dy="0.35em" fill="${textColor}" font-family="system-ui, -apple-system, sans-serif" font-size="${fontSize}" font-weight="600" text-anchor="middle">${initials}</text></svg>`;

  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
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
