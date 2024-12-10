import Alpine from 'alpinejs';

Alpine.data('ClickToSeeUser', (userId) => {
  return {
    userId: userId,
    usersIdAlreadyDiscovered: [],
    displayUser: false,
    init() {
      this.usersIdAlreadyDiscovered =
        JSON.parse(localStorage.getItem('users')) || [];
      this.displayUser = this.usersIdAlreadyDiscovered.includes(this.userId);
    },
    handleClickToSeeInfo() {
      if (!this.usersIdAlreadyDiscovered.includes(this.userId)) {
        this.usersIdAlreadyDiscovered.push(this.userId);
        localStorage.setItem(
          'users',
          JSON.stringify(this.usersIdAlreadyDiscovered)
        );
      }
      this.displayUser = true;
    },
  };
});
