describe("I can't access privates notes as a non positionned adviser", () => {

    beforeEach(() => {
        cy.login("jeannot");
    })

    it('goes to the project page and not beeing able to see the private note tab', () => {

        cy.visit('/project/2')

        cy.contains("Suivi interne").should('not.exist')
    })
})
