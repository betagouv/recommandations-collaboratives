describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject(1)
    })

    it('change task position above', () => {

        cy.becomeAdvisor();

        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask(1);
        cy.createTask(2);

        cy.contains("Thématique").should('have.class', 'active')

        cy.get('#task-move-above').click({force:true});
    })
})
