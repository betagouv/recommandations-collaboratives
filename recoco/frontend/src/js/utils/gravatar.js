import md5 from 'md5';

const cache = {};
const pendingChecks = new Set();

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
function generateLocalAvatar(size, name, hexColor = 'DDDDDD') {
  const initials = getInitials(name);
  const bgColor = `#${hexColor.replace('#', '')}`;
  const textColor = '#000000';
  const fontSize = size * 0.4;

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><rect width="100%" height="100%" fill="${bgColor}"/><text x="50%" y="50%" dy="0.35em" fill="${textColor}" font-family="system-ui, -apple-system, sans-serif" font-size="${fontSize}" font-weight="600" text-anchor="middle">${initials}</text></svg>`;

  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

/**
 * Checks Gravatar in background using Image preload.
 */
function checkGravatarInBackground(email, size, name, hexColor, cacheKey) {
  if (email == 'anouk.jeanneau@beta.gouv.fr') debugger;
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
  if (email == 'anouk.jeanneau@beta.gouv.fr') debugger;
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
