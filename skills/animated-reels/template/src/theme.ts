import {loadFont as loadSerif} from '@remotion/google-fonts/InstrumentSerif';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';

const serif = loadSerif('normal', {weights: ['400'], subsets: ['latin']});
loadSerif('italic', {weights: ['400'], subsets: ['latin']});
const inter = loadInter('normal', {weights: ['400', '500', '600', '700', '800', '900'], subsets: ['latin']});
const mono = loadMono('normal', {weights: ['400', '500', '700'], subsets: ['latin']});

export const F = {
  serif: serif.fontFamily,
  sans: inter.fontFamily,
  mono: mono.fontFamily,
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
