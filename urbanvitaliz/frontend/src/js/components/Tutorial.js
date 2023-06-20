import Alpine from 'alpinejs'
import introJs from 'intro.js';
import tutorials from '../config/tutorials'
import 'intro.js/introjs.css'
import api, { challengeDefinitionUrl } from '../utils/api'

//Custom introjs CSS
import '../../css/introJs.css'

function Tutorial(user, challengeCode, autoStart = false) {
    return {
        steps: [],
        hints: [],
        tour: null,
        startButton: null,
        startButtonDescription: "",
        init() {

            console.log('current user : ', user)
            const challenge = this.getChallengeDefinition(challengeCode)

            // console.log('challenge : ', challenge);
            // this.steps = tutorials[challenge.code].steps
            // this.startButtonDescription = challenge.description

            // this.tour = introJs().setOptions({
            //     tooltipClass: 'introjs-uv',
            //     prevLabel: 'Précédent',
            //     nextLabel: 'Suivant',
            //     doneLabel: 'C\'est parti !',
            //     steps: this.steps,
            // })

            // if (autoStart) {
            //     return this.tour.start();
            // }
        },
        async getChallengeDefinition(code) {
            try {
                const json = await api.get(challengeDefinitionUrl(code))
                return json.data
            }
            catch(err) {
                console.error(err);
            }
        },
        handleStartTour() {
            this.startButton = this.$refs.startTourButton
            this.startButton.style.display = "none"
            this.tour.start();
        }
    }
}

Alpine.data("Tutorial", Tutorial)
