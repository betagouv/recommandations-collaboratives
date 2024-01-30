import { copy } from '@web/rollup-plugin-copy';

export default {
	input: 'src/lib/fonts/index.js',
	output: {
		dir: '../../static/assets/',
		format: 'esm',
		assetFileNames: '[name][extname]'
	},
	plugins: [copy({ patterns: '**/*.{woff,woff2}', rootDir: './src/lib/' })],
	watch: {
		include: 'src/**'
	}
};
