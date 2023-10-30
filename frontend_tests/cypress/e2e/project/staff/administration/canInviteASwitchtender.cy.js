import projects from '../../../../fixtures/projects/projects.json'
import users from '../../../../fixtures/users/users.json'

const currentProject = projects[1]
const userToInvite = users[3]

describe('I can go to administration area of a project and invite a switchtender', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to the administration tab of a project and invite a switchtender', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.get("[data-test-id='navigation-administration-tab']").click({force:true})
        cy.url().should('include', '/administration')

        cy.contains('Inviter un conseiller').click({ force: true });

        cy.get('.invite-switchtender-modal-email')
            .type(`${userToInvite.fields.email}`, { force: true })
            .should('have.value', `${userToInvite.fields.email}`)

        cy.get('.invite-switchtender-modal-textarea')
            .type(`Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon projet friche numéro 2`, { force: true })
            .should('have.value', `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon projet friche numéro 2`)
            
        cy.get('.invite-switchtender-modal-button').click({ force: true })
        cy.contains(`Un courriel d'invitation à rejoindre le projet a été envoyé à ${userToInvite.fields.email}`)

        cy.get("[data-test-id='administration-advisor-invitation-list']").siblings('ul').children('li').contains(userToInvite.fields.email)
    })
})
