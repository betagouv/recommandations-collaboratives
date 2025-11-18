import Alpine from 'alpinejs';
import '../../store/tutorialsEvents';
import api, { challengeUrl, challengeDefinitionUrl } from '../../utils/api';

Alpine.data('ProjectPageTutorial', () => {
  return {
    isOpenTutorialButtonVisible: false,
    challengesStatus: [],
    challenges: [],
    firstChallengeNotAcquired: null,
    isTutorialPopupOpen: true,
    async init() {
      if( localStorage.getItem('projectPageTutorialPopupOpen') === 'true' ) {
        this.isTutorialPopupOpen = true;
      }
      const challengesName = [
        'project-page-tutorial-part1',
        'project-page-tutorial-part2',
        'project-page-tutorial-part3',
        'project-page-tutorial-part4',
        'project-page-tutorial-part5',
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
      // Watch for completion of step 1 triggered on a navigation click
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageOneCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 1 &&
            isCompleted
          ) {
            this.acquireChallenge('project-page-tutorial-part1');
            this.challengesStatus[0] = 'acquired';
            this.challengesStatus[1] = 'todo';
            this.$store.tutorialsEvents.isTutorialForProjectPage = 0;
            localStorage.setItem('isTutorialForProjectPage', '0');
          }
        }
      );
      // Watch for completion of step 2 triggered on role selection validation
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageTwoCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 2.5 &&
            isCompleted
          ) {
            this.acquireChallenge('project-page-tutorial-part2');
            this.challengesStatus[1] = 'acquired';
            this.challengesStatus[2] = 'todo';
            this.$store.tutorialsEvents.isTutorialForProjectPage = 0;
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
            this.acquireChallenge('project-page-tutorial-part3');
            this.challengesStatus[2] = 'acquired';
            this.challengesStatus[3] = 'todo';
            this.$store.tutorialsEvents.isTutorialForProjectPage = 0;
            localStorage.setItem('isTutorialForProjectPage', '0');
          }
        }
      );
      // Watch for completion of step 4 triggered on click on create reco button
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageFourCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 4.6 &&
            isCompleted
          ) {
            this.acquireChallenge('project-page-tutorial-part4');
            this.challengesStatus[3] = 'acquired';
            this.challengesStatus[4] = 'todo';
            this.$store.tutorialsEvents.isTutorialForProjectPage = 0;
          }
        }
      );
      // Watch for completion of step 5 triggered on click on invite collaborators button
      this.$watch(
        () => this.$store.tutorialsEvents.isTutorialForProjectPageFiveCompleted,
        (isCompleted) => {
          if (
            this.$store.tutorialsEvents.isTutorialForProjectPage === 5.5 &&
            isCompleted
          ) {
            this.acquireChallenge('project-page-tutorial-part5');
            this.challengesStatus[4] = 'acquired';
            this.challengesStatus[5] = 'todo';
            this.$store.tutorialsEvents.isTutorialForProjectPage = 0;
            localStorage.removeItem('isTutorialForProjectPage');
            localStorage.removeItem('projectPageTutorialPopupOpen');
          }
        }
      );
    },
    launchChallenge1() {
      this.$store.tutorialsEvents.isTutorialForProjectPage = 1;
    },
    launchChallenge2(isSwitchTender) {
      if (isSwitchTender) {
        this.acquireChallenge('project-page-tutorial-part2');
            this.challengesStatus[1] = 'acquired';
            this.challengesStatus[2] = 'todo';
            this.$store.tutorialsEvents.isTutorialForProjectPage = 0;
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
        if (currentUrl.pathname.includes('/conversations')) {
            this.$store.tutorialsEvents.isTutorialForProjectPage = 4.3;
        }
        else {
            this.$store.tutorialsEvents.isTutorialForProjectPage = 4;
        }
    },
    launchChallenge5() {
      // TODO: trigger the recommendation creation flow
      const currentUrl = new URL(location.href);
      if (currentUrl.pathname.includes('/administration/#user-management')) {
        this.$store.tutorialsEvents.isTutorialForProjectPage = 5.5;
      }
      else if (currentUrl.pathname.includes('/administration')) {
        this.$store.tutorialsEvents.isTutorialForProjectPage = 5.5;
      }
      else {é
        this.$store.tutorialsEvents.isTutorialForProjectPage = 5;
      }
    },
    async acquireChallenge(code) {
      try {
        const json = await api.patch(challengeUrl(code), {
          acquire: true,
        });
        return json.data;
      } catch (err) {
        console.warn(err);
      }
    },
    handleTutorialPopup() {
      this.isTutorialPopupOpen = !this.isTutorialPopupOpen;
      localStorage.setItem('projectPageTutorialPopupOpen', this.isTutorialPopupOpen);
    },
    handleCloseTutorialPopup() {
      this.isTutorialPopupOpen = false;
      localStorage.setItem('projectPageTutorialPopupOpen', 'false');
    },
  };
});
