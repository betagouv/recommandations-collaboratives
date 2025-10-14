import Alpine from 'alpinejs';
import '../../store/tutorialsEvents';
import api, { challengeUrl, challengeDefinitionUrl } from '../../utils/api';

Alpine.data('ProjectPageTutorial', () => {
    return {
        isOpenTutorialButtonVisible: false,
        challengesStatus: [],
        challenges: [],
        firstChallengeNotAcquired: null,
        isPopupOpen: false,
        async init() {
            this.$store.tutorialsEvents.isTutorialForProjectPage = 0;

            const challengesName = ['project-page-tutorial-part1', 'project-page-tutorial-part2', 'project-page-tutorial-part3', 'project-page-tutorial-part4'];
            const requests = [
              ...challengesName.map(name => api.get(challengeUrl(name)))
            ]
            const responses = await Promise.all(requests);
            if (responses) {
                for (const response of responses) {
                    this.challenges.push(response.data);
                    if (response.data.acquired_on == null && this.isOpenTutorialButtonVisible == false) {
                        this.firstChallengeNotAcquired = response.data;
                        this.isOpenTutorialButtonVisible = true;
                        this.challengesStatus.push("todo");
                    }
                    else if (response.data.acquired_on == null && this.isOpenTutorialButtonVisible == true) {
                        this.challengesStatus.push("not-acquired");
                    }
                    else {
                        this.challengesStatus.push("acquired");
                    }
                }
            }
        },
        launchChallenge1() {
            this.$store.tutorialsEvents.isTutorialForProjectPage = 1;
            this.$nextTick(() => {
                if (this.$store.tutorialsEvents.isTutorialForProjectPageOneCompleted) {
                    alert("Vous avez déjà complété cette étape !");
                }
            });
        },
        launchChallenge2() {
            this.$store.tutorialsEvents.isTutorialForProjectPage = 2;
        },
        launchChallenge3() {
            this.$store.tutorialsEvents.isTutorialForProjectPage = 3;
        },
        launchChallenge4() {
            this.$store.tutorialsEvents.isTutorialForProjectPage = 4;
        },
    };
});
