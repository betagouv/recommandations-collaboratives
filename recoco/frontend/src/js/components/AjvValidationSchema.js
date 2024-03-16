import Alpine from 'alpinejs';
import { schemaOnboardingStep1SignupFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSignupForm';
import { schemaOnboardingEmailFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingEmailForm';
import { schemaOnboardingStep1SigninFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSigninForm';
import { schemaOnboardingStep2ProjectFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingProjectForm';

Alpine.data('AjvValidationSchema', (schemaValidatorName) => {
  const schemasValidator = {
    schemaOnboardingStep1SignupFormValidator,
    schemaOnboardingStep1SigninFormValidator,
    schemaOnboardingEmailFormValidator,
    schemaOnboardingStep2ProjectFormValidator,
  };
  return {
    schemaValidator: schemasValidator[schemaValidatorName],
  };
});
