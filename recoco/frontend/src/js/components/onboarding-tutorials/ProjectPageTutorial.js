import Alpine from 'alpinejs';
import '../../store/tutorialsEvents';
import { ToastType } from '../../models/toastType';
import api, { challengeUrl, challengeDefinitionUrl } from '../../utils/api';

Alpine.data('ProjectPageTutorial', () => {
  return {
    isOpenTutorialButtonVisible: false,
    challengesStatus: [],
    challenges: [],
    firstChallengeNotAcquired: null,
    async init() {
      const challengesName = [
        'project-page-tutorial-part1',
        'project-page-tutorial-part2',
        'project-page-tutorial-part3',
        'project-page-tutorial-part4',
      ];
      const requests = [
        ...challengesName.map((name) => api.get(challengeUrl(name))),
      ];
      const responses = await Promise.all(requests);
      if (responses) {
        for (const response of responses) {
          this.challenges.push(response.data);
          if ( response.data.challenge_definition == undefined ) {
            this.challengesStatus.push('acquired');
          }
          else if (
            response.data.acquired_on == null &&
            this.isOpenTutorialButtonVisible == false
          ) {
            this.firstChallengeNotAcquired = response.data;
            this.isOpenTutorialButtonVisible = true;
            this.challengesStatus.push('todo');
          } else if (
            response.data.acquired_on == null &&
            this.isOpenTutorialButtonVisible == true
          ) {
            this.challengesStatus.push('not-acquired');
          }
        }
      }
      if( localStorage.getItem('projectPageTutorialPopupOpen') === 'true' || localStorage.getItem('projectPageTutorialPopupOpen') === null ) {
        this.$store.tutorialsEvents.isTutorialPopupOpen = true;
      }
      // Watch for completion of step 1 triggered on role selection validation
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageOneCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 1.5 &&
            isCompleted
          ) {
            this.handleNextTutorialStep(1);
            localStorage.setItem('isTutorialForProjectPage', '0');
          }
        }
      );
      // Watch for completion of step 2 triggered on a navigation click
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageTwoCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 2 &&
            isCompleted
          ) {
            this.handleNextTutorialStep(2);
            localStorage.setItem('isTutorialForProjectPage', '0');
          }
        }
      );
      // Watch for completion of step 3 triggered on tiptatp editor focus
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageThreeCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 3.5 &&
            isCompleted
          ) {
            this.handleNextTutorialStep(3);
            localStorage.setItem('isTutorialForProjectPage', '0');
          }
        }
      );
      // Watch for completion of step 4 triggered on click on invite collaborators button
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageFourCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 4.5 &&
            isCompleted
          ) {
            this.handleNextTutorialStep(4);
            localStorage.removeItem('isTutorialForProjectPage');
            localStorage.removeItem('projectPageTutorialPopupOpen');
          }
        }
      );
    },
    launchChallenge1(isSwitchTender) {
      if (isSwitchTender) {
        this.handleNextTutorialStep(1);
      }
      else {
        this.$store.tutorialsEvents.isTutorialForProjectPage = 1;
      }
    },
    launchChallenge2() {
      const currentUrl = new URL(location.href);
      if (currentUrl.pathname.includes('/connaissance')) {
        this.handleNextTutorialStep(2);
      }
      else {
        this.$store.tutorialsEvents.isTutorialForProjectPage = 2;
      }
    },
    launchChallenge3() {
        const currentUrl = new URL(location.href);
        if (currentUrl.pathname.includes('/conversations')) {
          this.$store.tutorialsEvents.isTutorialForProjectPage = 3.5;
        }
        else {
          this.$store.tutorialsEvents.isTutorialForProjectPage = 3;
        }
    },
    launchChallenge4() {
      const currentUrl = new URL(location.href);
      if (currentUrl.pathname.includes('/administration/#user-management')) {
        this.$store.tutorialsEvents.isTutorialForProjectPage = 4.5;
      }
      else if (currentUrl.pathname.includes('/administration')) {
        this.$store.tutorialsEvents.isTutorialForProjectPage = 4.5;
      }
      else {
        this.$store.tutorialsEvents.isTutorialForProjectPage = 4;
      }
    },
    async acquireChallenge(code) {
      try {
        const json = await api.patch(challengeUrl(code), {
          acquire: true,
        });
        return json.data;
      } catch (err) {
        this.$store.app.displayToastMessage({
                message: `Erreur lors de l'étape ${code.substring(code.length - 1)} du tutoriel`,
                timeout: 5000,
                type: ToastType.error,
              });
        throw new Error(`Failed to acquire challenge ${code.substring(code.length - 1)}`);
      }
    },
    handleNextTutorialStep(step) {
      this.acquireChallenge(`project-page-tutorial-part${step}`);
      this.challengesStatus[step - 1] = 'acquired';
      this.challengesStatus[step] = 'todo';
      this.$store.tutorialsEvents.isTutorialForProjectPage = 0;
    },
    handleTutorialPopup() {
      this.$store.tutorialsEvents.isTutorialPopupOpen = !this.$store.tutorialsEvents.isTutorialPopupOpen;
      localStorage.setItem('projectPageTutorialPopupOpen', this.$store.tutorialsEvents.isTutorialPopupOpen);
    },
    handleCloseTutorialPopup() {
      this.$store.tutorialsEvents.isTutorialPopupOpen = false;
      localStorage.setItem('projectPageTutorialPopupOpen', 'false');
    },
  };
});
