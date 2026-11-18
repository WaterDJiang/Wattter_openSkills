import {paint, sampleWorld} from './shared/world.js';
export {sampleWorld};
export const draw = (ctx, state) => paint(ctx, state, 1);
export const drawTransition = (ctx, state) => paint(ctx, state, state.mix);
