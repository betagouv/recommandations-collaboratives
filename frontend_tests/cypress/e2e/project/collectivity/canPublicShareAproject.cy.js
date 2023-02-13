describe('I can have a public url to share', () => {

    beforeEach(() => {
        cy.login("boba");
    })

    it('goes to share a project page', () => {

        cy.visit('/project/3/')

        cy.contains("Partager l'état des lieux").click({ force: true })

        // cy.url().should('include', '/access/')

        cy.document().then((doc) => {
            const value = doc.querySelector('[x-ref="input"]').value;
            cy.visit(value)
            cy.url().should('include', '/project/partage/')
        });
    })
})
