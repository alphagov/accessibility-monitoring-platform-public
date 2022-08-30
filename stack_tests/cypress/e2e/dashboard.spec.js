/// <reference types="cypress" />

context('Platform dashboard', () => {
  beforeEach(() => {
    cy.visit('http://web:8001/')
  })

  it('cy.window() - get the global window object', () => {
    cy.window().should('have.property', 'top')
  })

  it('cy.document() - get the document object', () => {
    cy.document().should('have.property', 'charset').and('eq', 'UTF-8')
  })

  it('cy.title() - get the title', () => {
    cy.title().should('include', 'Dashboard')
  })
})
