const taskName = "to inprogress"

describe('I can go to tasks tab', () => {
    beforeEach(() => {

        cy.visit('/')
    
        cy.get('[data-test-id="fr-consent-banner"]').find('[data-test-id="button-consent-accept-all"]').click({ force: true })
        cy.login("jean");
        cy.createProject("qsdzed")
    })

    it('drags n drops no status task to in progress status', () => {

        cy.becomeAdvisor();

        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask(taskName);

        cy.get('[data-test-id="kanban-tasks-switch-button"]').click({ force: true })
        cy.get('[data-test-id="kanban-tasks-switch-button"]').should('have.class', 'active')

        let droppableCoords = {}

        cy.get('[data-test-id="inprogress-drag-target"]').then($el => {
            droppableCoords = {
                x: $el[0].getBoundingClientRect().x,
                y: $el[0].getBoundingClientRect().y
            }

            console.log(droppableCoords)

            cy.get('[data-test-id="task-kanban-item-draggable"]')
                .trigger('mousedown', { eventConstructor: 'MouseEvent' }, { which: 1 })
                .trigger('mousemove', { eventConstructor: 'MouseEvent' }, { clientX: droppableCoords.x, clientY: droppableCoords.y })
                .trigger('mouseup', { eventConstructor: 'MouseEvent' }, { force: true })
        })

        // TODO : finish this test to trigger api calls
    })
})
