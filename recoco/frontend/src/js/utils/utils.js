export function stringToColor(str, palette) {
  const defaultPalette = [
    '#fbaff5',
    '#79e7d5',
    '#fcb0a2',
    '#b6cffb',
    '#fde39c',
    '#fd9c9c',
    '#d6fd9c',
    '#af9cfd',
    '#9cb1fd',
    '#9cf2fd',
  ];
  const colors = palette || defaultPalette;

  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + (hash * 32 - hash); // Hash simple
  }

  const colorIndex = Math.abs(hash) % colors.length; // Assurer un index positif
  return colors[colorIndex];
}
