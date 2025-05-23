import Alpine from 'alpinejs';
import introJs from 'intro.js';
import tutorials from '../config/tutorials';
import 'intro.js/introjs.css';
import api, { challengeUrl, challengeDefinitionUrl } from '../utils/api';

//Custom introjs CSS
import '../../css/introJs.css';

function Tutorial(challengeCode) {
  return {
    steps: [],
    hints: [],
    tour: null,
    hasAlreadyStartedTheChallenge: false,
    startButton: null,
    startButtonDescription: '',
    challengeCode: null,
    showTuto: false,
    async init() {
      this.challengeCode = challengeCode;
      const challengeDefinition =
        await this.getChallengeDefinition(challengeCode);
      if (!challengeDefinition) return;
      //Get current challenge for current user
      //Can be empty object
      const challenge = await this.getChallenge(this.challengeCode);
      if (!challenge) return;
      const userHasActiveChallenge = !(Object.keys(challenge).length === 0);

      if (challengeDefinition && userHasActiveChallenge) {
        this.showTuto = true;
      } else {
        return;
      }

      this.steps = tutorials[challengeDefinition.code].steps;
      this.startButtonDescription = challengeDefinition.description;

      this.tour = introJs().setOptions({
        tooltipClass: 'introjs-uv',
        prevLabel: 'Précédent',
        nextLabel: 'Suivant',
        doneLabel: 'Ne plus afficher',
        skipLabel: '✕',
        steps: this.steps,
      });

      if (
        this.showTuto &&
        this.challengeCode == 'time-filter-tutorial-on-kanban'
      ) {
        this.handleStartTour();
      }

      this.tour.oncomplete(async () => {
        this.acquireChallenge(this.challengeCode);
      });

      this.tour.onexit(async () => {
        this.snoozeChallenge(this.challengeCode);
      });
    },
    async getChallengeDefinition(code) {
      try {
        const json = await api.get(challengeDefinitionUrl(code));
        return json.data;
      } catch (err) {
        console.warn(err);
      }
    },
    async getChallenge(code) {
      try {
        const json = await api.get(challengeUrl(code));
        return json.data;
      } catch (err) {
        console.warn(err);
      }
    },
    async startChallenge(code) {
      try {
        const json = await api.patch(challengeUrl(code), {
          start: true,
        });
        return json.data;
      } catch (err) {
        console.warn(err);
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
    async snoozeChallenge(code) {
      try {
        const json = await api.patch(challengeUrl(code), {
          snooze: true,
        });
        return json.data;
      } catch (err) {
        console.warn(err);
      }
    },
    async hideStartModal() {
      this.startButton = this.$refs.startTourButton;
      this.startButton.style.display = 'none';
      this.handleStartTour();
    },
    async handleStartTour() {
      if (!this.tour) return;
      this.tour.start();
      await this.startChallenge(this.challengeCode);
    },
    async handleEndChallenge() {
      this.startButton = this.$refs.startTourButton;
      this.startButton.style.display = 'none';
      await this.acquireChallenge(this.challengeCode);
    },
    async handleSnoozeChallenge() {
      this.startButton = this.$refs.startTourButton;
      this.startButton.style.display = 'none';
      await this.snoozeChallenge(this.challengeCode);
    },
  };
}

Alpine.data('Tutorial', Tutorial);
