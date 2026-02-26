import Alpine from 'alpinejs';
import {
  initGravatarCache,
  gravatar_url,
} from '../utils/gravatar';

Alpine.data('GravatarCache', () => ({
  gravatarUrl: gravatar_url,
  init() {
    initGravatarCache();
  },
}));
