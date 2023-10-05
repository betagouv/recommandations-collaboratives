import projects from '../../../fixtures/projects/projects.json'

describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('displays a banner for unread tasks', () => {
        const currentProject = projects[1];
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        // Test that icons are displayed correctly
        cy.get('[data-test-id="banner-new-tasks"]')
        .find('[data-test-id="img-presentation"]').then(($img) => {
            cy.testImage($img[0], 'img-presentation');
        })
    })
})
