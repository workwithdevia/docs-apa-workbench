#import "sections/abstract.typ": abstract-content
#import "sections/introduction.typ": introduction-content
#import "sections/literature-review.typ": literature-content
#import "sections/method.typ": method-content
#import "sections/results.typ": results-content
#import "sections/discussion.typ": discussion-content
#import "sections/conclusion.typ": conclusion-content

#let paper-content = (
  abstract: abstract-content,
  introduction: introduction-content,
  literature_review: literature-content,
  method: method-content,
  results: results-content,
  discussion: discussion-content,
  conclusion: conclusion-content,
  acknowledgments: none,
  appendices: none,
)
