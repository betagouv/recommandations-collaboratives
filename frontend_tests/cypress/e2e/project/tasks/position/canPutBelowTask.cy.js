describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject("task below")
    })

    it('change task position below', () => {

        cy.becomeAdvisor();

        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask(1);
        cy.createTask(2);

        cy.get('[data-test-id="list-tasks-switch-button"]').should('have.class', 'active')

        cy.get('#task-move-below').click({force:true});
    })
})
