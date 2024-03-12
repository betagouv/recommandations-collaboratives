import * as glob from 'glob';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import terser from '@rollup/plugin-terser';
import resolve from '@rollup/plugin-node-resolve';

export default {
	// The source JavaScript files that we want to bundle
	input: {
		...Object.fromEntries(
			glob.sync('src/ext/**/*.js').map((file) => [
				// This removes `src/` as well as the file extension from each
				// file, so e.g. src/nested/foo.js becomes nested/foo
				path.relative('src/ext/', file.slice(0, file.length - path.extname(file).length)),
				// This expands the relative paths to absolute paths, so e.g.
				// src/nested/foo becomes /project/src/nested/foo.js
				fileURLToPath(new URL(file, import.meta.url))
			])
		)
	},
	output: { dir: './dist/js/', format: 'esm' },
	plugins: [
		resolve({
			browser: true
		}),
		// terser() // TODO: env based minification
	],
	watch: {
		include: 'src/**'
	}
};
