import re

class Html_remove():
    def __init__(self):
        pass

    def filterHtmlTag(self, htmlStr):
        '''''
        过滤html中的标签
        :param htmlStr:html字符串 或是网页源码
        '''
        self.htmlStr = htmlStr
        # 先过滤CDATA
        re_cdata = re.compile('//<!CDATA\[[ >]∗ //\] > ', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)
        re_metal = re.compile('<\s*meta[^>]*>[^<]*<\s*/\s*meta\s*>', re.I)
        # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
        # style
        re_br = re.compile('</?br\s*?/?>')
        re_span_font = re.compile('</?(xml|meta|font|center|col|thead|colgroup|tbody|input|strong|em)+[^>]*>')
        re_b = re.compile('</?b\s*?/?>')
        re_num = re.compile('[一二三四五六七八九十]+、')

        re_nature = re.compile('(style|alt|class|align)=[\"](.*?)[\"]')
        # HTML标签
        re_comment = re.compile('<!--[\w\W]*?-->')
        re_space = re.compile('(&nbsp;|&nbsp)')
        # HTML注释
        s = re_cdata.sub('', htmlStr)
        # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_metal.sub('', s)
        s = re_style.sub('', s)
        s = re_nature.sub('', s)
        # 去掉style
        s = re_br.sub('\n', s)
        s = re_span_font.sub('', s)
        s = re_b.sub('', s)
        s = re_comment.sub('', s)
        s = re_space.sub('',s)
        s = re_num.sub('', s)
        s = s.replace(':', '：')
        return s