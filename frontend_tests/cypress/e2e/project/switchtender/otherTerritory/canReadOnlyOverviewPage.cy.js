import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can read only overview page', () => {

    beforeEach(() => {
        cy.login("jeannot");
    })

    it('goes to the overview page and not see the advisor note', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Note interne").should('not.exist')
    })
})
