export function stringToColor(str, palette) {
  str = str.slice(0, 10);
  const defaultPalette = [
    '#fbaff5', // Rose
    '#79e7d5', // Turquoise
    '#fcb0a2', // Rouge
    '#b6cffb', // Bleu
    '#fde39c', // Jaune
    '#9cb1fd', // Bleu foncé
    '#d6fd9c', // Vert
    '#af9cfd', // Violet
    '#9cf2fd', // Bleu clair
  ];
  const colors = palette || defaultPalette;

  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + (hash * 32 - hash); // Hash simple
  }

  const colorIndex = Math.abs(hash) % colors.length; // Assurer un index positif
  return colors[colorIndex];
}
