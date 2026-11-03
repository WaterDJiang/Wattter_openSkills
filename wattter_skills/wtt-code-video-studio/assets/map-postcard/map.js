/* One entry for the default spatial postcard and the explicitly requested old scroll. */
(function(root){'use strict';
const node=typeof module!=='undefined'&&module.exports;
const P=node?require('./presentation.js'):root.PostcardPresentation;
const Legacy=node?require('./legacy-scroll.js'):root.LegacyScrollPostcard;
const Spatial=node?require('./world.js'):root.SpatialPostcard;
const VIEWS=['multi-angle','top-down','isometric','scroll-top-down'];
function resolve(config={}){
 if(!config||typeof config!=='object'||Array.isArray(config))throw Error('config须为对象');
 const c={season:'春',scene:'village',seed:20261103,viewProfile:'multi-angle',palette:'vivid',paletteOverrides:{},...config};
 if(!VIEWS.includes(c.viewProfile))throw Error('viewProfile须为multi-angle/top-down/isometric/scroll-top-down');
 if(c.reveal===undefined)c.reveal=c.viewProfile==='scroll-top-down';
 if(!['village','city'].includes(c.scene))throw Error('scene须为village/city');
 if(!Number.isInteger(c.seed))throw Error('seed须为整数');
 if(c.reveal!==undefined&&typeof c.reveal!=='boolean')throw Error('reveal须为布尔值');
 if(c.labels!==undefined&&typeof c.labels!=='boolean')throw Error('labels须为布尔值');
 for(const [key,max]of [['latitude',90],['longitude',180]])if(c[key]!=null&&(!Number.isFinite(c[key])||Math.abs(c[key])>max))throw Error('无效坐标 '+key);
 P.seasonPalette(c.season,{palette:c.palette,overrides:c.paletteOverrides});return c;
}
function make(canvas,config={}){
 const resolved=resolve(config),colors=P.seasonPalette(resolved.season,{palette:resolved.palette,overrides:resolved.paletteOverrides});
 const movie=resolved.viewProfile==='scroll-top-down'?Legacy.make(canvas,resolved):Spatial.make(canvas,resolved,colors),draw=movie.frame,c=canvas.getContext('2d');
 movie.frame=(i,options={})=>{if(!Number.isInteger(i))throw Error('frame index must be integer');if(c.reset)c.reset();else{c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';c.textBaseline='alphabetic';c.setLineDash([]);}return draw(i,options);};
 return {...movie,config:resolved,colors};
}
const api={make,resolve,N:Legacy.N,H:Legacy.H,model:Legacy.model,river:Legacy.river,road:Legacy.road,mod:Legacy.mod};if(node)module.exports=api;else root.MapPostcard=api;
})(typeof window==='undefined'?globalThis:window);
