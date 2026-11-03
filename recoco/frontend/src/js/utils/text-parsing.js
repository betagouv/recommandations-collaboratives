export function truncate(input, size = 30) {
  if (input.length > size) {
    const truncated = input.substring(0, size);

    // If the truncated string does not contain an opening <a> tag, we can safely truncate it
    if (!truncated.includes('<a')) {
      return `${truncated}...`;
    }

    // If the truncated string contains an opening <a> tag, we need to find the closing </a> tag
    const indexLink = input.indexOf('</a>');
    return `${input.substring(0, indexLink + 4)}...`;
  }
  return input;
}
