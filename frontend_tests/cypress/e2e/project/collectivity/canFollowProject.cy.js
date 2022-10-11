describe('I can follow a project', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to overview page and follow the project', () => {

        cy.visit('/project/1')
        
        // cy.contains("suivre le projet").click({ force: true })
    })
})
