import Alpine from 'alpinejs';
import {
  getFileExtension,
  getFilenameWithoutExt,
  getFilenameFromPath,
  getExternalFileUrl,
} from '../utils/file.js';

/**
 * SharedContentsFileCard - Alpine component for file cards in shared contents panel
 * Handles both internal files (conversation attachments) and external files (EDL)
 *
 * @param {Object} config
 * @param {boolean} config.isExternal - If true, uses external file URL construction
 */
Alpine.data('SharedContentsFileCard', (config = {}) => ({
  isExternal: config.isExternal || false,
  file: config.file || null,

  /**
   * Get the full filename from the file object
   * Supports multiple property names (filename, name, attachment)
   */
  getFullFilename() {
    const file = this.file;
    if (!file) return 'Fichier';

    if (file.filename) return file.filename;
    if (file.name) return file.name;
    if (file.attachment) return getFilenameFromPath(file.attachment);

    return 'Fichier';
  },

  /**
   * Get filename without extension for display
   */
  getFilenameWithoutExt() {
    return getFilenameWithoutExt(this.getFullFilename());
  },

  /**
   * Get file extension in uppercase for badge display
   */
  getFileExtension() {
    return getFileExtension(this.getFullFilename(), { uppercase: true });
  },

  /**
   * Get the download/view URL for the file
   * Handles both internal and external file URL construction
   */
  getFileUrl() {
    const file = this.file;
    if (!file) return '';

    if (this.isExternal) {
      return getExternalFileUrl(file.attachment);
    }

    return file.the_file || file.url || '';
  },
}));
