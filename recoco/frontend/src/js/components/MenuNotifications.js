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
    async clickConsummeNotificationAndRedirect(
      event,
      notificationId,
      targetUrl,
      { conversationContext } = { conversationContext: false }
    ) {
      // Logic when user want to open it in another window
      const isModifierClick =
        event.ctrlKey || event.metaKey || event.shiftKey || event.button === 1;

      if (isModifierClick) {
        if (!conversationContext) {
          api
            .patch(notificationsMarkAsReadByIdUrl(notificationId), {})
            .catch(() => {});
        }
        return;
      }

      event.preventDefault();
      if (!conversationContext) {
        try {
          await api.patch(notificationsMarkAsReadByIdUrl(notificationId), {});
        } catch (e) {
          this.showToast(
            'Erreur lors de la mise à jour de la notification. Merci de réessayer plus tard.'
          );
        }
      }
      window.location.href = `${window.location.origin}${targetUrl}`;
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
    getSummaryNotification(notificationId) {
      const notification = this.listNofification.find(
        (notification) => notification.pk === notificationId
      );
      return this.summarizeNotification(notification);
    },
    summarizeNotification(notification) {
      const annotations = JSON.parse(notification?.fields?.data)?.annotations;
      if (!annotations) {
        return notification.verb;
      }
      let summary = [];
      const count =
        annotations.recommendations.count +
        annotations.contacts.count +
        annotations.documents.count;
      if (count === 0) {
        return ` envoyé un message`;
      }
      if (annotations.recommendations.count > 0) {
        summary.push(
          `${annotations.recommendations.count} recommandation${annotations.recommendations.count > 1 ? 's' : ''}`
        );
      }
      if (annotations.contacts.count > 0) {
        summary.push(
          `${annotations.contacts.count} contact${annotations.contacts.count > 1 ? 's' : ''}`
        );
      }
      if (annotations.documents.count > 0) {
        summary.push(
          `${annotations.documents.count} document${annotations.documents.count > 1 ? 's' : ''}`
        );
      }
      summary = summary
        .map((item, index) => {
          if (index == 0) {
            return `${item}`;
          }
          if (index == summary.length - 1 && summary.length > 1) {
            return ` et ${item} `;
          }
          return `, ${item} `;
        })
        .join('');
      return ` envoyé ${summary}`;
    },
  };
}

Alpine.data('MenuNotifications', MenuNotifications);
