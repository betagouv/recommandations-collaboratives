import path from 'node:path';
import commonjs from '@rollup/plugin-commonjs';

const config = {
	root: path.resolve('./src'),
	base: '/static/',
	server: {
		host: '0.0.0.0',
		port: 3000,
		open: false,
		watch: {
			usePolling: true,
			disableGlobbing: false
		}
	},
	resolve: {
		extensions: ['.js', '.json']
	},
	build: {
		outDir: path.resolve('./dist'),
		assetsDir: '',
		manifest: true,
		emptyOutDir: true,
		target: 'es2020',
		lib: {
			entry: path.resolve('./src/lib/index.js'),
			name: 'DsrcUi',
			fileName: 'dsrc-ui'
		},
		rollupOptions: {
			plugins: [commonjs({ transformMixedEsModules: true })],
			external: [
				"alpinejs",
        "@gouvfr/dsfr/dist/dsfr.module"
			],
			output: {
				dir: path.resolve('./dist/js/'),
				format: 'esm',
				chunkFileNames: undefined
			}
		}
	}
};

export default config;
