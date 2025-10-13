import { Dropdown } from 'bootstrap';
import Alpine from 'alpinejs';
import api, {
  markAllNotificationsAsReadUrl,
  notificationsMarkAsReadByIdUrl,
} from '../utils/api';
import appStore from '../store/app';
import { ToastType } from '../models/toastType';

function MenuNotifications(notificationNumber, listNofification) {
  return {
    notificationNumber: notificationNumber,
    notificationNextIndex: 0,
    isNotificationShown: {},
    listNofification: listNofification,
    initNewNotification(notificationIndex) {
      this.isNotificationShown[notificationIndex] = true;
    },
    async clickConsummeNotificationAndRedirect(notificationId, targetUrl) {
      await api.patch(notificationsMarkAsReadByIdUrl(notificationId), {});
      // redirect to the notification target
      window.open(`${window.location.origin}${targetUrl}`, '_blank');
    },
    getNotificationLink(targetUrl) {
      return `${window.location.origin}${targetUrl}`;
    },
    async markNotificationAsRead(notificationId, el, notificationIndex) {
      try {
        const reqMarkNotifAsRead = await api.patch(
          notificationsMarkAsReadByIdUrl(notificationId),
          {}
        );
        if (reqMarkNotifAsRead.data.marked_as_read > 0) {
          this.removeNotificationInDomByIndex(el, notificationIndex);
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
        window.location.reload();
      } catch (error) {
        this.showToast(
          'Erreur lors de la mise à jour des notifications. Merci de réessayer plus tard.'
        );
        return;
      }
    },
    removeNotificationInDomByIndex(el, notificationIndex) {
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
