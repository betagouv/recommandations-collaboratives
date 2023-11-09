import projects from '../../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can go to administration area of a project and change the active status of a project', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('puts the project on stand-by', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.get("[data-test-id='navigation-administration-tab']").click({force:true})
        cy.url().should('include', '/administration')

        cy.get('[data-test-id="button-open-modal-deactivate-project"]')
            .click({force:true})

        cy.get('[data-test-id="form__admin-deactivate-project"]')
            .submit()

        cy.visit(`/project/${currentProject.pk}`)
        cy.get('[data-test-id="banner-activate-project"]')
            .should.exist
    })
})
