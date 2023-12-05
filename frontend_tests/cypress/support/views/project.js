/**
 * Common actions in the projects page
 */

const domElements = {
	// Project dashboard tabs
	ACTIONS_PATH:'/actions',
	ACTIONS_TAB:'[data-test-id="project-navigation-actions"]',

	// Project dashboard tabs
	OVERVIEW_PATH:'/presentation',
	OVERVIEW_TAB:'[data-test-id="project-navigation-overview"]',

	// Project dashboard tabs
	KNOWLEDGE_PATH:'/connaissance',
	KNOWLEDGE_TAB:'[data-test-id="project-navigation-knowledge"]',

	// Actions Tab - Tasks List
	TASK_CARD:'[data-test-id="task-kanban-topic"]',

	// Positioning Banner
	HEADER_BANNER_ADVISING_POSITION:'[data-test-id="header-banner-advising-position"]',
	BUTTON_JOIN_AS_ADVISOR:'[data-test-id="button-join-as-advisor"]',
}

class Project {
	dom

	constructor(dom) {
		this.dom = dom
	}

	// Navigation
	
	navigateToTab(tabName, path) {
		cy.get(tabName).click({force:true})
		cy.url().should('include', path)
	}

	navigateToActionsTab() {
		this.navigateToTab(this.dom.ACTIONS_TAB, this.dom.ACTIONS_PATH)
	}

	navigateToOverviewTab() {
		this.navigateToTab(this.dom.OVERVIEW_TAB, this.dom.OVERVIEW_PATH)
	}

	navigateToKnowledgeTab() {
		this.navigateToTab(this.dom.KNOWLEDGE_TAB, this.dom.KNOWLEDGE_PATH)
	}

	// Actions

	joinAsAdvisor() {
		cy.get(this.dom.BUTTON_JOIN_AS_ADVISOR).click({force:true}).then(() => {
			cy.get(this.dom.HEADER_BANNER_ADVISING_POSITION).should('not.exist')
		})
	}

	openTask() {
		cy.get(this.dom.TASK_CARD).click({force:true})
	}
}

const projectView = new Project(domElements)

export default projectView
