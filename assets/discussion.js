(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const el = (tag, text, cls) => { const n=document.createElement(tag); if(text)n.textContent=text; if(cls)n.className=cls; return n; };
  let session={user:null,csrf:'',loginEnabled:false}, chapter='', blocks=[], items=[], next=null, generation=0, anchor=null, busy=false;
  const account=el('div',null,'reading-account');
  $('#headerAccountArea').append(account);
  const panel=el('section',null,'chapter-discussion'); panel.id='chapterDiscussion'; panel.setAttribute('aria-label','本章笔记与留言');
  $('.chapter-pager').after(panel);
  const title=el('h2','一起读这一章');
  const hint=el('p','选择正文中的一段文字，可以划线或写下想法。','discussion-hint');
  const tabs=el('div',null,'discussion-tabs');
  const notesButton=el('button','划线与想法'); notesButton.type='button';
  const commentsButton=el('button','章节留言'); commentsButton.type='button';
  tabs.append(notesButton,commentsButton);
  const list=el('div',null,'discussion-list'); list.setAttribute('aria-live','polite');
  const more=el('button','加载更多','discussion-more'); more.type='button'; more.hidden=true;
  const form=el('form',null,'discussion-form');
  const label=el('label','读完这一章，你有什么想法？'); label.htmlFor='chapterMessage';
  const textarea=el('textarea'); textarea.id='chapterMessage'; textarea.maxLength=2000; textarea.rows=3; textarea.placeholder='分享你的实践、疑问或补充…';
  const submit=el('button','发表留言','discussion-primary'); submit.type='submit';
  const formHint=el('p','留言对所有读者可见。','discussion-hint');
  form.append(label,textarea,formHint,submit);
  const status=el('p',null,'discussion-status'); status.setAttribute('role','status');
  const replyHint=el('p',null,'discussion-reply-hint'),cancelReply=el('button','取消回复');cancelReply.type='button';
  form.prepend(replyHint);let replyTo=null;
  function setReply(entry){replyTo=entry;replyHint.replaceChildren();replyHint.hidden=!entry;label.textContent=entry?'回复 '+entry.name:'读完这一章，你有什么想法？';submit.textContent=entry?'发表回复':'发表留言';if(entry)replyHint.append(el('span','正在回复：'+entry.text),cancelReply);}
  cancelReply.onclick=()=>setReply(null);setReply(null);
  panel.append(title,hint,tabs,list,more,form,status);
  let tab='comment';
  const discussionJump=el('button','笔记与留言');discussionJump.type='button';discussionJump.onclick=()=>panel.scrollIntoView({block:'start',behavior:'smooth'});$('.reading-tools').append(discussionJump);
  const toast=el('p',null,'reading-toast');toast.hidden=true;toast.setAttribute('role','status');document.body.append(toast);let toastTimer;
  function notify(message){toast.textContent=message;toast.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>{toast.hidden=true;},3500);}
  const selectionBar=el('div',null,'selection-actions'); selectionBar.hidden=true; selectionBar.setAttribute('aria-label','选中文字操作');
  const save=el('button','划线 · 仅自己可见'), write=el('button','写想法'), dismiss=el('button','取消');
  selectionBar.append(save,write,dismiss); document.body.append(selectionBar);
  const dialog=el('dialog',null,'annotation-dialog'); dialog.setAttribute('aria-labelledby','annotationTitle');
  const dTitle=el('h2','写下这段文字带来的想法'); dTitle.id='annotationTitle';
  const quote=el('blockquote'); const dForm=el('form');
  const dLabel=el('label','你的想法'); dLabel.htmlFor='annotationText';
  const dText=el('textarea'); dText.id='annotationText';dText.rows=5;dText.maxLength=2000;dText.required=true;
  const dStatus=el('p');dStatus.setAttribute('role','status');
  const dSubmit=el('button','公开发表','discussion-primary');dSubmit.type='submit';
  const dClose=el('button','取消'); dClose.type='button';
  dForm.append(dLabel,dText,el('p','想法将与引用的文字一起公开展示。','discussion-hint'),dStatus,dSubmit,dClose);
  dialog.append(dTitle,quote,dForm);document.body.append(dialog);

  async function api(path,options={}) {
    const response=await fetch(path,{credentials:'same-origin',...options,headers:{'Content-Type':'application/json','X-CSRF-Token':session.csrf,...options.headers}});
    let data;try{data=await response.json();}catch{throw new Error('评论服务暂时不可用，请稍后重试。');}
    if(!response.ok){if(response.status===401)refreshSession();throw new Error(typeof data.detail==='string'?data.detail:'请求未完成，请重试。');}
    if(options.method&&options.method!=='GET'&&path.includes('/entries'))window.dispatchEvent(new Event('purplebook:discussion-changed'));
    return data;
  }
  function loginLink(text='使用魔搭账号登录') {
    const a=el('a',text,'discussion-login');a.href='/auth/login?return_to='+encodeURIComponent(location.hash||'#home');
    // A top-level context is required for OAuth and SameSite cookies in Studio embeds.
    a.target='_blank';a.rel='noopener';return a;
  }
  function renderAccount() {
    account.replaceChildren();
    if(session.user){
      account.append(authorLink(session.user,'account-name'));
      const logout=el('button','退出');logout.type='button';logout.onclick=async()=>{try{await api('/api/logout',{method:'POST'});await refreshSession();await load();}catch(e){status.textContent=e.message;}};account.append(logout);
    }else if(session.loginEnabled) account.append(loginLink('魔搭登录'));
    else {const pending=el('span','魔搭登录','account-pending');pending.title='魔搭登录尚未配置';pending.setAttribute('aria-disabled','true');account.append(pending);}
    window.dispatchEvent(new CustomEvent('purplebook:session',{detail:session}));
    textarea.disabled=!session.user;submit.disabled=!session.user;
    formHint.replaceChildren(el('span','留言对所有读者可见。'));
    if(!session.user) formHint.append(' ',session.loginEnabled?loginLink('登录后参与讨论'):el('span','登录开放后即可参与讨论。'));
  }
  function authorLink(entry,cls='discussion-author'){
    const node=el(entry.profileUrl?'a':'strong',entry.name,cls);
    if(entry.profileUrl){node.href=entry.profileUrl;node.target='_blank';node.rel='noopener noreferrer';node.setAttribute('aria-label',entry.name+'的魔搭主页（新窗口）');}
    return node;
  }
  async function refreshSession(){try{session=await api('/api/session');renderAccount();}catch(e){status.textContent=e.message;renderAccount();}}
  function chapterKey(){return location.hash.slice(1).split('?')[0].split('/')[0];}
  function collectBlocks(){
    blocks=[...$('#articleBody').querySelectorAll('p,li,h2,h3,h4,blockquote,td')].filter(n=>!n.closest('pre,.katex')&&!n.querySelector('p,li,h2,h3,h4,blockquote,td'));
  }
  function textNodes(block){const walker=document.createTreeWalker(block,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest('button,.katex,script,style')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);return nodes;}
  function blockText(block){return textNodes(block).map(n=>n.textContent).join('');}
  function rangeFor(entry){
    const block=blocks[entry.block];if(!block)return null;
    const text=blockText(block);let start=entry.start;
    if(text.slice(start,entry.end)!==entry.quote){start=text.indexOf(entry.quote);if(start<0||text.indexOf(entry.quote,start+1)>=0)return null;}
    const end=start+entry.quote.length;const range=document.createRange();let offset=0,started=false;
    for(const node of textNodes(block)){
      const last=offset+node.length;
      if(!started&&start<last){range.setStart(node,start-offset);started=true;}
      if(started&&end<=last){range.setEnd(node,end-offset);return range;}
      offset=last;
    }return null;
  }
  function paint(){
    if(!window.CSS?.highlights||!window.Highlight)return;
    const mine=[],shared=[];
    for(const entry of items){if(entry.kind==='comment')continue;const range=rangeFor(entry);if(range)(entry.kind==='highlight'?mine:shared).push(range);}
    CSS.highlights.set('reader-lines',new Highlight(...mine));CSS.highlights.set('reader-thoughts',new Highlight(...shared));
  }
  function showTab(value){tab=value;render();}
  notesButton.onclick=()=>showTab('annotation');commentsButton.onclick=()=>showTab('comment');
  function render(){
    notesButton.setAttribute('aria-pressed',String(tab==='annotation'));commentsButton.setAttribute('aria-pressed',String(tab==='comment'));
    form.hidden=tab!=='comment';list.replaceChildren();
    const visible=items.filter(i=>tab==='comment'?i.kind==='comment':i.kind!=='comment');
    if(!visible.length)list.append(el('p',tab==='comment'?'还没有留言，来分享第一个想法吧。':'还没有划线或想法。选中正文后即可开始。','discussion-empty'));
    const cards=new Map();
    for(const entry of visible){
      const card=el('article',null,'discussion-entry');card.id='entry-'+entry.id;cards.set(entry.id,card);const header=el('header');
      header.append(authorLink(entry),el('span',entry.kind==='highlight'?'仅自己可见':new Date(entry.created*1000).toLocaleString('zh-CN',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'})));
      card.append(header);
      if(entry.replyTo)card.append(el('blockquote',entry.replyTo.id?'回复 '+entry.replyTo.name+'：'+entry.replyTo.text:'回复的原留言已删除','reply-context'));
      if(entry.quote){const jump=el('button',entry.quote,'quoted-passage');jump.type='button';jump.onclick=()=>{const r=rangeFor(entry);if(!r){status.textContent='正文已更新，暂时无法定位这段原文。';return;}blocks[entry.block].scrollIntoView({block:'center',behavior:'smooth'});getSelection().removeAllRanges();getSelection().addRange(r);};card.append(jump);}
      if(entry.text)card.append(el('p',entry.text));
      if(entry.kind==='comment'){const reply=el('button','回复','entry-reply');reply.type='button';reply.onclick=()=>{if(!canWrite())return;setReply(entry);form.scrollIntoView({block:'center',behavior:'smooth'});textarea.focus({preventScroll:true});};card.append(reply);}
      if(entry.canDelete){const del=el('button',entry.kind==='highlight'?'取消划线':'删除','entry-delete');del.type='button';del.onclick=async()=>{if(!confirm('确定删除这条'+(entry.kind==='highlight'?'划线':'内容')+'？'))return;del.disabled=true;try{await api('/api/entries/'+entry.id,{method:'DELETE'});await load();}catch(e){status.textContent=e.message;del.disabled=false;}};card.append(del);}
      list.append(card);
    }
    // Keep loaded replies under their original comment. Replies whose parent is
    // on an older page retain the quoted context until that page is loaded.
    for(const entry of [...visible].reverse()){
      const parent=cards.get(entry.replyTo?.id);if(!parent)continue;
      let replies=parent.querySelector(':scope > .entry-replies');if(!replies){replies=el('div',null,'entry-replies');parent.append(replies);}
      replies.append(cards.get(entry.id));
    }
    more.hidden=!next;paint();
  }
  async function load(append=false){
    const current=chapterKey();if(!/^chapter-\d+$/.test(current)){panel.hidden=true;selectionBar.hidden=true;return;}
    const record=window.BOOK_DATA.chapters.find(c=>c.id===current);if(!record||record.status==='pending'){panel.hidden=true;return;}
    panel.hidden=false;chapter=current;collectBlocks();
    const ticket=++generation;status.textContent='';
    try{const data=await api(`/api/chapters/${current}/entries${append&&next?'?before='+next:''}`);if(ticket!==generation||chapterKey()!==current)return;items=append?items.concat(data.items):data.items;next=data.next;render();}
    catch(e){if(ticket!==generation)return;items=[];next=null;render();status.textContent=e.message;}
  }
  more.onclick=()=>load(true);
  function capture(){
    const selection=getSelection();if(!selection||selection.isCollapsed||!selection.rangeCount){selectionBar.hidden=true;return;}
    const r=selection.getRangeAt(0),block=blocks.find(b=>b.contains(r.startContainer)&&b.contains(r.endContainer));
    if(!block||r.toString().length>2000||!r.toString().trim()||r.cloneContents().querySelector('.katex,button')){selectionBar.hidden=true;return;}
    const prefix=document.createRange();prefix.selectNodeContents(block);prefix.setEnd(r.startContainer,r.startOffset);
    const text=r.toString();const start=prefix.toString().length;
    if(blockText(block).slice(start,start+text.length)!==text){selectionBar.hidden=true;return;}
    anchor={chapter:chapterKey(),quote:text,block:blocks.indexOf(block),start,end:start+text.length};selectionBar.hidden=false;
  }
  document.addEventListener('pointerup',e=>{if(!selectionBar.contains(e.target)&&!dialog.contains(e.target))setTimeout(capture,40);});
  document.addEventListener('keyup',e=>{if(e.key==='Shift'||e.key.startsWith('Arrow'))capture();if(e.key==='Escape')selectionBar.hidden=true;});
  selectionBar.addEventListener('pointerdown',e=>e.preventDefault());dismiss.onclick=()=>{selectionBar.hidden=true;getSelection().removeAllRanges();};
  function canWrite(){if(session.user)return true;status.replaceChildren(el('span','请先登录。 '),session.loginEnabled?loginLink():el('span','魔搭登录尚未开启。'));panel.scrollIntoView({block:'start',behavior:'smooth'});selectionBar.hidden=true;return false;}
  save.onclick=async()=>{
    if(!canWrite()||!anchor||busy)return;busy=true;save.disabled=true;const selected={...anchor};
    try{await api(`/api/chapters/${selected.chapter}/entries`,{method:'POST',body:JSON.stringify({...selected,kind:'highlight'})});selectionBar.hidden=true;getSelection().removeAllRanges();showTab('annotation');await load();status.textContent='已划线，仅自己可见。';notify(status.textContent);}catch(e){status.textContent=e.message;notify(e.message);}finally{busy=false;save.disabled=false;}
  };
  write.onclick=()=>{if(!canWrite()||!anchor)return;quote.textContent=anchor.quote;dText.value='';dStatus.textContent='';selectionBar.hidden=true;dialog.showModal();dText.focus();};
  dClose.onclick=()=>dialog.close();
  dForm.onsubmit=async e=>{e.preventDefault();if(busy||!anchor||!dText.value.trim())return;busy=true;dSubmit.disabled=true;
    try{await api(`/api/chapters/${anchor.chapter}/entries`,{method:'POST',body:JSON.stringify({...anchor,kind:'annotation',text:dText.value})});dialog.close();showTab('annotation');getSelection().removeAllRanges();await load();}catch(error){dStatus.textContent=error.message;}finally{busy=false;dSubmit.disabled=false;}
  };
  form.onsubmit=async e=>{e.preventDefault();if(!canWrite()||busy||!textarea.value.trim())return;busy=true;submit.disabled=true;const target=chapterKey();
    try{await api(`/api/chapters/${target}/entries`,{method:'POST',body:JSON.stringify({kind:'comment',text:textarea.value,parentId:replyTo?.id})});if(chapterKey()===target){textarea.value='';setReply(null);await load();status.textContent='留言已发表。';}}catch(error){status.textContent=error.message;}finally{busy=false;submit.disabled=!session.user;}
  };
  window.addEventListener('hashchange',()=>{generation++;selectionBar.hidden=true;dialog.close();anchor=null;if(chapter!==chapterKey()){textarea.value='';setReply(null);items=[];next=null;tab='comment';render();}renderAccount();requestAnimationFrame(()=>load());});
  window.addEventListener('focus',async()=>{await refreshSession();await load();});
  refreshSession().then(load);
  if(new URLSearchParams(location.search).get('login')==='failed'){status.textContent='登录未完成，请重新使用魔搭账号登录。';}
})();
