(() => {
  'use strict';
  const data = window.BOOK_DATA;
  const chapters = new Map(data.chapters.map(c => [c.id, c]));
  const $ = selector => document.querySelector(selector);
  const $$ = selector => [...document.querySelectorAll(selector)];
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const shortTitle = title => title.replace(/^第[^　\s]+章[　\s]*/, '');
  const partNames = data.parts.map(p => p.shortTitle || p.title);
  const projectLinks = '<a href="https://github.com/modelscope/ms-cookbook" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a href="https://modelscope.cn/spotlight" target="_blank" rel="noopener noreferrer">魔搭开发者实践 ↗</a><a href="#contribute">社区共建</a>';
  $$('.project-links').forEach(el=>{el.innerHTML=projectLinks;});
  $$('.quiet-footer').forEach(el=>{el.insertAdjacentHTML('beforeend',`<div class="project-links">${projectLinks}</div>`);});
  const arrow = '<img class="arrow" src="assets/home/arrow.svg" alt="">';
  const artSource = art => `assets/editorial-art/${art}.png`;
  const paths = {
    beginner: {name:'从零开始',title:'从零开始，跑通第一个模型',art:'seedling',desc:'适合刚接触开源模型的读者。从理解模型，到选择任务，再到看到第一个结果。',brief:'建立基础认知，快速上手实践。',steps:'认识 → 选型 → 运行',link:'开始这条路径',chapters:[1,5,7],labels:['建立基础认知','找到业务任务','跑通第一个示例'],notes:['理解开源模型与使用边界','明确输入、输出与评估方式','完成一次模型运行']},
    model: {name:'深入模型',title:'深入模型，把通用能力变成场景能力',art:'mountain',desc:'适合已经跑通过模型的开发者。从业务数据准备开始，完成轻量微调，并用评测检验模型效果。',brief:'掌握核心技术，提升实践能力。',steps:'数据 → 微调 → 评测',link:'探索核心内容',chapters:[12,13,15],labels:['准备训练数据','完成轻量微调','验证模型效果'],notes:['将业务知识整理成训练样本','用 ms-swift 完成模型训练','比较基线与微调后的表现']},
    application: {name:'走向应用',title:'带着真实任务，探索模型的应用方式',art:'cubes',desc:'从企业知识问答到 MCP 与 Skill。结合任务选择章节，理解模型与工具怎样协同工作。',brief:'将模型能力转化为实际价值。',steps:'知识问答 → 工具 → Agent',link:'查看应用实践',chapters:[19,27,28],labels:['知识问答','连接工具','封装能力'],notes:['结合知识库生成有依据的回答','通过 MCP 连接外部工具','用 Skill 组织可复用的任务方法']},
    aigc: {name:'AIGC 创作',title:'从生成到定制，探索 AIGC 创作',art:'palette',desc:'面向创作者与 AIGC 实践者。从开源生成模型的案例出发，学习图像 LoRA 定制、商品营销图创作，再补充生成模型的理论知识。',brief:'理解生成能力，跑通创作流程。',steps:'案例 → 定制 → 图像创作',link:'开始 AIGC 创作',chapters:[21,22,23,25],labels:['认识生成能力','定制图像 LoRA','创作商品营销图','补充理论基础'],notes:['通过现有案例了解开源模型的创作能力','使用 DiffSynth 训练图像 LoRA','完成图像生成与修改流程','理解 AIGC 相关理论知识']}
  };
  const scenes = [
    {id:16,title:'AI 健身教练',desc:'识别人体关键点，对比跟练动作与示范。',type:'视觉',art:'fitness'},
    {id:17,title:'智能客服质检',desc:'从通话转写到服务过程分析。',type:'语音分析',art:'service'},
    {id:18,title:'能听也能说的语音助手',desc:'串联语音识别、模型问答与语音合成。',type:'语音',art:'speech'},
    {id:19,title:'企业知识问答助手',desc:'结合知识库，让回答有据可查。',type:'RAG',art:'knowledge'},
    {id:23,title:'商品营销图',desc:'从图像生成到修改，完成商品视觉创作。',type:'AIGC',art:'product'}
  ];
  let currentChapter = null;
  let currentView = '';
  let currentPathKey = '';
  let activeHeading = '';
  const {chapterHash, pathStep, parseHash} = window.ReaderRoutes;
  let headingObserver;
  let searchTimer;
  const searchIndex = new Map(data.chapters.map(c => {
    const holder = document.createElement('div'); holder.innerHTML = c.html;
    return [c.id, (c.title+' '+c.headings.map(h=>h.text).join(' ')+' '+holder.textContent).toLowerCase()];
  }));

  $('#homePaths').innerHTML = Object.entries(paths).map(([key,p]) => `<article><a class="path-art-link" href="#paths/${key}" aria-label="${p.name}"><img src="${artSource(p.art)}" alt="" width="400" height="250"></a><h3>${p.name}</h3><p class="path-brief">${p.brief}</p><p>${p.steps}</p><a class="text-link" href="#paths/${key}">${p.link} ${arrow}</a></article>`).join('');
  $('#sceneGrid').innerHTML = scenes.map(s=>`<article class="scene"><a class="scene-art" href="#chapter-${s.id}" aria-label="${s.title}"><img src="${artSource(s.art)}" alt="" width="320" height="260" loading="lazy"></a><div class="scene-copy"><h2><a href="#chapter-${s.id}">${s.title}</a></h2><p>${s.desc}</p><div class="scene-meta"><span>第 ${s.id} 章 · ${s.type}</span><a class="text-link" href="#chapter-${s.id}">${chapters.get('chapter-'+s.id).status==='pending'?'查看章节':'阅读实践'} ${arrow}</a></div></div></article>`).join('');

  function highlighted(text,query) {
    if (!query) return esc(text);
    const index = text.toLowerCase().indexOf(query.toLowerCase());
    if (index<0) return esc(text);
    return esc(text.slice(0,index))+'<mark>'+esc(text.slice(index,index+query.length))+'</mark>'+esc(text.slice(index+query.length));
  }
  function renderIndex() {
    const query = $('#chapterSearch').value.trim();
    const q = query.toLowerCase();
    let count = 0;
    $('#bookIndex').innerHTML = data.parts.map((part,i)=> {
      const ids = part.chapters.filter(id=>!q || searchIndex.get(id).includes(q) || partNames[i].toLowerCase().includes(q));
      count += ids.length;
      if (!ids.length) return '';
      return `<section class="index-part"><div class="part-badge"><small>PART</small><span>${String(i+1).padStart(2,'0')}</span></div><div><h2>${partNames[i]}</h2><nav aria-label="${partNames[i]}">${ids.map(id=>{
        const c=chapters.get(id);
        const heading=q ? c.headings.find(h=>h.text.toLowerCase().includes(q)) : null;
        return `<a href="#${id}"><span class="chapter-index">${String(c.number).padStart(2,'0')}</span><span>${highlighted(shortTitle(c.title),query)}${c.status==='pending'?'<small class="pending-badge">待补充</small>':''}${heading ? `<small class="search-context">${highlighted(heading.text,query)}</small>`:''}</span>${arrow}</a>`;
      }).join('')}</nav></div></section>`;
    }).join('');
    $('#searchStatus').hidden = !query;
    $('#searchStatus').textContent = `“${query}”相关章节：${count} 个`;
    $('#emptySearch').hidden = count>0;
  }
  $('#chapterSearch').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(renderIndex,100);});
  $('#clearSearch').addEventListener('click',()=>{$('#chapterSearch').value='';renderIndex();$('#chapterSearch').focus();});

  let bookSearchDocuments;
  let bookSearchTimer;
  function createBookSearchDocuments() {
    return data.chapters.flatMap(chapter => {
      const holder=document.createElement('div');holder.innerHTML=chapter.html;
      const headings=new Map(chapter.headings.filter(h=>h.text.trim()).map(h=>[h.id,h]));
      const base={chapterId:chapter.id,number:chapter.number,title:shortTitle(chapter.title),status:chapter.status};
      let section={...base,headingId:'',heading:'',text:[]};
      const sections=[section];
      const walker=document.createTreeWalker(holder,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);
      let node;
      while((node=walker.nextNode())) {
        if(node.nodeType===Node.ELEMENT_NODE&&headings.has(node.id)) {
          section={...base,headingId:node.id,heading:headings.get(node.id).text,text:[]};sections.push(section);
        } else if(node.nodeType===Node.TEXT_NODE&&!headings.has(node.parentElement.closest('h2,h3,h4')?.id)) section.text.push(node.textContent);
      }
      return sections.map(s=>({...s,text:s.text.join(' ').replace(/\s+/g,' ').trim()}));
    });
  }
  function searchHighlight(text,query) {
    const tokens=query.trim().split(/\s+/).filter(Boolean).map(token=>token.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
    if(!tokens.length)return esc(text);
    const pattern=new RegExp(tokens.join('|'),'gi');
    let result='',end=0;
    for(const match of text.matchAll(pattern)) {
      result+=esc(text.slice(end,match.index))+'<mark>'+esc(match[0])+'</mark>';end=match.index+match[0].length;
    }
    return result+esc(text.slice(end));
  }
  function renderBookSearch() {
    clearTimeout(bookSearchTimer);bookSearchTimer=null;
    const query=$('#bookSearchInput').value.trim();
    let results,total;
    if(query) ({results,total}=window.BookSearch.search(bookSearchDocuments,query));
    else {
      const ids=[...new Set([currentChapter?.id,'chapter-1','chapter-13','chapter-19','chapter-22','chapter-27'])];
      results=ids.map(id=>bookSearchDocuments.find(d=>d.chapterId===id&&!d.headingId)).filter(Boolean);
    }
    $('#bookSearchStatus').textContent=query?(total?`找到 ${total} 处匹配${total>results.length?`，显示前 ${results.length} 条；可添加关键词缩小范围`:''}`:'没有找到匹配内容'):'输入关键词搜索全书，或直接打开以下章节';
    $('#bookSearchResults').innerHTML=results.length?results.map(result=>{
      const label=result.heading||result.title;
      const context=result.heading?result.title:(result.chapterId===currentChapter?.id&&!query?'正在阅读':result.status==='pending'?'正文待补充':'章节起点');
      const pathKey=pathStep(paths,currentPathKey,result.number)?currentPathKey:'';
      return `<a class="book-search-result" href="${chapterHash(result.chapterId,result.headingId,pathKey)}"><small>第 ${result.number} 章 · ${esc(context)}</small><strong>${searchHighlight(label,query)}</strong>${query&&result.snippet?`<p>${searchHighlight(result.snippet,query)}</p>`:''}</a>`;
    }).join(''):'<div class="book-search-empty"><strong>换个关键词试试</strong>可以缩短描述，或搜索“微调”“LoRA”“RAG”。</div>';
    $('#bookSearchResults').scrollTop=0;
  }
  function openBookSearch() {
    if(!bookSearchDocuments)bookSearchDocuments=createBookSearchDocuments();
    clearTimeout(bookSearchTimer);renderBookSearch();openDialog('#bookSearchDialog');
    $('#bookSearchInput').focus();$('#bookSearchInput').select();
  }
  $('#readerSearchButton').addEventListener('click',openBookSearch);
  $('#bookSearchInput').addEventListener('input',()=>{clearTimeout(bookSearchTimer);bookSearchTimer=setTimeout(renderBookSearch,100);});
  $('#bookSearchDialog').addEventListener('keydown',e=>{
    if(e.isComposing)return;
    if(['ArrowDown','ArrowUp'].includes(e.key)&&bookSearchTimer)renderBookSearch();
    const results=$$('#bookSearchResults a');
    if(['ArrowDown','ArrowUp'].includes(e.key)&&results.length) {
      e.preventDefault();const index=results.indexOf(document.activeElement);
      const next=index<0?(e.key==='ArrowDown'?0:results.length-1):(index+(e.key==='ArrowDown'?1:-1)+results.length)%results.length;
      results[next].focus({preventScroll:true});results[next].scrollIntoView({block:'nearest',behavior:'instant'});
    } else if(e.key==='Enter'&&e.target===$('#bookSearchInput')) {
      e.preventDefault();clearTimeout(bookSearchTimer);renderBookSearch();$('#bookSearchResults a')?.click();
    }
  });
  $('#searchShortcut').textContent=/Mac|iPhone|iPad/.test(navigator.platform)?'⌘ K':'Ctrl K';
  document.addEventListener('keydown',e=>{
    if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'&&!e.isComposing) {
      e.preventDefault();openBookSearch();
    }
  });

  function ensureCurrentChapterVisible() {
    const nav=$('#chapterNav'),active=nav.querySelector('[aria-current="page"]');
    if(!active||!nav.clientHeight)return;
    const rect=active.getBoundingClientRect(),bounds=nav.getBoundingClientRect();
    if(rect.top<bounds.top||rect.bottom>bounds.bottom)nav.scrollTop+=rect.top-bounds.top-(nav.clientHeight-rect.height)/2;
  }
  function setSidebarCollapsed(collapsed,keepPosition=false) {
    const top=$('.app-header').getBoundingClientRect().bottom+24;
    const anchor=keepPosition?$$('#article h1,#article h2,#article h3,#article p,#article pre').find(el=>el.getBoundingClientRect().bottom>top):null;
    const before=anchor?.getBoundingClientRect().top;
    document.body.classList.toggle('sidebar-collapsed',collapsed);
    $('#bookSidebar').hidden=collapsed;$('#expandSidebar').hidden=!collapsed;
    if(anchor)window.scrollBy({top:anchor.getBoundingClientRect().top-before,behavior:'instant'});
    if(keepPosition)(collapsed?$('#expandSidebar'):$('#collapseSidebar')).focus({preventScroll:true});
    if(!collapsed)ensureCurrentChapterVisible();
    try{localStorage.setItem('ms-cookbook-sidebar-collapsed',String(collapsed));}catch{/* Storage can be disabled in embedded readers. */}
    updateProgress();
  }
  $('#collapseSidebar').addEventListener('click',()=>setSidebarCollapsed(true,true));
  $('#expandSidebar').addEventListener('click',()=>setSidebarCollapsed(false,true));
  try{setSidebarCollapsed(localStorage.getItem('ms-cookbook-sidebar-collapsed')==='true');}catch{/* Keep the default expanded view. */}

  function buildChapterNav() {
    const markup = data.parts.map((p,i)=>`<details data-part="${i}"><summary><span class="part-index">${String(i+1).padStart(2,'0')}</span><span>${partNames[i]}</span></summary><div class="chapter-list">${p.chapters.map(id=>{const c=chapters.get(id);return `<a href="#${id}" data-chapter="${id}"><span>${String(c.number).padStart(2,'0')}</span>${esc(shortTitle(c.title))}</a>`;}).join('')}</div></details>`).join('');
    $('#chapterNav').innerHTML = markup; $('#mobileChapterNav').innerHTML = markup;
  }
  function renderPath(key) {
    const p=paths[key] || paths.beginner;
    const selected = paths[key] ? key : 'beginner';
    $$('.path-tabs button').forEach(b=>{const on=b.dataset.path===selected;b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;});
    $('#pathPanel').setAttribute('aria-labelledby','tab-'+selected);
    $('#pathArt').src=artSource(p.art); $('#pathArt').alt=p.name+' · 黑色手绘插画';
    $('#aigcContributions').hidden=selected!=='aigc';
    $('#pathTitle').textContent=p.title; $('#pathDescription').textContent=p.desc;
    $('#pathStart').href=chapterHash('chapter-'+p.chapters[0],'',selected);
    $('#pathStations').style.setProperty('--stations',p.chapters.length);
    $('#pathStations').innerHTML=p.chapters.map((n,i)=>`<li><span class="station-number">${String(i+1).padStart(2,'0')}</span><h3>${p.labels[i]}</h3><small>第 ${n} 章</small><p class="station-title">${esc(shortTitle(chapters.get('chapter-'+n).title))}</p><p>${p.notes[i]}</p><a class="text-link" href="${chapterHash('chapter-'+n,'',selected)}">阅读章节 ${arrow}</a></li>`).join('');
  }
  function renderPathNavigation(chapter) {
    const step=pathStep(paths,currentPathKey,chapter.number);
    document.body.classList.toggle('reading-path-active',!!step);
    const panels=$$('[data-path-reader]');
    panels.forEach(panel=>{panel.hidden=!step;});
    $('#previousChapter small').textContent=step?'全书上一章':'上一章';
    $('#nextChapter small').textContent=step?'全书下一章':'下一章';
    $('#mobilePrevious').textContent=step?'本路径上一步':'上一章';
    $('#mobileNext').textContent=step?'本路径下一步':'下一章 →';
    if(!step)return;
    const path=paths[currentPathKey];
    const previous=step.previous?chapterHash('chapter-'+step.previous,'',currentPathKey):'';
    const next=step.next?chapterHash('chapter-'+step.next,'',currentPathKey):'';
    const markup=`<div class="path-reader-heading"><span>阅读路径 · <strong>${esc(path.name)}</strong><small>第 ${step.index+1} / ${step.total} 步</small></span><a href="#paths/${currentPathKey}">返回路径 ↗</a></div><ol class="path-reader-steps">${path.chapters.map(n=>`<li><a href="${chapterHash('chapter-'+n,'',currentPathKey)}"${n===chapter.number?' aria-current="step"':''} title="${esc(shortTitle(chapters.get('chapter-'+n).title))}">第 ${n} 章</a></li>`).join('')}</ol><div class="path-reader-actions">${previous?`<a href="${previous}" data-path-direction="previous">← 本路径上一步 · 第 ${step.previous} 章</a>`:'<span>从这里开始</span>'}${next?`<a href="${next}" data-path-direction="next">本路径下一步 · 第 ${step.next} 章 →</a>`:'<span class="path-reader-last">已到本路径最后一步</span>'}</div>`;
    panels.forEach(panel=>{panel.innerHTML=markup;});
    setPager($('#mobilePrevious'),step.previous?chapters.get('chapter-'+step.previous):null);
    if(previous)$('#mobilePrevious').href=previous;
    if(next)$('#mobileNext').href=next;
    else {
      $('#mobileNext').href='#paths/'+currentPathKey;$('#mobileNext').textContent='返回路径';
      $('#mobileNext').classList.remove('disabled');$('#mobileNext').removeAttribute('tabindex');$('#mobileNext').setAttribute('aria-disabled','false');
    }
  }
  $$('.path-tabs button').forEach((b,i)=> {
    b.addEventListener('click',()=>{location.hash='paths/'+b.dataset.path;});
    b.addEventListener('keydown',e=> {
      if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
      e.preventDefault();const list=$$('.path-tabs button');
      const next=e.key==='Home'?0:e.key==='End'?list.length-1:(i+(e.key==='ArrowRight'?1:-1)+list.length)%list.length;
      list[next].focus();list[next].click();
    });
  });
  function setPager(node,chapter) {
    node.classList.toggle('disabled',!chapter);
    node.setAttribute('aria-disabled',String(!chapter));
    if(chapter){node.href='#'+chapter.id;node.removeAttribute('tabindex');const text=node.querySelector('span');if(text)text.textContent=shortTitle(chapter.title);}
    else {node.removeAttribute('href');node.tabIndex=-1;}
  }
  function closeDialogs() {$$('dialog[open]').forEach(d=>d.close());document.body.classList.remove('modal-open');}
  function openDialog(id) {
    closeDialogs();$(id).showModal();document.body.classList.add('modal-open');
    if(id==='#tocDialog')requestAnimationFrame(()=>{
      const active=$('#mobileToc [aria-current="location"]')||$('#mobileToc a');
      if(active){active.focus({preventScroll:true});active.scrollIntoView({block:'nearest',behavior:'instant'});}
    });
  }
  $$('[data-close]').forEach(b=>b.addEventListener('click',()=>$('#'+b.dataset.close).close()));
  $$('dialog').forEach(d=>{
    d.addEventListener('close',()=>document.body.classList.toggle('modal-open',!!$('dialog[open]')));
    d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}});
  });
  $('#menuButton').addEventListener('click',()=>openDialog('#siteMenu'));
  $('#tocButton').addEventListener('click',()=>openDialog('#tocDialog'));
  $('#readerTocButton').addEventListener('click',()=>openDialog('#tocDialog'));
  $('#backTop').addEventListener('click',e=>{e.preventDefault();window.scrollTo({top:0,behavior:'smooth'});});

  function renderChapter(chapter) {
    currentChapter=chapter;
    const index=data.chapters.indexOf(chapter);
    const partIndex=data.parts.findIndex(p=>p.chapters.includes(chapter.id));
    $('#partLabel').textContent=`第${['一','二','三','四','五','六','七','八'][partIndex]}篇 / ${partNames[partIndex]}`;
    $('#chapterTitle').textContent=shortTitle(chapter.title);
    $('#chapterNumber').textContent='第 '+chapter.number+' 章';
    $('#readTime').textContent=chapter.status==='pending'?'正文待补充':'阅读约 '+chapter.minutes+' 分钟';
    $('#chapterSource').href=chapter.sourceUrl;
    $('#chapterEdit').href=chapter.editUrl;
    $('#articleBody').innerHTML=chapter.html;
    $$('#articleBody .arithmatex').forEach(el=>{
      const text=el.textContent, display=el.classList.contains('display-math');
      const formula=text.slice(2,-2);
      if(window.katex)window.katex.render(formula,el,{displayMode:display,throwOnError:false,strict:'ignore',trust:false});
    });
    document.title=chapter.title+'｜魔搭紫皮书';
    const prev=data.chapters[index-1],next=data.chapters[index+1];
    setPager($('#previousChapter'),prev);setPager($('#nextChapter'),next);
    setPager($('#mobilePrevious'),prev);setPager($('#mobileNext'),next);
    renderPathNavigation(chapter);
    const toc=chapter.headings.filter(h=>h.text.trim()).map(h=>`<a href="${chapterHash(chapter.id,h.id,currentPathKey)}" data-heading="${h.id}" data-level="${h.level}">${esc(h.text)}</a>`).join('');
    $('#localToc').innerHTML=toc || '<p class="toc-empty">本章暂无小节目录</p>';$('#mobileToc').innerHTML=toc || '<p class="toc-empty">本章暂无小节目录</p>';
    $('#localToc').scrollTop=0;activeHeading='';
    $$('.chapter-nav details').forEach(d=>{d.open=Number(d.dataset.part)===partIndex;});
    $$('[data-chapter]').forEach(a=>{const active=a.dataset.chapter===chapter.id;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    $$('#articleBody img').forEach(img=> {
      img.tabIndex=0;img.setAttribute('role','button');img.setAttribute('aria-label','放大查看图片');
      const show=()=>{$('#viewerImage').src=img.src;$('#viewerImage').alt=img.alt;openDialog('#imageViewer');};
      img.addEventListener('click',show);img.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();show();}});
    });
    $$('#articleBody pre').forEach(pre=>{
      const code=pre.querySelector('code')?.textContent||pre.textContent;
      const button=document.createElement('button');button.className='copy-code';button.textContent='复制';button.setAttribute('aria-label','复制代码');
      button.addEventListener('click',async()=>{
        try{await navigator.clipboard.writeText(code);button.textContent='已复制';}
        catch{const range=document.createRange();range.selectNodeContents(pre.querySelector('code')||pre);getSelection().removeAllRanges();getSelection().addRange(range);button.textContent='已选中，请复制';}
        setTimeout(()=>button.textContent='复制',2000);
      });pre.append(button);
    });
    if(headingObserver)headingObserver.disconnect();
    headingObserver=new IntersectionObserver(updateActiveHeading,{rootMargin:'-12% 0px -65% 0px',threshold:0});
    chapter.headings.filter(h=>h.text.trim()).forEach(h=>{const target=document.getElementById(h.id);if(target)headingObserver.observe(target);});
  }
  function updateActiveHeading() {
    if(currentView!=='reader'||!currentChapter)return;
    const headings=currentChapter.headings.filter(h=>h.text.trim());
    let active=headings[0]?.id;
    for(const h of headings){const el=document.getElementById(h.id);if(el&&el.getBoundingClientRect().top<=window.innerHeight*.24)active=h.id;}
    $$('[data-heading]').forEach(a=>{const on=a.dataset.heading===active;a.classList.toggle('active',on);if(on)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});
    if(active!==activeHeading) {
      activeHeading=active;
      const nav=$('#localToc'),link=nav.querySelector('[aria-current="location"]');
      if(link&&nav.clientHeight) {
        const bounds=nav.getBoundingClientRect(),rect=link.getBoundingClientRect();
        if(rect.top<bounds.top||rect.bottom>bounds.bottom)nav.scrollTop+=rect.top-bounds.top-(nav.clientHeight-rect.height)/2;
      }
    }
  }
  function updateProgress() {
    if(currentView!=='reader')return;
    const article=$('#article'),total=Math.max(1,article.offsetHeight-window.innerHeight);
    $('#readingProgress').style.width=Math.max(0,Math.min(100,-article.getBoundingClientRect().top/total*100))+'%';
    updateActiveHeading();
  }
  function route() {
    // Preserve community links published before the route was named contribute.
    if(location.hash==='#community')history.replaceState(null,'','#contribute');
    const {name,sub,pathKey}=parseHash(location.hash,paths);
    const previousPage=currentView==='reader'?currentChapter?.id:currentView;
    const pathChanged=currentPathKey!==pathKey;
    currentPathKey=pathKey;
    const chapter=chapters.get(name);
    const view=chapter?'reader':['contents','paths','practice','contribute'].includes(name)?name:'home';
    const samePath=currentView==='paths'&&view==='paths';
    closeDialogs();
    $$('[data-page]').forEach(p=>p.hidden=p.dataset.page!==view);
    document.body.dataset.view=view;
    $$('.desktop-nav [data-route]').forEach(a=>{if(a.dataset.route===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    $('#headerAction').textContent=view==='reader'?'返回首页':'开始阅读';$('#headerAction').href=view==='reader'?'#home':'#chapter-1';
    $('#mobileChapterNav').hidden=view!=='reader';
    if(view==='reader') {
      if(currentChapter?.id!==chapter.id||currentView!=='reader'||pathChanged)renderChapter(chapter);
    } else {
      if(headingObserver)headingObserver.disconnect();
      document.title=({home:'让开源模型，从知识走向实践',contents:'全书目录',paths:'阅读路径',practice:'场景实践',contribute:'社区共建'}[view])+'｜魔搭紫皮书';
      if(view==='contents')renderIndex();if(view==='paths')renderPath(sub);
    }
    currentView=view;
    const analyticsPage=view==='reader'?chapter.id:view;
    if(analyticsPage!==previousPage)window.dispatchEvent(new CustomEvent('purplebook:route',{detail:{page:analyticsPage}}));
    requestAnimationFrame(()=>{
      if(view==='reader'&&sub){const target=document.getElementById(sub);if(target){target.scrollIntoView({block:'start',behavior:'instant'});target.tabIndex=-1;target.focus({preventScroll:true});}}
      else if(!samePath)window.scrollTo({top:0,behavior:'instant'});
      if(view==='reader')ensureCurrentChapterVisible();
      updateProgress();
    });
  }
  document.addEventListener('click',e=>{
    const a=e.target.closest('a[href^="#"]');
    if(a&&a.getAttribute('href')===location.hash&&a.id!=='backTop'){e.preventDefault();route();}
  });
  window.addEventListener('hashchange',route);
  window.addEventListener('scroll',updateProgress,{passive:true});
  window.addEventListener('resize',updateProgress);
  buildChapterNav();renderIndex();route();
})();
