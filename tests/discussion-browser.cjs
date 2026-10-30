// NODE_PATH must resolve Playwright. Uses isolated SQLite, never the preview database.
const {chromium}=require('playwright');
const {spawn,spawnSync}=require('node:child_process');
const fs=require('node:fs');const os=require('node:os');const path=require('node:path');const assert=require('node:assert/strict');
(async()=>{
 const root=path.resolve(__dirname,'..'), data=fs.mkdtempSync(path.join(os.tmpdir(),'purplebook-browser-'));
 const env={...process.env,DATA_DIR:data,APP_BASE_URL:'http://127.0.0.1:7861',PYTHONPATH:root,OAUTH_CLIENT_ID:'',OAUTH_CLIENT_SECRET:''};
 const python=process.env.TEST_PYTHON||path.join(root,'.venv/bin/python');
 const setup=spawnSync(python,['tests/prepare_browser_fixture.py'],{cwd:root,env,encoding:'utf8'});assert.equal(setup.status,0,setup.stderr);
 const server=spawn(python,['-m','uvicorn','app:app','--host','127.0.0.1','--port','7861','--no-access-log'],{cwd:root,env,stdio:'ignore'});
 let browser;
 try{
  for(let i=0;i<50;i++){try{const r=await fetch(env.APP_BASE_URL+'/api/session');if(r.ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
  browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHANNEL?{channel:process.env.PLAYWRIGHT_CHANNEL}:{})});const context=await browser.newContext({viewport:{width:1280,height:900}});
  await context.addCookies([{name:'purplebook_session',value:JSON.parse(fs.readFileSync(path.join(data,'browser-cookie.json'),'utf8')),url:env.APP_BASE_URL}]);
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(env.APP_BASE_URL+'/#chapter-1');await page.getByText('测试读者',{exact:true}).first().waitFor();
  await page.locator('#chapterMessage').fill('这是一条端到端测试留言');await page.getByRole('button',{name:'发表留言',exact:true}).click();
  await page.locator('.discussion-entry').getByText('这是一条端到端测试留言').waitFor();
  const parentCard=page.locator('.discussion-entry').filter({hasText:'这是一条端到端测试留言'});
  assert.equal(await parentCard.locator('.discussion-author').getAttribute('href'),'https://modelscope.cn/profile/test-reader');
  await context.route('https://modelscope.cn/profile/test-reader',route=>route.fulfill({body:'Profile destination'}));
  const popupPromise=context.waitForEvent('page');await parentCard.locator('.discussion-author').click();
  const popup=await popupPromise;await popup.waitForLoadState();assert.equal(popup.url(),'https://modelscope.cn/profile/test-reader');await popup.close();
  await parentCard.getByRole('button',{name:'回复',exact:true}).click();
  await page.locator('#chapterMessage').fill('收到，这是一条回复');await page.getByRole('button',{name:'发表回复',exact:true}).click();
  await page.locator('.entry-replies').getByText('收到，这是一条回复',{exact:true}).waitFor();
  await page.reload();await page.locator('.entry-replies').getByText('收到，这是一条回复',{exact:true}).waitFor();
  await page.locator('.entry-replies').getByRole('button',{name:'回复',exact:true}).click();
  await page.getByRole('button',{name:'取消回复',exact:true}).click();assert.equal(await page.getByRole('button',{name:'发表留言',exact:true}).count(),1);
  const contentCheck=await page.evaluate(()=>{
    let links=0;
    for(const chapter of BOOK_DATA.chapters){
      const holder=document.createElement('div');holder.innerHTML=chapter.html;
      links+=holder.querySelectorAll('a[href^="http"]').length;
      const walker=document.createTreeWalker(holder,NodeFilter.SHOW_TEXT);
      while(walker.nextNode()){
        const node=walker.currentNode;if(node.parentElement.closest('a,.arithmatex'))continue;
        if(/https?:\/\/[^\s<>"'`\u3000-\u9fff\uff00-\uffef]+/i.test(node.textContent))return {unlinked:chapter.id,text:node.textContent};
      }
    }
    return {links};
  });assert.ok(contentCheck.links>50,JSON.stringify(contentCheck));
  await page.goto(env.APP_BASE_URL+'/#home');
  await page.locator('.fact-label').filter({hasText:'互动交流'}).waitFor();
  assert.equal(await page.locator('.home-fact').count(),4);
  await page.waitForFunction(()=>document.querySelector('#communityCommentCount').textContent==='3');
  assert.equal(await page.locator('[data-fact="tasks"]').textContent(),await page.evaluate(()=>String(BOOK_DATA.scenes.length)));
  assert.equal(await page.locator('[data-fact="contributors"]').textContent(),'17');
  assert.equal(await page.locator('[data-fact="tasks"]').textContent(),'7');
  await page.screenshot({path:'/tmp/purplebook-updates-home-desktop.png'});
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'homepage mobile overflow');
  const factBounds=await page.locator('.home-fact').evaluateAll(nodes=>nodes.map(node=>node.getBoundingClientRect().bottom));
  assert.ok(factBounds.every(bottom=>bottom<=844),'all four homepage figures should fit the first mobile screen');
  await page.screenshot({path:'/tmp/purplebook-updates-home-mobile.png'});
  await page.setViewportSize({width:1280,height:900});
  await page.goto(env.APP_BASE_URL+'/#practice');
  assert.equal(await page.locator('#sceneGrid .scene').count(),7);
  assert.equal(await page.locator('#sceneGrid').getByText('阅读实践',{exact:true}).count(),0);
  assert.equal(await page.locator('#sceneGrid .scene').filter({hasText:'手机巡检助手'}).locator('img').getAttribute('src'),'assets/editorial-art/phone.png');
  assert.equal(await page.locator('#sceneGrid .scene').filter({hasText:'教学海报生成'}).locator('img').getAttribute('src'),'assets/editorial-art/poster.png');
  for(const title of ['手机巡检助手','教学海报生成']){
    const image=page.locator('#sceneGrid .scene').filter({hasText:title}).locator('img');
    await image.scrollIntoViewIfNeeded();
    await image.evaluate(image=>image.decode());
    assert.ok(await image.evaluate(image=>image.naturalWidth>0),'practice illustration should load');
  }
  await page.locator('#sceneGrid').screenshot({path:'/tmp/purplebook-practice-art-desktop.png'});
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'practice mobile overflow');
  await page.locator('#sceneGrid').screenshot({path:'/tmp/purplebook-practice-art-mobile.png'});
  await page.setViewportSize({width:1280,height:900});
  for(const [title,id] of [['手机巡检助手',21],['教学海报生成',26]]){
    await page.getByRole('heading',{name:title,exact:true}).getByRole('link').click();
    await page.locator('#chapterNumber').getByText('第 '+id+' 章',{exact:true}).waitFor();
    await page.goto(env.APP_BASE_URL+'/#practice');
  }
  await page.goto(env.APP_BASE_URL+'/#contribute');
  assert.equal(await page.locator('#contentContributors .contributor-person').count(),13);
  assert.equal(await page.locator('#codeContributors > a').count(),4);
  assert.equal(await page.locator('[data-page="contribute"]').getByRole('link',{name:'丰富的共学共建活动',exact:true}).count(),0);
  await page.getByText('吴晨飞',{exact:true}).waitFor();
  assert.equal(await page.getByText('与 GitHub 仓库名单同步',{exact:true}).count(),0);
  assert.equal(await page.locator('.contributor-name > nav').count(),13);
  await page.locator('#contentContributors').scrollIntoViewIfNeeded();
  await page.screenshot({path:'/tmp/purplebook-github-sync-community-desktop.png'});
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'contributors mobile overflow');
  await page.locator('#contentContributors').scrollIntoViewIfNeeded();
  await page.screenshot({path:'/tmp/purplebook-github-sync-community-mobile.png'});
  await page.setViewportSize({width:1280,height:900});
  await page.goto(env.APP_BASE_URL+'/#events');
  await page.getByRole('link',{name:'感兴趣组织工作坊？',exact:true}).click();
  await page.getByRole('heading',{name:'加入交流群',exact:true}).waitFor();
  await page.goto(env.APP_BASE_URL+'/#chapter-23');
  const videos=page.locator('#articleBody video');assert.equal(await videos.count(),5);
  for(let i=0;i<5;i++){
    await videos.nth(i).evaluate(async video=>{video.muted=true;await video.play();});
    await page.waitForFunction(index=>{const video=document.querySelectorAll('#articleBody video')[index];return video.currentTime>0&&video.videoWidth>0&&video.duration>0;},i);
    await videos.nth(i).evaluate(video=>video.pause());
  }
  assert.equal(await page.locator('#articleBody a[download]').count(),0);
  await page.goto(env.APP_BASE_URL+'/#chapter-1');
  await page.locator('.entry-replies').getByText('收到，这是一条回复',{exact:true}).waitFor();
  const select=async()=>{await page.evaluate(()=>{const p=[...document.querySelectorAll('#articleBody p')].find(p=>p.firstChild?.nodeType===3&&p.firstChild.length>15);const r=document.createRange();r.setStart(p.firstChild,0);r.setEnd(p.firstChild,10);getSelection().removeAllRanges();getSelection().addRange(r);document.dispatchEvent(new KeyboardEvent('keyup',{key:'Shift',bubbles:true}));});};
  await select();await page.getByRole('button',{name:'划线 · 仅自己可见',exact:true}).click();await page.locator('.discussion-entry').getByText('仅自己可见').waitFor();
  await select();await page.getByRole('button',{name:'写想法',exact:true}).click();await page.locator('#annotationText').fill('<img src=x onerror=alert(1)> 这段很有帮助');await page.getByRole('button',{name:'公开发表',exact:true}).click();
  await page.locator('.discussion-entry').getByText('<img src=x onerror=alert(1)> 这段很有帮助',{exact:true}).waitFor();
  assert.equal(await page.locator('.discussion-entry p img').count(),0);
  await page.reload();await page.getByRole('button',{name:'划线与想法',exact:true}).click();await page.locator('.discussion-entry').getByText('仅自己可见').waitFor();
  await page.goto(env.APP_BASE_URL+'/#chapter-2');await page.getByRole('link',{name:'fanxiansheng00的魔搭主页（新窗口）',exact:true}).waitFor();
  await page.waitForFunction(()=>document.querySelector('.discussion-author')?.getAttribute('href')==='https://modelscope.cn/profile/fanxiansheng00');
  const legacyPopupPromise=context.waitForEvent('page');const intermediateNavigations=[];
  context.on('request',request=>{if(request.isNavigationRequest()&&/\/readers\/[^/]+\/profile/.test(request.url()))intermediateNavigations.push(request.url());});
  await context.route('https://modelscope.cn/profile/fanxiansheng00',route=>route.fulfill({body:'Verified fanxiansheng00 profile'}));
  await page.getByRole('link',{name:'fanxiansheng00的魔搭主页（新窗口）',exact:true}).click();
  const legacyPopup=await legacyPopupPromise;await legacyPopup.waitForURL('https://modelscope.cn/profile/fanxiansheng00');assert.equal(legacyPopup.url(),'https://modelscope.cn/profile/fanxiansheng00');assert.deepEqual(intermediateNavigations,[],'Studio must not wrap an application redirect in an iframe');await legacyPopup.close();
  await page.setViewportSize({width:390,height:844});await page.goto(env.APP_BASE_URL+'/#chapter-1');await page.locator('#chapterDiscussion').scrollIntoViewIfNeeded();
  await page.screenshot({path:'/tmp/purplebook-updates-comments-mobile.png'});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth), 'mobile page overflow');
  await page.screenshot({path:path.join(data,'mobile.png')});
  const guest=await browser.newPage();await guest.goto(env.APP_BASE_URL+'/#chapter-1');await guest.getByRole('button',{name:'划线与想法',exact:true}).click();await guest.locator('.discussion-entry').getByText('<img src=x onerror=alert(1)> 这段很有帮助',{exact:true}).waitFor();
  assert.equal(await guest.getByText('仅自己可见',{exact:true}).count(),0);assert.equal(await guest.locator('#chapterMessage').isDisabled(),true);
  await page.setViewportSize({width:1280,height:900});await page.goto(env.APP_BASE_URL+'/#contribute');
  await page.locator('#wishText:not([disabled])').waitFor();
  await page.locator('#wishText').fill('<img src=x onerror=alert(1)> 希望补充 RAG 本地部署教程');
  await page.getByRole('button',{name:'投下愿望',exact:true}).click();
  await page.locator('.wish-entry').getByText('<img src=x onerror=alert(1)> 希望补充 RAG 本地部署教程',{exact:true}).waitFor();
  assert.equal(await page.locator('.wish-entry img').count(),0);
  await page.reload();await page.locator('.wish-entry').waitFor();
  await page.locator('#wishPool').scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/purplebook-wishes-desktop.png'});
  await guest.goto(env.APP_BASE_URL+'/#contribute');await guest.locator('.wish-entry').waitFor();
  assert.equal(await guest.locator('#wishText').isDisabled(),true);assert.equal(await guest.locator('.wish-entry button').count(),0);
  await page.setViewportSize({width:390,height:844});await page.locator('#wishPool').scrollIntoViewIfNeeded();
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'wish pool mobile overflow');
  await page.screenshot({path:'/tmp/purplebook-wishes-mobile.png'});
  page.once('dialog',d=>d.accept());await page.locator('.wish-entry button').click();
  await page.getByText('还没有人许愿。你希望紫皮书补上的第一份实践是什么？',{exact:true}).waitFor();
  assert.deepEqual(errors,[]);console.log('PASS: browser comment, highlight, annotation, XSS text rendering, reload, chapter isolation, guest privacy, wishes publish/persist/delete/XSS/guest permissions, mobile layout');
 }finally{if(browser)await browser.close();server.kill();fs.rmSync(data,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
