describe('I can advice a project', () => {

    beforeEach(() => {
        cy.login("switchtender2");
    })

    it('goes to overview page and advise the project', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({ force: true });

        cy.url().should('include', '/presentation')

        cy.contains("Conseiller ce projet").click({ force: true })
        cy.wait(500);
        cy.contains("Ne plus conseiller ce projet")
    })
})
