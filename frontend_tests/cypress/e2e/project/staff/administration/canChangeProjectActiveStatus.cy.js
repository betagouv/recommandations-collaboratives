import projects from '../../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can go to administration area of a project and change the active status of a project', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('can change project active status', () => {

			cy.visit(`/project/${currentProject.pk}`)
			cy.get("[data-test-id='navigation-administration-tab']").click({force:true})
			cy.url().should('include', '/administration')

			cy.get('[data-test-id="button-open-modal-deactivate-project"]')
					.click({force:true})

			cy.get('[data-test-id="button-deactivate-project"')
					.click({force:true})

			cy.visit(`/project/${currentProject.pk}`)
			cy.get('[data-test-id="fr-consent-banner"]').find('[data-test-id="button-consent-decline-all"]').click()
			cy.get('[data-test-id="button-open-modal-deactivate-project"]').should('not.exist')
			cy.get('[data-test-id="banner-activate-project"]')
					.get('[data-test-id="button-activate-project"]').click({force:true})
			cy.visit(`/project/${currentProject.pk}`).then(() => {
				cy.reload()
				cy.get('[data-test-id="banner-activate-project"]').should('not.exist')
			})
    })
})
