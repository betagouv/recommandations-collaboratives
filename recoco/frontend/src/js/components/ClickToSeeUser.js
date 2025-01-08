import Alpine from 'alpinejs';

Alpine.data('ClickToSeeUser', (ownerId, currentUserId, currentUserIsStaff) => {
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
      this.displayUser = true;
    },
  };
});
