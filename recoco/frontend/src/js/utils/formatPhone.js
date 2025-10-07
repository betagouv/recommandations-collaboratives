/**
 * Formats a phone number by adding spaces between every two digits.
 * It replaces the +33 by 0 at the begining
 */
export function formatPhone(phone_number) {
  phone_number = String(phone_number).replace(' ', '');
  if (phone_number.startsWith('+33')) {
    phone_number = '0' + phone_number.slice(3);
  }
  return phone_number.match(/.{1,2}/g).join(' ');
}

export default formatPhone;
