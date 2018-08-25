import codecs
import time

date = time.strftime('%m-%d', time.localtime())

with codecs.open('./data/%s.txt' % date, 'a', 'utf-8') as file:
    file.write('Hello World!\n')
    file.write('哈哈哈2\n')
    file.close()
