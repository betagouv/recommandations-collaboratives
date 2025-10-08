import { Dropdown } from 'bootstrap';
import Alpine from 'alpinejs';
import api, {
  markAllNotificationsAsReadUrl,
  notificationsMarkAsReadByIdUrl,
} from '../utils/api';
import appStore from '../store/app';
import { ToastType } from '../models/toastType';
import { unreadNotificationsListUrl } from '../utils/api';
import { formatDateFrench } from '../utils/date';

function MenuNotifications() {
  return {
    formatDateFrench,
    notifications: [],
    isLoading: true,
    lastMessageDate: null,
    async init() {
      try {
        const response = await api.get(unreadNotificationsListUrl());
        this.notifications = response.data;
        this.isLoading = false;
      } catch (error) {
        this.showToast(
          'Erreur lors de la récupération des notifications. Merci de réessayer plus tard.',
          ToastType.error
        );
        return;
      }
    },
    getNotificationLabel() {
      if (this.notifications.unread_count === 0) {
        return 'Aucune nouvelle notification';
      }
      if (this.notifications.unread_count === 1) {
        return '1 nouvelle notification';
      }
      return `${this.notifications.unread_count} nouvelles notifications`;
    },
    // Simple ifchanged implementation
    shouldShowDate(notification) {
      const dateToCompare = this.formatDateFrench(notification.timestamp);
      if (dateToCompare !== this.lastMessageDate) {
        this.lastMessageDate = dateToCompare;
        return true;
      }
      return false;
    },
    summarizeNotification(notification) {
      const annotations = notification?.data?.annotations;
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
    async markAllNotificationsAsRead() {
      try {
        const response = await api.patch(markAllNotificationsAsReadUrl(), {});
        this.notifications = {
          unread_count: 0,
          unread_list: this.notifications.unread_list.forEach(
            (notification) => {
              notification.unread = false;
            }
          ),
        };
        if (response.data.marked_as_read === 0) {
          this.showToast(
            'Les notifications ne sont pas réellement consommées en mode usurpation.',
            ToastType.warning
          );
          return;
        }
        for (const key in this.isNotificationShown) {
          if (Object.hasOwnProperty.call(this.isNotificationShown, key)) {
            this.isNotificationShown[key] = false;
          }
        }
        this.notifications.unread_count = 0;
      } catch (error) {
        this.showToast(
          'Erreur lors de la mise à jour des notifications. Merci de réessayer plus tard.'
        );
        return;
      }
    },
    async markNotificationAsRead(notificationId) {
      try {
        const response = await api.patch(
          notificationsMarkAsReadByIdUrl(notificationId),
          {}
        );
        if (response.data.marked_as_read === 0) {
          this.showToast(
            'Les notifications ne sont pas réellement consommées en mode usurpation',
            ToastType.warning
          );
        }
        this.notifications.unread_list.find(
          (notification) => notification.id === notificationId
        ).unread = false;
        this.notifications.unread_count--;
      } catch (error) {
        this.showToast(
          'Erreur lors de la mise à jour de la notification. Merci de réessayer plus tard.'
        );
        return;
      }
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
