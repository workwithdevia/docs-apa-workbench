// The manifest supplies content; the library controls its rendering order.
#let paper-content = (
  abstract: include("sections/abstract.typ"),
  introduction: include("sections/introduction.typ"),
  literature_review: include("sections/literature-review.typ"),
  method: include("sections/method.typ"),
  results: include("sections/results.typ"),
  discussion: include("sections/discussion.typ"),
  conclusion: include("sections/conclusion.typ"),
  acknowledgments: none,
  appendices: none,
)
