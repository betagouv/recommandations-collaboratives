import Ajv from 'ajv';

const ajv = new Ajv({ code: { esm: true } });

addFormats(ajv);

function generateValidator(schema) {
	validate = Ajv.compile(schema);
	return validate;
}

export default generateValidator;
