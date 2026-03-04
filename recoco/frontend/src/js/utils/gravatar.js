import md5 from 'md5';
import { generateLocalAvatar } from './avatarUtils';
import { LocalStorageMgmt } from './localStorageMgmt';

// Global cache shared across all usages
let globalCache = null;
let gravatarLocalStorage = null;
const pendingChecks = new Set();

/**
 * Initializes the global cache from localStorage.
 */
export function initGravatarCache() {
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
 * Gets the current cache value for a key.
 */
export function getCachedGravatar(cacheKey) {
  if (!globalCache) {
    initGravatarCache();
  }
  return globalCache[cacheKey];
}

/**
 * Checks Gravatar in background using Image preload.
 * @param {string} email - The email address.
 * @param {number} size - The avatar size.
 * @param {string} name - The name for fallback initials.
 * @param {string} hexColor - The background color for fallback avatar.
 * @param {string} cacheKey - The cache key.
 * @param {HTMLImageElement} [imgElement] - Optional image element to update.
 */
export function checkGravatarInBackground(email, size, name, hexColor, cacheKey, imgElement = null) {
  if (!globalCache) {
    initGravatarCache();
  }

  const hash = md5(email.toLowerCase().trim());
  const gravatarUrl = `https://www.gravatar.com/avatar/${hash}?s=${size}&d=404`;

  const testImg = new Image();

  testImg.onload = () => {
    // Gravatar exists, cache and persist
    globalCache[cacheKey] = gravatarUrl;
    gravatarLocalStorage.set(globalCache);
    // Update specific element if provided
    if (imgElement) {
      imgElement.src = gravatarUrl;
    }
    // Also update any elements with data-gravatar-key attribute
    document.querySelectorAll(`img[data-gravatar-key="${cacheKey}"]`).forEach((img) => {
      img.src = gravatarUrl;
    });
    pendingChecks.delete(cacheKey);
  };

  testImg.onerror = () => {
    // No Gravatar, cache local avatar
    globalCache[cacheKey] = generateLocalAvatar(size, name, hexColor);
    gravatarLocalStorage.set(globalCache);
    pendingChecks.delete(cacheKey);
  };

  testImg.src = gravatarUrl;
}

/**
 * Checks if a Gravatar check is already pending for this key.
 */
export function isPendingCheck(cacheKey) {
  return pendingChecks.has(cacheKey);
}

/**
 * Marks a cache key as having a pending check.
 */
export function addPendingCheck(cacheKey) {
  pendingChecks.add(cacheKey);
}

/**
 * Returns avatar URL. Shows local avatar first, then checks Gravatar in background.
 *
 * @param {string} email - The email address.
 * @param {number} [size=50] - The size of the avatar image.
 * @param {string} [name='Inconnu'] - The name for fallback initials.
 * @param {string} [hexColor='DDDDDD'] - The background color for fallback avatar.
 * @returns {string} - The cached avatar URL or local avatar.
 */
export function gravatar_url(
  email,
  size = 50,
  name = 'Inconnu',
  hexColor = 'DDDDDD',
  imgElement = null
) {
  if (!name || name.trim() === '') name = 'Inconnu';
  hexColor = hexColor.replace('#', '');

  const cacheKey = `${email}-${size}`;

  // If we have a cached value, use it immediately
  const cached = getCachedGravatar(cacheKey);
  if (cached) {
    return cached;
  }

  const localAvatar = generateLocalAvatar(size, name, hexColor);

  // Check Gravatar in background (only once per cacheKey)
  if (!isPendingCheck(cacheKey)) {
    addPendingCheck(cacheKey);
    setTimeout(() => {
      checkGravatarInBackground(email, size, name, hexColor, cacheKey, imgElement);
    }, 100);
  }

  return localAvatar;
}
