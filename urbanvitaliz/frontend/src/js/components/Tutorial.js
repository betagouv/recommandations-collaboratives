import Alpine from 'alpinejs'
import introJs from 'intro.js';
import tutorials from '../config/tutorials'
import 'intro.js/introjs.css'

//Custom introjs CSS
import '../../css/introJs.css'

function Tutorial(tutorial, autoStart=false) {
    return {
        steps: [],
        hints: [],
        tour: null,
        startButton:null,
        init() {
            this.steps = tutorials[tutorial].steps

            this.tour = introJs().setOptions({
                tooltipClass: 'introjs-uv',
                prevLabel: 'Précédent',
                nextLabel: 'Suivant',
                doneLabel: 'C\'est parti !',
                steps: this.steps,
            })

            if (autoStart) {
                return this.tour.start();
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
