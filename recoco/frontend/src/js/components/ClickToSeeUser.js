import Alpine from 'alpinejs';
import axios from 'axios';
import { hitcountUrl } from '../utils/api';

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

        this.axios.post(hitcountUrl(), {
          content_object_ct: 'projects.member',
          content_object_id: this.userId,
          context_object_ct: 'projects.project',
          context_object_id: 1,
        });

        this.displayUser = true;
      },
    };
  }
);
