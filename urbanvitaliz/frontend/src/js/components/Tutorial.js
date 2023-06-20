import Alpine from 'alpinejs'
import introJs from 'intro.js';
import tutorials from '../config/tutorials'
import 'intro.js/introjs.css'
import api, { challengeUrl, challengeDefinitionUrl } from '../utils/api'

//Custom introjs CSS
import '../../css/introJs.css'

function Tutorial(challengeCode, autoStart = false) {
    return {
        steps: [],
        hints: [],
        tour: null,
        hasAlreadyStartedTheChallenge: false,
        startButton: null,
        startButtonDescription: "",
        challengeCode: null,
        async init() {
            this.challengeCode = challengeCode

            //Check if the user has already started the Challenge

            const challenge = await this.getChallenge(this.challengeCode)

            if (challenge && challenge.started_on) {
                return this.hasAlreadyStartedTheChallenge = true
            }

            const ChallengeDefinition = await this.getChallengeDefinition(challengeCode)

            if (!ChallengeDefinition) {
                return this.hasAlreadyStartedTheChallenge = true
            }

            this.steps = tutorials[ChallengeDefinition.code].steps
            this.startButtonDescription = ChallengeDefinition.description

            this.tour = introJs().setOptions({
                tooltipClass: 'introjs-uv',
                prevLabel: 'Précédent',
                nextLabel: 'Suivant',
                doneLabel: 'C\'est parti !',
                steps: this.steps,
            })

            this.tour.oncomplete(async () => {
                this.acquireChallenge(this.challengeCode)
            })

            if (autoStart) {
                this.tour.start();
                await this.startChallenge(this.challengeCode)
            }
        },
        async getChallengeDefinition(code) {
            try {
                const json = await api.get(challengeDefinitionUrl(code))
                return json.data
            }
            catch (err) {
                console.warn(err);
            }
        },
        async getChallenge(code) {
            try {
                const json = await api.get(challengeUrl(code))
                return json.data
            }
            catch (err) {
                console.warn(err);
            }
        },
        async startChallenge(code) {
            try {
                const json = await api.patch(challengeUrl(code), { started_on: true })
                return json.data
            }
            catch (err) {
                console.warn(err);
            }
        },
        async acquireChallenge(code) {
            try {
                const json = await api.patch(challengeUrl(code), { acquired_on: true })
                return json.data
            }
            catch (err) {
                console.warn(err);
            }
        },
        async handleStartTour() {
            this.startButton = this.$refs.startTourButton
            this.startButton.style.display = "none"
            this.tour.start();
            await this.startChallenge(this.challengeCode)
        }
    }
}

Alpine.data("Tutorial", Tutorial)
