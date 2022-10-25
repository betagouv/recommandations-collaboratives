describe('I can follow a project', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('goes to the homepage and create a project with the main CTA', () => {

        cy.visit('/')
        cy.visit('/project/2')

        cy.contains("Friche numéro 1")
        cy.contains("Présentation")

        cy.contains("Contexte")
        cy.contains("La toute première friche")

        cy.contains("Difficultés rencontrées")
        cy.contains("La toute première friche")

        cy.contains("Bob Collectivité")
        cy.contains("Organisation de test")
        cy.contains("bob@test.fr")
        cy.contains("+33101010101")

        cy.contains("Jean Conseille")

        cy.contains("Bob Collectivité")

        // cy.contains("Boba Collectivité")
    })
})
