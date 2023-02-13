import projects from '../../../fixtures/projects/projects.json'
import users from '../../../fixtures/users/users.json'

const currentProject = projects[1];
const currentUser = users[4]

console.log(currentUser);

describe('I can see general informations', () => {

    beforeEach(() => {
        cy.login(currentUser.fields.first_name.toLowerCase());
    })

    it('goes to the overview page and read project informations', () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.contains(currentProject.fields.name)
        cy.contains(currentProject.fields.description)

        cy.contains("Bob Collectivité")
        cy.contains(currentUser.fields.email)
        cy.contains(currentUser.fields.first_name)
        cy.contains(currentUser.fields.last_name)
        cy.contains("Organisation de test")
        cy.contains("bob@test.fr")
        cy.contains("+33101010101")

        cy.contains("Jean Conseille")

        cy.contains("Bob Collectivité")
    })
})
