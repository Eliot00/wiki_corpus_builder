处理中文维基百科，用于训练隐马尔可夫模型。

## 使用说明

GitHub action会自动构建语料文件，可以直接在仓库的release页面下载。如果需要本地手动构建，可以遵循以下步骤：

1. 下载wiki dump文件：`curl -O https://dumps.wikimedia.org/zhwiki/latest/zhwiki-latest-pages-articles.xml.bz2`
2. python安装依赖：`pip install -r requirements.txt`
3. 从原始文件中提取有效信息：`python extract.py`
4. 格式化语料文件：`python format.py`，最终得到格式化的`corpus.tsv`

## 语料文件格式说明

语料文件使用`tsv`格式，其中第一列是句子，第二列是对应的拼音：

```tsv
西 元 前 三 世 紀 的 古 希 臘 數 學 家	xi yuan qian san shi ji de gu xi la shu xue jia
```

句子中每个字及对应的拼音用空格隔开。
