import switchtender from '../../fixtures/users/switchtender.json'


describe('The Login Page', () => {
    
    let currentUser = {}

    beforeEach(() => {
        //Logging user for debug purposes
        console.log('switchtender : ', switchtender)
        currentUser = switchtender[0].fields
    })

    it('sets auth cookie when logging in via form submission', function () {
        const { username } = currentUser

        cy.visit('/accounts/login/')

        cy.url().should('include', '/accounts/login/')

        cy.get('#id_login').type(username, { force: true }).should('have.value', username)

        cy.get('#id_password').type("derpderp", { force: true }).should('have.value', "derpderp")

        cy.get("[type=submit]").click({ force: true });

        cy.contains(`Connexion avec ${username} réussie.`)

        // // we should be redirected to /dashboard
        cy.url().should('include', '/projects')

        // // our auth cookie should be present
        cy.getCookie('sessionid').should('exist')
    })
})
