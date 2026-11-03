/**
 * Shared utilities for avatar generation.
 */

/**
 * Extracts initials from a name (max 2 characters).
 * @param {string} name - The full name.
 * @returns {string} - The initials (1-2 uppercase characters) or '?' if invalid.
 */
export function getInitials(name) {
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
 * @param {number} size - The size of the avatar in pixels.
 * @param {string} [name='?'] - The name to extract initials from.
 * @param {string} [hexColor='DDDDDD'] - The background color (hex without #).
 * @returns {string} - The SVG avatar as a data URI.
 */
export function generateLocalAvatar(size, name = '?', hexColor = 'DDDDDD') {
  const initials = getInitials(name);
  const bgColor = `#${hexColor.replace('#', '')}`;
  const textColor = '#000000';
  const fontSize = Math.round(size * 0.4);

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><rect width="100%" height="100%" fill="${bgColor}"/><text x="50%" y="50%" dy="0.35em" fill="${textColor}" font-family="system-ui, -apple-system, sans-serif" font-size="${fontSize}" font-weight="600" text-anchor="middle">${initials}</text></svg>`;

  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}
