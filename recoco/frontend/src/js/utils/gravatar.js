import md5 from 'md5';

const cache = {};

export function gravatar_url(
  email,
  size = 50,
  name = 'Inconnu',
  hexColor = 'e6e6e6'
) {
  hexColor = hexColor.replace('#', '');
  if (!cache[email]) {
    if (name.trim() == '') name = 'Inconnu';

    const hash = md5(email);
    const encoded_fallback_uri = encodeURIComponent(
      `https://ui-avatars.com/api/${name}/${size}/${hexColor}/000000`
    ).trimEnd();

    cache[email] =
      `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${encoded_fallback_uri}`;
  }

  return cache[email];
}
