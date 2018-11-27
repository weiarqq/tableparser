from bs4 import BeautifulSoup
import bs4
import re
from htmlself.titlepredict import PredictTitle
from htmlself.removehtml import Html_remove
import logging



class HtmlParser:

    def __init__(self):
        self.predict_title = PredictTitle()
        self.html_remove = Html_remove()


    def init(self,pags):
        self.predict_title.init(pags)
        logging.info('加载标题关键字！！！！！！')

    def parser_html(self, html):
        html = self.html_remove.filterHtmlTag(html)
        soup = BeautifulSoup(html, 'lxml')
        table_list = []
        content = self.parser_label(soup.body, table_list)
        content = self.remove_specifechar(content)
        # lines, text = self.handle_content(content)
        #bul_name = self.handle_bulname(bul_name)
        return content, table_list

    def parser_label(self, label, table_list):
        content = ''
        if label is None:
            return content
        for children in label.children:
            if children.name == 'table':
                content = '%s%s%s' % (content, self.parser_table(children, table_list), '\n')
            elif children.name == 'div' or children.name == 'form':
                content = '%s%s%s' % (content, self.parser_label(children, table_list), '\n')
            elif children.name == 'p':
                content = '%s%s%s' % (content, self.parser_label(children, table_list), '\n')
            elif isinstance(children, bs4.element.NavigableString):
                if children.string is not None:
                    if len(children.string.strip()) > 10:
                        content = '%s%s%s' % (content, children.string.strip(), '\n')
                    else:
                        content = '%s%s' % (content, children.string.strip())
            else:
                content = '%s%s' % (content, self.parser_label(children, table_list))
        return content

    def parser_table(self, table, table_list):
        content = ''
        childrens = table.children
        list_tr = []
        for children in childrens:
            if children.name == 'tbody':
                content = '%s%s%s' % (content, self.parser_table(children, table_list), '\n')
            elif children.name == 'tr':
                list_tr.append(children)
            elif isinstance(children, bs4.element.NavigableString):
                if children.string is not None:
                    content = '%s%s' % (content, children.string.strip())
        # 存放表格内容
        table_text = [[]]*len(list_tr)
        # 存放表格每行长度
        table_length = [0]*len(list_tr)
        # 存放表格每行实际长度
        table_real_length = [0]*len(list_tr)
        # 统计需要合并的上下列
        col_indexs = [[]]*len(list_tr)
        list_row = []
        if len(list_tr) > 0:
            for index, tr in enumerate(list_tr):
                tr_children = []
                for td in tr.children:
                    if isinstance(td, bs4.element.Tag):
                        tr_children.append(td)
                list_row.append(self.get_tr_length(tr_children, index, table_length))
                table_real_length[index] = len(tr_children)
                col_indexs[index] = [0]*table_length[index]
                table_text[index] = ['']*table_length[index]

            for x, row in enumerate(list_row):
                tr_ele = row['element']
                for z, td in enumerate(tr_ele):
                    if row['isrow']:
                        for i in range(1, row['rowarray'][z]):
                            if (x+i) < len(table_text):
                                for y in range(z, table_length[x+i]):
                                    if table_text[x+i][y] == '':
                                       if td.get_text(strip=True) is not None:
                                            table_text[x+i][y] = td.get_text(strip=True)
                                            col_indexs[x+i][y] = row['colarray'][z]
                                       break
                    for y in range(z, table_length[x]):
                        if table_text[x][y] == '':
                            if isinstance(td, bs4.element.NavigableString):
                                if td.get_text(strip=True) is not None:
                                    table_text[x][y] = td.get_text(strip=True)
                            else:
                                table_text[x][y] = self.table_in_td(td, table_list)
                                break
                b = 0
                for p in range(len(col_indexs[x])):
                    if col_indexs[x][p] == 0 and b < len(row['colarray']):
                        col_indexs[x][p] = row['colarray'][b]
                        b = b+1
                row['text'] = table_text[x]
                row['istitle'] = self.predict_title.is_title(table_text[x])
                row['colarry'] = col_indexs[x]

        for m in range(len(list_row)-1):
            new_text = [None]*len(list_row[m+1])
            row_one = list_row[m]
            row_two = list_row[m+1]
            if row['istitle'] != 0 and len(list_row[m]['colarray']) < len(list_row[m+1]['colarray']) and len(list_row[m]['colarray'])!=1:
                for q in range(len(list_row[m]['colarray'])):
                    if row_one['colarray'][q] > row_two['colarray'][q]:
                        num = 0
                        for h in range(len(row_two['colarray'])):
                            num += row_two['colarray'][h]
                            if num == row_one['colarray'][q]:
                                for o in range(q, h+1):
                                    if len(new_text) > o:
                                        new_text[o] = row_one['text'][q]
                    if row_one['colarray'][q] == row_two['colarray'][q]:
                        for e in range(len(new_text)):
                            if new_text[e] == None:
                                new_text[e] = row_one['text'][q]
                row_one['text'] = new_text
        new_table_text = [[]]*len(list_row)
        new_table_length = ['']*len(list_row)

        for w, new_row in enumerate(list_row):
            if new_row['text'] is None:
                new_table_text[w] = []
            else:
                row_l = []
                for row in new_row['text']:
                    if row is None:
                        row_l.append('')
                    elif len(row.split()) <= 0:
                        row_l.append('')
                    else:
                        row_l.append(self.remove_specifechar(row))
                new_table_text[w] = row_l
            new_table_length[w] = len(new_row['text'])
        k = 0
        while len(list_row) > 0:
            if new_table_length[k] == 1:
                content = '%s%s%s' % (content, new_table_text[k][0], '\n')
            else:
                nature = self.has_key(k, new_table_text, new_table_length)
                table_list = self.adjust_table(nature, new_table_text, new_table_length, table_list)
                content = '%s%s' % (content, self.append_text(nature, new_table_text, new_table_length))
                k = nature['endline']
            k = k+1
            if k == len(list_row):
                return content
        return content

    def get_tr_length(self, tr_children, x, table_length):
        row_list = []
        col_list = []
        elements = []
        for td in tr_children:
            if td.name == 'td' or td.name == 'th':
                elements.append(td)
                attrs_dict = td.attrs
                if 'colspan' in attrs_dict.keys() and len(attrs_dict['colspan']) > 0:
                    try:
                        col_list.append(int(attrs_dict['colspan'][0]))
                    except Exception:
                        col_list.append(1)
                else:
                    col_list.append(1)
                if 'rowspan' in attrs_dict.keys() and len(attrs_dict['rowspan']) > 0:
                    try:
                        row_list.append(int(attrs_dict['rowspan'][0]))
                    except Exception:
                        row_list.append(1)
                else:
                    row_list.append(1)
        wa = False
        if len(row_list) > 1:
            row_one = row_list[0]
            for row_case in row_list[1:]:
                if row_case != row_one:
                    wa = True
        if wa:
            for case in row_list:
                for i in range(1, case):
                    if (x+i) < len(table_length):
                        table_length[x+i] += 1
        element_row = {}
        element_row['element'] = elements
        element_row['isrow'] = wa
        element_row['rowarray'] = row_list
        element_row['colarray'] = col_list

        table_length[x] += len(elements)
        return element_row

    def table_in_td(self, td, table_list):
        content = ''
        for child in td.children:
            if child.name == 'table':
                content = '%s%s%s' % (content, self.parser_table(child, table_list), '\n')
            elif child.name == 'blockquote':
                content = '%s%s%s' % (content, self.table_in_td(child, table_list), '\n')
            elif child.name == 'div':
                content = '%s%s%s' % (content, self.parser_label(child, table_list), '\n')
            elif child.name == 'p':
                content = '%s%s%s' % (content, self.parser_label(child, table_list), '\n')
            elif isinstance(child, bs4.element.NavigableString):
                if child.string is not None:
                    if len(child.string.strip()) > 10:
                        content = '%s%s%s' % (content, child.string.strip(), '\n')
                    else:
                        content = '%s%s' % (content, child.string.strip())
            else:
                content = '%s%s' % (content, self.parser_label(child, table_list))

        return content

    def has_key(self, m, new_table_text, new_table_length):
        point = {}
        point['startline'] = m
        list_row = []
        list_col = []
        for n in range(new_table_length[m]):
            if new_table_text[m][n] is not None:
                list_row.append(new_table_text[m][n])
        bol_row = self.predict_title.is_title(list_row)
        #if bol_row == 1 or bol_row == 2:
        while m+1 < len(new_table_text):
            if len(new_table_text[m+1]) > 0:
                if new_table_length[m] == new_table_length[m+1]:
                    list_col.append(new_table_text[m+1][0])
                    m += 1
                else:
                    break
            else:
                break
        point['endline'] = m

        if bol_row == 2:
            point["status"] = 1  #表头为行
        if bol_row == 1:
            point["status"] = 11  #表头为行 含包号
        if bol_row == 0:
            point["status"] = 2  #无表头
        return point

    def adjust_table(self, point, table_text, table_length, table_list):
        n = point['startline']
        if point['startline'] == point['endline']:
            row_list = []
            for k in range(table_length[n]):
                if k % 2 == 0 and k+1 < table_length[n]:
                    group_tup = (table_text[n][k].replace('\n', ''), table_text[n][k+1].replace('\n', ''))
                    if group_tup not in row_list:
                        row_list.append(group_tup)
            if row_list not in table_list:
                table_list.append(row_list)

        # 表头为行
        if point['status'] == 1:
            for v in range(n+1, point['endline']+1):
                row_list = []
                for k in range(table_length[n]):
                    group_tup = (table_text[n][k].replace('\n', ''), table_text[v][k].replace('\n', ''))
                    if group_tup not in row_list:
                        row_list.append(group_tup)
                if row_list not in table_list:
                    table_list.append(row_list)
        # 表头为行  且分包
        if point['status'] == 11:
            row_list = []
            for l in range(n+1, point['endline']+1):
                for c in range(table_length[n]):
                    group_tup = (table_text[n][c].replace('\n', ''), table_text[l][c].replace('\n', ''))
                    if group_tup not in row_list:
                        row_list.append(group_tup)
            if row_list not in table_list:
                table_list.append(row_list)
        # 表头为列
        if point['status'] == 2:
            row_list = []
            for l in range(n, point['endline'] + 1):
                for c in range(1, table_length[n]):
                    group_tup = (table_text[l][0].replace('\n', ''), table_text[l][c].replace('\n', ''))
                    if group_tup not in row_list:
                        row_list.append(group_tup)
            if row_list not in table_list:
                table_list.append(row_list)
        #交叉表头
        if point['status'] == 3:
            row_list = []
            for l in range(n+1, point['endline']+1):
                for c in range(table_length[n]):
                    group_tup = (table_text[n][c].replace('\n', ''), table_text[l][c].replace('\n', ''))
                    if group_tup not in row_list:
                        row_list.append(group_tup)
            if row_list not in table_list:
                table_list.append(row_list)
        return table_list
    def append_text(self, point, tabletext, tableLength):
        content = ''
        n = point['startline']
        if point['startline'] == point['endline']:
            for l, text in enumerate(tabletext[n]):
                if text == None:
                    continue
                if text.find('：') != -1:
                    if l % 2 == 0:
                        if text is not None and len(text) > 0:
                            content = '%s%s' % (content, text)
                else:
                    if l % 2 == 0:
                        if text is not None and len(text) > 0:
                            content = '%s%s%s' % (content, text, ':')
                if l % 2 == 1:
                    if text is not None and len(text) > 0:
                        content = '%s%s%s' % (content, text, '\n')
            content = '%s%s' % (content, '\n')
            return content

        if point['status'] == 1:
            start = 0
            if tabletext[n][0] is not None and (tabletext[n][0].strip()) == '排名':
                start = 1
            for k in range(start, tableLength[n]):
                title_arr = [None] * tableLength[n]
                if tabletext[n][k] is not None:
                    if tabletext[n][k].find('：') != -1:
                        title_arr[k] = tabletext[n][k].strip()
                    else:
                        if tabletext[n][k] is not None and len(tabletext[n][k]) > 0:
                            title_arr[k] = '%s%s' % (tabletext[n][k].strip(), '：')
                        else:
                            title_arr[k] = ''
                for j in range(n + 1, point['endline'] + 1):
                    if k < len(tabletext[j]):
                        if j != point['endline'] and tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                            if tabletext[j][k].find('：') == -1:
                                content = '%s%s%s' % (content, title_arr[k], tabletext[j][k])
                            else:
                                content = '%s%s%s%s' % (content, title_arr[k], tabletext[j][k], '：')
                        if j == point['endline'] and tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                            content = '%s%s%s%s' % (content, title_arr[k], tabletext[j][k], '\n')

        if point['status'] == 11:
            for j in range(n + 1, point['endline']+1):
                for k in range(len(tabletext[j])):
                    if k < len(tabletext[n]) and tabletext[n][k] is not None:
                        if tabletext[n][k].find("：") != -1:
                            content = '%s%s' % (content, tabletext[n][k].strip())
                        else:
                            if tabletext[n][k] is not None and len(tabletext[n][k]) > 0:
                                content = '%s%s%s' % (content, tabletext[n][k].strip(), '：')
                        if j != point['endline'] and tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                            if tabletext[j][k].find("：") == -1:
                                content = '%s%s%s' % (content, tabletext[j][k], "：")
                            else:
                                content = '%s%s' % (content, tabletext[j][k])
                        if j == point['endline'] and tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                            content = '%s%s%s' % (content, tabletext[j][k], '\n')
        if point['status'] == 2:
            for j in range(n, point["endline"]+1):
                if tabletext[j][0] is not None:
                    if tabletext[j][0].find("：") != -1:
                        content = '%s%s' % (content, tabletext[j][0].strip())
                    else:
                        if len(tabletext[j][0]) > 0:
                            content = '%s%s%s' % (content, tabletext[j][0].strip(), ":")

                for k in range(1, tableLength[j]):
                    if (tableLength[j] - 1) != k:
                        if tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                            if tabletext[j][0].find("：") == -1:
                                content = '%s%s%s' % (content, tabletext[j][k], "：")
                            else:
                                content = '%s%s' % (content, tabletext[j][k])
                    else:
                        if tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                            content = '%s%s%s' % (content, tabletext[j][k], '\n')
        if point['status'] == 3:
            for k in range(1, tableLength[n]):
                for j in range(n + 1, point['endline']+1):
                    if tabletext[n][k] is not None:
                        if tabletext[n][k].find("：") != -1:
                            content = '%s%s' % (content, tabletext[n][k].strip())
                        else:
                            if len(tabletext[n][k]) > 0:
                                content = '%s%s%s' % (content, tabletext[n][k].strip(), "：")
                    if k < len(tabletext[j]):
                        content += tabletext[j][0]
                        if point['endline'] != j:
                            if tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                                if tabletext[j][k].find("：") == -1:
                                    content = '%s%s%s' % (content, tabletext[j][k], "：")
                                else:
                                    content = '%s%s' % (content, tabletext[j][k])
                        else:
                            if tabletext[j][k] is not None and len(tabletext[j][k]) > 0:
                                content = '%s%s%s' % (content, tabletext[j][k], '\n')
        return content


    def remove_specifechar(self, content):
        content = content.replace(' ', '').replace('   ', '').replace('  ', '').replace(' ', '').replace(':', '：').replace('\u3000','')
        lines = []
        for line in content.split('\n'):
            if len(line) > 0:
                lines.append(line)
        return '\n'.join(lines)



if __name__ == '__main__':
    print(1)
    s = 'aaabaabacabaa'
    a = [i.start() for i in re.finditer('a', s)]
    print(a)