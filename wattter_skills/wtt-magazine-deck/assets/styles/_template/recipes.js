/* =============== STYLE_ID 专属动效 recipe ==============
   如果新风格只使用 core/subtle/cinematic 的通用 data-anim，可以保留本文件为空。
   如果定义 data-animate="recipe-name"，在这里实现进入/离开逻辑。 */
(function(){
  window.__STYLE_IDOnEnter = function(idx, slide) {
    if (!slide) return;
    slide.querySelectorAll('[data-anim]').forEach(function(el){
      el.classList.add('in');
    });
  };

  window.__STYLE_IDOnLeave = function(idx, slide) {
    if (!slide) return;
    slide.querySelectorAll('[data-anim]').forEach(function(el){
      el.classList.remove('in');
    });
  };
})();
