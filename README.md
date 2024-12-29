# Python-Web-
2024/12/29



学习了如何使用streamlit快速部署前后端，并且了解了大量的python的数据可视化库，这这个程序中我学习的是pyechart库，里面包含了很多基础图表与扩展图表，我学习了以下七个简单图表的api使用。而且在词汇过滤器中也了解到很多的过滤方法，使用了一些列自己修改的过滤器后还是存在一些特殊符号与单字符和无效字符无法被过滤的情况，所以我大量查阅了ai的写法：

def word_frequency(text):

"""优化的分词和词频统计"""

# 过滤规则

filtered_words = []

for word in jieba.cut(text):

if (len(word) > 1 and  # 过滤单字

word not in STOP_WORDS and  # 过滤停用词

not word.isdigit() and  # 过滤纯数字

not bool(re.search(r'[^\u4e00-\u9fff]', word))  # 只保留中文词

):

filtered_words.append(word)

return Counter(filtered_words)



# 定义停用词列表

STOP_WORDS = set([

'的', '了', '在', '是', '我', '有', '和', '就',

'不', '人', '都', '一', '一个', '上', '也', '很',

'到', '说', '要', '去', '你', '会', '着', '没有',

'看', '好', '自己', '这', '年', '做', '来', '后'

])

但是经过修改后存在每个图表页面所表示的总字符数量有差异，我无法理解与解决，ai告诉我将第一次得到的数据缓存session中即可解决差异的问题















