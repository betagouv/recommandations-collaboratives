import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can read only project state', () => {

    beforeEach(() => {
        cy.login("jeannot");
    })

    it('goes to project state and read only content', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.get('li').contains("État des lieux").click({force:true})

        cy.url().should('include', '/connaissance')

        cy.contains("Compléter cette section").should('not.exist')
    })
})
