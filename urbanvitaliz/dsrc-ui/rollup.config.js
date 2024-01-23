import terser from '@rollup/plugin-terser';
import resolve from '@rollup/plugin-node-resolve';

import path from 'path';

export default {
	// The source JavaScript files that we want to bundle
	input: path.resolve('src/lib/index.js'),
	output: {
		format: 'esm',
		// The destination for our bundled JavaScript
		file: '../../static/assets/components/dsrc-main.js'
	},
	plugins: [
		resolve({
			browser: true
		}),
		terser() // TODO: env based minification
	]
};
