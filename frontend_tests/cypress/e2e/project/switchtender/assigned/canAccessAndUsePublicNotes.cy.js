import projects from '../../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can access and use public notes', () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to public notes', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        const now = new Date();

        cy.get('textarea')
            .type(`test : ${now}`, { force: true })
            .should('have.value', `test : ${now}`)

        cy.contains("Envoyer").click({ force: true })

        cy.contains(`test : ${now}`)
    })
})
