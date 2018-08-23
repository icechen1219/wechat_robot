# coding=utf-8
import re

group_name = '广州达木令水产交易达令家群'
pass_groups = re.search(r'达.*?令', group_name, re.M | re.I)
if pass_groups is None:
    print(None)
else:
    print(pass_groups)  # output: <_sre.SRE_Match object; span=(2, 5), match='达木令'>
    print(pass_groups.groups())  # output: () --- 因为正则没有用分组，所以这里为空
    print(pass_groups.group(0))  # output: 达木令 --- 第一个跟正则表达式匹配的内容
    print(pass_groups.group(1))  # output: IndexError
