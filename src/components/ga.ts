// The one switch between the private preview and the public site: DOCS_GA=true at build time
// (README, "Private preview and GA"). It drops the preview banner and the noindex tag, hides
// <Preview> content and shows <Ga> content.
export const ga = import.meta.env.DOCS_GA === 'true' || process.env.DOCS_GA === 'true';
