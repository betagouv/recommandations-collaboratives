import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can read only overview page', () => {

    beforeEach(() => {
        cy.login("jeanne");
    })

    it('goes to overview and read only content', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.url().should('include', '/presentation')

        cy.contains("Note interne").should('not.exist')
    })
})
