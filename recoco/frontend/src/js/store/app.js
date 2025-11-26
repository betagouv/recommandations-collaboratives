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
  displayToastMessage({
    message = '',
    type = ToastType.error,
    timeout = 5000,
  } = {}) {
    this.notification.message = message;
    this.notification.timeout = timeout;
    this.notification.isOpen = true;
    this.notification.type = type;
  },
});

export default Alpine.store('app');
