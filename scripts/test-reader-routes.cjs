const {test} = require('node:test');
const assert = require('node:assert/strict');
const {parseHash, chapterHash, pathStep} = require('../assets/reader-routes.js');
const paths = {beginner:{name:'从零开始',chapters:[1,5,7]},aigc:{name:'AIGC 创作',chapters:[24,25,26,27,29]}};

test('从零开始沿 1→5→7 导航，首尾不越界',()=>{
  assert.equal(pathStep(paths,'beginner',1).next,5);
  assert.equal(pathStep(paths,'beginner',1).previous,null);
  assert.equal(pathStep(paths,'beginner',5).previous,1);
  assert.equal(pathStep(paths,'beginner',5).next,7);
  assert.equal(pathStep(paths,'beginner',7).next,null);
  assert.equal(pathStep(paths,'beginner',7).index,2);
});
test('AIGC 路径顺延后包含第 27 章，再跳过待补充的 28',()=>{
  assert.equal(pathStep(paths,'aigc',26).next,27);
  assert.equal(pathStep(paths,'aigc',27).previous,26);
  assert.equal(pathStep(paths,'aigc',27).next,29);
  assert.equal(pathStep(paths,'aigc',29).total,5);
});
test('路径与小节可同时写入链接，刷新后可从 URL 恢复',()=>{
  const hash=chapterHash('chapter-5','c5-s2','beginner');
  assert.equal(hash,'#chapter-5/c5-s2?path=beginner');
  assert.deepEqual(parseHash(hash,paths),{name:'chapter-5',sub:'c5-s2',pathKey:'beginner'});
});
test('普通章节和历史小节链接继续有效，不携带路径',()=>{
  assert.equal(chapterHash('chapter-2'),'#chapter-2');
  assert.deepEqual(parseHash('#chapter-12/c12-s6',paths),{name:'chapter-12',sub:'c12-s6',pathKey:''});
  assert.deepEqual(parseHash('#paths/beginner',paths),{name:'paths',sub:'beginner',pathKey:''});
});
test('无效路径或不属于路径的章节回到普通阅读',()=>{
  for(const hash of ['#chapter-2?path=beginner','#chapter-1?path=missing','#chapter-1?path=__proto__','#chapter-1?path=constructor']) {
    assert.equal(parseHash(hash,paths).pathKey,'');
  }
  assert.equal(pathStep(paths,'beginner',2),null);
});
