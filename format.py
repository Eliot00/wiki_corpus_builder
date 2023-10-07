import csv
import re
import pypinyin
from tqdm import tqdm
import itertools

digit_pattern = re.compile(r'(?<=[\u4e00-\u9fff])\d+\.?\d*|\d*\.?\d+(?=[\u4e00-\u9fff%])')
percent_pattern = re.compile(r'(?<=[\u4e00-\u9fff])\d+\.?\d*%')

def convert_digit_to_chinese(sentence: str) -> str:
    # 年份需要特殊转换
    sentence = year_special_convert(sentence)

    # 处理百分数
    percent_matches = percent_pattern.findall(sentence)
    for match in percent_matches:
        num = float(match[:-1])
        try:
            cn_num = num2chinese(num, simp=False, o=True, twoalt=True)
            sentence = sentence.replace(match, '百分之' + cn_num)
        except Exception:
            print(f"match: {match} sentence: {sentence}")

    matches = digit_pattern.findall(sentence)
    for match in matches:
        try:
            cn_num = num2chinese(match, simp=False, o=True, twoalt=True)
            sentence = sentence.replace(match, cn_num)
        except Exception:
            print(f"match: {match} sentence: {sentence}")
    return sentence

year_digit_map = {
    '0': '〇',
    '1': '一',
    '2': '二',
    '3': '三',
    '4': '四',
    '5': '五',
    '6': '六',
    '7': '七',
    '8': '八',
    '9': '九',
    '０': '〇',
    '１': '一',
    '２': '二',
    '３': '三',
    '４': '四',
    '５': '五',
    '６': '六',
    '７': '七',
    '８': '八',
    '９': '九',
}
year_patter = re.compile(r'\d+年')

def year_special_convert(sentence: str) -> str:
    matches = year_patter.findall(sentence)
    for match in matches:
        year = match[:-1]  # 去掉年字
        cn_year = ''.join(year_digit_map[digit] for digit in year)
        sentence = sentence.replace(match, cn_year + '年')
    return sentence

# https://gist.github.com/gumblex/0d65cad2ba607fd14de7
def num2chinese(num, big=False, simp=True, o=False, twoalt=False):
    """
    Converts numbers to Chinese representations.
    `big`   : use financial characters.
    `simp`  : use simplified characters instead of traditional characters.
    `o`     : use 〇 for zero.
    `twoalt`: use 两/兩 for two when appropriate.
    Note that `o` and `twoalt` is ignored when `big` is used, 
    and `twoalt` is ignored when `o` is used for formal representations.
    """
    # check num first
    nd = str(num)
    if abs(float(nd)) >= 1e48:
        raise ValueError('number out of range')
    elif 'e' in nd:
        raise ValueError('scientific notation is not supported')
    c_symbol = '正负点' if simp else '正負點'
    if o:  # formal
        twoalt = False
    if big:
        c_basic = '零壹贰叁肆伍陆柒捌玖' if simp else '零壹貳參肆伍陸柒捌玖'
        c_unit1 = '拾佰仟'
        c_twoalt = '贰' if simp else '貳'
    else:
        c_basic = '〇一二三四五六七八九' if o else '零一二三四五六七八九'
        c_unit1 = '十百千'
        if twoalt:
            c_twoalt = '两' if simp else '兩'
        else:
            c_twoalt = '二'
    c_unit2 = '万亿兆京垓秭穰沟涧正载' if simp else '萬億兆京垓秭穰溝澗正載'
    revuniq = lambda l: ''.join(k for k, g in itertools.groupby(reversed(l)))
    nd = str(num)
    result = []
    if nd[0] == '+':
        result.append(c_symbol[0])
    elif nd[0] == '-':
        result.append(c_symbol[1])
    if '.' in nd:
        integer, remainder = nd.lstrip('+-').split('.')
    else:
        integer, remainder = nd.lstrip('+-'), None
    if integer and int(integer):
        splitted = [integer[max(i - 4, 0):i]
                    for i in range(len(integer), 0, -4)]
        intresult = []
        for nu, unit in enumerate(splitted):
            # special cases
            if int(unit) == 0:  # 0000
                intresult.append(c_basic[0])
                continue
            elif nu > 0 and int(unit) == 2:  # 0002
                intresult.append(c_twoalt + c_unit2[nu - 1])
                continue
            ulist = []
            unit = unit.zfill(4)
            for nc, ch in enumerate(reversed(unit)):
                if ch == '0':
                    if ulist:  # ???0
                        ulist.append(c_basic[0])
                elif nc == 0:
                    ulist.append(c_basic[int(ch)])
                elif nc == 1 and ch == '1' and unit[1] == '0':
                    # special case for tens
                    # edit the 'elif' if you don't like
                    # 十四, 三千零十四, 三千三百一十四
                    ulist.append(c_unit1[0])
                elif nc > 1 and ch == '2':
                    ulist.append(c_twoalt + c_unit1[nc - 1])
                else:
                    ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
            ustr = revuniq(ulist)
            if nu == 0:
                intresult.append(ustr)
            else:
                intresult.append(ustr + c_unit2[nu - 1])
        result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    if remainder:
        result.append(c_symbol[2])
        result.append(''.join(c_basic[int(ch)] for ch in remainder))
    return ''.join(result)

def get_words_and_pinyins(sentence: str) -> tuple[str, str]:
    # 过滤掉非汉字
    filtered_words = []
    for word in sentence:
        if '\u4e00' <= word <= '\u9fff':
            filtered_words.append(word)

    # 使用pypinyin将句子转换为拼音
    pinyin_list = pypinyin.lazy_pinyin(''.join(filtered_words))

    return (' '.join(filtered_words), ' '.join(pinyin_list))

if __name__ == '__main__':
    with open('wiki.txt', 'r', encoding='utf-8') as wiki:
        with open('corpus.tsv', 'w', encoding='utf-8', newline='') as formatted:
            writer = csv.writer(formatted, delimiter='\t')
            for line in tqdm(wiki):
                sentences: list[str] = re.findall('[^，。！？\n]+[，。！？\n]', line)
                for sentence in sentences:
                    sentence = sentence.strip()
                    # 过滤掉不包含汉字或长度不够的句子
                    if len(sentence) > 1 and re.search('[\u4e00-\u9fff]', sentence):
                        sentence = convert_digit_to_chinese(sentence)
                        writer.writerow(get_words_and_pinyins(sentence))
