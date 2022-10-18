describe("I can access overview page and can't see the synopsis", () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it("goes to overview page and can't see synopsis", () => {

        cy.visit('/project/2')

        cy.contains("Reformulation du besoin").should('not.exist')
    })
})
