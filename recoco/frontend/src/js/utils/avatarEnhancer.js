/**
 * Avatar Enhancer
 *
 * Intercepts images with gravatar.com URLs that use ui-avatars.com as fallback.
 * Replaces them with local SVG avatars and checks gravatar in background.
 *
 * Works automatically with Django's {% gravatar_url %} template tag.
 */

// Cache for gravatar check results: hash -> gravatarUrl or null
const gravatarCache = new Map();
// Pending checks to avoid duplicate requests
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
function generateLocalAvatar(size, name = '?') {
  const initials = getInitials(name);
  const bgColor = '#DDDDDD';
  const textColor = '#000000';
  const fontSize = Math.round(size * 0.4);

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><rect width="100%" height="100%" fill="${bgColor}"/><text x="50%" y="50%" dy="0.35em" fill="${textColor}" font-family="system-ui, -apple-system, sans-serif" font-size="${fontSize}" font-weight="600" text-anchor="middle">${initials}</text></svg>`;

  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

/**
 * Parses a gravatar URL and extracts hash, size, and fallback name.
 * Returns null if not a gravatar URL with ui-avatars fallback.
 */
function parseGravatarUrl(url) {
  if (!url) return null;

  // Match gravatar.com URLs
  const gravatarMatch = url.match(
    /(?:https?:)?\/\/(?:www\.|secure\.)?gravatar\.com\/avatar\/([a-f0-9]+)\?(.+)/i
  );
  if (!gravatarMatch) return null;

  const hash = gravatarMatch[1];
  const params = new URLSearchParams(gravatarMatch[2]);

  // Check if fallback is ui-avatars.com
  const fallback = params.get('d');
  if (!fallback || !fallback.includes('ui-avatars.com')) return null;

  // Extract size
  const size = parseInt(params.get('s') || '50', 10);

  // Try to extract name from ui-avatars URL
  let name = '?';
  try {
    const decodedFallback = decodeURIComponent(fallback);
    // ui-avatars.com/api/{name}/{size} or ui-avatars.com/api/{name}/{size}/{bg}/{fg}
    const nameMatch = decodedFallback.match(/ui-avatars\.com\/api\/([^/]+)/);
    if (nameMatch) {
      name = decodeURIComponent(nameMatch[1]);
    }
  } catch {
    // Ignore decoding errors
  }

  return { hash, size, name };
}

/**
 * Checks if gravatar exists and updates the image.
 */
function checkGravatar(img, hash, size) {
  const cacheKey = `${hash}-${size}`;

  // If already cached, apply immediately
  if (gravatarCache.has(cacheKey)) {
    const cachedUrl = gravatarCache.get(cacheKey);
    if (cachedUrl) {
      img.src = cachedUrl;
    }
    // If null, keep the local avatar (already set)
    return;
  }

  // If already checking, just wait
  if (pendingChecks.has(cacheKey)) {
    return;
  }

  pendingChecks.add(cacheKey);

  // Check gravatar with d=404
  const testUrl = `https://www.gravatar.com/avatar/${hash}?s=${size}&d=404`;
  const testImg = new Image();

  testImg.onload = () => {
    // Gravatar exists
    gravatarCache.set(cacheKey, testUrl);
    pendingChecks.delete(cacheKey);

    // Update all images with this cache key
    document
      .querySelectorAll(`img[data-gravatar-hash="${hash}"]`)
      .forEach((el) => {
        el.src = testUrl;
      });
  };

  testImg.onerror = () => {
    // No gravatar, cache null
    gravatarCache.set(cacheKey, null);
    pendingChecks.delete(cacheKey);
  };

  testImg.src = testUrl;
}

/**
 * Processes an image element with a gravatar URL.
 */
function processGravatarImage(img) {
  // Skip if already processed
  if (img.dataset.gravatarProcessed) return;

  const parsed = parseGravatarUrl(img.src);
  if (!parsed) return;

  const { hash, size, name } = parsed;

  // Mark as processed and store hash for later updates
  img.dataset.gravatarProcessed = 'true';
  img.dataset.gravatarHash = hash;

  // Replace with local avatar immediately
  img.src = generateLocalAvatar(size, name);

  // Check gravatar in background
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => checkGravatar(img, hash, size));
  } else {
    setTimeout(() => checkGravatar(img, hash, size), 100);
  }
}

/**
 * Enhances all gravatar images in a container.
 */
export function enhanceAvatars(container = document) {
  // Find all images (we'll filter by URL)
  const images = container.querySelectorAll('img');
  images.forEach((img) => {
    // Process images with gravatar URLs
    if (
      img.src &&
      img.src.includes('gravatar.com') &&
      img.src.includes('ui-avatars.com')
    ) {
      processGravatarImage(img);
    }
  });
}

/**
 * Initialize avatar enhancer.
 * Runs on page load and sets up a MutationObserver for dynamic content.
 */
export function initAvatarEnhancer() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => enhanceAvatars());
  } else {
    enhanceAvatars();
  }

  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
          // Check if the node itself is an image
          if (node.tagName === 'IMG') {
            processGravatarImage(node);
          }
          // Check for images inside the node
          if (node.querySelectorAll) {
            enhanceAvatars(node);
          }
        }
      });
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}
