"""Export GitHub-readable Markdown without rewriting the source manuscript.

HTML remains the canonical import format. Complex tables stay as inline HTML
inside Markdown so headerless rows, cell paragraphs and images keep their order.
This module uses only the Python standard library.
"""
import copy
import html
import re
import xml.etree.ElementTree as ET


def plain(node):
    return (node.text or '') + ''.join(plain(c) + (c.tail or '') for c in node)


def escape(text, preserve_urls=True):
    # Escape Markdown syntax in prose; code and TeX take separate paths.
    if preserve_urls:
        pieces = re.split(r'(https?://[^\s<>\u3000-\u9fff]+)', text)
        if len(pieces) > 1:
            return ''.join(piece if i % 2 else escape(piece, False) for i, piece in enumerate(pieces))
    text = html.escape(text, quote=False)
    # Entities keep underscores literal even when GFM auto-links a bare URL.
    text = text.replace('_', '&#95;')
    # Split the text node so GitHub cannot rewrite literal names as mentions.
    text = text.replace('@', '<span>@</span>')
    text = re.sub(r'([\\`*\[\]$~])', r'\\\1', text)
    text = re.sub(r'(?m)^([ \t]{4,})', lambda m: '&#32;' + m[0][1:], text)
    text = re.sub(r'(?m)^(\s*)([#+>-])', r'\1\\\2', text)
    return re.sub(r'(?m)^(\s*\d+)([.)])(?=\s)', r'\1\\\2', text)


def destination(url):
    match = re.fullmatch(r'#chapter-(\d+)(?:/(.+))?', url)
    if match:
        return f'chapter-{int(match[1]):02d}.md' + (f'#{match[2]}' if match[2] else '')
    return url


def to_markdown(article, number):
    heading_index = 0

    def children(node):
        output = escape(node.text or '')
        previous = None
        for child in node:
            if previous is not None and previous.tag == child.tag == 'code' and not previous.tail:
                output += '<!-- -->'
            output += inline(child) + escape(child.tail or '')
            previous = child
        return output

    def inline(node):
        tag = node.tag
        if tag == 'code':
            text = plain(node)
            fence = '`' * max(1, 1 + max((len(m[0]) for m in re.finditer(r'`+', text)), default=0))
            padding = ' ' if text.startswith(('`', ' ')) or text.endswith(('`', ' ')) else ''
            return fence + padding + text + padding + fence
        if tag == 'span' and 'arithmatex' in node.get('class', ''):
            text = plain(node)
            if not (text.startswith('\\(') and text.endswith('\\)')):
                raise ValueError('Unknown formula delimiters')
            # GitHub supports $`...`$ inline math, including literal dollar signs.
            formula = text[2:-2]
            if '\n' in formula or 'display-math' in node.get('class', ''):
                return '\n\n```math\n' + formula + ('' if formula.endswith('\n') else '\n') + '```\n\n'
            return '$`' + formula + '`$'
        if tag == 'img':
            if node.get('width') or node.get('height'):
                image = copy.deepcopy(node)
                image.tail = None
                return ET.tostring(image, encoding='unicode', method='html')
            alt = escape(node.get('alt', ''))
            return f'![{alt}](<{destination(node.get("src", ""))}>)'
        if tag == 'a':
            return f'[{children(node)}](<{destination(node.get("href", ""))}>)'
        if tag == 'br':
            return '<br>\n'
        if tag in {'b', 'strong', 'em', 'i', 'u', 'sup', 'sub', 's', 'del'}:
            # Inline tags avoid ambiguous emphasis boundaries in Chinese prose.
            tag = {'b': 'strong', 'i': 'em'}.get(tag, tag)
            # Block math must sit outside inline HTML for GitHub to render it.
            # TeX controls formula styling; retain emphasis on surrounding prose.
            parts = re.split(r'(\n\n```math\n.*?\n```\n\n)', children(node), flags=re.S)
            return ''.join(part if i % 2 else (f'<{tag}>' + part + f'</{tag}>' if part else '')
                           for i, part in enumerate(parts))
        if tag in {'span', 'p'}:
            return children(node)
        raise ValueError(f'Unsupported inline element: {tag}')

    def block(node):
        nonlocal heading_index
        tag = node.tag
        if re.fullmatch('h[1-6]', tag):
            anchor = ''
            if tag != 'h1':
                heading_index += 1
                anchor = f'<a id="c{number}-s{heading_index}"></a>\n\n'
            text = children(node)
            return anchor + '#' * int(tag[1]) + (' ' + text if text else '') + '\n\n'
        if tag == 'pre':
            text = plain(node)
            fence = '`' * max(3, 1 + max((len(m[0]) for m in re.finditer(r'`+', text)), default=0))
            language = node.get('data-language', 'text').lower()
            language = {'plain text': 'text', 'c++': 'cpp'}.get(language, language)
            if not re.fullmatch(r'[a-z0-9_+-]+', language):
                language = 'text'
            return fence + language + '\n' + text + ('' if text.endswith('\n') else '\n') + fence + '\n\n'
        if tag == 'p':
            return (children(node) or '<p></p>') + '\n\n'
        if tag in {'article', 'figure', 'div'}:
            output = escape(node.text) if (node.text or '').strip() else ''
            for child in node:
                output += block(child)
                if (child.tail or '').strip():
                    output += escape(child.tail)
            return output
        if tag in {'ul', 'ol'}:
            items = []
            for i, child in enumerate(node, start=int(node.get('start', '1'))):
                if child.tag != 'li':
                    raise ValueError('Unexpected list element')
                prefix = f'{i}. ' if tag == 'ol' else '- '
                if any(c.tag in {'p', 'ul', 'ol', 'pre', 'blockquote'} for c in child):
                    text = escape(child.text or '') + ''.join(block(c) + escape(c.tail or '') for c in child)
                else:
                    text = children(child)
                lines = text.rstrip('\n').split('\n')
                items.append(prefix + lines[0] + ''.join('\n' + ' ' * len(prefix) + line for line in lines[1:]))
            return '\n'.join(items) + '\n\n'
        if tag == 'blockquote':
            text = escape(node.text or '') + ''.join(block(c) + escape(c.tail or '') for c in node)
            return '\n'.join('> ' + line if line else '>' for line in text.rstrip('\n').split('\n')) + '\n\n'
        if tag == 'table':
            table = copy.deepcopy(node)
            # GFM renders raw tables, including image cells and headerless rows.
            for parent in table.iter():
                for child in list(parent):
                    if child.tag == 'colgroup':
                        parent.remove(child)
                for attr in list(parent.attrib):
                    if attr not in {'src', 'href', 'alt', 'title', 'colspan', 'rowspan'}:
                        del parent.attrib[attr]
            table.tail = None
            return ET.tostring(table, encoding='unicode', method='html') + '\n\n'
        if tag == 'hr':
            return '---\n\n'
        return inline(node) + '\n\n'

    return '<!-- Generated from ../source-html/chapter-%02d.html; do not edit independently. -->\n\n' % number + block(article).rstrip('\n') + '\n'
