import sys
import os

# 保证能 import 项目根目录下的 config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from pymysql import connect


def _new_conn():
    return connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT,
        charset=config.DB_CHARSET,
    )


def querys(sql, params=None, type='no_select'):
    """执行 SQL。type='select' 时返回查询结果列表，否则返回 '执行成功'。"""
    params = tuple(params or [])
    conn = _new_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if type != 'no_select':
            data_list = cursor.fetchall()
            return data_list
        conn.commit()
        return '执行成功'
    finally:
        conn.close()
