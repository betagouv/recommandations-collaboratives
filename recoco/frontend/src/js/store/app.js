import Alpine from 'alpinejs';
import { ToastType } from '../models/toastType';

Alpine.store('app', {
  isLoading: false,
  notification: {
    isOpen: false,
    message: '',
    timeout: 2000,
    type: ToastType.success,
  },
});

export default Alpine.store('app');
export default Alpine.store('app');
