#!/usr/bin/env python3
"""Render the supplied activity manuscript into the website and GitHub reading view.

Keep source.md verbatim; manifest.json contains presentation metadata only.
No external Markdown dependency or runtime fetch is required.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'content/events/source.md'
MANIFEST = ROOT / 'content/events/manifest.json'
PLATFORMS = {
    'modelscope.cn': ('魔搭', 'modelscope.ico'),
    'github.com': ('GitHub', 'github.svg'),
    'zhihu.com': ('知乎', 'zhihu.ico'),
}
TOKEN = re.compile(r'!\[([^\]]*)\]\((https://[^)]+)\)|\[([^\]]+)\]\((https://[^)]+)\)|https://[^\s<>；]+|\*\*([^*]+)\*\*')


def clean_url(url):
    return url.replace('\\_', '_')


def platform(url):
    host = urlparse(url).hostname or ''
    return PLATFORMS.get(host.removeprefix('www.'))


def icon_link(url, prefix=''):
    label, icon = platform(url)
    return (f'<a class="event-profile-link" href="{html.escape(clean_url(url), quote=True)}" '
            f'target="_blank" rel="noopener noreferrer" title="{label}" aria-label="{label}（新窗口）">'
            f'<img src="{prefix}assets/brand/{icon}" width="18" height="18" alt="{label}"></a>')


def inline(text, speaker=False):
    result = []
    offset = 0
    for match in TOKEN.finditer(text):
        result.append(html.escape(text[offset:match.start()]))
        if match.group(1) is not None:
            url = clean_url(match.group(2))
            path = 'assets/events/' + url.rsplit('/', 1)[-1]
            if not (ROOT / path).is_file():
                raise ValueError(f'Missing activity image: {path}')
            result.append(f'<a class="event-image" href="{path}" target="_blank" rel="noopener noreferrer" aria-label="放大查看活动图片"><img src="{path}" alt="{html.escape(match.group(1), quote=True)}" loading="lazy"></a>')
        elif match.group(3) is not None:
            url = clean_url(match.group(4))
            result.append(icon_link(url) if speaker and platform(url) else f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(match.group(3))}</a>')
        elif match.group(5) is not None:
            result.append('<strong>' + html.escape(match.group(5)) + '</strong>')
        else:
            url = clean_url(match.group())
            result.append(icon_link(url) if speaker and platform(url) else f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(url)}</a>')
        offset = match.end()
    result.append(html.escape(text[offset:]))
    return ''.join(result)


def blocks(body):
    paragraphs = re.split(r'\n\s*\n', body.strip())
    rendered, speaker_next = [], False
    for paragraph in paragraphs:
        value = paragraph.strip()
        # A standalone 主讲人 label is followed by either a list or prose.
        plain = value.replace('**', '')
        boundary = re.match(r'^(面向人群|直播内容|简介|直播时间|时间|地点|直播回放)[:：]|^!\[', plain)
        speaker = '主讲人：' in value or (speaker_next and not boundary)
        is_label = re.sub(r'\*\*|\s', '', value) == '主讲人：'
        speaker_next = is_label or (speaker_next and speaker)
        if re.match(r'^\*\s', value):
            items = re.split(r'\n\s*\*\s+', re.sub(r'^\*\s+', '', value))
            markup = '<ul>' + ''.join('<li>' + inline(item.strip(), speaker) + '</li>' for item in items) + '</ul>'
        elif value.startswith('!['):
            markup = '<div class="event-gallery">' + inline(value) + '</div>'
        else:
            markup = '<p>' + inline(value, speaker) + '</p>'
        kind = 'speaker' if speaker else 'meta' if re.match(r'^(直播时间|时间|地点)：', value) else 'image' if value.startswith('![') else 'body'
        rendered.append((kind, markup, value))
    return rendered


def load_events():
    parts = re.split(r'^### ', SOURCE.read_text(), flags=re.M)[1:]
    metadata = json.loads(MANIFEST.read_text())['events']
    assert len(parts) == len(metadata), 'Each source activity needs exactly one manifest entry'
    assert sorted(event['sourceIndex'] for event in metadata) == list(range(len(parts)))
    assert len({event['id'] for event in metadata}) == len(metadata)
    events = []
    for item in metadata:
        title, body = parts[item['sourceIndex']].split('\n', 1)
        assert re.fullmatch(r'[a-z0-9-]+', item['id'])
        assert item['start'] <= item['end']
        events.append({**item, 'title': title, 'body': body.strip(), 'blocks': blocks(body)})
    return sorted(events, key=lambda event: (event['start'], event['sourceIndex']), reverse=True)


def date_label(event):
    start, end = event['start'], event['end']
    return start[5:].replace('-', '.') + (('–' + end[-2:]) if end != start else '')


def card(event):
    intro = ''.join(markup for kind, markup, _ in event['blocks'] if kind in ('speaker', 'meta'))
    detail = ''.join(markup for kind, markup, _ in event['blocks'] if kind == 'body')
    gallery = ''.join(markup for kind, markup, _ in event['blocks'] if kind == 'image')
    replay = re.search(r'https://www\.bilibili\.com/[^\s)\]]+', event['body'])
    replay_link = f'<a class="text-link event-replay" href="{html.escape(clean_url(replay.group()), quote=True)}" target="_blank" rel="noopener noreferrer">观看回放 ↗</a>' if replay else ''
    # The body itself retains the original 直播回放 label and link.
    details = f'<details class="event-details"><summary>活动详情</summary><div class="event-body">{detail}{gallery}</div></details>' if detail else gallery
    return (f'<li class="event-node" id="event-{event["id"]}" data-start="{event["start"]}" data-end="{event["end"]}">'
            f'<div class="event-date"><time datetime="{event["start"]}">{date_label(event)}</time></div>'
            '<article class="event-card">'
            f'<div class="event-kicker"><span>{event["type"]}</span><span class="event-status"></span></div>'
            f'<h3>{html.escape(event["title"])}</h3><div class="event-intro">{intro}</div>'
            f'{replay_link}{details}</article></li>')


def timeline(events):
    groups = {}
    for event in events:
        groups.setdefault(event['start'][:7], []).append(event)
    return '\n'.join(f'<section class="event-month" data-month="{month}"><h2>{month[:4]} 年 {int(month[5:])} 月</h2><ol class="event-timeline">' + ''.join(card(event) for event in items) + '</ol></section>' for month, items in groups.items())


def preview(events):
    return '<ol class="event-preview-list">' + ''.join(
        f'<li><a href="#events/{event["id"]}"><time datetime="{event["start"]}">{date_label(event)}</time>'
        f'<span><small>{event["type"]}</small><strong>{html.escape(event["title"])}</strong></span><span aria-hidden="true">↗</span></a></li>'
        for event in events[:3]) + '</ol>'


def github_body(event):
    # GFM treats **label：** followed directly by Chinese as literal asterisks.
    # Reuse the rendered manuscript so both views preserve the same prose and
    # URL destinations, including Markdown-escaped underscores in replay URLs.
    return '\n\n'.join(markup.replace('src="assets/', 'src="../../assets/')
                       .replace('href="assets/', 'href="../../assets/')
                       for _, markup, _ in event['blocks'])


def github_timeline(events):
    content = ['# 共建活动时间线', '', '[在线查看时间线](https://modelscope.cn/studios/ms-cookbook-team/ms-cookbook) · [返回项目首页](../../README.md)', '']
    for event in events:
        content += [f'<a id="{event["id"]}"></a>', '', f'## {event["start"]}' + (f' 至 {event["end"]}' if event['end'] != event['start'] else '') + f' · {event["type"]}', '', f'### {event["title"]}', '', github_body(event), '', '---', '']
    return '\n'.join(content)


def github_preview(events):
    return '\n'.join([f'- **{date_label(event)} · {event["type"]}**　[{event["title"]}](content/events/README.md#{event["id"]})' for event in events[:3]]) + '\n\n[查看完整活动时间线 →](content/events/README.md)'


def replace_region(text, name, value):
    pattern = re.compile(rf'(<!-- {name}:start -->).*?(<!-- {name}:end -->)', re.S)
    assert len(pattern.findall(text)) == 1, f'Missing or duplicate {name} markers'
    return pattern.sub(lambda match: match[1] + '\n' + value + '\n' + match[2], text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    events = load_events()
    index = ROOT / 'index.html'
    page = replace_region(index.read_text(), 'events-timeline', timeline(events))
    page = replace_region(page, 'events-preview', preview(events))
    for asset in ('assets/paper.js', 'assets/events.js', 'assets/events.css'):
        digest = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:12]
        page = re.sub(rf'((?:src|href)="{re.escape(asset)})(?:\?v=[^"]+)?(")', rf'\1?v={digest}\2', page)
    outputs = {index: page, ROOT / 'content/events/README.md': github_timeline(events)}
    for name in ('README.md', 'README.zh-CN.md'):
        path = ROOT / name
        outputs[path] = replace_region(path.read_text(), 'events-preview', github_preview(events))
    for path, output in outputs.items():
        if args.check:
            if not path.exists() or path.read_text() != output:
                raise SystemExit(f'{path.relative_to(ROOT)} is out of date; run python3 scripts/build-events.py')
        else:
            path.write_text(output)
    print(f'PASS: {len(events)} activities; manuscript-based website and GitHub timeline ' + ('verified.' if args.check else 'generated.'))


if __name__ == '__main__':
    main()
