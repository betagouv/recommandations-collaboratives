import Alpine from 'alpinejs';

Alpine.store('tutorialsEvents', {
    isTutorialForProjectPage: 0,
    isTutorialForProjectPageOneCompleted: false,
    isTutorialForProjectPageTwoCompleted: false,

    init() {
        if (localStorage.getItem('isTutorialForProjectPage')) {
            this.isTutorialForProjectPage = parseFloat(localStorage.getItem('isTutorialForProjectPage'));
            console.log('Loaded isTutorialForProjectPage from localStorage:', typeof this.isTutorialForProjectPage);
            console.log('Loaded isTutorialForProjectPage from localStorage:', typeof localStorage.getItem('isTutorialForProjectPage'));
        } else {
            this.isTutorialForProjectPage = 0;
        }
    },


});

export default Alpine.store('tutorialsEvents');
