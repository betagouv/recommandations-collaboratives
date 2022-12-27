export function generateGravatarUrl(person, size = 50) {
    const hash = md5(person.email);
    let name = `${person.first_name}+${person.last_name}`;
    if (name.trim() === "+") name = "Inconnu";
    const encoded_fallback_uri = encodeURIComponent(`https://ui-avatars.com/api/${name}/${size}`);
    return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${encoded_fallback_uri}`
}
