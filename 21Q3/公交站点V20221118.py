# encoding:utf-8
# Author:   xiaoyi | 小一
# wechat:   xiaoyixy512
# 公众号：   小一的学习笔记
# email:    zhiqiuxiaoyi@qq.com
# Date:     2022/11/18 23:49
# Description:
import os
import random

import pandas as pd
import numpy as np
import warnings

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


def get_bus_list(city):
    """
    获取公交站点信息
    :return:
    """
    url = 'https://{0}.8684.cn/'.format(city)
    header = {'User-Agent': '"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"'}
    response = requests.get(url, headers=header)
    """获取数据并解析"""
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_buslayer = soup.find('div', class_='bus-layer depth w120')
    
    """解析公交路线类型"""
    dic_result = {}
    soup_buslist = soup_buslayer.find_all('div', class_='pl10')
    for soup_bus in soup_buslist:
        name = soup_bus.find('span', class_='kt').get_text()
        if '线路分类' in name:
            soup_a_list = soup_bus.find('div', class_='list')
            for soup_a in soup_a_list.find_all('a'):
                text = soup_a.get_text()
                href = soup_a.get('href')
                dic_result[text] = "https://{0}.8684.cn{1}".format(city, href)
                
    return dic_result
    
    
def get_line_info(dic_result):
    """
    解析并获取每个线路的数据
    :param dic_result:
    :return:
    """
    """解析公交站点"""
    bus_arr = []
    for key, value in dic_result.items():
        print('[ 提示 ]: 正在爬取城市 {0} 的 {1} 的数据中：{2}'.format(city, key, value))
        header = {'User-Agent': '"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"'}
        response = requests.get(value, headers=header)
        """获取数据并解析"""
        soup = BeautifulSoup(response.text, 'html.parser')
        # 详细线路
        soup_buslist = soup.find('div', class_='list clearfix')
        for soup_a in soup_buslist.find_all('a'):
            text = soup_a.get_text()
            href = soup_a.get('href')
            title = soup_a.get('title')
            bus_arr.append([key, title, text, "https://{0}.8684.cn{1}".format(city, href), city, '未更新'])
    df_bus = pd.DataFrame(bus_arr, columns=['线路类型', '线路名称', '标记', '链接', '城市', '详情'])

    return df_bus


if __name__ == '__main__':
    df_data = pd.DataFrame()
    city_list = ['shenzhen', 'guangzhou', 'beijing', 'shanghai']
    for city in city_list:
        dic_city = get_bus_list(city)
        df_per_city = get_line_info(dic_city)
        df_data = df_data.append(df_per_city, ignore_index=True)

    filepath = os.path.join('data', '北上广深公交站点数据V202211.csv')
    df_data.to_csv(filepath, encoding='gbk', index=False)
    print('[ 提示 ]: 爬取成功，数据已保存在：{0} '.format(filepath))