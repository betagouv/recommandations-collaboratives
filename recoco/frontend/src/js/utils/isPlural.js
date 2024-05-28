export function isPlural(singularString, pluralString, count) {
  return count > 1 ? pluralString : singularString;
}
