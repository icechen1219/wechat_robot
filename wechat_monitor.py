# coding=utf-8
# author:微信公众号：威扬咨询
# 基于itchat项目的微信自动回复聊天机器人，纯粹是为了在朋友群里好玩，可以处理文本消息、图片和红包信息。
import codecs
import itchat
import json
import requests
import time
import re
from itchat.content import *
from numpy import random
from collections import Counter
import os
import jieba.analyse
from pyecharts import WordCloud
from pyecharts import Bar
from pyecharts import Grid
import custom_logger

at_msg_dict = ['收到', '这...', '在', '套我话？', '咋啦？', '哦哦', '我不在', '我是隐身的', 'copy that', '……', '哈', '吼吼', '赫赫', '汗']

# 用于控制同一个群恶意艾特我的逻辑处理
at_msg_counter = Counter()
first_at_time = {}
# 败友群id
money_notify_groups = ''
# 兄弟姐妹群id
brother_sister_group = ''
# 吃货群的id
beauty_foodie_group = ''
groups = None
# 我的微信小号
notify_user = None


def download_pictures(msg):
    """
    处理群聊图片
    :param msg: 源消息对象
    :return:
    """

    if msg['FileName'].endswith('.gif'):  # 不要gif图片
        return
    # 群名
    group_name = msg['User']['NickName']
    custom_logger.info('收到一个文件: %s' % group_name)
    filter_groups = re.search(r'(达令|电商|开发|答疑|咨询|讨论|配送|系)', group_name, re.M | re.I)
    if filter_groups is None:  # 不在上述过滤词内
        msg['Text'](msg['FileName'])  # 先下载至本地，分析结束再决定是否删除
        type_symbol = {PICTURE: 'img', VIDEO: 'vid', }.get(msg.type, 'fil')
        custom_logger.debug('@%s@%s' % (type_symbol, msg.fileName))
        custom_logger.info('文件来自群：%s' % group_name)

        reply_msg = generate_reply_msg(msg.fileName, msg['ActualNickName'])
        if reply_msg:
            custom_logger.info(reply_msg)
    else:
        custom_logger.info("此群不用回复！")


def record_text_msg(msg):
    """
    监听群的文字聊天记录并处理艾特我的信息
    :param msg:
    :return:
    """

    from_group_id_ = msg['FromUserName']  # 收到消息的群的标识
    group_name = msg['User']['NickName']  # 群名
    custom_logger.debug('收到一条%s群的消息:%s' % (group_name, msg['Content']))

    # 2018.8.17 只记录本群的聊天记录; 2018.8.21 增加我发出去的消息的判断
    if from_group_id_ == money_notify_groups or msg['ToUserName'] == money_notify_groups:
        custom_logger.debug(u"记录败友群聊天记录...%s" % money_notify_groups)

    # 处理艾特我的信息，给予简单自动回复
    match_groups = re.search(r'(兄弟|西大|读书|广州|吃货|深圳)', group_name, re.M | re.I)
    if match_groups is None:  # 只处理上述群
        return
    if msg['IsAt']:
        at_msg_counter[from_group_id_] += 1
        reply_msg = deal_at_msg(from_group_id_)
        if reply_msg:
            itchat.send(reply_msg, from_group_id_)


@itchat.msg_register([TEXT, MAP, CARD, SHARING, PICTURE, RECORDING, VIDEO], isGroupChat=True)
def group_msg_monitor(msg):
    """
    监听群聊天记录，并作出各种统计分析的响应
    :param msg:
    :return:
    """
    global money_notify_groups, brother_sister_group, groups, beauty_foodie_group
    if len(money_notify_groups) == 0:  # 因为群组搜索会产生网络请求，所以只在第一次搜索
        groups = itchat.get_chatrooms(update=True)
        users = itchat.search_chatrooms(name=u'败友')  # 把红包消息通知给这个群
        money_notify_groups = users[0]['UserName']  # 获取这个群的唯一标识
        custom_logger.info(u'已获得败友群id: %s' % money_notify_groups)
        users2 = itchat.search_chatrooms(name=u'兄弟姐妹')
        brother_sister_group = users2[0]['UserName']
        custom_logger.info(u'已获得兄弟姐妹群id: %s' % brother_sister_group)
        beauty_foodie_group = itchat.search_chatrooms(name=u'颜值吃货')[0]['UserName']

    if msg.type == PICTURE:
        download_pictures(msg)
    elif msg.type == TEXT:
        record_text_msg(msg)

    if msg['FromUserName'] == money_notify_groups or msg['ToUserName'] == money_notify_groups:
        # 2018.8.21 统计败友群的发言次数
        custom_logger.logmessage("bad-%s" % msg['ActualNickName'], msg['Content'] if msg.type == TEXT else 'NoneText')

    if msg['FromUserName'] == brother_sister_group or msg['ToUserName'] == brother_sister_group:
        # 2018.8.23 统计兄弟姐妹群的发言次数
        custom_logger.logmessage("brother-%s" % msg['ActualNickName'],
                                 msg['Content'] if msg.type == TEXT else 'NoneText')

    if msg['FromUserName'] == beauty_foodie_group or msg['ToUserName'] == beauty_foodie_group:
        # 2018.11.25 统计吃货群的发言次数
        custom_logger.foodie_debug("颜值吃货-%s" % msg['ActualNickName'], msg['Content'] if msg.type == TEXT else 'NoneText')


@itchat.msg_register(NOTE, isGroupChat=True)
def receive_red_packet(msg):
    """
    监听群内红包消息
    :param msg:
    :return:
    """
    if u"收到红包" in msg['Content']:
        custom_logger.info(u'收到一个群红包')
        group_name = msg['User']['NickName']  # 群名
        global money_notify_groups, groups
        if len(money_notify_groups) == 0:  # 因为群组搜索会产生网络请求，所以只在第一次搜索
            groups = itchat.get_chatrooms(update=True)
            users = itchat.search_chatrooms(name=u'败友')  # 把红包消息通知给这个群
            money_notify_groups = users[0]['UserName']  # 获取这个群的唯一标示
            custom_logger.info(money_notify_groups)
        if msg['FromUserName'] == money_notify_groups:  # 2018.8.6 过滤本群的红包通知
            custom_logger.info(u"同一个群的红包不通知...")
            return
        match_groups = re.search(r'(兄弟|西大|读书|广州|吃货|深圳)', group_name, re.M | re.I)
        if match_groups:
            msgbody = u'"%s"群红包,@Tonny @All' % group_name
            itchat.send(msgbody, toUserName=money_notify_groups)  # 告诉指定的好友群内有红包
            if '颜值吃货' in group_name:
                custom_logger.foodie_warn("颜值吃货", "收到红包")
                custom_logger.info(msg)
        else:
            custom_logger.info("此群红包不用通知那帮二货...")

        filter_groups = re.search(r'(达令|电商|珠海)', group_name, re.M | re.I)
        if filter_groups is None:  # 不在上述过滤词内
            notify_user.send(u'"%s"群红包' % group_name)  # 通知我自己的小号


def deal_at_msg(to_group):
    """
    处理在群聊中艾特我的函数\n
    基本思路：
        首次艾特，正常回复\n
        1分钟内被连续艾特5次，视为恶意测试，怼回去
    :param to_group: 艾特我的群
    :return: 不同情形下的回复内容，或空
    """
    tmp_msg = ''
    if is_first_at(to_group):  # 如果是首次艾特，则记录时间，以备后续判断
        first_at_time[to_group] = time.time()
        tmp_msg = at_msg_dict[random.randint(len(at_msg_dict))]
        custom_logger.info('第一次被艾特：%s' % tmp_msg)
    elif is_at_too_many(to_group):
        tmp_msg = ['皮这一下，你们开心了？', '艾特我这么多次，是想发红包吗？', '这么多人想我了？', '爱我你就大声说，何必艾特这么多^_^', '艾特这么多，累不？'][random.randint(5)]
        custom_logger.info(tmp_msg)
    return tmp_msg


def is_first_at(to_group):
    """
    判断是否是首次艾特，业务逻辑参考对应的uml图
    :param to_group: 所在群
    :return: True - 首次@，False - 非首次@
    """
    now = time.time()
    if at_msg_counter[to_group] <= 1:
        return True
    elif (now - first_at_time[to_group]) > 90:
        at_msg_counter[to_group] = 1
        return True
    return False


def is_at_too_many(to_group):
    """
    判断短时间是否被艾特多次
    :param to_group: 所在群
    :return: True - 恶意艾特，False - 非恶意
    """
    now = time.time()
    custom_logger.debug(at_msg_counter)
    custom_logger.debug(first_at_time)
    at_num = at_msg_counter[to_group]
    at_time = first_at_time[to_group]
    if (now - at_time) <= 90:  # 设1.5分钟为监测期限
        if at_num >= 5:
            return True
    else:  # 超过监测期限重置@状态为第一条
        at_msg_counter[to_group] = 1
    return False


def generate_reply_msg(image_file_name, user_name):
    """
    调用威扬咨询后台API，获得图片的一些原始信息，然后通过一定的算法逻辑，生成待回复的内容
    :param image_file_name: 图片文件名
    :param user_name: 图片的作者
    :return: 可回复的消息或者空
    """
    custom_logger.info('%s, %s' % (image_file_name, user_name))
    url = 'http://loveboyin.cn/WechatDetect'  # 微信聊天监控API
    files = {'uploadFile': (image_file_name, open(image_file_name, 'rb'))}
    data = {'user': user_name}
    r = requests.post(url, files=files, data=data)
    custom_logger.info(r.text)
    res_list = json.loads(r.text)
    if res_list['errorCode'] == 0:  # 正常返回数据
        if res_list['faceCount'] > 0:
            reply_msg = guess_person_action(res_list['faceCount'], res_list)  # 猜测人的行为
        else:
            custom_logger.info('删掉非人类的图片')
            os.remove(image_file_name)  # 人脸以外的图片删掉，浪费内存
            if res_list['isFood']:
                reply_msg = guess_food_action(time.time())  # 根据时间猜测大家在吃什么饭？
            else:
                return ''

        custom_logger.info(reply_msg)
        return reply_msg
    else:
        return ''


def guess_person_action(num, res_list):
    """
    根据照片猜测人的行为
    :param num: 人的数量
    :param res_list: 服务器返回的json结果
    :return: 回复内容
    """
    custom_logger.info("识别出的人数：%s" % num)
    custom_logger.debug(res_list['faceList'])
    if num == 1:
        score = res_list['faceList'][0]['beauty']  # 颜值
        sex = res_list['faceList'][0]['gender']  # 性别
        if score > 90:
            return ['这个美女的简直亮瞎了我的双眼', '这颜值，至少95分，啧啧', '美，比杨幂都美！', '经过大数据分析，此人有入选全球最美脸蛋的潜质'][
                random.randint(4)] if sex < 50 else '这个超级大帅哥是谁？请收下我的膝盖'
        if sex < 50 and (75 < score <= 90):
            return ['经鉴定，美女一枚', '看到美女一天心情就好了', '你们觉得这个姑娘美不美？'][random.randint(3)]
        else:
            custom_logger.info('要么是男的，要么是长的丑，不理会，嘿嘿...')
    if num == 2:
        return ['这两个人是谁呀？', '看着眼熟', '他们两个在干啥？', '二人行必有一照'][random.randint(4)]
    if 2 < num <= 5:  # 人多就PK颜值，让大家对话题感兴趣
        tmp_msg = res_list['imageStory']
        if res_list['bestLoc'] != -1:  # 如果发现美女（因为后台程序只计算了女性）就不用默认的内容
            tmp_msg = ['有没有觉得左起第%d颜值特别高啊？', '感觉第%d个是个大美女', '经过大数据分析，第%d最受宅男欢迎'][random.randint(
                3)] % (res_list['bestLoc'] + 1)
        return tmp_msg
    if num > 5:
        return ['好热闹啊～', '好多人', '人多热闹', '一言不合就合照'][random.randint(4)]

    return ''


def guess_food_action(now):
    """
    根据晒食物的时间猜测人的行为
    :param now: 晒图时间
    :return: 回复内容
    """
    hour = time.localtime(now).tm_hour
    custom_logger.info('晒美食时间：%d' % hour)
    if hour > 21 or hour < 6:
        return ['深夜投毒啊这是！', '不发红包就胖八斤', '这样拉仇恨好吗？', '又在夜夜笙歌了', '这个时候发吃的，良心不会痛吗？'][random.randint(5)]
    if 6 <= hour <= 10:
        return ['这个时候吃早餐？', '这吃的是啥呀？', '好吃吗？', '看到就饿了'][random.randint(4)]
    if 10 < hour <= 13:
        return ['中午少吃点，晚上好战斗，嘿嘿', '好丰盛的午餐', '看起来不错哦', '真好吃（四声）', '一大波美食来袭...'][random.randint(5)]
    if 16 < hour <= 21:
        return ['晚餐吃这么好，祝你明早胖4斤', '鼓励晚餐吃的好的发红包', '革命尚未成功，吃饱了再努力', '这是晚餐还是夜宵哦？'][random.randint(4)]
    return ''


def get_tag(text, cnt):
    """
    关键词统计函数
    :param text: 待解析字符串
    :param cnt: 计数器
    :return:
    """
    text = re.sub(r"\[.*\]", "", text)  # 用正则表达式去掉表情符号
    text = re.sub(r"@\S+?\s+", "", text)  # 去掉艾特的用户信息部分
    custom_logger.info('正在分析句子:%s' % text)
    tag_list = jieba.analyse.extract_tags(text)  # 关键词提取模式
    # tag_list = jieba.cut(text, cut_all=False)  # 直接切词模式
    custom_logger.info(tag_list)
    for tag in tag_list:
        cnt[tag] += 1
    custom_logger.debug(cnt)


def counter2list(_counter):
    """
    二元组转list
    :param _counter: 需要转换的二元组
    :return: key和value对应的list
    """
    name_list = []
    num_list = []

    for item in _counter:
        name_list.append(item[0])
        num_list.append(item[1])
    return name_list, num_list


def word_cloud(item_name, item_name_list, item_num_list, word_size_range):
    """
    根据key、value对应的list生成词云
    :param item_name: 文件名
    :param item_name_list: 词云的文本
    :param item_num_list: 词云文本的数量
    :param word_size_range: 单词字体大小范围
    :return:
    """
    wordcloud = WordCloud(width=1400, height=900)
    # 生成的词云图轮廓， 有'circle', 'cardioid', 'diamond', 'triangle-forward', 'triangle', 'pentagon', 'star'可选
    wordcloud.add("", item_name_list, item_num_list, word_size_range=word_size_range, shape='circle')
    out_file_name = '/virtualhost/webapp/love/wechat/' + item_name + '.html'
    wordcloud.render(out_file_name)


def get_bar(item_name, item_name_list, item_num_list):
    """
    根据key、value的对应list生成柱状图
    :param item_name: 文件名
    :param item_name_list: 柱状图的x坐标
    :param item_num_list: 柱状图的y坐标
    :return:
    """
    subtitle = "败友群友情统计^_^\n" + time.strftime('%Y-%m-%d', time.localtime())
    bar = Bar(item_name, page_title=item_name, title_text_size=30, title_pos='center', subtitle=subtitle,
              subtitle_text_size=25)

    bar.add("", item_name_list, item_num_list, title_pos='center', xaxis_interval=0, xaxis_rotate=27,
            xaxis_label_textsize=20, yaxis_label_textsize=20, yaxis_name_pos='end', yaxis_pos="%50")
    bar.show_config()

    grid = Grid(width=1300, height=800)
    grid.add(bar, grid_top="13%", grid_bottom="23%", grid_left="15%", grid_right="15%")
    out_file_name = '/virtualhost/webapp/love/wechat/' + item_name + '.html'
    grid.render(out_file_name)


def save_msg_data(msg_counter, out_file_name):
    """
    将聊天记录写入json文件
    :param msg_counter:
    :param out_file_name:
    :return:
    """
    with codecs.open(out_file_name, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(msg_counter, ensure_ascii=False))
        json_file.close()


if __name__ == '__main__':
    itchat.auto_login(enableCmdQR=2)  # 在命令行打开二维码

    friends = itchat.get_friends(update=True)[0:]  # 获取好友信息
    notify_user = itchat.search_friends(name=u'威扬咨询')[0]
    notify_user.send(u'hello,这是一条来自机器人的消息')
    custom_logger.info(u'hello,这是一条来自机器人的消息')
    itchat.run()
