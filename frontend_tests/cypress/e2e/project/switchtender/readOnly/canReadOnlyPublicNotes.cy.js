import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can read only public notes', () => {

    beforeEach(() => {
        cy.login("jeannot");
    })

    it('goes to public notes and read only content', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        // cy.contains("Conversation").click({ force: true })

        // cy.url().should('include', '/conversations')

        // cy.get('textarea').should('not.exist')
    })
})
