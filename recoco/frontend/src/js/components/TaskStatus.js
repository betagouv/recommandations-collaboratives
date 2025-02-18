import Alpine from 'alpinejs';

import { humanReadableTaskStatus } from '../utils/taskStatus';

/**
 * Represents a TaskStatus component.
 */
Alpine.data('TaskStatus', () => {
  return {
    humanReadableTaskStatus,
  };
});
