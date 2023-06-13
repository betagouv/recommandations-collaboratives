export default {
    survey: [
        {
            intro: "<strong>Obtenez des recommandations plus efficaces</strong> en répondant à quelques questions ! <br/>Ce parcours vous guide pour structurer votre <strong>connaissance sur le projet</strong>.<br/>Vous pouvez quitter et reprendre le questionnaire à tout moment, et inviter des participants pour le remplir."
        },
        {
            element: document.querySelector('#qs-heading'),
            intro: "Le parcours est divisé en sections thématiques. Vous pouvez les enchaîner, ou y revenir plus tard : pas de pression 😉"
        },
        {
            element: document.querySelector('#section-why'),
            intro: "🌱 Certaines informations sont plus importantes qu’elles n’en ont l’air. Découvrez ici pourquoi."
        },
        {
            element: document.querySelector('#section-how'),
            intro: "🔍 Vous ne savez pas répondre à la question ? Cet encart vous indiquer où trouver l’information manquante."
        },
        {
            element: document.querySelector('#button-skip'),
            intro: "✨ Vous pouvez aussi enchaîner les questions, et laisser de côté celles où vous ne savez pas répondre.",
        },
        {
            element: document.querySelector('#project-link'),
            intro: "Ici, vous retrouverez le récapitulatif de vos réponses, et les questions que vous avez laissées vides : vous pouvez y revenir une fois l’information trouvée. <br/>Bonne exploration de votre site 👋"
        }
    ],
    overview: {
        tooltipClass: 'introjs-uv',
        prevLabel: 'Précédent',
        nextLabel: 'Suivant',
        doneLabel: 'C\'est parti !',
        steps: [
            {
                intro: "Ici, familiarisez-vous avec le projet",
                element: '#overview-step-1',
            },
            {
                intro: "UrbanVitaliz et les acteurs locaux comme vous conseillent la collectivité ici.",
                element: '#overview-step-2',
            },
            {
                intro: "Vous devez être conseiller ou observateur pour accéder aux échanges.",
                element: '#overview-step-3',
            },
            {
                intro: "La collectivité n’a pas accès à cet onglet d’échanges.",
                element: '#overview-step-4',
            },
            {
                intro: "Pour vous déclarer conseiller ou observateur sur ce projet, c’est ici.",
                element: '#overview-step-5',
            },
        ]
    }
}



