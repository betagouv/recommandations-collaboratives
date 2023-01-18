import md5 from 'md5'

export function gravatar_url(email, size=50, name="Inconnu") {
    if (name.trim() == '') name = "Inconnu";

    const hash = md5(email);
    const encoded_fallback_uri = encodeURIComponent(`https://ui-avatars.com/api/${name}/${size}`);

    return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${encoded_fallback_uri}`
}
