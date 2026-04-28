/**
 * Formate la taille d'un fichier en bytes vers une représentation lisible
 * @param {number} bytes - Taille en bytes
 * @returns {string} Taille formatée (ex: "1.5 MB")
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Obtient l'extension d'un fichier à partir de son nom
 * @param {string} fileName - Nom du fichier
 * @param {boolean} uppercase - Si true, retourne l'extension en majuscules
 * @returns {string} Extension du fichier
 */
export const getFileExtension = (fileName, { uppercase = false } = {}) => {
  if (!fileName) return '';
  const lastDot = fileName.lastIndexOf('.');
  if (lastDot <= 0) return '';
  const ext = fileName.substring(lastDot + 1);
  return uppercase ? ext.toUpperCase() : ext.toLowerCase();
};

/**
 * Obtient le nom du fichier sans son extension
 * @param {string} fileName - Nom du fichier
 * @returns {string} Nom du fichier sans extension
 */
export const getFilenameWithoutExt = (fileName) => {
  if (!fileName) return '';
  const lastDot = fileName.lastIndexOf('.');
  return lastDot > 0 ? fileName.substring(0, lastDot) : fileName;
};

/**
 * Extrait le nom de fichier depuis un chemin ou une URL
 * @param {string} path - Chemin ou URL du fichier
 * @returns {string} Nom du fichier
 */
export const getFilenameFromPath = (path) => {
  if (!path) return '';
  return path.split('/').pop() || '';
};

/**
 * Construit l'URL d'un fichier externe (EDL)
 * @param {string} attachment - Chemin ou URL du fichier
 * @returns {string} URL complète du fichier
 */
export const getExternalFileUrl = (attachment) => {
  if (!attachment) return '';
  if (attachment.startsWith('/') || attachment.startsWith('http')) {
    return attachment;
  }
  return '/media/' + attachment;
};

/**
 * Obtient le type MIME à partir de l'extension du fichier
 * @param {string} fileName - Nom du fichier
 * @returns {string} Type MIME
 */
export const getMimeType = (fileName) => {
  const extension = getFileExtension(fileName);

  const mimeTypes = {
    pdf: 'application/pdf',
    doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ppt: 'application/vnd.ms-powerpoint',
    pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    txt: 'text/plain',
    rtf: 'application/rtf',
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    gif: 'image/gif',
    svg: 'image/svg+xml',
    mp4: 'video/mp4',
    avi: 'video/x-msvideo',
    mov: 'video/quicktime',
    mp3: 'audio/mpeg',
    wav: 'audio/wav',
    zip: 'application/zip',
    rar: 'application/x-rar-compressed',
    '7z': 'application/x-7z-compressed',
  };

  return mimeTypes[extension] || 'application/octet-stream';
};
