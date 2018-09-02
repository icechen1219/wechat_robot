# coding=utf-8
# author:微信公众号：威扬咨询
# 查看代码讲解，视频教程，请微信添加好友搜索公众号[威扬咨询]查看历史消息获取。
import json
import re
from pyecharts import Bar
from pyecharts import Grid
from pyecharts import Line
from collections import Counter
import os
import codecs


def get_bar(item_name, subtitle, item_name_list, item_num_list):
    bar = Bar(item_name, page_title=item_name, title_text_size=30, title_pos='center', subtitle=subtitle,
              subtitle_text_size=25)

    bar.add("", item_name_list, item_num_list, title_pos='center', xaxis_interval=0, xaxis_rotate=27,
            xaxis_label_textsize=20, yaxis_label_textsize=20, yaxis_name_pos='end', yaxis_pos="%50")
    bar.show_config()

    grid = Grid(width=1300, height=800)
    grid.add(bar, grid_top="13%", grid_bottom="23%", grid_left="15%", grid_right="15%")
    out_file_name = './analyse/' + item_name + '.html'
    grid.render(out_file_name)


def get_line(item_name, subtitle, item_name_list, item_num_list):
    line = Line(item_name, subtitle, title_text_size=30, subtitle_text_size=25, title_pos='center')
    line.add("", item_name_list, item_num_list, mark_point=["max", "min"], mark_line=["average"], title_pos='center',
             xaxis_interval=0, xaxis_rotate=27, xaxis_label_textsize=20, yaxis_label_textsize=20, yaxis_name_pos='end',
             yaxis_pos="%50")
    line.show_config()

    grid = Grid(width=1300, height=800)
    grid.add(line, grid_top="13%", grid_bottom="23%", grid_left="15%", grid_right="15%")

    out_file_name = './analyse/' + item_name + '.html'
    grid.render(out_file_name)


def all_in_line(item_name, subtitle, _counter1, _counter2, _counter3):
    line = Line(item_name, subtitle, title_text_size=30, subtitle_text_size=18, title_pos='center')

    item_name_list, item_num_list = counter2seven_list(_counter1)
    line.add("小群", item_name_list, item_num_list, mark_point=["max"], legend_pos='65%',
             xaxis_interval=0, xaxis_rotate=27, xaxis_label_textsize=20, yaxis_label_textsize=20, yaxis_name_pos='end',
             yaxis_pos="%50")

    item_name_list, item_num_list = counter2seven_list(_counter2)
    line.add("大群", item_name_list, item_num_list, mark_point=["max"], legend_pos='65%',
             xaxis_interval=0, xaxis_rotate=27, xaxis_label_textsize=20, yaxis_label_textsize=20, yaxis_name_pos='end',
             yaxis_pos="%50")

    item_name_list, item_num_list = counter2seven_list(_counter3)
    line.add("综合", item_name_list, item_num_list, mark_point=["max"], legend_pos='65%',
             xaxis_interval=0, xaxis_rotate=27, xaxis_label_textsize=20, yaxis_label_textsize=20, yaxis_name_pos='end',
             yaxis_pos="%50")
    line.show_config()

    grid = Grid(width=1300, height=800)
    grid.add(line, grid_top="13%", grid_bottom="23%", grid_left="15%", grid_right="15%")

    out_file_name = './analyse/' + item_name + '.html'
    grid.render(out_file_name)


def dict2sorted_list(_dict):
    """
    将字典按key排序
    :param _dict: 标准字典
    :return: 二元组列表，按key递增
    """
    name_list = []
    num_list = []

    print(_dict)
    # 用lambda表达式来排序，x[0]表示按key排序，x[1]表示按value排序
    list1 = sorted(_dict.items(), key=lambda x: x[0])
    print(list1)
    return list1


def dict2list(_dict):
    """
    字典转列表
    :param _dict: 标准字典
    :return:
    """
    name_list = []
    num_list = []

    for key, value in _dict.items():
        name_list.append(key)
        num_list.append(value)

    return name_list, num_list


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


def count_by_day(_counter):
    sum = 0
    for person in _counter:
        sum += _counter[person]
    return sum


def counter2seven_list(_counter):
    """
    计算器转最近七天的列表
    :param _counter:
    :return:
    """
    # 只统计最近七天
    days_counter_list = dict2sorted_list(_counter)
    if len(_counter) > 7:
        days_counter_list = days_counter_list[len(_counter) - 7:]

    name_list, num_list = counter2list(days_counter_list)
    return name_list, num_list


if __name__ == '__main__':
    # 败友群计数器
    bad_days_counter = Counter()
    # 兄弟姐妹群计数器
    brother_days_counter = Counter()
    # 两个群综合计数器
    both_days_counter = Counter()

    work_dir = './data'
    for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            match_obj = re.search(r'^(\w+)\-(\d{2}\-\d{2})\.json$', filename)
            if match_obj:
                # print('\n文件名：%s' % filename)
                # print('文件完整路径：%s' % file_path)
                print(match_obj.group(1))  # 群英文名
                print(match_obj.group(2))  # 日期
                with codecs.open(file_path, 'r', 'utf-8') as jsonfile:
                    msg_counter = json.load(jsonfile)
                    if match_obj.group(1).startswith("bad"):
                        bad_days_counter[match_obj.group(2)] += count_by_day(msg_counter)
                    elif match_obj.group(1).startswith("brother"):
                        brother_days_counter[match_obj.group(2)] += count_by_day(msg_counter)
                    both_days_counter[match_obj.group(2)] += count_by_day(msg_counter)

    all_in_line("败友吹水七天走势", "威扬咨询友情统计", bad_days_counter, brother_days_counter, both_days_counter)
