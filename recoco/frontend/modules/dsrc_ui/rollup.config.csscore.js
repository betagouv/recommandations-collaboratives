import scss from 'rollup-plugin-scss';
import postcss from 'postcss';
import autoprefixer from 'autoprefixer';
import jitProps from 'postcss-jit-props';

/**
 * Preprocess scss in `src/styles/` to use plain CSS in library components
 */
export default {
	input: 'src/lib/styles/scss/core/index.js',
	output: { dir: './dist/css/', format: 'esm' },
	plugins: [
		scss({
			fileName: 'dsrc-csscore.css',
			processor: () =>
				postcss([
					jitProps({
						files: ['./dist/**/*.css']
					}),
					autoprefixer()
				]),
			watch: 'src/lib/styles/scss/core/'
		})
	]
};
