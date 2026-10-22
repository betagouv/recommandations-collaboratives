import Alpine from 'alpinejs';
import { isPlural } from '../utils/isPlural';
import { gravatar_url } from '../utils/gravatar';
import { isPreviewableFile } from '../utils/file';

Alpine.store('utils', {
  isPlural,
  gravatar_url,
  isPreviewableFile,
});

export default Alpine.store('utils');
