from django.test import TestCase
from django.template import Template, Context
from urbanvitaliz.apps.crm.templatetags.phone_filters import format_phone

class PhoneFiltersTestCase(TestCase):
  def test_format_classic_mobile_33_phone(self):
    phone_number = '+33612345678'
    expected_output = '06 12 34 56 78'
    result = format_phone(phone_number)
    self.assertEqual(result, expected_output)

  def test_format_classic_phone(self):
    phone_number = '0123456789'
    expected_output = '01 23 45 67 89'
    result = format_phone(phone_number)
    self.assertEqual(result, expected_output)

  def test_format_classic_33_phone(self):
    phone_number = '+33123456789'
    expected_output = '01 23 45 67 89'
    result = format_phone(phone_number)
    self.assertEqual(result, expected_output)

  def test_format_classic_without_0_phone(self):
    phone_number = '123456789'
    expected_output = '12 34 56 78 9'
    result = format_phone(phone_number)
    self.assertEqual(result, expected_output)

  def test_format_broken_with_33_phone(self):
    phone_number = '+33'
    expected_output = '0'
    result = format_phone(phone_number)
    self.assertEqual(result, expected_output)

  def test_format_already_format_phone(self):
    phone_number = '01 23 45 67 89'
    expected_output = '01 23 45 67 89'
    result = format_phone(phone_number)
    self.assertEqual(result, expected_output)
