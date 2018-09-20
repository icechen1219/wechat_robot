import codecs
import time
import re
import math
from collections import Counter
from pyecharts import Line, Pie, Graph, Bar, WordCloud
from pyecharts import Page
from snownlp import SnowNLP
import wechat_monitor

date = time.strftime('%m-%d', time.localtime())
earlest_reply = None
earlest_reply_msg = None
latest_reply = None
latest_reply_msg = None
msg_dict = {}
date_msg_counter = Counter()
emotions = []
keywords_counter = Counter()


def all_in_page():
    pass


def dict2sorted_by_key(_dict):
    """
    将字典按key排序
    :param _dict: 标准字典
    :return: 二元组列表，按key递增
    """
    name_list = []
    num_list = []

    # 用lambda表达式来排序，x[0]表示按key排序，x[1]表示按value排序
    list1 = sorted(_dict.items(), key=lambda x: x[0])
    return list1


def dict2sorted_by_value(_dict):
    """
    将字典按key排序
    :param _dict: 标准字典
    :return: 二元组列表，按key递增
    """
    name_list = []
    num_list = []

    # 用lambda表达式来排序，x[0]表示按key排序，x[1]表示按value排序
    list1 = sorted(_dict.items(), key=lambda x: x[1])
    return list1


def counter2list(_counter):
    """
    二元组计数器转列表
    :param _counter: 调用过most_common(n)的计数器
    :return:
    """
    name_list = []
    num_list = []

    for item in _counter:
        name_list.append(item[0])
        num_list.append(item[1])

    return name_list, num_list


def emotions_count(_emotions):
    count_good = len(list(filter(lambda x: x > 0.66, _emotions)))
    count_normal = len(list(filter(lambda x: 0.33 <= x <= 0.66, _emotions)))
    count_bad = len(list(filter(lambda x: x < 0.33, _emotions)))
    labels = [u'负面消极', u'中性', u'正面积极']
    values = (count_bad, count_normal, count_good)
    return labels, values


if __name__ == '__main__':
    # 群消息日志的正则表达式（群标识-发言人-正文），用于提取聊天正文
    regex = re.compile(r'(.+)\-(.+)\-(.+)', re.I | re.M)
    with codecs.open('./log/merge.log', 'r', 'utf-8') as logfile:
        for line in logfile:
            time_match = re.search(r'^#(.{5}).{5}\s(.{8}).+?#\s(.+)', line)
            if time_match:
                # print(time_match.group(0))  # 整行日志
                # print(time_match.group(1))  # 日期
                # print(time_match.group(2))  # 时间
                # print(time_match.group(3))  # 消息正文
                # 字符串转时间
                # date = time.strptime(time_match.group(1) + " " + time_match.group(2), "%m/%d/%Y %H:%M:%S")
                # 时间转时间戳
                # print(time.mktime(date))
                # 以时间为key，将每条信息存入dict，方便后续做排序统计
                msg_dict[time_match.group(2)] = (time_match.group(1), time_match.group(3))
                # 按天统计聊天总数
                date_msg_counter[time_match.group(1)] += 1
                content_match = regex.search(time_match.group(3))
                # 对纯文字聊天进行情感分析（积极指数）
                if content_match and content_match.group(3) != 'NoneText':
                    nlp = SnowNLP(content_match.group(3))
                    emotions.append(nlp.sentiments)
                    wechat_monitor.get_tag(content_match.group(3), keywords_counter)

        # print(msg_dict)
        msg_list = dict2sorted_by_key(msg_dict)
        # print(msg_list)
        print("%s天总共发言：%d条" % (len(date_msg_counter), len(msg_list)))
        print("平均每天发言：%d条" % math.floor(len(msg_list) / len(date_msg_counter)))
        dict_sorted_by_value = dict2sorted_by_value(date_msg_counter)
        print(dict_sorted_by_value)
        most_msg_count = dict_sorted_by_value[len(dict_sorted_by_value) - 1]
        print("发言最多的一天：%s %s条" % (most_msg_count[0], most_msg_count[1]))
        print("发言最少的一天：%s %s条" % (dict_sorted_by_value[0][0], dict_sorted_by_value[0][1]))

        if len(msg_list) > 0:
            earlest_reply = msg_list[0][0]
            earlest_reply_msg = msg_list[0][1]
            content_match = regex.search(earlest_reply_msg[1])
            if content_match:
                earlest_time_node = "最早一条发言：%s %s，来自：%s群" % (
                    earlest_reply_msg[0], earlest_reply, content_match.group(1))
                print(earlest_time_node)
                earlest_msg_node = '"%s" 说 「%s」' % (content_match.group(2), content_match.group(3))
                print(earlest_msg_node)

            latest_reply = msg_list[len(msg_list) - 1][0]
            latest_reply_msg = msg_list[len(msg_list) - 1][1]
            content_match = regex.search(latest_reply_msg[1])
            if content_match:
                latest_time_node = "最晚一条发言：%s %s，来自：%s群" % (latest_reply_msg[0], latest_reply, content_match.group(1))
                print(latest_time_node)
                latest_msg_node = '"%s" 说 「%s」' % (content_match.group(2), content_match.group(3))
                print(latest_msg_node)

    page = Page()

    # line
    item_name_list, item_num_list = counter2list(dict2sorted_by_key(date_msg_counter))
    line = Line("群心情走势图", "截至日期：%s" % item_name_list[len(item_name_list) - 1], title_text_size=30,
                subtitle_text_size=18, title_pos='center')
    line.add("", item_name_list, item_num_list, mark_point=["max"], legend_pos='65%',
             xaxis_interval=0, xaxis_rotate=27, xaxis_label_textsize=20, yaxis_label_textsize=20, yaxis_name_pos='end',
             yaxis_pos="%50", is_label_show=True)
    page.add(line)

    # pie
    attr = ["总发言数", "日均发言", "发言最多", "发言最少"]
    v1 = [len(msg_list), math.floor(len(msg_list) / len(date_msg_counter)), most_msg_count[1],
          dict_sorted_by_value[0][1]]
    pie = Pie("群聊数据统计", title_pos='center')
    pie.add("", attr, v1, radius=[40, 75], label_text_color=None,
            is_label_show=True, legend_orient='vertical', legend_pos='left')
    page.add(pie)

    # bar
    bar = Bar("群聊情感分析", title_pos='center')
    item_name_list, item_num_list = emotions_count(emotions)
    bar.add("", item_name_list, item_num_list, title_pos='center', is_label_show=True)
    page.add(bar)

    # graph
    nodes = [{"name": earlest_time_node, "symbolSize": 30},
             {"name": latest_time_node, "symbolSize": 50},
             {"name": earlest_msg_node, "symbolSize": 30},
             {"name": latest_msg_node, "symbolSize": 50}]
    links = [{"source": nodes[0].get('name'), "target": nodes[2].get('name')},
             {"source": nodes[1].get('name'), "target": nodes[3].get('name')}]

    graph = Graph("爱群关系图", title_pos='center')
    graph.add("", nodes, links, is_label_show=True, graph_repulsion=8000, graph_layout="circular",
              label_text_color=None)
    page.add(graph)

    # wordcloud
    item_name_list, item_num_list = counter2list(keywords_counter.most_common(100))
    wordcloud = WordCloud("话题排行", title_pos='center', width=800, height=800)
    wordcloud.add("", item_name_list, item_num_list, word_size_range=[9, 108], shape='circle')
    page.add(wordcloud)

    page.render('./analyse/九月统计与分析.html')
    # page.render('/virtualhost/webapp/love/wechat/九月统计与分析.html')
