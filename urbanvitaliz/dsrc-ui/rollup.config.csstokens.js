import scss from 'rollup-plugin-scss';
import postcss from 'postcss';
import autoprefixer from 'autoprefixer';
import jitProps from 'postcss-jit-props';

/**
 * Preprocess scss in `src/styles/` to use plain CSS in library components
 */
export default {
	input: 'src/lib/styles/scss/tokens/index.js',
	output: { dir: '../../static/assets/css/', format: 'esm' },
	plugins: [
		scss({
			fileName: 'dsrc-csstokens.css',
			processor: () =>
				postcss([
					autoprefixer(),
					jitProps({
						files: ['../../static/assets/css/**/*.css']
					})
				]),
			watch: 'src/lib/styles/scss/tokens/'
		})
	]
};
