import codecs
import time
import re

date = time.strftime('%m-%d', time.localtime())

# with codecs.open('./data/%s.txt' % date, 'a', 'utf-8') as file:
#     file.write('Hello World!\n')
#     file.write('哈哈哈2\n')
#     file.close()

with codecs.open('./messages.log', 'r', 'utf-8') as logfile:
    for line in logfile:
        print(line)
        time_match = re.search(r'^#(.{19}).+?#\s(.+)', line)
        print(time_match.group(0))  # 整行日志
        print(time_match.group(1))  # 时间
        print(time_match.group(2))  # 消息正文
        date = time.strptime(time_match.group(1), "%m/%d/%Y %H:%M:%S")
        print(date.tm_hour)
