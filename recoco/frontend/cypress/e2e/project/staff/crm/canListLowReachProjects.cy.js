describe('I can browse the low reach projects page in CRM @page-crm-dossiers-a-relancer', () => {
  const lowReachUrl = '/crm/low-reach-projects';
  const csvUrl = '/crm/low-reach-projects-csv';

  beforeEach(() => {
    cy.login('staff');
    cy.visit(lowReachUrl);
  });

  it('displays the low reach projects page with its filters', () => {
    cy.get('[data-test-id="low-reach-title"]').should('contain.text', 'relancer');
    cy.contains('Vous trouverez ici tous les dossiers').should('be.visible');
    cy.get('[data-test-id="low-reach-table"]').should('be.visible');

    // Filter controls introduced by the rework are present
    cy.get('#days-filter').should('exist');
    cy.get('#status-filter').should('exist');
    cy.get('#mine-only-toggle').should('exist');
    cy.get('[data-test-id="low-reach-csv-export"]').should('be.visible');
  });

  it('keeps the "last activity" filter in the url and selection', () => {
    cy.get('#days-filter').select('30'); // triggers form submit (onchange)
    cy.url().should('include', 'days=30');
    cy.get('#days-filter').should('have.value', '30');
  });

  it('keeps the "status" filter in the url and selection', () => {
    cy.get('#status-filter').select('low_read'); // triggers form submit (onchange)
    cy.url().should('include', 'status=low_read');
    cy.get('#status-filter').should('have.value', 'low_read');
    cy.contains('Recos non lues').should('be.visible');
  });

  it('keeps the "only my projects" toggle in the url', () => {
    cy.get('#mine-only-toggle').check({ force: true }); // triggers form submit
    cy.url().should('include', 'mine=1');
    cy.get('#mine-only-toggle').should('be.checked');
  });

  it('exports the filtered low reach projects as a CSV file', () => {
    // The export keeps the active filters and returns a downloadable CSV.
    cy.request(`${csvUrl}?days=0&status=no_reaction`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.headers['content-type']).to.include('text/csv');
      expect(response.headers['content-disposition'])
        .to.include('attachment')
        .and.to.include('projets-a-relancer')
        .and.to.include('.csv');
      // Header row of the export is always present, even with no matching project.
      expect(response.body).to.include('nom_dossier');
    });
  });
});
