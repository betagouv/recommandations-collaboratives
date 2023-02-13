import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can invite a switchtender as a regional actor', () => {

    beforeEach(() => {
        cy.login("jeannot");
    })

    it('goes to the overview page and invite a switchtender', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        // cy.contains('Inviter un conseiller').click({ force: true });

        // cy.get('.invite-switchtender-modal-email')
        //     .type('advisor@test.fr', { force: true })
        //     .should('have.value', 'advisor@test.fr')

        // cy.get('.invite-switchtender-modal-textarea')
        //     .type("Bonjour advisor, je t'invite à conseiller mon projet friche numéro 1", { force: true })
        //     .should('have.value', "Bonjour advisor, je t'invite à conseiller mon projet friche numéro 1")

        // cy.get('.invite-switchtender-modal-button').click({force:true});

        // cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à advisor@test.fr")

    })
})
