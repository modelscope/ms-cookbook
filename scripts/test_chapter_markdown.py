"""Unit tests for the source-preserving Markdown exporter."""
import unittest
import xml.etree.ElementTree as ET
from chapter_markdown import to_markdown


class MarkdownTests(unittest.TestCase):
    def render(self, source):
        return to_markdown(ET.fromstring('<article>' + source + '</article>'), 7)

    def test_headings_and_unicode(self):
        text = self.render('<h1>标题</h1><h2>小节</h2><h3 />')
        self.assertIn('# 标题', text)
        self.assertIn('<a id="c7-s1"></a>\n\n## 小节', text)
        self.assertIn('<a id="c7-s2"></a>', text)

    def test_fences_preserve_code(self):
        code = 'print("``` nested fence")\n  indented\n'
        text = self.render('<pre data-language="Python"><code>' + code + '</code></pre>')
        self.assertIn('````python\n' + code + '````', text)

    def test_math(self):
        text = self.render('<p><span class="arithmatex">\\(x_y\\)</span></p><p><span class="arithmatex display-math">\\(a\n\n+b\n\\)</span></p>')
        self.assertIn('$`x_y`$', text)
        self.assertIn('```math\na\n\n+b\n```', text)

    def test_links(self):
        text = self.render('<p><a href="#chapter-2/c2-s1">下一节</a><img src="../../assets/test.png" alt="配图" /></p>')
        self.assertIn('[下一节](<chapter-02.md#c2-s1>)', text)
        self.assertIn('![配图](<../../assets/test.png>)', text)

    def test_profile_link_icons_keep_small_dimensions_and_adjacent_text(self):
        text = self.render('<p>作者 <a href="https://github.com/example"><img src="../../assets/brand/github.svg" alt="GitHub 主页" width="20" height="20" /> 主页</a> 后文</p>')
        self.assertIn('[<img src="../../assets/brand/github.svg" alt="GitHub 主页" width="20" height="20"> 主页](<https://github.com/example>) 后文', text)

    def test_emphasis_around_block_math(self):
        text = self.render('<p><em>前<span class="arithmatex display-math">\\(x\n\\)</span>后</em></p>')
        self.assertIn('<em>前</em>\n\n```math\nx\n```\n\n<em>后</em>', text)

    def test_adjacent_inline_code(self):
        self.assertIn('`Q`<!-- -->`wen3`', self.render('<p><code>Q</code><code>wen3</code></p>'))

    def test_table_structure(self):
        text = self.render('<table><tbody><tr><td><p>表格</p><img src="../../assets/test.png" /></td></tr></tbody></table>')
        self.assertIn('<table><tbody><tr><td><p>表格</p><img', text)
        self.assertNotIn('<th>', text)

    def test_prose_markdown_characters(self):
        text = self.render('<p>1. a_b * [literal] $5</p>')
        self.assertIn('1\\. a&#95;b \\* \\[literal\\] \\$5', text)

    def test_urls_and_mentions(self):
        self.assertIn('https://example.com/get_started', self.render('<p>https://example.com/get_started</p>'))
        self.assertIn('<span>@</span>witcheer', self.render('<p>@witcheer</p>'))

    def test_indented_prose(self):
        self.assertIn('&#32;   正文', self.render('<p>    正文</p>'))


if __name__ == '__main__':
    unittest.main()
