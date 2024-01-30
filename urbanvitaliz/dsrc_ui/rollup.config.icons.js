import * as glob from 'glob';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

function svgResolverPlugin() {
	return {
		name: 'svg-resolver',
		resolveId(source, importer) {
			if (source.endsWith('.svg')) {
				return path.resolve(path.dirname(importer), source);
			}
		},
		load(id) {
			if (id.endsWith('.svg')) {
				const relativePath = path.relative(
					'src/lib/',
					id.slice(0, id.length - path.extname(id).length)
				);
				const referenceId = this.emitFile({
					type: 'asset',
					name: `${relativePath}${path.extname(id)}`,
					source: fs.readFileSync(id)
				});
				return `export default import.meta.ROLLUP_FILE_URL_${referenceId};`;
			}
		}
	};
}

export default {
	// The source JavaScript files that we want to bundle
	input: {
		...Object.fromEntries(
			glob.sync('src/lib/icons/**/*.js').map((file) => [
				// This removes `src/` as well as the file extension from each
				// file, so e.g. src/nested/foo.js becomes nested/foo
				path.relative('src/lib/', file.slice(0, file.length - path.extname(file).length)),
				// This expands the relative paths to absolute paths, so e.g.
				// src/nested/foo becomes /project/src/nested/foo.js
				fileURLToPath(new URL(file, import.meta.url))
			])
		)
	},
	output: {
		dir: '../../static/assets/',
		format: 'esm',
		assetFileNames: '[name]-[extname]'
	},
	plugins: [svgResolverPlugin()],
	watch: {
		include: 'src/**'
	}
};
