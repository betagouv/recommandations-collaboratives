import project from '../../../fixtures/projects/project.json'

describe('I can create a project when im not logged in', () => {

    beforeEach(() => {
    })

    it('goes to the onboarding page and create a project with the main CTA without an account and check firstname & lastname information about the project owner', () => {
        cy.session("test", () => {
            cy.visit('/')

            cy.get('a').should('have.class', 'fr-btn fr-text--xl custom-button').contains('Solliciter UrbanVitaliz').click({ force: true })

            cy.url().should('include', '/onboarding/')

            cy.get('#id_first_name')
                .type(project.firstname, { force: true })
                .should('have.value', project.firstname)

            cy.get('#id_email')
                .type(project.email, { force: true })
                .should('have.value', project.email)

            cy.get('#id_last_name')
                .type(project.lastname, { force: true })
                .should('have.value', project.lastname)

            cy.get('#id_phone')
                .type(project.phone, { force: true })
                .should('have.value', project.phone)

            cy.get('#id_org_name')
                .type(project.org, { force: true })
                .should('have.value', project.org)

            cy.get('#id_name')
                .type(project.name, { force: true })
                .should('have.value', project.name)

            cy.get('#input-project-address')
                .type(project.address, { force: true })
                .should('have.value', project.address)

            cy.get('[name=postcode]')
                .type(project.zipcode, { force: true })
                .should('have.value', project.zipcode)

            cy.get('#input-project-description')
                .type(project.description, { force: true })
                .should('have.value', project.description)

            cy.get('#id_response_1')
                .type(project.response1, { force: true })
                .should('have.value', project.response1)

            cy.get('#id_response_2_0')
                .check({ force: true })

            cy.document().then((doc) => {
                var iframe = doc.getElementById('id_captcha').querySelector('iframe');
                var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
                innerDoc.querySelector('.recaptcha-checkbox').click()
            })

            cy.wait(500)

            cy.contains('Envoyer ma demande').click({ force: true });

            cy.contains(project.name).click({ force: true });

            cy.contains(project.firstname)
            cy.contains(project.lastname)
        })
    })
})
