import csv
import re
import pypinyin
from tqdm import tqdm
import jieba
from pycnnum import num2cn

digit_pattern = re.compile(r'(?<=[\u4e00-\u9fff])\d+\.?\d*|\d*\.?\d+(?=[\u4e00-\u9fff%])')
percent_pattern = re.compile(r'(?<=[\u4e00-\u9fff])\d+\.?\d*%')

def convert_digit_to_chinese(sentence: str) -> str:
    # 年份需要特殊转换
    sentence = year_special_convert(sentence)

    # 处理百分数
    percent_matches = percent_pattern.findall(sentence)
    for match in percent_matches:
        num = float(match[:-1])
        cn_num = num2cn(str(num), traditional=True, alt_two=True, alt_zero=True)
        sentence = sentence.replace(match, '百分之' + cn_num)

    matches = digit_pattern.findall(sentence)
    for match in matches:
        if '.' in match:  # 匹配到小数
            cn_num = num2cn(match, traditional=True, alt_two=True, alt_zero=True)
            sentence = sentence.replace(match, cn_num)
        # pycnnum遇到1会出现IndexError，临时处理一下
        elif match == '1':
            sentence = sentence.replace(match, '一')
        else:  # 匹配到整数
            cn_num = num2cn(match, traditional=True, alt_two=True, alt_zero=True)
            sentence = sentence.replace(match, cn_num)
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

def get_words_and_pinyins(sentence: str) -> tuple[str, str]:
    words = jieba.cut(sentence, cut_all=False)

    # 过滤掉不包含汉字的词语
    filtered_words = []
    for word in words:
        for char in word:
            if '\u4e00' <= char <= '\u9fff': # 如果词语包含汉字
                filtered_words.append(word)
                break

    # 如果一行只有一个词，拆出第一个字，方便HMM计算初始概率
    if len(filtered_words) == 1:
        word = filtered_words[0]
        pinyin = pypinyin.lazy_pinyin(word)
        pinyin_list = [pinyin[0], ' '.join(pinyin[1:])]
        words = [word[0], word[1:]]
        return (','.join(words), ','.join(pinyin_list))

    # 使用pypinyin将词语转换为拼音
    pinyin_list = []
    for word in filtered_words:
        pinyin_list.append(' '.join(pypinyin.lazy_pinyin(word)))

    return (','.join(filtered_words), ','.join(pinyin_list))

if __name__ == '__main__':
    jieba.set_dictionary('dict.txt.big')
    with open('wiki.txt', 'r', encoding='utf-8') as wiki:
        with open('corpus.tsv', 'w', encoding='utf-8', newline='') as formatted:
            writer = csv.writer(formatted, delimiter='\t')
            for line in tqdm(wiki):
                sentences: list[str] = re.findall('[^。！？\n]+[。！？\n]', line)
                for sentence in sentences:
                    sentence = sentence.strip()
                    # 过滤掉不包含汉字或长度不够的句子
                    if len(sentence) > 1 and re.search('[\u4e00-\u9fff]', sentence):
                        sentence = convert_digit_to_chinese(sentence)
                        writer.writerow(get_words_and_pinyins(sentence))
