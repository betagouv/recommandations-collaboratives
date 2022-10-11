describe('I can access overview page and see the synopsis', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to overview page and see synopsis', () => {

        cy.visit('/project/1')

        cy.contains("Reformulation du besoin")
    })
})
