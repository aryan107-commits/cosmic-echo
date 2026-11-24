# COSMIC ECHO — External AI Review Briefs

These briefs are for independent review of the website added under \`docs/\`. The GitHub repository remains the single source of truth. Do not merge or replace code automatically; return findings for human review.

## 1. Claude — Frontend engineering and interaction review

Review these files:
- \`docs/index.html\`
- \`docs/styles.css\`
- \`docs/app.js\`

Tasks:
1. Audit semantic HTML, keyboard navigation, focus states, accessible names, contrast, responsive behaviour and reduced-motion support.
2. Inspect the mobile navigation, synthetic field layer controls, local image upload, brightness/contrast/gamma controls and preview export.
3. Look for JavaScript runtime errors, layout overflow, inefficient canvas work, memory leaks and browser compatibility issues.
4. Check that the site works as a static GitHub Pages site served from the repository's \`/docs\` directory, including relative asset paths.
5. Recommend concrete, minimal changes. Do not add a framework or build system unless there is a compelling technical reason.

Return:
- Findings ranked Critical / High / Medium / Low.
- Exact file and line references.
- Reproducible test steps.
- A proposed patch or code snippets for each confirmed issue.
- A short list of items that already work well.

Do not change the scientific meaning of the project.

## 2. Gemini — Astronomy and scientific-accuracy review

Review the website copy against the repository scripts and authoritative NASA/SPHEREx, IRSA and Photutils documentation.

Tasks:
1. Verify the descriptions of SPHEREx, IRSA archive access, FITS image layers, zodiacal-light subtraction and the role of variance/flag layers.
2. Verify the description of the current V2 implementation: source detection, mask combination, Photutils Background2D, MedianBackground, SigmaClip, background RMS and corrected residual.
3. Check the stated V2 defaults against \`scripts/photutils_background_v2.py\`: box size, detection threshold, mask dilation radius and other parameters mentioned on the site.
4. Verify the validation description against \`scripts/audit_mask_decomposition.py\` and the V3 validation scripts.
5. Flag any sentence that overstates the project's maturity, implies a scientific result not supported by the repository, or confuses an illustrative graphic with observational data.

Return:
- A claim-by-claim table: website wording, verdict, evidence/source, recommended correction.
- Exact references to repository files and authoritative external documentation.
- A list of scientific statements that should be removed or qualified.

Do not infer results from code that has not been run on the relevant observation.

## 3. Kimi — Independent red-team audit

Conduct an independent audit without relying on Claude's conclusions.

Tasks:
1. Challenge every scientific claim and project-status label for unsupported certainty.
2. Test the user experience on narrow mobile, tablet and desktop layouts.
3. Inspect the local image upload flow for privacy, file handling, memory cleanup and error handling.
4. Check canvas rendering, display transformations, preview export, navigation, keyboard use and reduced-motion behaviour.
5. Identify performance bottlenecks, browser edge cases, accessibility failures and confusing interactions.
6. Consider whether a first-time visitor can understand the project's purpose, current scope and limitations within one minute.

Return:
- A severity-ranked audit with evidence.
- Reproduction steps for each issue.
- The three most important improvements.
- A go/no-go recommendation for a public research-project landing page.

Do not assume that the synthetic field is real astronomical data.

## Integration protocol

1. Keep the GitHub repository as the source of truth.
2. Treat each AI review as a proposal, not an automatic approval.
3. Reconcile disagreements against the source code and authoritative scientific documentation.
4. Do not describe the pipeline as scientifically validated without adequate evidence.
5. The repository owner approves the final integration.
