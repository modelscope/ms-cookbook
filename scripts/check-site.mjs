import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import vm from 'node:vm';
import {spawnSync} from 'node:child_process';

const root=resolve(import.meta.dirname,'..');
const read=path=>readFileSync(resolve(root,path),'utf8');
const context={window:{}};
vm.runInNewContext(read('assets/content.js'),context);
const data=context.window.BOOK_DATA;
const manifest=JSON.parse(read('content/manifest.json'));
assert.equal(data.chapters.length,manifest.chapters.length);
assert.equal(new Set(data.chapters.map(c=>c.id)).size,data.chapterCount);
assert.deepEqual(manifest.chapters.map(c=>c.number),Array.from({length:data.chapterCount},(_,i)=>i+1),'Chapter numbers must follow book order');
assert.equal(new Set(data.chapters.map(c=>c.discussionId)).size,data.chapterCount,'Discussion storage keys must be unique');
const ids=new Set(data.chapters.map(c=>c.id));
const partIds=data.parts.flatMap(p=>p.chapters);
assert.equal(partIds.length,ids.size);
assert.equal(new Set(partIds).size,ids.size);
for(const id of partIds)assert(ids.has(id));
let imageCount=0,attachmentCount=0;
function checkLinks(html,base='.'){
  for(const tag of html.matchAll(/<(?:a|img|video|script|link)\b[^>]*>/g))for(const m of tag[0].matchAll(/(?:src|href)="([^"]+)"/g)){
    const url=m[1];
    assert(!/^(javascript|data|vbscript):/i.test(url),'Unsafe URL');
    if(/^#chapter-/.test(url))assert(ids.has(url.slice(1).split('/')[0]),'Unknown chapter '+url);
    if(/^(?:[a-z]+:|#|\/\/)/i.test(url))continue;
    const path=decodeURIComponent(url.split(/[?#]/)[0]);
    if(path)assert(existsSync(resolve(root,base,path)),'Missing local file '+path);
  }
}
for(const chapter of data.chapters){
  assert(!/<(?:script|iframe|object|embed)\b/i.test(chapter.html));
  assert(chapter.sourceUrl.startsWith('https://github.com/modelscope/ms-cookbook/blob/main/content/chapters/'));
  assert(chapter.sourceUrl.endsWith('.md'));
  assert(chapter.editUrl.startsWith('https://github.com/modelscope/ms-cookbook/edit/main/content/source-html/'));
  assert(existsSync(resolve(root,'content/chapters',`chapter-${String(chapter.number).padStart(2,'0')}.md`)));
  const anchors=new Set([...chapter.html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]));
  for(const heading of chapter.headings)assert(anchors.has(heading.id));
  imageCount+=(chapter.html.match(/<img\b/g)||[]).length;
  attachmentCount+=(chapter.html.match(/class="attachment"/g)||[]).length;
  checkLinks(chapter.html);
}
assert.equal(imageCount,data.imageCount);assert.equal(attachmentCount,data.attachmentCount);
checkLinks(read('index.html'));
const eventsCheck=spawnSync('python3',[resolve(root,'scripts/build-events.py'),'--check'],{encoding:'utf8'});
assert.equal(eventsCheck.status,0,eventsCheck.stderr||eventsCheck.stdout);
checkLinks(read('assets/analytics.html'));
assert(!/feishu\.cn/.test(read('index.html')),'Source UI must point to GitHub');
assert(!/art:'plane'|paper\/plane\.webp/.test(read('assets/paper.js')+read('index.html')));
checkLinks(read('README.md'));checkLinks(read('README.zh-CN.md'));
for(const css of ['assets/styles.css','assets/paper.css','assets/review.css','assets/reader-tools.css']){
  for(const m of read(css).matchAll(/url\(['"]?([^)'"\s]+)['"]?\)/g)){
    if(!/^(?:https?:|data:)/.test(m[1]))assert(existsSync(resolve(root,dirname(css),m[1].split('?')[0])),m[1]);
  }
}
console.log(`PASS: ${data.chapterCount} chapters, ${data.parts.length} parts, ${imageCount} image references, ${attachmentCount} attachments; local links and source routes valid.`);
