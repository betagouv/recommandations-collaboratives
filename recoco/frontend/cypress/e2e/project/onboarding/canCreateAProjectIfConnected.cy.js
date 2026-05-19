describe("I can create a project if i'm connected @deposer-projet @critical", () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to the onboarding process step by step and create a project ', () => {
    cy.createProject('Coucou');
  });

  it('goes to the onboarding process step by step and create a project without any adress ', () => {
    cy.createProject('Project without location', {
      name: 'Friche nomade',
      location: '',
      postcode: 42424,
      description: 'Je suis une friche nomade',
    });
  });
});
