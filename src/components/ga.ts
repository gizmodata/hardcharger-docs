// The switch between the public site and the old private preview. Hardcharger has shipped
// (2026-11-17), so every build is the public site unless DOCS_GA=false is set explicitly: no
// preview banner, no noindex tag. The pages no longer carry preview-only text.
const setting = import.meta.env.DOCS_GA ?? process.env.DOCS_GA;
export const ga = setting !== 'false';
