import importlib.util
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('build_content',ROOT/'scripts/build-content.py')
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

def test_linkify_preserves_prose_code_and_existing_anchors():
    article=ET.fromstring('''<article><p>访问https://example.com/a_(b)，或 www.modelscope.cn。<b>https://example.com/?a=1&amp;b=2</b> (https://example.org/test). <a href="https://existing.com">现有链接</a></p><pre><code>url = "https://example.com/api"</code></pre></article>''')
    before=builder.plain(article)
    builder.linkify(article)
    assert builder.plain(article)==before
    assert [a.get('href') for a in article.iter('a')]==[
        'https://example.com/a_(b)','https://www.modelscope.cn','https://example.com/?a=1&b=2',
        'https://example.org/test','https://existing.com','https://example.com/api']
    assert all(a.get('target')=='_blank' and a.get('rel')=='noopener noreferrer' for a in article.iter('a'))
    assert not any(list(a.iter('a'))[1:] for a in article.iter('a'))
    builder.linkify(article)
    assert len(list(article.iter('a')))==6

def test_word_count_has_a_documented_reproducible_unit():
    assert builder.word_count(ET.fromstring('<p>你好 ModelScope AI 2026。</p>'))==5

def test_repository_changes_recompute_homepage_counts(tmp_path,monkeypatch):
    content=tmp_path/'content';content.mkdir()
    profiles=tmp_path/'assets/contributors';profiles.mkdir(parents=True)
    (content/'chapter.html').write_text('<article><h1>标题</h1><p>你好 AI</p></article>')
    manifest={'title':'Test','sourceUpdated':'2026-10-30','parts':[{'title':'篇'}],
              'chapters':[{'number':1,'title':'标题','file':'chapter.html','status':'ready','partIndex':0}]}
    (content/'manifest.json').write_text(json.dumps(manifest))
    (content/'practice.json').write_text('[{"id":1},{"id":2}]')
    (profiles/'profiles.json').write_text('[{"handle":"Alice"},{"handle":"alice"},{"handle":"Bob"}]')
    monkeypatch.setattr(builder,'ROOT',tmp_path);monkeypatch.setattr(builder,'CONTENT',content)
    def stats():
        builder.build()
        payload=(tmp_path/'assets/content.js').read_text().removeprefix('window.BOOK_DATA = ').removesuffix(';\n')
        return json.loads(payload)['stats']
    assert stats()=={'contributors':2,'tasks':1,'words':5}
    (content/'chapter.html').write_text('<article><h1>标题</h1><p>你好世界 AI</p></article>')
    (profiles/'profiles.json').write_text('[{"handle":"Alice"}]')
    (content/'practice.json').write_text('[]')
    assert stats()=={'contributors':1,'tasks':0,'words':7}
