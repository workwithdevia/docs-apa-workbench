// The manifest supplies content; the library controls its rendering order.
#let report-content = (
  abstract: include("sections/abstract.typ"),
  introduction: include("sections/introduction.typ"),
  theoretical_framework: none,
  objectives: include("sections/objectives.typ"),
  materials_methods: include("sections/materials-methods.typ"),
  results: include("sections/results.typ"),
  discussion: include("sections/discussion.typ"),
  conclusion: include("sections/conclusion.typ"),
  appendices: none,
)
