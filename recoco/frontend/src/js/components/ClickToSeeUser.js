import Alpine from 'alpinejs';
import api, { hitcountUrl } from '../utils/api';

Alpine.data(
  'ClickToSeeUser',
  (ownerId, currentUserId, currentUserIsStaff, projetId) => {
    return {
      userId: ownerId,
      usersIdAlreadyDiscovered: [],
      displayUser: false,
      init() {
        if (currentUserIsStaff || ownerId === currentUserId) {
          this.displayUser = true;
          return;
        }
        this.usersIdAlreadyDiscovered =
          JSON.parse(localStorage.getItem('displayUsersContact')) || [];
        this.displayUser = this.usersIdAlreadyDiscovered.includes(this.userId);
      },
      handleClickToSeeInfo() {
        if (!this.usersIdAlreadyDiscovered.includes(this.userId)) {
          this.usersIdAlreadyDiscovered.push(this.userId);
          localStorage.setItem(
            'displayUsersContact',
            JSON.stringify(this.usersIdAlreadyDiscovered)
          );
        }

        api.post(hitcountUrl(), {
          content_object_ct: 'projects.projectmember',
          content_object_id: this.userId,
          context_object_ct: 'projects.project',
          context_object_id: projetId,
        });

        this.displayUser = true;
      },
    };
  }
);
