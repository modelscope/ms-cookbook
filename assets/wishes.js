(() => {
  'use strict';
  const $=s=>document.querySelector(s), el=(tag,text,cls)=>{const n=document.createElement(tag);if(text)n.textContent=text;if(cls)n.className=cls;return n;};
  const form=$('#wishForm'),input=$('#wishText'),submit=$('#wishSubmit'),account=$('#wishAccount'),list=$('#wishList'),status=$('#wishListStatus'),formStatus=$('#wishFormStatus'),more=$('#wishMore'),retry=$('#wishRetry');
  let session={user:null,csrf:'',loginEnabled:false},items=[],next=null,busy=false,loading=false,generation=0;
  const active=()=>location.hash.split('?')[0]==='#contribute';
  async function api(path,options={}){
    const r=await fetch(path,{credentials:'same-origin',...options,headers:{'Content-Type':'application/json','X-CSRF-Token':session.csrf}});
    let data;try{data=await r.json();}catch{throw Error('许愿池暂时无法连接，请稍后重试。');}
    if(!r.ok){if(r.status===401)refreshSession();throw Error(typeof data.detail==='string'?data.detail:'请求未完成，请重试。');}return data;
  }
  function renderAccount(){
    input.disabled=!session.user;submit.disabled=!session.user||busy;account.replaceChildren();
    if(session.user){account.textContent='以 '+session.user.name+' 的名字许愿';}
    else if(session.loginEnabled){const a=el('a','魔搭登录后许愿');a.href='/auth/login?return_to=%23contribute';a.target='_blank';a.rel='noopener';account.append(a);}
    else account.textContent='魔搭登录开放后，就可以投下你的愿望。';
  }
  function acceptSession(value){const changed=session.user?.id!==value.user?.id;session=value;renderAccount();if(changed&&active())load();}
  async function refreshSession(){try{acceptSession(await api('/api/session'));}catch(e){formStatus.textContent=e.message;}}
  window.addEventListener('purplebook:session',e=>acceptSession(e.detail));
  function render(){
    list.replaceChildren();
    if(!items.length)list.append(el('p','还没有人许愿。你希望紫皮书补上的第一份实践是什么？','wish-empty'));
    for(const wish of items){
      const card=el('article',null,'wish-entry'),header=el('header'),date=el('time',new Date(wish.created*1000).toLocaleDateString('zh-CN'));
      const author=el(wish.profileUrl?'a':'strong',wish.name);if(wish.profileUrl){author.href=wish.profileUrl;author.target='_blank';author.rel='noopener noreferrer';window.ReaderProfiles.bind(author);}
      date.dateTime=new Date(wish.created*1000).toISOString();header.append(author,date);card.append(header,el('p',wish.text));
      if(wish.canDelete){const del=el('button','删除','entry-delete');del.type='button';del.onclick=async()=>{if(!confirm('确定删除这条愿望？'))return;del.disabled=true;try{await api('/api/wishes/'+wish.id,{method:'DELETE'});await load();}catch(e){status.textContent=e.message;del.disabled=false;}};card.append(del);}
      list.append(card);
    }
    more.hidden=!next;
  }
  async function load(append=false){
    if(append&&loading)return;
    const ticket=++generation;loading=true;more.disabled=true;retry.hidden=true;status.textContent='正在收集大家的愿望…';
    try{const data=await api('/api/wishes'+(append&&next?'?before='+next:''));if(ticket!==generation)return;items=append?items.concat(data.items):data.items;next=data.next;render();status.textContent='';}
    catch(e){if(ticket!==generation)return;status.textContent=e.message;retry.hidden=false;}
    finally{if(ticket===generation){loading=false;more.disabled=false;}}
  }
  input.addEventListener('input',()=>{$('#wishCount').textContent=input.value.length+' / 2000';});
  form.addEventListener('submit',async e=>{
    e.preventDefault();if(busy||!session.user)return;
    if(!input.value.trim()){formStatus.textContent='请写下希望补充的内容。';input.focus();return;}
    busy=true;renderAccount();formStatus.textContent='正在投下愿望…';
    try{await api('/api/wishes',{method:'POST',body:JSON.stringify({text:input.value})});input.value='';$('#wishCount').textContent='0 / 2000';formStatus.textContent='愿望已发布，期待有经验的伙伴来补上这一页。';await load();}
    catch(e){formStatus.textContent=e.message;}
    finally{busy=false;renderAccount();}
  });
  more.onclick=()=>load(true);retry.onclick=()=>load();
  window.addEventListener('hashchange',()=>{if(active())load();});
  window.addEventListener('focus',()=>{if(active())load();});
  refreshSession().then(()=>{if(active())load();});
})();
