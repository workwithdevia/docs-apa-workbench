#import "sections/abstract.typ": abstract-content
#import "sections/introduction.typ": introduction-content
#import "sections/objectives.typ": objectives-content
#import "sections/materials-methods.typ": materials-methods-content
#import "sections/results.typ": results-content
#import "sections/discussion.typ": discussion-content
#import "sections/conclusion.typ": conclusion-content

#let report-content = (
  abstract: abstract-content,
  introduction: introduction-content,
  theoretical_framework: none,
  objectives: objectives-content,
  materials_methods: materials-methods-content,
  results: results-content,
  discussion: discussion-content,
  conclusion: conclusion-content,
  appendices: none,
)
