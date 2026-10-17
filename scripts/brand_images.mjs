// Writes public/favicon.png (the GizmoData hex logo) and public/og.png (the social card,
// the Hardcharger banner) from src/assets. Run: node scripts/brand_images.mjs
import sharp from 'sharp';

await sharp('src/assets/gizmodata-logo.png')
	.resize({ width: 64, height: 64, fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
	.png()
	.toFile('public/favicon.png');
await sharp('src/assets/banners/hardcharger-banner.svg', { density: 144 })
	.resize({ width: 1280, height: 400 })
	.png()
	.toFile('public/og.png');
console.log('wrote public/favicon.png and public/og.png');
