import Alpine from 'alpinejs'
import introJs from 'intro.js';
import 'intro.js/introjs.css'


Alpine.data("Tutorial", Tutorial)

function Tutorial() {
    return {
        init() {
            console.log('Tutorial component ready : ');
            introJs().start();
        },
    }
}
