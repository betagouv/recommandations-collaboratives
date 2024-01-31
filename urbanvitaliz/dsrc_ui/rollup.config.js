import terser from '@rollup/plugin-terser';
import resolve from '@rollup/plugin-node-resolve';

export default {
	// The source JavaScript files that we want to bundle
	input: 'src/lib/index.js',
	output: { dir: '../../static/assets/js/', format: 'esm' },
	plugins: [
		resolve({
			browser: true
		}),
		terser() // TODO: env based minification
	],
	watch: {
		include: 'src/**'
	}
};
