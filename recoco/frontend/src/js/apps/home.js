import '../components/ModalVideo';

import '../components/DsrcFormValidatorActivate';
import {schemaOnboardingEmailFormValidator} from '../utils/ajv/schema/ajv.schema.OnboardingEmailForm';
import Alpine from 'alpinejs';

Alpine.data('AjvValidationSchema', () => {
  return { schemaOnboardingEmailFormValidator };
});
