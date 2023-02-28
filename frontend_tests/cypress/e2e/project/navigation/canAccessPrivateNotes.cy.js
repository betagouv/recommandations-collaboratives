import projects from '../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can access private notes tab in a project as a switchtender', () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to the private notes page of my project', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Espace conseillers').click({ force: true })
        cy.url().should('include', '/suivi')
    })
})
