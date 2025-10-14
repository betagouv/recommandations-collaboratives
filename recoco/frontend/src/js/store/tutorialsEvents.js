import Alpine from 'alpinejs';

Alpine.store('tutorialsEvents', {
    isTutorialForProjectPage: 0,
    isTutorialForProjectPageOneCompleted: false,
});

export default Alpine.store('tutorialsEvents');
