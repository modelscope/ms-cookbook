"""Build BOOK_DATA from reviewable chapter HTML; optionally import a Feishu snapshot.

Usage: python3 scripts/build-content.py
       python3 scripts/build-content.py --snapshot /path/to/snapshot --date YYYY-MM-DD
The importer needs Pillow. Normal builds and validation use only Python's stdlib.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from chapter_markdown import to_markdown

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / 'content'
REPO = 'https://github.com/modelscope/ms-cookbook'
SHORT_PARTS = ['认识开源模型', '从问题出发', '让模型工作起来', '微调与评测', '业务系统实践', 'AIGC 特别篇', 'Agent 特别篇', '基础知识补充']
SAFE = set('article p br hr h1 h2 h3 h4 h5 h6 ul ol li blockquote pre code strong em b i s del sup sub table thead tbody tr th td colgroup col a img span div figure u'.split())

def digest(value):
    return hashlib.sha256(value).hexdigest()

def plain(node):
    return (node.text or '') + ''.join(('\n' if c.tag == 'br' else plain(c)) + (c.tail or '') for c in node)

def dump(node):
    return ET.tostring(node, encoding='unicode', method='html')

def xml_dump(node):
    return ET.tostring(node, encoding='unicode', short_empty_elements=True)

URL_PATTERN = re.compile(r'(?:https?://|www\.)[^\s<>"\'`\u3000-\u303f\u3400-\u9fff\uff00-\uffef]+', re.I)

def linkify(article):
    """Link visible URLs without changing text, code copying or existing anchors."""
    def fragments(text):
        output=[];start=0
        for match in URL_PATTERN.finditer(text or ''):
            url=match[0].rstrip('.,;:!?')
            while url and url[-1] in ')]}' and url.count(url[-1]) > url.count({')':'(',']':'[','}':'{'}[url[-1]]):
                url=url[:-1]
            if not url or url.lower() in ('http://','https://','www.'): continue
            output.append(html.escape(text[start:match.start()]))
            href=url if not url.lower().startswith('www.') else 'https://'+url
            output.append('<a href="'+html.escape(href,quote=True)+'" target="_blank" rel="noopener noreferrer">'+html.escape(url)+'</a>')
            start=match.start()+len(url)
        output.append(html.escape((text or '')[start:]))
        return ET.fromstring('<span>'+''.join(output)+'</span>')
    def walk(node):
        if node.tag=='a':
            if re.match(r'https?://',node.get('href',''),re.I):
                node.set('target','_blank');node.set('rel','noopener noreferrer')
            return
        if node.tag=='span' and 'arithmatex' in node.get('class',''): return
        original=list(node)
        for child in original: walk(child)
        content=fragments(node.text);node.text=content.text
        for index,link in enumerate(content): node.insert(index,link)
        for child in original:
            content=fragments(child.tail);child.tail=content.text
            index=list(node).index(child)+1
            for offset,link in enumerate(content): node.insert(index+offset,link)
    walk(article)

def word_count(article):
    """Count Han characters plus Latin/number words in visible chapter text."""
    return len(re.findall(r'[\u3400-\u9fff]|[A-Za-z0-9]+(?:[\x27_-][A-Za-z0-9]+)*', plain(article)))

def import_snapshot(snapshot, date):
    from PIL import Image, ImageOps
    catalog = json.loads((snapshot / 'catalog.json').read_text())
    chapter_dir = CONTENT / 'source-html'
    chapter_dir.mkdir(parents=True, exist_ok=True)
    routes = {c['token']: '#chapter-' + str(c['number']) for c in catalog['chapters']}
    media_index = {m['token']: m for m in json.loads((snapshot / 'media-index.json').read_text())}
    localized = {}
    def media(token, number):
        if token in localized:
            return localized[token]
        matches = list((snapshot / 'media').glob(token + '.*'))
        if (snapshot / 'media' / token).exists():
            matches.append(snapshot / 'media' / token)
        if len(matches) != 1:
            raise ValueError(f'Missing or ambiguous media: {token}')
        source = matches[0]
        is_image = media_index[token]['type'] == 'img'
        suffix = '.webp' if is_image else Path(media_index[token]['name']).suffix.lower()
        filename = f'c{number:02d}-{digest(source.read_bytes())[:14]}{suffix}'
        target = ROOT / 'assets/manuscript-20260914' / filename
        if not target.exists():
            if is_image:
                with Image.open(source) as opened:
                    im = ImageOps.exif_transpose(opened)
                    im.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
                    im.convert('RGBA' if 'A' in im.getbands() else 'RGB').save(target, 'WEBP', quality=88, method=6)
            else:
                shutil.copyfile(source, target)
        localized[token] = '../../' + str(target.relative_to(ROOT))
        return localized[token]

    entries, reports = [], []
    for c in catalog['chapters']:
        number = c['number']
        folder = snapshot / 'chapters' / f'{number:02d}'
        doc = json.loads((folder / 'xml.json').read_text())['document']
        md = json.loads((folder / 'markdown.json').read_text())['document']
        assert doc['revision_id'] == md['revision_id'], 'Document changed during fetch'
        original = ET.fromstring('<article>' + doc['content'] + '</article>')
        expected_headings = [(n.tag, plain(n)) for n in original.iter() if re.fullmatch('h[1-6]', n.tag)]
        expected_code = [plain(n) for n in original.iter('pre')]
        expected_math = [plain(n) for n in original.iter('latex')]
        sheet_evidence = []
        def convert(node):
            tag = node.tag
            if tag == 'title':
                tag = 'h1'
            if tag == 'sheet':
                source = json.loads((snapshot / 'sheets' / (node.attrib['sheet-id'] + '.json')).read_text())
                sheet = source['sheets'][0]
                assert sheet['range'].startswith('A1:'), sheet['range']
                structure = json.loads((snapshot / 'sheets' / (node.attrib['sheet-id'] + '-structure.json')).read_text())
                assert not structure['merged_cells'], 'Merged sheet requires explicit span mapping'
                assert not structure['hidden_rows'] and not structure['hidden_columns'], 'Review hidden sheet cells before publishing'
                assert structure['range'] == sheet['range'], 'Incomplete sheet range'
                table = ET.Element('table')
                for row in sheet['data']:
                    tr = ET.SubElement(table, 'tr')
                    for value in row:
                        td = ET.SubElement(tr, 'td')
                        td.text = '' if value is None else str(value)
                sheet_evidence.append({'sheetId': node.attrib['sheet-id'], 'range': sheet['range'], 'revision': structure['revision'], 'mergedCells': structure['merged_cells'], 'rows': len(sheet['data']), 'sha256': digest(json.dumps(sheet['data'], ensure_ascii=False).encode())})
                return table
            if tag == 'latex':
                formula = plain(node)
                return ET.fromstring('<span class="arithmatex' + (' display-math' if '\n' in formula else '') + '">\\(' + html.escape(formula) + '\\)</span>')
            if tag == 'source':
                return ET.Element('a', {'href': media(node.attrib['token'], number), 'class': 'attachment', 'download': node.attrib['name']})
            if tag == 'pre':
                result = ET.Element('pre', {'data-language': node.attrib.get('lang', 'text')})
                ET.SubElement(result, 'code').text = plain(node)
                return result
            if tag in {'grid', 'column'}:
                tag = 'div'
            if tag not in SAFE:
                raise ValueError(f'Unsupported source element {tag}')
            attrs = {k: v for k, v in node.attrib.items() if k in {'href', 'src', 'alt', 'title', 'colspan', 'rowspan', 'start', 'span'}}
            if node.tag in {'grid', 'column'}:
                attrs['class'] = 'source-' + node.tag
            if tag == 'img':
                attrs = {'src': media(node.attrib['src'], number), 'alt': '正文配图', 'class': 'article-image', 'loading': 'lazy', 'decoding': 'async'}
            if tag == 'a':
                parsed = urlparse(attrs.get('href', ''))
                if parsed.scheme and parsed.scheme not in {'https', 'http', 'mailto'}:
                    raise ValueError('Unsafe link in source')
                token = parsed.path.rstrip('/').split('/')[-1]
                if parsed.hostname and parsed.hostname.endswith('.feishu.cn') and token in routes:
                    attrs['href'] = routes[token]
                elif parsed.scheme in {'http', 'https'}:
                    attrs.update(target='_blank', rel='noopener noreferrer')
            result = ET.Element(tag, attrs)
            result.text = node.text
            for child in node:
                new = convert(child)
                if child.tag == 'source':
                    new.text = child.attrib['name']
                new.tail = child.tail
                result.append(new)
            return result
        article = convert(original)
        actual_headings = [(n.tag, plain(n)) for n in article.iter() if re.fullmatch('h[1-6]', n.tag)][1:]
        assert actual_headings == expected_headings, f'Heading mismatch in {number}'
        assert [plain(n) for n in article.iter('pre')] == expected_code, f'Code mismatch in {number}'
        assert [plain(n)[2:-2] for n in article.iter('span') if 'arithmatex' in n.attrib.get('class', '')] == expected_math
        # Compare every original prose node in sequence, including list/table nesting.
        prose_tags = {'p', 'li', 'blockquote', 'h2', 'h3', 'h4', 'h5', 'h6'}
        def prose(node):
            if node.tag in {'img', 'source', 'sheet'}:
                return ''
            if node.tag == 'latex':
                return '\\(' + plain(node) + '\\)'
            return (node.text or '') + ''.join(('\n' if x.tag == 'br' else prose(x)) + (x.tail or '') for x in node)
        expected = [(n.tag, prose(n)) for n in original.iter() if n.tag in prose_tags]
        actual = [(n.tag, plain(n)) for n in article.iter() if n.tag in prose_tags]
        assert actual == expected, f'Prose mismatch in {number}'
        file = f'source-html/chapter-{number:02d}.html'
        # Newlines between top-level blocks make source reviewable without altering inline text/code.
        source_html = '<article>\n' + '\n'.join(xml_dump(n) for n in article) + '\n</article>\n'
        (CONTENT / file).write_text(source_html)
        status = 'pending' if '敬请期待' in plain(article) and len(plain(article)) < 150 else 'ready'
        entries.append({'number': number, 'title': c['title'], 'partIndex': c['partIndex'], 'file': file, 'status': status})
        reports.append({'number': number, 'revision': doc['revision_id'], 'sourceXmlSha256': digest(doc['content'].encode()), 'sourceMarkdownSha256': digest(md['content'].encode()), 'chapterFileSha256': digest(source_html.encode()), 'headings': len(expected_headings), 'codeBlocks': len(expected_code), 'formulas': len(expected_math), 'images': len(list(original.iter('img'))), 'attachments': len(list(original.iter('source'))), 'embeddedSheets': sheet_evidence, 'proseVerified': True, 'headingOrderVerified': True, 'codeVerified': True, 'formulasVerified': True})
        print(f'Imported {number:02d}: revision {doc["revision_id"]}; prose, headings, code and math verified')
    manifest = {'title': '魔搭紫皮书', 'sourceUpdated': date, 'parts': [{'title': p['title'], 'shortTitle': SHORT_PARTS[i]} for i,p in enumerate(catalog['parts'])], 'chapters': entries}
    (CONTENT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (CONTENT / 'sync-report.json').write_text(json.dumps({'syncedAt': date, 'method': 'Feishu XML and embedded sheet values; no prose rewriting', 'chapters': reports}, ensure_ascii=False, indent=2) + '\n')

def build(check=False):
    manifest = json.loads((CONTENT / 'manifest.json').read_text())
    chapters = []
    for entry in manifest['chapters']:
        number = entry['number']
        article = ET.fromstring((CONTENT / entry['file']).read_text())
        markdown = CONTENT / 'chapters' / f'chapter-{number:02d}.md'
        markdown_output = to_markdown(article, number)
        if check:
            if not markdown.exists() or markdown.read_text() != markdown_output:
                raise SystemExit(f'{markdown.relative_to(ROOT)} is out of date. Run python3 scripts/build-content.py.')
        else:
            markdown.parent.mkdir(parents=True, exist_ok=True)
            markdown.write_text(markdown_output)
        title = article.find('h1')
        assert title is not None and plain(title) == entry['title']
        article.remove(title)
        headings = []
        for node in article.iter():
            assert node.tag in SAFE, f'Unsupported HTML: {node.tag}'
            assert not any(k.lower().startswith('on') for k in node.attrib)
            if re.fullmatch('h[1-6]', node.tag):
                anchor = f'c{number}-s{len(headings)+1}'
                node.set('id', anchor)
                headings.append({'id': anchor, 'text': plain(node), 'level': node.tag})
            for attr in ('href', 'src'):
                value = node.get(attr, '')
                if value.startswith('../../assets/'):
                    value = value[6:]
                    assert (ROOT / value).is_file(), value
                    node.set(attr, value)
                assert not urlparse(value).scheme or urlparse(value).scheme in {'https', 'http', 'mailto'}, 'Unsafe URL'
        linkify(article)
        for parent in list(article.iter()):
            for i, child in enumerate(list(parent)):
                if child.tag == 'table':
                    wrapper = ET.Element('div', {'class': 'table-scroll'})
                    parent.remove(child)
                    wrapper.append(child)
                    parent.insert(i, wrapper)
        body = '\n'.join(dump(n) for n in article)
        chapters.append({'id': f'chapter-{number}', 'number': number, 'title': entry['title'], 'sourceUrl': f'{REPO}/blob/main/content/chapters/chapter-{number:02d}.md', 'editUrl': f'{REPO}/edit/main/content/{entry["file"]}', 'minutes': max(1, round(len(re.sub(r'\s+', '', plain(article))) / 520)) if entry['status']=='ready' else 0, 'status': entry['status'], 'headings': headings, 'html': body, 'imageCount': len(list(article.iter('img'))), 'attachmentCount': sum(n.get('class') == 'attachment' for n in article.iter('a'))})
    for chapter, entry in zip(chapters, manifest['chapters']):
        chapter['discussionId'] = entry.get('discussionId', chapter['id'])
    payload = {k: manifest[k] for k in ('title', 'sourceUpdated')}
    payload.update(sourceUrl=f'{REPO}/tree/main/content', chapterCount=len(chapters), readyCount=sum(c['status']=='ready' for c in chapters), imageCount=sum(c['imageCount'] for c in chapters), attachmentCount=sum(c['attachmentCount'] for c in chapters))
    payload['parts'] = [{'id': f'part-{i+1:02d}', **p, 'chapters': [f'chapter-{c["number"]}' for c in manifest['chapters'] if c['partIndex']==i]} for i,p in enumerate(manifest['parts'])]
    payload['chapters'] = chapters
    profiles=json.loads((ROOT/'assets/contributors/profiles.json').read_text())
    scenes=json.loads((CONTENT/'practice.json').read_text())
    ready={c['number'] for c in chapters if c['status']=='ready'}
    payload['scenes']=[s for s in scenes if s['id'] in ready]
    payload['stats']={
        'contributors':len({p['handle'].casefold() for p in profiles}),
        'tasks':len(payload['scenes']),
        'words':sum(word_count(ET.fromstring((CONTENT/e['file']).read_text())) for e in manifest['chapters'] if e['status']=='ready'),
    }
    output = 'window.BOOK_DATA = ' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n'
    target = ROOT / 'assets/content.js'
    if check:
        if not target.exists() or target.read_text() != output:
            raise SystemExit('assets/content.js is out of date. Run python3 scripts/build-content.py.')
    else:
        target.write_text(output)
    print(f'{"Verified" if check else "Built"} {len(chapters)} chapters, {payload["imageCount"]} images, {payload["attachmentCount"]} attachments')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--date')
    parser.add_argument('--check', action='store_true', help='Validate generated content without writing files')
    args = parser.parse_args()
    if args.check and args.snapshot:
        parser.error('--check cannot be combined with --snapshot')
    if args.snapshot:
        if not args.date:
            parser.error('--date is required with --snapshot')
        import_snapshot(args.snapshot.resolve(), args.date)
    build(check=args.check)
