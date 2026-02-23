import md5 from 'md5';
import { generateLocalAvatar } from './avatarUtils';

const cache = {};
const pendingChecks = new Set();

/**
 * Checks Gravatar in background using Image preload.
 */
function checkGravatarInBackground(email, size, name, hexColor, cacheKey) {
  const hash = md5(email.toLowerCase().trim());
  const gravatarUrl = `https://www.gravatar.com/avatar/${hash}?s=${size}&d=404`;

  const testImg = new Image();

  testImg.onload = () => {
    // Gravatar exists, cache it
    cache[cacheKey] = gravatarUrl;
    // Update any existing images with this cache key
    document.querySelectorAll(`img[data-gravatar-key="${cacheKey}"]`).forEach((img) => {
      img.src = gravatarUrl;
    });
    pendingChecks.delete(cacheKey);
  };

  testImg.onerror = () => {
    // No Gravatar, cache local avatar
    cache[cacheKey] = generateLocalAvatar(size, name, hexColor);
    pendingChecks.delete(cacheKey);
  };

  testImg.src = gravatarUrl;
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
  hexColor = 'DDDDDD'
) {
  if (!name || name.trim() === '') name = 'Inconnu';
  hexColor = hexColor.replace('#', '');

  const cacheKey = `${email}-${size}`;

  // If we have a cached value, use it immediately
  if (cache[cacheKey]) {
    return cache[cacheKey];
  }

  const localAvatar = generateLocalAvatar(size, name, hexColor);

  // Check Gravatar in background (only once per cacheKey)
  if (!pendingChecks.has(cacheKey)) {
    pendingChecks.add(cacheKey);
    setTimeout(() => {
      checkGravatarInBackground(email, size, name, hexColor, cacheKey);
    }, 100);
  }

  return localAvatar;
}
