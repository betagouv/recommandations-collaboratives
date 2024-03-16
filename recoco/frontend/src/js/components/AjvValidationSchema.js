import Alpine from 'alpinejs';
import { schemaOnboardingStep1SignupFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSignupForm';
import { schemaOnboardingEmailFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingEmailForm';
import { schemaOnboardingStep1SigninFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSigninForm';

Alpine.data('AjvValidationSchema', (schemaValidatorName) => {
  const schemasValidator = {
    schemaOnboardingStep1SignupFormValidator:
      schemaOnboardingStep1SignupFormValidator,
    schemaOnboardingStep1SigninFormValidator:
      schemaOnboardingStep1SigninFormValidator,
    schemaOnboardingEmailFormValidator: schemaOnboardingEmailFormValidator,
  };
  return {
    schemaValidator: schemasValidator[schemaValidatorName],
  };
});
