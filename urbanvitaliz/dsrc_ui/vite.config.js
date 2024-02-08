import * as glob from 'glob';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const config = {
	plugins: [],
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
		rollupOptions: {
			input: {
				...Object.fromEntries(
					glob.sync('src/lib/components/**/*.js').map((file) => [
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
				dir: '../../static/assets/js/',
				format: 'esm',
				chunkFileNames: undefined,
				assetFileNames: '[name][extname]'
			}
		}
	},
	optimizeDeps: {
		include: ['ajv']
	},
	test: {
		globals: true
	}
};

export default config;
