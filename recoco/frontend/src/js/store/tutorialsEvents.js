import Alpine from 'alpinejs';

Alpine.store('tutorialsEvents', {
    isTutorialForProjectPage: 0,
    isTutorialForProjectPageOneCompleted: false,
    isTutorialForProjectPageTwoCompleted: false,
});

export default Alpine.store('tutorialsEvents');
