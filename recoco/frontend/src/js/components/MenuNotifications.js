import { Dropdown } from 'bootstrap';
import Alpine from 'alpinejs';
import api, {
  markAllNotificationsAsReadUrl,
  notificationsMarkAsReadByIdUrl,
} from '../utils/api';
import appStore from '../store/app';
import { ToastType } from '../models/toastType';

function MenuNotifications(notificationNumber) {
  return {
    notificationNumber: notificationNumber,
    notificationNextIndex: 0,
    isNotificationShown: {},
    initNewNotification(notificationIndex) {
      this.isNotificationShown[notificationIndex] = true;
    },
    async markNotificationAsRead(notificationId, el, notificationIndex) {
      try {
        const reqMarkNotifAsRead = await api.patch(
          notificationsMarkAsReadByIdUrl(notificationId),
          {}
        );
        if (reqMarkNotifAsRead.data.marked_as_read > 0) {
          this.removeNotificationInDom(el, notificationIndex);
        }
      } catch (error) {
        this.showToast(
          'Erreur lors de la mise à jour de la notification. Merci de réessayer plus tard.'
        );
        return;
      }
    },
    async markAllNotificationsAsRead() {
      try {
        await api.patch(markAllNotificationsAsReadUrl(), {});
        for (const key in this.isNotificationShown) {
          if (Object.hasOwnProperty.call(this.isNotificationShown, key)) {
            this.isNotificationShown[key] = false;
          }
        }
        this.notificationNumber = 0;
      } catch (error) {
        this.showToast(
          'Erreur lors de la mise à jour des notifications. Merci de réessayer plus tard.'
        );
        return;
      }
    },
    removeNotificationInDom(el, notificationIndex) {
      this.notificationNumber -= 1;
      const nextEl = el.parentElement.nextElementSibling;
      const previousEl = el.parentElement.previousElementSibling;
      this.isNotificationShown[notificationIndex] = false;
      this.isNotificationShown = { ...this.isNotificationShown };
      if (
        nextEl &&
        previousEl &&
        nextEl.classList.contains('notification__date') &&
        previousEl.classList.contains('notification__date')
      ) {
        setTimeout(() => {
          previousEl.remove();
        }, 500);
      }
      setTimeout(() => {
        el.parentElement.remove();
      }, 500);
    },
    closeNotificationsMenu() {
      const notificationsMenu = document.querySelector(
        '.dropdown-menu.notifications'
      );
      const dropdownInstance = new Dropdown(notificationsMenu);
      dropdownInstance.hide();
    },
    showToast(message, type) {
      appStore.notification.message = message;
      appStore.notification.timeout = 5000;
      appStore.notification.isOpen = true;
      appStore.notification.type = type || ToastType.error;
    },
  };
}

Alpine.data('MenuNotifications', MenuNotifications);
