import sys
from opencc import OpenCC

def convert_text(input_file, output_file, conversion):
    cc = OpenCC(conversion)
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # 提取文字部分
            text = line.split('\t')[0]
            # 合并回句子
            text = ''.join(text.split(' '))
            # 转换文本
            converted_text = cc.convert(text)
            outfile.write(converted_text + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input_file output_file conversion")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    conversion = sys.argv[3]  # 's2t' 或 't2s'

    convert_text(input_file, output_file, conversion)

