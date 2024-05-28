import scss from 'rollup-plugin-scss';

/**
 * Preprocess scss in `src/styles/` to use plain CSS in library components
 */
export default {
	input: 'src/lib/styles/scss/tokens/index.js',
	// The destination for our bundled CSS (here: the Django project's root `static` folder)
	output: { dir: './dist/css/', format: 'esm' },
	plugins: [
		scss({
			fileName: 'dsrc-csstokens.css',
			watch: 'src/lib/styles/scss/tokens/',
		}),
	],
};
