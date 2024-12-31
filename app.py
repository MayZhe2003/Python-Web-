import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Funnel, Scatter, Radar
import pyecharts.options as opts
import string
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import plotly.express as px
import plotly.graph_objects as go
import platform
import seaborn as sns
sns.set_theme(style="whitegrid")  # 设置默认主题样式
matplotlib.use('Agg')  # 设置后端
import io




font_family = ['Arial Unicode MS', 'PingFang SC', 'STHeiti']

# 设置 Matplotlib 字体
matplotlib.rcParams['font.sans-serif'] = font_family
matplotlib.rcParams['axes.unicode_minus'] = False

# 创建字体对象，用于确保中文显示
try:
    from matplotlib.font_manager import FontProperties
    font = FontProperties(family=font_family[0])
except:
    # 如果上述字体都不可用，尝试使用系统默认字体
    font = FontProperties()

# 定义停用词列表
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就',
    '不', '人', '都', '一', '一个', '上', '也', '很',
    '到', '说', '要', '去', '你', '会', '着', '没有',
    '看', '好', '自己', '这', '年', '做', '来', '后'
])

# 设置页面配置
st.set_page_config(
    page_title="智能文本分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 全局样式 */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 标题样式 */
    .custom-title {
        background: linear-gradient(45deg, #FF512F, #DD2476);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 800;
        text-align: center;
        padding: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 卡片容器 */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 2rem;
        transition: transform 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #FF512F 0%, #DD2476 100%);
        padding: 2rem;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(45deg, #FF512F, #DD2476);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 50px;
        border: 2px solid #DD2476;

        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* 数据指标样式 */
    .metric-card {
        background: linear-gradient(135deg, #FF512F, #DD2476);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.9;
    }
    
    /* Radio按钮组样式 */
    .stRadio>div {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Select下拉框样式 */
    .stSelectbox>div>div {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        color: white;
    }
    
    /* 数据表格样式 */
    .stDataFrame {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* 进度条样式 */
    .stProgress>div>div>div {
        background: linear-gradient(45deg, #FF512F, #DD2476);
        border-radius: 10px;
    }
    
    /* 动画效果 */
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .animate-gradient {
        background-size: 200% 200%;
        animation: gradient 15s ease infinite;
    }
    
    /* 图表容器样式 */
    .chart-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    /* 页脚样式 */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(45deg, #FF512F, #DD2476);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        margin-top: 3rem;
    }
    
    /* Streamlit 侧边栏主容器 */
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
    }
    
    /* Streamlit 侧边栏内容 */
    section[data-testid="stSidebar"] .element-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Streamlit Radio 按钮组 */
    section[data-testid="stSidebar"] .st-emotion-cache-1629p8f {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Streamlit Radio 按钮标签 */
    section[data-testid="stSidebar"] .st-emotion-cache-1629p8f label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Streamlit Radio 按钮选项 */
    section[data-testid="stSidebar"] .st-emotion-cache-1629p8f .st-emotion-cache-ue6h4q {
        color: white !important;
    }
    
    /* Streamlit Select 下拉框 */
    section[data-testid="stSidebar"] .st-emotion-cache-12w0qpk {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Streamlit Select 下拉框标签 */
    section[data-testid="stSidebar"] .st-emotion-cache-12w0qpk label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Streamlit Select 下拉框内容 */
    section[data-testid="stSidebar"] .st-emotion-cache-12w0qpk > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }
    
    /* Streamlit 标题文本 */
    section[data-testid="stSidebar"] .st-emotion-cache-10trblm {
        color: white !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Streamlit 图片容器 */
    section[data-testid="stSidebar"] .st-emotion-cache-1v0mbdj {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    /* Streamlit 图片 */
    section[data-testid="stSidebar"] img {
        border-radius: 50%;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Streamlit 分割线 */
    section[data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            rgba(255,255,255,0), 
            rgba(255,255,255,0.3), 
            rgba(255,255,255,0));
    }
    
    /* Streamlit 滚动条 */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 5px;
        background: transparent;
    }
    
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
    }
    
    /* 悬浮效果 */
    section[data-testid="stSidebar"] .element-container:hover {
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="custom-title animate-gradient">✨ 智能文本分析平台</h1>', unsafe_allow_html=True)

# 侧边栏设计
with st.sidebar:
    # 标题和图标
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("分析控制台")
    
    # 可视化库选择
    viz_library = st.radio(
        "选择可视化库",
        ["📊 Pyecharts", "📈 Matplotlib", "🎨 Plotly", "🎨 Seaborn"],
        captions=["交互式图表库", "静态图表库", "现代交互图表库", "统计可视化库"]
    )
    
    # 图表类型选择
    if viz_library == "📊 Pyecharts":
        graph_type = st.selectbox(
            "选择图表类型",
            ["🌈 炫彩词云", "📊 动态柱图", "🎨 艺术饼图", 
             "📈 智能折线", "⚡ 炫酷漏斗", "✨ 星空散点",
             "🎯 魔法雷达"]
        )
    elif viz_library == "📈 Matplotlib":
        graph_type = st.selectbox(
            "选择可视化类型",
            ["📊 柱状图", "🥧 饼图", "📈 折线图", 
             "🎯 散点图", "📊 水平柱状图"]
        )
    elif viz_library == "🎨 Plotly":
        graph_type = st.selectbox(
            "选择可视化类型",
            ["📊 交互柱状图", "🥧 动态饼图", "📈 平滑折线图", 
             "🎯 气泡散点图", "📊 瀑布图", "🌈 树形图"]
        )
    else:  # Seaborn
        graph_type = st.selectbox(
            "选择可视化类型",
            ["📊 增强柱图", "🎯 高级散点", "📈 回归曲线", 
             "🌈 小提琴图", "📊 核密度图"]
        )
    
    st.markdown("""
    <div style='background: rgba(255,255,255,0.1); 
                padding: 1.5rem; 
                border-radius: 15px; 
                margin-top: 2rem;'>
        <h3 style='color: white; text-align: center;'>🎯 使用指南</h3>
        <ol style='color: white; margin-top: 1rem;'>
            <li>输入任意网址</li>
            <li>选择喜欢的图表</li>
            <li>等待智能分析</li>
            <li>导出分析结果</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# 主要内容区
st.markdown("""
<div class="custom-card">
    <h3>🔍 输入网址开始分析</h3>
</div>
""", unsafe_allow_html=True)

url = st.text_input(
    "",
    placeholder="请输入完整网址 (例如: https://example.com)",
    help="需要包含 http:// 或 https://"
)

@st.cache_data
def get_text_from_url(url):
    """获取网页文本内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding  # 自动检测编码
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)  # 规范化空白字符
        return text.strip()
    except Exception as e:
        st.error(f"获取网页内容出错: {str(e)}")
        return ""

@st.cache_data
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

def create_chart_options():
    """创建通用图表配置"""
    return opts.InitOpts(
        width="100%",
        height="600px",
        theme="light",
        animation_opts=opts.AnimationOpts(animation=True)
    )

def draw_wordcloud(word_counts):
    """优化的词云图"""
    wordcloud = WordCloud(init_opts=create_chart_options())
    wordcloud.add(
        series_name="",
        data_pair=word_counts.most_common(30),
        word_size_range=[20, 100],
        textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei")
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-词云图"),
        tooltip_opts=opts.TooltipOpts(is_show=True)
    )
    return wordcloud

def draw_bar_chart(word_counts):
    """优化的柱状图"""
    data = word_counts.most_common(20)
    bar = Bar(init_opts=create_chart_options())
    bar.add_xaxis([item[0] for item in data])
    bar.add_yaxis(
        "词频",
        [item[1] for item in data],
        label_opts=opts.LabelOpts(position="top")
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-柱状图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        datazoom_opts=[opts.DataZoomOpts()],
        toolbox_opts=opts.ToolboxOpts()
    )
    return bar

def draw_pie_chart(word_counts):
    """优化的饼图"""
    pie = Pie(init_opts=create_chart_options())
    data = word_counts.most_common(10)  # 只展示前10个词，避免饼图过于复杂
    pie.add(
        series_name="词频",
        data_pair=data,
        radius=["30%", "75%"],
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-饼图"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="left")
    )
    return pie

def draw_line_chart(word_counts):
    """优化的折线图"""
    data = word_counts.most_common(20)
    line = Line(init_opts=create_chart_options())
    line.add_xaxis([item[0] for item in data])
    line.add_yaxis(
        "词频",
        [item[1] for item in data],
        markpoint_opts=opts.MarkPointOpts(data=[
            opts.MarkPointItem(type_="max", name="最大值"),
            opts.MarkPointItem(type_="min", name="最小值"),
        ])
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-折线图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
    )
    return line

def draw_funnel_chart(word_counts):
    """优化的漏斗图"""
    funnel = Funnel(init_opts=create_chart_options())
    data = word_counts.most_common(10)  # 使用前10个词
    funnel.add(
        "词频漏斗",
        data,
        label_opts=opts.LabelOpts(position="inside")
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-漏斗图")
    )
    return funnel

def draw_scatter_chart(word_counts):
    """优化的散点图"""
    scatter = Scatter(init_opts=create_chart_options())
    data = word_counts.most_common(20)
    scatter.add_xaxis([i for i in range(1, len(data) + 1)])
    scatter.add_yaxis(
        "词频",
        [item[1] for item in data],
        tooltip_opts=opts.TooltipOpts(
            formatter=lambda params: f'排名：{params.value[0]}<br/>词语：{data[params.value[0]-1][0]}<br/>频次：{params.value[1]}'
        )
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-散点图"),
        xaxis_opts=opts.AxisOpts(name="排名"),
        yaxis_opts=opts.AxisOpts(name="词频")
    )
    return scatter

def draw_radar_chart(word_counts):
    """优化的雷达图"""
    radar = Radar(init_opts=create_chart_options())
    data = word_counts.most_common(8)  # 使用前8个词，避免过于密集
    max_value = max([count for _, count in data])
    
    schema = [
        opts.RadarIndicatorItem(name=word, max_=max_value)
        for word, _ in data
    ]
    radar.add_schema(schema)
    
    radar.add(
        "词频",
        [[count for _, count in data]],
        areastyle_opts=opts.AreaStyleOpts(opacity=0.3)
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-雷达图")
    )
    return radar

def create_wordcloud(word_counts):
    """创建词云图"""
    wordcloud = WordCloud(init_opts=opts.InitOpts(width="100%", height="600px"))
    wordcloud.add(
        series_name="词频",
        data_pair=word_counts.most_common(30),
        word_size_range=[20, 100]
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-词云图"),
        tooltip_opts=opts.TooltipOpts(is_show=True)
    )
    return wordcloud

def create_bar(word_counts):
    """创建柱状图"""
    bar = Bar(init_opts=opts.InitOpts(width="100%", height="600px"))
    items = word_counts.most_common(20)
    x_data = [item[0] for item in items]
    y_data = [item[1] for item in items]
    bar.add_xaxis(x_data)
    bar.add_yaxis("词频", y_data)
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-柱状图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        datazoom_opts=[opts.DataZoomOpts()]
    )
    return bar

def create_pie(word_counts):
    """创建饼图"""
    pie = Pie(init_opts=opts.InitOpts(width="100%", height="600px"))
    items = word_counts.most_common(10)
    pie.add(
        series_name="词频",
        data_pair=items,
        radius=["30%", "75%"]
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-饼图")
    )
    return pie

def create_line(word_counts):
    """创建折线图"""
    line = Line(init_opts=opts.InitOpts(width="100%", height="600px"))
    items = word_counts.most_common(20)
    x_data = [item[0] for item in items]
    y_data = [item[1] for item in items]
    line.add_xaxis(x_data)
    line.add_yaxis("词频", y_data)
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-折线图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
    )
    return line

def create_funnel(word_counts):
    """创建漏斗图"""
    funnel = Funnel(init_opts=opts.InitOpts(width="100%", height="600px"))
    items = word_counts.most_common(10)
    funnel.add(
        series_name="词频",
        data_pair=items
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-漏斗图")
    )
    return funnel

def create_scatter(word_counts):
    """创建散点图"""
    scatter = Scatter(init_opts=opts.InitOpts(width="100%", height="600px"))
    items = word_counts.most_common(20)
    x_data = [item[0] for item in items]
    y_data = [item[1] for item in items]
    scatter.add_xaxis(x_data)
    scatter.add_yaxis("词频", y_data)
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-散点图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
    )
    return scatter

def create_radar(word_counts):
    """创建雷达图"""
    radar = Radar(init_opts=opts.InitOpts(width="100%", height="600px"))
    items = word_counts.most_common(8)  # 雷达图最好不要太多数据
    c_schema = [
        opts.RadarIndicatorItem(name=item[0], max_=max(dict(items).values()))
        for item in items
    ]
    radar.add_schema(schema=c_schema)
    radar.add(
        series_name="词频",
        data=[[item[1] for item in items]]
    ).set_global_opts(
        title_opts=opts.TitleOpts(title="词频统计-雷达图")
    )
    return radar

# 定义图表函数字典
chart_functions = {
    "炫彩词云": create_wordcloud,
    "动态柱图": create_bar,
    "艺术饼图": create_pie,
    "智能折线": create_line,
    "炫酷漏斗": create_funnel,
    "星空散点": create_scatter,
    "魔法雷达": create_radar
}

# 添加 Matplotlib 图表函数
def plot_matplotlib_bar(word_counts):
    """创建 Matplotlib 柱状图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(15)
    x = [item[0] for item in data]
    y = [item[1] for item in data]
    
    plt.bar(x, y, color='skyblue')
    plt.title('词频统计-柱状图', fontsize=15, fontproperties=font)
    plt.xlabel('词语', fontsize=12, fontproperties=font)
    plt.ylabel('频次', fontsize=12, fontproperties=font)
    plt.xticks(rotation=45, fontproperties=font)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_matplotlib_pie(word_counts):
    """创建 Matplotlib 饼图"""
    plt.figure(figsize=(10, 10))
    data = word_counts.most_common(8)
    labels = [item[0] for item in data]
    sizes = [item[1] for item in data]
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title('词频统计-饼图', fontsize=15, fontproperties=font)
    for text in plt.gca().texts:
        text.set_fontproperties(font)
    plt.axis('equal')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_matplotlib_line(word_counts):
    """创建 Matplotlib 折线图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(15)
    x = [item[0] for item in data]
    y = [item[1] for item in data]
    
    plt.plot(x, y, marker='o')
    plt.title('词频统计-折线图', fontsize=15, fontproperties=font)
    plt.xlabel('词语', fontsize=12, fontproperties=font)
    plt.ylabel('频次', fontsize=12, fontproperties=font)
    plt.xticks(rotation=45, fontproperties=font)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_matplotlib_scatter(word_counts):
    """创建 Matplotlib 散点图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(15)
    x = range(len(data))
    y = [item[1] for item in data]
    labels = [item[0] for item in data]
    
    plt.scatter(x, y, s=100)
    plt.title('词频统计-散点图', fontsize=15, fontproperties=font)
    plt.xlabel('词语排名', fontsize=12, fontproperties=font)
    plt.ylabel('频次', fontsize=12, fontproperties=font)
    
    for i, label in enumerate(labels):
        plt.annotate(label, (x[i], y[i]), xytext=(5, 5), 
                    textcoords='offset points', fontproperties=font)
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_matplotlib_barh(word_counts):
    """创建 Matplotlib 水平柱状图"""
    plt.figure(figsize=(10, 8))
    data = word_counts.most_common(10)
    labels = [item[0] for item in data]
    values = [item[1] for item in data]
    
    y_pos = range(len(labels))
    plt.barh(y_pos, values, color='lightcoral')
    plt.yticks(y_pos, labels, fontproperties=font)
    plt.title('词频统计-水平柱状图', fontsize=15, fontproperties=font)
    plt.xlabel('频次', fontsize=12, fontproperties=font)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

# 定义 Matplotlib 图表函数字典
matplotlib_functions = {
    "柱状图": plot_matplotlib_bar,
    "饼图": plot_matplotlib_pie,
    "折线图": plot_matplotlib_line,
    "散点图": plot_matplotlib_scatter,
    "水平柱状图": plot_matplotlib_barh
}

# 添加 Plotly 图表函数
def plot_plotly_bar(word_counts):
    """创建 Plotly 交互柱状图"""
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    
    fig = px.bar(df, x='词语', y='频次',
                 title='词频统计-交互柱状图',
                 color='频次',  # 添加颜色渐变
                 color_continuous_scale='Viridis',
                 template='plotly_white')
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        showlegend=False,
        xaxis_title="词语",
        yaxis_title="出现频次",
        hoverlabel=dict(bgcolor="white"),
        height=600
    )
    
    return fig

def plot_plotly_pie(word_counts):
    """创建 Plotly 动态饼图"""
    data = word_counts.most_common(8)
    labels = [item[0] for item in data]
    values = [item[1] for item in data]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,  # 设置成环形图
        textinfo='label+percent',
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title='词频统计-动态饼图',
        title_x=0.5,
        title_font_size=20,
        height=600
    )
    
    return fig

def plot_plotly_line(word_counts):
    """创建 Plotly 平滑折线图"""
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    
    fig = px.line(df, x='词语', y='频次',
                  title='词频统计-平滑折线图',
                  markers=True,  # 显示数据点
                  line_shape='spline',  # 使用平滑曲线
                  template='plotly_white')
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        xaxis_title="词语",
        yaxis_title="出现频次",
        height=600
    )
    
    return fig

def plot_plotly_scatter(word_counts):
    """创建 Plotly 气泡散点图"""
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    df['大小'] = df['频次'] / df['频次'].max() * 100  # 计算气泡大小
    
    fig = px.scatter(df, x=range(len(df)), y='频次',
                     size='大小',
                     text='词语',
                     title='词频统计-气泡散点图',
                     color='频次',
                     color_continuous_scale='Viridis',
                     template='plotly_white')
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        xaxis_title="词语排名",
        yaxis_title="出现频次",
        showlegend=False,
        height=600
    )
    
    return fig

def plot_plotly_waterfall(word_counts):
    """创建 Plotly 瀑布图"""
    data = word_counts.most_common(10)
    
    fig = go.Figure(go.Waterfall(
        name="词频",
        orientation="v",
        measure=["relative"] * len(data),
        x=[item[0] for item in data],
        y=[item[1] for item in data],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "Maroon"}},
        increasing={"marker": {"color": "Teal"}},
        text=[item[1] for item in data],
        textposition="outside"
    ))
    
    fig.update_layout(
        title='词频统计-瀑布图',
        title_x=0.5,
        title_font_size=20,
        showlegend=False,
        height=600
    )
    
    return fig

def plot_plotly_treemap(word_counts):
    """创建 Plotly 树形图"""
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    
    fig = px.treemap(df, 
                     path=['词语'],
                     values='频次',
                     title='词频统计-树形图',
                     color='频次',
                     color_continuous_scale='RdBu',
                     template='plotly_white')
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        height=600
    )
    
    return fig

# 定义 Plotly 图表函数字典
plotly_functions = {
    "交互柱状图": plot_plotly_bar,
    "动态饼图": plot_plotly_pie,
    "平滑折线图": plot_plotly_line,
    "气泡散点图": plot_plotly_scatter,
    "瀑布图": plot_plotly_waterfall,
    "树形图": plot_plotly_treemap
}

# 添加 Seaborn 图表函数
def plot_seaborn_bar(word_counts):
    """创建 Seaborn 增强柱状图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    
    # 创建基础柱状图
    ax = sns.barplot(data=df, x='词语', y='频次', palette='husl')
    
    # 自定义样式
    plt.title('词频统计-增强柱图', fontsize=15, fontproperties=font)
    plt.xlabel('词语', fontsize=12, fontproperties=font)
    plt.ylabel('频次', fontsize=12, fontproperties=font)
    plt.xticks(rotation=45, fontproperties=font)
    
    # 添加数值标签
    for i in ax.containers:
        ax.bar_label(i, fontproperties=font)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_seaborn_scatter(word_counts):
    """创建 Seaborn 高级散点图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    df['排名'] = range(1, len(df) + 1)
    
    # 创建散点图
    sns.scatterplot(data=df, x='排名', y='频次', size='频次', 
                   sizes=(100, 1000), legend=False)
    
    # 添加标签
    for i, row in df.iterrows():
        plt.annotate(row['词语'], 
                    (row['排名'], row['频次']),
                    xytext=(5, 5), textcoords='offset points',
                    fontproperties=font)
    
    plt.title('词频统计-高级散点图', fontsize=15, fontproperties=font)
    plt.xlabel('排名', fontsize=12, fontproperties=font)
    plt.ylabel('频次', fontsize=12, fontproperties=font)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_seaborn_regplot(word_counts):
    """创建 Seaborn 回归曲线图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    df['排名'] = range(1, len(df) + 1)
    
    # 创建回归图
    sns.regplot(data=df, x='排名', y='频次', 
                scatter_kws={'s': 100},
                line_kws={'color': 'red'})
    
    # 添加词语标签
    for i, row in df.iterrows():
        plt.annotate(row['词语'], 
                    (row['排名'], row['频次']),
                    xytext=(5, 5), textcoords='offset points',
                    fontproperties=font)
    
    plt.title('词频统计-回归曲线图', fontsize=15, fontproperties=font)
    plt.xlabel('排名', fontsize=12, fontproperties=font)
    plt.ylabel('频次', fontsize=12, fontproperties=font)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_seaborn_violin(word_counts):
    """创建 Seaborn 小提琴图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(10)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    
    # 创建小提琴图
    sns.violinplot(data=df, x='词语', y='频次', palette='husl')
    
    plt.title('词频统计-小提琴图', fontsize=15, fontproperties=font)
    plt.xlabel('词语', fontsize=12, fontproperties=font)
    plt.ylabel('频次', fontsize=12, fontproperties=font)
    plt.xticks(rotation=45, fontproperties=font)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

def plot_seaborn_kde(word_counts):
    """创建 Seaborn 核密度图"""
    plt.figure(figsize=(12, 6))
    data = word_counts.most_common(15)
    df = pd.DataFrame(data, columns=['词语', '频次'])
    
    # 创建核密度图
    sns.kdeplot(data=df, x='频次', fill=True)
    
    # 添加垂直线标记每个词的频次
    for i, row in df.iterrows():
        plt.axvline(x=row['频次'], ymax=0.3, alpha=0.3)
        plt.text(row['频次'], 0.01, row['词语'], 
                rotation=90, fontproperties=font)
    
    plt.title('词频统计-核密度图', fontsize=15, fontproperties=font)
    plt.xlabel('频次', fontsize=12, fontproperties=font)
    plt.ylabel('密度', fontsize=12, fontproperties=font)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return buf

# 定义 Seaborn 图表函数字典
seaborn_functions = {
    "增强柱图": plot_seaborn_bar,
    "高级散点": plot_seaborn_scatter,
    "回归曲线": plot_seaborn_regplot,
    "小提琴图": plot_seaborn_violin,
    "核密度图": plot_seaborn_kde
}

if url:
    with st.spinner('🚀 AI正在分析中...'):
        # 创建进度条
        progress = st.progress(0)
        
        # 获取文本
        text = get_text_from_url(url)
        progress.progress(50)
        
        if text:
            # 分析文本
            word_counts = word_frequency(text)
            progress.progress(100)
            
            if word_counts:
                # 数据概览
                st.markdown("""
                <div class="custom-card animate-fade-in">
                    <h2 style='text-align: center; color: #DD2476;'>📊 智能分析报告</h2>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                metrics = [
                    ("📚 总词数", len(word_counts)),
                    ("🔤 独立词汇", len(set(word_counts))),
                    ("🏆 最高词频", max(word_counts.values()))
                ]
                
                for col, (label, value) in zip([col1, col2, col3], metrics):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card animate-gradient">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{value:,}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                
                
                
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # 可视化图表
                st.markdown(f"""
                <div class="custom-card animate-fade-in">
                    <h3 style='color: #DD2476;'>📈 {graph_type} 分析</h3>
                """, unsafe_allow_html=True)
                
                # 图表说明
                with st.expander("💡 查看图表说明"):
                    st.markdown(f"""
                    - 图表类型：{graph_type}
                    - 数据范围：Top 30 高频词
                    - 交互方式：支持缩放、平移、数据显示
                    """)
                
                # 渲染图表
                if viz_library == "📊 Pyecharts":
                    if graph_type.split()[1] in chart_functions:
                        chart = chart_functions[graph_type.split()[1]](word_counts)
                        st.components.v1.html(
                            chart.render_embed(),
                            height=600,
                            scrolling=True
                        )
                elif viz_library == "📈 Matplotlib":
                    graph_type_clean = graph_type.split()[1]
                    if graph_type_clean in matplotlib_functions:
                        buf = matplotlib_functions[graph_type_clean](word_counts)
                        st.image(buf, use_container_width=True)
                elif viz_library == "🎨 Plotly":
                    graph_type_clean = graph_type.split()[1]
                    if graph_type_clean in plotly_functions:
                        fig = plotly_functions[graph_type_clean](word_counts)
                        st.plotly_chart(fig, use_container_width=True)
                else:  # Seaborn
                    graph_type_clean = graph_type.split()[1]
                    if graph_type_clean in seaborn_functions:
                        buf = seaborn_functions[graph_type_clean](word_counts)
                        st.image(buf, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                

                # 词频排行
                st.markdown("""
                <div class="custom-card animate-fade-in">
                    <h3 style='color: #DD2476;'>🏅 热门词汇 TOP 10</h3>
                """, unsafe_allow_html=True)
                
                df = pd.DataFrame(word_counts.most_common(10), columns=["词语", "频次"])
                
                # 使用原生dataframe显示，添加高亮样式
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "词语": st.column_config.TextColumn(
                            "词语",
                            help="出现的词语",
                            width="medium",
                        ),
                        "频次": st.column_config.NumberColumn(
                            "频次",
                            help="词语出现的次数",
                            format="%d",
                        ),
                    },
                    hide_index=True,
                )
                # 数据导出
                st.markdown("""
                <div class="custom-card animate-fade-in">
                    <h3 style='color: #DD2476;'>📥 导出分析结果</h3>
                """, unsafe_allow_html=True)
                
                df_download = pd.DataFrame(word_counts.most_common(), columns=["词语", "频次"])
                st.download_button(
                    label="💾 导出完整数据 (CSV)",
                    data=df_download.to_csv(index=False).encode('utf-8'),
                    file_name='text_analysis_result.csv',
                    mime='text/csv'
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ 未能提取有效文本，请检查网址是否正确")
        
        progress.empty()

# 页脚
st.markdown("""
<div class="footer">
    <h3>智能文本分析平台</h3>
    <p>Created with 💖 by 马宇哲</p>
    <p>Version 3.0.0 | © 2024 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)