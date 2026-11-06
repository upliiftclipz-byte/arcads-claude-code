// Fonts are bundled from npm (@fontsource), not fetched from Google Fonts at render time,
// so renders work offline and behind proxies. To change a font, add its @fontsource
// package and import its .woff2 files here.
import {loadFont} from '@remotion/fonts';
import serif400 from '@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2';
import serif400i from '@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2';
import inter400 from '@fontsource/inter/files/inter-latin-400-normal.woff2';
import inter500 from '@fontsource/inter/files/inter-latin-500-normal.woff2';
import inter600 from '@fontsource/inter/files/inter-latin-600-normal.woff2';
import inter700 from '@fontsource/inter/files/inter-latin-700-normal.woff2';
import inter800 from '@fontsource/inter/files/inter-latin-800-normal.woff2';
import inter900 from '@fontsource/inter/files/inter-latin-900-normal.woff2';
import mono400 from '@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2';
import mono500 from '@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2';
import mono700 from '@fontsource/jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2';

const FONTS: [string, string, string, 'normal' | 'italic'][] = [
  ['Instrument Serif', serif400, '400', 'normal'],
  ['Instrument Serif', serif400i, '400', 'italic'],
  ['Inter', inter400, '400', 'normal'],
  ['Inter', inter500, '500', 'normal'],
  ['Inter', inter600, '600', 'normal'],
  ['Inter', inter700, '700', 'normal'],
  ['Inter', inter800, '800', 'normal'],
  ['Inter', inter900, '900', 'normal'],
  ['JetBrains Mono', mono400, '400', 'normal'],
  ['JetBrains Mono', mono500, '500', 'normal'],
  ['JetBrains Mono', mono700, '700', 'normal'],
];
for (const [family, url, weight, style] of FONTS) loadFont({family, url, weight, style});

export const F = {
  serif: '"Instrument Serif", serif',
  sans: 'Inter, sans-serif',
  mono: '"JetBrains Mono", monospace',
};

// Anthropic / Claude palette
export const C = {
  bg: '#FAF9F5',
  ink: '#141413',
  ink2: '#3D3D3A',
  muted: '#8C8A82',
  faint: '#B0AEA5',
  line: '#E8E6DC',
  line2: '#DEDACE',
  card: '#FFFFFF',
  chip: '#F3F1EA',
  orange: '#D97757',
  orangeDeep: '#C2613F',
  orangeSoft: '#F6E3D9',
  orangeTint: '#FBEFE8',
  green: '#4E9A5B',
  red: '#C94A3A',
  redSoft: '#FBE7E3',
};

export const W = 1080;
export const H = 1920;

export const SHADOW = {
  sm: '0 1px 2px rgba(20,20,19,0.05), 0 4px 14px rgba(70,45,25,0.07)',
  md: '0 1px 2px rgba(20,20,19,0.05), 0 10px 30px rgba(70,45,25,0.09), 0 30px 70px rgba(70,45,25,0.10)',
  lg: '0 1px 3px rgba(20,20,19,0.06), 0 14px 40px rgba(70,45,25,0.10), 0 50px 120px rgba(70,45,25,0.14)',
};
