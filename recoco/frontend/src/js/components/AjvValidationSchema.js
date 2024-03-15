import Alpine from 'alpinejs';
import { schemaOnboardingStep1FormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSigninForm';
import { schemaOnboardingEmailFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingEmailForm';

Alpine.data('AjvValidationSchema', (schemaValidatorName) => {
  const schemasValidator = {
    schemaOnboardingStep1FormValidator: schemaOnboardingStep1FormValidator,
    schemaOnboardingEmailFormValidator: schemaOnboardingEmailFormValidator,
  };
  return {
    schemaValidator: schemasValidator[schemaValidatorName],
  };
});
