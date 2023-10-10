import projects from '../../../../fixtures/projects/projects.json'
import tutorials from '../../../../fixtures/training/challengesDefinition.json'
const discoverTaskTutorial = tutorials[5]

const currentProject = projects[1];

describe('I can go to tasks tab as a collectivity and see task discover tutorial', () => {

    it('creates a new task from an advisor', () => {
        cy.login("jean");
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains("Recommandations").click({ force: true })
        cy.url().should('include', '/actions')
        cy.createTask("new task");
    })

    it('can see the discover task tutorial hint', () => {
        cy.login("bob");
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains("Recommandations").click({ force: true })
        cy.url().should('include', '/actions')

        cy.get('[data-test-id="tutorial-hint"]').should('exist')

    })

    it('can start discover task tutorial', () => {
        cy.login("bob");
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains("Recommandations").click({ force: true })
        cy.url().should('include', '/actions')

        cy.get('[data-test-id="tutorial-hint"]').should('exist')
        cy.contains(discoverTaskTutorial.fields.name)

        cy.get('[data-test-id="start-tutorial-button"]').click({ force: true })
        cy.get('[data-test-id="tasks-discover-step-1"]').should('exist')
    })

    it('can end discover task tutorial', () => {
        cy.login("bob");
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains("Recommandations").click({ force: true })
        cy.url().should('include', '/actions')

        cy.get('[data-test-id="tutorial-hint"]').should('exist')
        cy.contains(discoverTaskTutorial.fields.name)

        cy.get('[data-test-id="end-tutorial-button"]').click({ force: true })
        cy.get('[data-test-id="tasks-discover-step-1"]').should('not.exist')
    })
})
