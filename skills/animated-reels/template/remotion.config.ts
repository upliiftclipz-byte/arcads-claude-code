import os from 'os';
import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);

// Use up to 6 render threads, but never more than this machine has cores.
Config.setConcurrency(Math.max(1, Math.min(6, os.cpus().length)));

// 'angle' uses the GPU (fast, best on a Mac). On a machine with no GPU, such as a cloud
// container, set REMOTION_GL=swangle.
Config.setChromiumOpenGlRenderer((process.env.REMOTION_GL as any) || 'angle');

// Remotion downloads its own headless Chrome on first render. Where that download is blocked,
// point REMOTION_BROWSER at a Chrome / Chromium headless shell that is already installed.
if (process.env.REMOTION_BROWSER) Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
