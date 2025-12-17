import Alpine from 'alpinejs';

Alpine.store('tutorialsEvents', {
    isTutorialForProjectPage: 0,
    isTutorialForProjectPageOneCompleted: false,
    isTutorialForProjectPageTwoCompleted: false,
    isTutorialPopupOpen : false,
    init() {
        if (localStorage.getItem('isTutorialForProjectPage')) {
            this.isTutorialForProjectPage = parseFloat(localStorage.getItem('isTutorialForProjectPage'));
        } else {
            this.isTutorialForProjectPage = 0;
        }
    }


});

export default Alpine.store('tutorialsEvents');
