import '../../css/onboarding.css';
import '../components/CitySelect';

import '../components/DsrcFormValidatorActivate';
import {schemaOnboardingStep1FormValidator} from '../utils/ajv/schema/ajv.schema.OnboardingSigninForm';
import Alpine from 'alpinejs';

Alpine.data('AjvValidationSchema', () => {
  return { schemaOnboardingStep1FormValidator };
});
