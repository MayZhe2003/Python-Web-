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

# 定义停用词列表
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就',
    '不', '人', '都', '一', '一个', '上', '也', '很',
    '到', '说', '要', '去', '你', '会', '着', '没有',
    '看', '好', '自己', '这', '年', '做', '来', '后'
])

# 在文件顶部添加自定义CSS样式
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTitle {
        font-size: 3rem !important;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stSubheader {
        color: #34495e;
        font-size: 1.5rem !important;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .css-1d391kg {  /* 修改侧边栏样式 */
        background-color: #f1f3f6;
        padding: 2rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #3498db;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

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

# 修改主页面布局
st.title("📊 网页文本分析工具")
st.markdown("---")

# 美化侧边栏
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1998/1998664.png", width=100)  # 添加一个图标
    st.header("🛠️ 配置选项")
    st.markdown("---")
    
    graph_type = st.selectbox(
        "📈 选择可视化图表",
        ["词云图", "柱状图", "饼图", "折线图", "漏斗图", "散点图", "雷达图"]
    )
    
    st.markdown("---")
    st.markdown("### 📝 使用说明")
    st.markdown("""
    1. 输入完整的网址（包含http://或https://）
    2. 选择想要的可视化图表类型
    3. 等待分析结果显示
    """)

# 美化URL输入区域
st.markdown("### 🌐 输入网页地址")
url = st.text_input(
    "",  # 移除默认标签
    placeholder="请输入要分析的网页URL...",
    help="输入完整的网址，包含http://或https://"
)

if url:
    # 添加进度条
    progress_bar = st.progress(0)
    with st.spinner('🚀 正在获取和分析网页内容...'):
        text = get_text_from_url(url)
        progress_bar.progress(50)
        
        if text:
            word_counts = word_frequency(text)
            progress_bar.progress(100)
            
            if word_counts:
                st.markdown("---")
                st.subheader("📊 基础统计信息")
                
                # 美化统计指标显示
                cols = st.columns(3)
                with cols[0]:
                    st.metric("📚 总词数", f"{len(word_counts):,}")
                with cols[1]:
                    st.metric("🔤 独立词数", f"{len(set(word_counts)):,}")
                with cols[2]:
                    st.metric("🏆 最高词频", f"{max(word_counts.values()):,}")

                st.markdown("---")
                st.subheader("🏅 词频排行（Top 3）")
                
                # 美化表格显示
                df = pd.DataFrame(word_counts.most_common(3), columns=["词语", "频次"])
                st.dataframe(
                    df.style.background_gradient(cmap='Blues'),
                    use_container_width=True
                )

                st.markdown("---")
                st.subheader(f"📈 {graph_type}可视化")
                
                # 添加图表说明
                with st.expander("📖 图表说明"):
                    st.markdown(f"""
                    - 当前显示: **{graph_type}**
                    - 数据范围: 根据图表类型显示top N个词频
                    - 可交互: 鼠标悬停可查看详细数据
                    """)

                # 根据用户选择显示对应图表
                chart_functions = {
                    "词云图": draw_wordcloud,
                    "柱状图": draw_bar_chart,
                    "饼图": draw_pie_chart,
                    "折线图": draw_line_chart,
                    "漏斗图": draw_funnel_chart,
                    "散点图": draw_scatter_chart,
                    "雷达图": draw_radar_chart
                }

                # 绘制选中的图表
                if graph_type in chart_functions:
                    chart = chart_functions[graph_type](word_counts)
                    st.components.v1.html(
                        chart.render_embed(),
                        height=600,
                        scrolling=True
                    )
                
                # 添加下载功能
                st.markdown("---")
                st.subheader("📥 数据下载")
                df_download = pd.DataFrame(word_counts.most_common(), columns=["词语", "频次"])
                st.download_button(
                    label="下载完整词频数据 (CSV)",
                    data=df_download.to_csv(index=False).encode('utf-8'),
                    file_name='word_frequency.csv',
                    mime='text/csv'
                )
            else:
                st.error("⚠️ 没有词频数据，请检查输入。")
        
        # 清除进度条
        progress_bar.empty()

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Made with ❤️ by Your Name</p>
    <p>版本 1.0.0 | © 2024 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)