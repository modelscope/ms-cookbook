(() => {
  'use strict';
  const resolutions=new Map();
  function resolve(path){
    if(!resolutions.has(path))resolutions.set(path,(async()=>{
      const response=await fetch('/api'+path,{credentials:'same-origin',cache:'no-store'});
      const data=await response.json();if(!response.ok)throw Error(data.detail||'主页暂时无法打开，请稍后重试。');
      const url=new URL(data.profileUrl);
      if(url.protocol!=='https:'||url.hostname!=='modelscope.cn'||!url.pathname.startsWith('/profile/'))throw Error('主页地址无效。');
      return url;
    })().catch(error=>{resolutions.delete(path);throw error;}));
    return resolutions.get(path);
  }
  window.ReaderProfiles={bind(link){
    const path=link.getAttribute('href');
    if(!/^\/readers\/[^/]+\/profile$/.test(path||''))return;
    // Resolve while the comment is being displayed. A normal external anchor
    // works in browsers that block programmatically opened blank windows.
    resolve(path).then(url=>{link.href=url.href;}).catch(()=>{});
    link.addEventListener('click',async event=>{
      if(!/^\/readers\//.test(link.getAttribute('href')))return;
      event.preventDefault();
      // Reserve a top-level window in the click gesture. Studio wraps a direct
      // application redirect in an iframe, where ModelScope profiles are blocked.
      const popup=window.open('about:blank','_blank');if(popup)popup.opener=null;
      try{
        const url=await resolve(path);
        link.href=url.href;
        if(popup)popup.location.replace(url.href);
        else window.dispatchEvent(new CustomEvent('purplebook:profile-error',{detail:'主页地址已就绪，请再次点击用户名打开。'}));
      }catch(error){if(popup)popup.close();window.dispatchEvent(new CustomEvent('purplebook:profile-error',{detail:error.message}));}
    });
  }};
})();
