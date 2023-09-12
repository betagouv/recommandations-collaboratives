describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject(1)
    })

    it('publishes a task', () => {

        cy.becomeAdvisor();

        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask(1);

        cy.contains("Thématique").should('have.class', 'active')
        cy.get('#unpublish-task-button').click({force:true});
        cy.contains('brouillon')
        cy.get('#publish-task-button').click({force:true});
        cy.contains('brouillon').should('not.exist')
    })
})
