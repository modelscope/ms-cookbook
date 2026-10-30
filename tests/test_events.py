"""Protect the activity manuscript while its links become platform icons."""
import importlib.util
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('activity_builder', ROOT / 'scripts/build-events.py')
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.images = []

    def handle_data(self, value):
        self.text.append(value)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a': self.links.append(attrs)
        if tag == 'img': self.images.append(attrs)


def normalized(value):
    return re.sub(r'\s+', '', value)


def test_guest_wording_and_profile_destinations_survive_rendering():
    for event in BUILDER.load_events():
        for kind, markup, source in event['blocks']:
            if kind != 'speaker': continue
            reader = Reader()
            reader.feed(markup)
            urls = re.findall(r'https://[^\s<>；]+', source)
            expected = re.sub(r'https://[^\s<>；]+|\*', '', source)
            assert normalized(''.join(reader.text)) == normalized(expected)
            assert [link['href'] for link in reader.links] == urls
            assert len(reader.images) == len(urls)
            assert all(image['width'] == image['height'] == '18' for image in reader.images)


def test_all_three_platforms_use_their_own_logos():
    for url, logo in [('https://modelscope.cn/profile/example', 'modelscope.ico'),
                      ('https://github.com/example', 'github.svg'),
                      ('https://www.zhihu.com/people/example', 'zhihu.ico')]:
        reader = Reader()
        reader.feed(BUILDER.inline(url, speaker=True))
        assert reader.links[0]['href'] == url
        assert reader.images[0]['src'].endswith('/' + logo)
        assert (ROOT / reader.images[0]['src']).is_file()


def test_markdown_replay_link_and_original_titles():
    for event in BUILDER.load_events():
        reader = Reader()
        reader.feed(BUILDER.card(event))
        assert event['title'] in ''.join(reader.text)
        for link in reader.links:
            assert '](' not in link['href']
        if 'bilibili.com' in event['body']:
            assert any(link.get('class') == 'text-link event-replay' for link in reader.links)


def test_exhibition_date_range_is_preserved():
    exhibition = next(event for event in BUILDER.load_events() if event['id'] == 'yunqi-20261021')
    assert exhibition['start'] == '2026-10-21' and exhibition['end'] == '2026-10-23'
    assert '时间：2026 年 10 月 21 日-23 日' in exhibition['body']


def test_github_renders_chinese_labels_and_replay_urls():
    for event in BUILDER.load_events():
        rendered = BUILDER.github_body(event)
        assert '**主讲人：**' not in rendered
        assert '\\_' not in rendered
        reader = Reader()
        reader.feed(rendered)
        for link in reader.links:
            assert '\\' not in link['href']
        assert all(image['src'].startswith('../../assets/') for image in reader.images)
