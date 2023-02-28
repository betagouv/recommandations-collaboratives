import projects from '../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can access administration tab in a project as staff', () => {

    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to the administration page of my project', () => {

        cy.visit(`/project/${currentProject.pk}`)
        // cy.contains('Administration').click({ force: true })
        cy.get('.project-navigation').children('li').contains('Administration').click({force:true})
        cy.url().should('include', '/administration')
    })
})
