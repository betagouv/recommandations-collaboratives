import Alpine from 'alpinejs';
import { schemaOnboardingStep1SignupFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSignupForm';
import { schemaOnboardingEmailFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingEmailForm';
import { schemaOnboardingStep1SigninFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSigninForm';
import { schemaOnboardingStep2ProjectFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingProjectForm';
import { schemaOnboardingPrefillSignupFormValidator } from '../utils/ajv/schema/ajv.schema.PrefillSignupForm';
import { schemaPrefillProjectFormValidator } from '../utils/ajv/schema/ajv.schema.PrefillProjectForm';

Alpine.data('AjvValidationSchema', (schemaValidatorName) => {
  const schemasValidator = {
    schemaOnboardingStep1SignupFormValidator,
    schemaOnboardingStep1SigninFormValidator,
    schemaOnboardingEmailFormValidator,
    schemaOnboardingStep2ProjectFormValidator,
    schemaOnboardingPrefillSignupFormValidator,
    schemaPrefillProjectFormValidator,
  };
  return {
    schemaValidator: schemasValidator[schemaValidatorName],
  };
});
