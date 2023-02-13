import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[2];

describe('I cannot invite a switchtender as a collectivity', () => {

    beforeEach(() => {
        cy.login("boba");
    })

    it('goes to the overview page and not show the switchtender invite button', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.url().should('include', '/presentation')
        cy.contains(currentProject.fields.name)
        cy.contains('Inviter un conseiller').should('not.be.visible')
    })
})
