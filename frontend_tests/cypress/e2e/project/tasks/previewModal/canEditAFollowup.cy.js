import projects from '../../../../fixtures/projects/projects.json'
import tasks from '../../../../fixtures/projects/tasks.json'

const currentProject = projects[1];
const task1 = tasks[0]
const task2 = tasks[1]
const task3 = tasks[2]
const task4 = tasks[3]


describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('list all inline tasks', () => {
        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.contains("Thématique").should('have.class', 'active')

        cy.contains(task1.fields.intent).click({ force: true })
        cy.contains(task1.fields.intent)

        const now = new Date();

        cy.get('.ProseMirror p').then(($el) => {
            const el = $el.get(0) //native DOM element
            el.innerHTML = `test ${now}`
        })

        cy.contains('Enregistrer').click({ force: true })

    })
})
