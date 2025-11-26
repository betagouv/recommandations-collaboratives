export function stringToColor(str, palette) {
  str = str.slice(0, 10);
  const defaultPalette = [
    '#667dcf', // Bleu foncé
    '#FB907D', // Rouge foncé
    '#D69978', // Orange foncé
    '#4A9DF7', // Bleu clair foncé
    '#FCC63A', // Jaune foncé
    '#58C5CF', // Turquoise foncé
    '#FA96F2', // Rose foncé
    '#FA794A', // Orange
    '#8ED654', // Vert
  ];
  const colors = palette || defaultPalette;

  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + (hash * 32 - hash); // Hash simple
  }

  const colorIndex = Math.abs(hash) % colors.length; // Assurer un index positif
  return colors[colorIndex];
}
