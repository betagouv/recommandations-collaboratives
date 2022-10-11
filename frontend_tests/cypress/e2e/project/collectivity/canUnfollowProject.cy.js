describe('I can unfollow a project', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to overview page and unfollow the project', () => {

        cy.visit('/project/1')
        
        // cy.contains("ne plus suivre le project").click({ force: true })
    })
})
