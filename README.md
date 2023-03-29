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
歐幾里得,西元前,三,世紀,的,古希臘,數學家,現在,被,認為,是,幾何,之,父,此畫,為,拉斐爾,的,作品,雅典,學院    ou ji 
```

句子中每个词用半角逗号分割，每个词对应的拼音也用半角逗号分割，词中的每个字对应的拼音用空格隔开。词是通过jieba分词得到的，如果一个句子中只有一个词，则将该词的第一个字和后续字分开，便于后续计算初始概率和转移概率。
