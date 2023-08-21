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
        showTuto: false,
        async init() {
            this.challengeCode = challengeCode

            const challengeDefinition = await this.getChallengeDefinition(challengeCode)

            //Get current challenge for current user
            //Can be empty object
            const challenge = await this.getChallenge(this.challengeCode)
            const userHasActiveChallenge = !(Object.keys(challenge).length === 0)

            if (challengeDefinition && userHasActiveChallenge) {
                this.showTuto = true
            } else {
                return
            }


            this.steps = tutorials[challengeDefinition.code].steps
            this.startButtonDescription = challengeDefinition.description

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
        },
        async handleEndChallenge() {
            this.startButton = this.$refs.startTourButton
            this.startButton.style.display = "none"
            await this.acquireChallenge(this.challengeCode)
        }
    }
}

Alpine.data("Tutorial", Tutorial)
