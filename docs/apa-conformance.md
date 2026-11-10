# APA 7 conformance notes

This project aims to implement common APA 7 student-paper conventions, but it is not affiliated with or certified by the American Psychological Association.

Implemented in this scaffold:

- Letter page and configurable margins.
- Page number in the upper-right header.
- Configurable font families and sizes for text, math and source code.
- First-line paragraph indentation and paragraph spacing controls.
- Heading levels 1–3.
- Explicit `apa-run-in-heading` helper for run-in heading patterns (levels 4 and 5).
- Student title page fields.
- Abstract and keywords.
- Figure and table labels/titles/notes, with in-flow placement by default.
- Native Typst bibliography using the built-in `apa` style.
- Labels and cross-references using Typst's native figure mechanism.

Must be verified visually and against the current APA Publication Manual before production use:

- Exact double-line spacing across all font families and line-box metrics.
- Complete professional title-page layout and author-note variants.
- Full heading behavior for nested level 4/5 paragraphs.
- Long-table pagination and table notes across pages.
- APA-specific edge cases in citations and bibliography output.
- Accessibility and tagged-PDF behavior in the target editor.

Use the official APA Style guidance and the current Publication Manual as normative sources. A template can automate layout but cannot determine whether a paper's content or references are substantively APA-compliant.
