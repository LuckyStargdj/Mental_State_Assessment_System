import os
import sqlite3
import time
from datetime import datetime

import pandas as pd

from utils.logger import logger


class api():
    """数据库操作接口
    """

    def __init__(self):
        cofig_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(cofig_dir)
        self.database_path = os.path.join(project_dir, 'data/db/medical_database.db')

    def get_users(self, user, password):
        """查询 用户是否存在,并判断他的用户类型
        参数:用户名 密码
        返回：
            成功与否，
        """
        conn = sqlite3.connect(self.database_path)

        try:
            cursor = conn.cursor()
            sql = f'SELECT * FROM users where username="{user}" and password="{password}";'
            cursor.execute(sql)
            res = cursor.fetchone()
            type = res[3]

            if not res:  # 如果没有查询结果
                return False, ""
            return True, type
        except Exception as ex:
            print(ex)
            return False, ""
        finally:
            conn.close()

    def get_user_type_id(self, user):
        """根据用户名查询账号类型,id
        参数:用户名
        返回：
            成功与否，
        """
        conn = sqlite3.connect(self.database_path)  # 注意这里如果不存在文件，会新建一个
        try:
            cursor = conn.cursor()
            sql = f'SELECT * FROM users where username="{user}";'
            cursor.execute(sql)
            res = cursor.fetchone()
            if not res:  # 如果没有查询结果
                return True, None
            type = res[3]
            id = res[0]
            return True, [type, id]
        except Exception as ex:
            return False, "查询错误"
        finally:
            conn.close()

    def update_user_password(self, user, password):
        ''' 修改用户表密码
        参数:

        返回：
            成功与否
        '''

        conn = sqlite3.connect(self.database_path)  # 注意这里如果不存在文件，会新建一个

        try:
            cursor = conn.cursor()
            sql = f'UPDATE users SET password = "{password}" WHERE username = "{user}";'
            # print(sql)
            cursor = cursor.execute(sql)
            conn.commit()
        except Exception as ex:
            # print("发生异常",ex)
            conn.rollback()
            return False
        finally:
            # 最终关闭数据库连接
            conn.close()

        return True

    def export_Current_page_tables(self, page_count, current_page, phone=None, name=None, time=None, grade=None,
                                   Class=None, level=None,time_suffix=None):
        """
        获取当前页面的数据。
        """
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            # 基础查询
            query_base = '''
                SELECT 
                    m.phone, m.name, m.grade, m.class, m.sex, m.age,
                    r.anxiety_score, r.anxiety_result, r.depressed_score, r.depressed_result,
                    r.count, r.createtime
                FROM report r
                LEFT JOIN medical_records m ON r.phone = m.phone
                WHERE r.is_delete = ?
            '''
            params = [1]

            # 动态添加条件
            if phone:
                query_base += ' AND r.phone LIKE ?'
                params.append(phone + '%')
            if name:
                query_base += ' AND m.name LIKE ?'
                params.append('%' + name + '%')
            if time:
                query_base += ' AND r.createtime LIKE ?'
                params.append(time + '%')
            if grade:
                query_base += ' AND m.grade = ?'
                params.append(grade)
            if Class:
                query_base += ' AND m.class = ?'
                params.append(Class)

            if time and time_suffix:
                query_base += ' AND r.createtime BETWEEN ? AND ?'
                time_prefix_full = f"{time} 00:00:00"
                time_suffix_full = f"{time_suffix} 23:59:59"
                params.extend([time_prefix_full, time_suffix_full])

            if level:
                query_base += ' AND (r.anxiety_result = ? OR r.depressed_result = ?)'
                params.extend([level, level])

            # 添加排序和分页
            query_base += ' ORDER BY r.id DESC LIMIT ?, ?'
            params.extend([page_count * (current_page - 1), page_count])

            # 执行查询
            cursor.execute(query_base, params)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                report_list = list(row[6:])  # report 表的列
                medical_list = list(row[:6])  # medical_records 表的列
                combined_list = medical_list + report_list
                combined_list = ["" if x is None else x for x in combined_list]
                result.append(combined_list)

            conn.close()
            return True, result

        except Exception as ex:
            logger.error('data_sqlite/export_Current_page_tables/%s', str(ex))
            conn.close()
            return False, str(ex)

    def export_total_tables(self):
        '''
        获取所有在'report'表中 'is_delete' 为 1 的记录，并从 'medical_records' 表中附加相关数据。
        '''
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            result = []

            # 使用 LEFT JOIN 将 report 表和 medical_records 表合并
            sql = '''
                SELECT 
                    m.phone, m.name, m.grade, m.class, m.sex, m.age,
                    r.anxiety_score, r.anxiety_result, r.depressed_score, r.depressed_result,
                    r.count, r.createtime
                FROM report r
                LEFT JOIN medical_records m ON r.phone = m.phone
                WHERE r.is_delete = 1
                ORDER BY r.id DESC;
            '''

            cursor.execute(sql)
            rows = cursor.fetchall()

            for row in rows:
                # 将结果中的字段按需要的顺序排列
                combined_list = list(row)
                combined_list = ["" if x is None else x for x in combined_list]

                result.append(combined_list)


            conn.close()
            return True, result

        except Exception as ex:
            err_info = str(ex)
            conn.close()
            return False, err_info

    def get_abnormal_count_page(self, phone, name, time, time_suffix, grade, Class, level,page_count):
        '''获取符合条件的总记录数'''
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # CTE 找到至少有3条符合条件的记录的手机号
            qualified_phones_cte = '''
                WITH QualifiedPhones AS (
                    SELECT phone
                    FROM report
                    WHERE is_delete = 1 AND (anxiety_score >= 50 OR depressed_score >= 50)
                    GROUP BY phone
                    HAVING COUNT(*) >= 3
                )
            '''

            # 构建用于计数的查询语句
            query_base = f'''
                {qualified_phones_cte}
                SELECT 
                    COUNT(*)
                FROM 
                    report r
                LEFT JOIN 
                    medical_records mr ON r.phone = mr.phone
                WHERE 
                    r.is_delete = ?
                    AND r.phone IN (SELECT phone FROM QualifiedPhones)
                    AND (r.anxiety_score >= 50 OR r.depressed_score >= 50)
            '''

            params = [1]

            # 动态条件
            if phone:
                query_base += ' AND r.phone LIKE ?'
                params.append(phone + '%')
            if name:
                query_base += ' AND r.name LIKE ?'
                params.append('%' + name + '%')
            if grade:
                query_base += ' AND mr.grade = ?'
                params.append(grade)
            if Class:
                query_base += ' AND mr.class = ?'
                params.append(Class)
            if time and time_suffix:
                query_base += ' AND r.createtime BETWEEN ? AND ?'
                time_prefix_full = f"{time} 00:00:00"
                time_suffix_full = f"{time_suffix} 23:59:59"
                params.extend([time_prefix_full, time_suffix_full])

            level_conditions = []
            if level:
                level_conditions.append('r.anxiety_result = ?')
                params.append(level)
                level_conditions.append('r.depressed_result = ?')
                params.append(level)

            if level_conditions:
                query_base += ' AND (' + ' OR '.join(level_conditions) + ')'

            # 执行查询获取总记录数
            cursor.execute(query_base, params)
            total_records = cursor.fetchone()[0]
            # 计算总页数

            total_page = (total_records + page_count - 1) // page_count


            return True, total_page, total_records

        except Exception as e:
            print(f"An error occurred: {e}")
            return False, 0
        finally:
            conn.close()


    def get_abnormal_data(self,page_count, current_page, phone=None, name=None, time=None, grade=None, Class=None,
                            level=None,time_suffix=None,export=False):
        '''获取所有异常的检测报告'''

        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # CTE to find phones with at least 3 qualifying records
            qualified_phones_cte = '''
                WITH QualifiedPhones AS (
                    SELECT phone
                    FROM report
                    WHERE is_delete = 1 AND (anxiety_score >= 50 OR depressed_score >= 50)
                    GROUP BY phone
                    HAVING COUNT(*) >= 3
                )
            '''

            # Main query to fetch all qualifying records for these phones
            query_base = f'''
                {qualified_phones_cte}
                SELECT 
                    r.phone, r.name, r.anxiety_score, r.depressed_score, r.anxiety_result, r.depressed_result, 
                    r.createtime, r.count, r.save_path, r.save_path_s, 
                    mr.sex, mr.age, mr.grade, mr.class
                FROM 
                    report r
                INNER JOIN 
                    medical_records mr ON r.phone = mr.phone
                WHERE 
                    r.is_delete = ?
                    AND r.phone IN (SELECT phone FROM QualifiedPhones)
                    AND (r.anxiety_score >= 50 OR r.depressed_score >= 50)
            '''

            params = [1]

            # Dynamic conditions
            if phone:
                query_base += ' AND r.phone LIKE ?'
                params.append(phone + '%')
            if name:
                query_base += ' AND r.name LIKE ?'
                params.append('%' + name + '%')
            if grade:
                query_base += ' AND mr.grade = ?'
                params.append(grade)
            if Class:
                query_base += ' AND mr.class = ?'
                params.append(Class)
            if time and time_suffix:
                query_base += ' AND r.createtime BETWEEN ? AND ?'
                time_prefix_full = f"{time} 00:00:00"
                time_suffix_full = f"{time_suffix} 23:59:59"
                params.extend([time_prefix_full, time_suffix_full])

            level_conditions = []
            if level:
                level_conditions.append('r.anxiety_result = ?')
                params.append(level)
                level_conditions.append('r.depressed_result = ?')
                params.append(level)

            if level_conditions:
                query_base += ' AND (' + ' OR '.join(level_conditions) + ')'

            if export:
                query_base += ' ORDER BY r.id DESC'
            else:
                query_base += ' ORDER BY r.id DESC LIMIT ?, ?'
                params.extend([page_count * current_page - page_count, page_count])

            res = cursor.execute(query_base, params)
            res_list = []

            for row in res:
                res_dict = {
                    'phone': row[0],
                    'name': row[1],
                    'anxiety_score': row[2],
                    'depressed_score': row[3],
                    'anxiety_result': row[4],
                    'depressed_result': row[5],
                    'createtime': row[6],
                    'count': row[7],
                    'save_path': row[8],
                    'save_path_s': row[9],
                    'sex': row[10] if row[10] else "",
                    'age': row[11] if row[11] else "",
                    'grade': row[12] if row[12] else grade,
                    'class': row[13] if row[13] else Class
                }
                res_list.append(res_dict)

            return True, res_list

        except Exception as e:
            print(f"An error occurred: {e}")
            return False, []
        finally:
            conn.close()

    #总检测人数
    def totle_check_people(self,school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询
            sql = """
                    SELECT 
                        COUNT(DISTINCT r.phone) AS total_people,
                        COUNT(DISTINCT CASE WHEN m.sex = '男' THEN r.phone END) AS male_total,
                        COUNT(DISTINCT CASE WHEN m.sex = '女' THEN r.phone END) AS female_total
                    FROM (
                        SELECT * FROM report 
                        WHERE id IN (
                            SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                        ) 
                        ORDER BY id DESC
                    ) r
                    INNER JOIN medical_records m 
                    ON r.phone = m.phone
                    WHERE 1=1
                  """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果
            total_people = result[0]  # 总人数
            male_total = result[1]  # 男性人数
            female_total = result[2]  # 女性人数

            conn.close()

            return True, {"total_people": total_people, "male_total": male_total, "female_total": female_total}

        except Exception as ex:
            err_info = str(ex)
            print("totle_check_people",ex)
            return False, err_info

    #正常人数
    def is_normal_people(self,school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询
            sql = """
                        SELECT 
                            COUNT(DISTINCT CASE WHEN r.anxiety_result = '正常' AND r.depressed_result = '正常' THEN r.phone END) AS normal_total,
                            COUNT(DISTINCT CASE WHEN r.anxiety_result = '正常' AND r.depressed_result = '正常' AND m.sex = '男' THEN r.phone END) AS male_normal_total,
                            COUNT(DISTINCT CASE WHEN r.anxiety_result = '正常' AND r.depressed_result = '正常' AND m.sex = '女' THEN r.phone END) AS female_normal_total
                        FROM (
                            SELECT * FROM report 
                            WHERE id IN (
                                SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                            ) 
                            ORDER BY id DESC
                        ) r
                        INNER JOIN medical_records m 
                        ON r.phone = m.phone
                        WHERE 1=1
                      """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果

            normal_total = result[0]  # 正常人数
            male_normal_total = result[1]  # 男性正常人数
            female_normal_total = result[2]  # 女性正常人数

            conn.close()

            return True, {
                "normal_total": normal_total,
                "male_normal_total": male_normal_total,
                "female_normal_total": female_normal_total
            }

        except Exception as ex:
            err_info = str(ex)
            logger.error('is_normal_people', err_info)
            return False, err_info

    #抑郁人数
    def is_depressed_people(self,school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询
            sql = """
                    SELECT 
                        COUNT(DISTINCT CASE WHEN r.depressed_result != '正常' THEN r.phone END) AS depressed_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result != '正常' AND m.sex = '男' THEN r.phone END) AS male_depressed_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result != '正常' AND m.sex = '女' THEN r.phone END) AS female_depressed_total
                    FROM (
                        SELECT * FROM report 
                        WHERE id IN (
                            SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                        ) 
                        ORDER BY id DESC
                    ) r
                    INNER JOIN medical_records m 
                    ON r.phone = m.phone
                    WHERE 1=1
                  """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果
            depressed_total = result[0]  # 抑郁总人数
            male_depressed_total = result[1]  # 男性抑郁人数
            female_depressed_total = result[2]  # 女性抑郁人数

            return True, {
                "depressed_total": depressed_total,
                "male_depressed_total": male_depressed_total,
                "female_depressed_total": female_depressed_total
            }

        except Exception as ex:
            err_info = str(ex)
            logger.error('is_depressed_people', err_info)
            return False, err_info

        finally:
            conn.close()

    #焦虑人数
    def is_anxiety_people(self,school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询
            sql = """
                    SELECT 
                        COUNT(DISTINCT CASE WHEN r.anxiety_result != '正常' THEN r.phone END) AS anxious_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result != '正常' AND m.sex = '男' THEN r.phone END) AS male_anxious_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result != '正常' AND m.sex = '女' THEN r.phone END) AS female_anxious_total
                    FROM (
                        SELECT * FROM report 
                        WHERE id IN (
                            SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                        ) 
                        ORDER BY id DESC
                    ) r
                    INNER JOIN medical_records m 
                    ON r.phone = m.phone
                    WHERE 1=1
                  """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果
            anxiety_total = result[0]  # 焦虑总人数
            male_anxiety_total = result[1]  # 男性焦虑人数
            female_anxiety_total = result[2]  # 女性焦虑人数

            return True, {
                "anxiety_total": anxiety_total,
                "male_anxiety_total": male_anxiety_total,
                "female_anxiety_total": female_anxiety_total
            }


        except Exception as ex:
            err_info = str(ex)
            logger.error('data_sqlite/get_anxious_result/%s', err_info)
            return False, err_info

        finally:
            conn.close()

    #抑郁焦虑共病
    def is_anxiety_depression_comorbidity_people(self,school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询
            sql = """
                    SELECT 
                        COUNT(DISTINCT CASE WHEN r.anxiety_result != '正常' AND r.depressed_result != '正常' THEN r.phone END) AS comorbidity_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result != '正常' AND r.depressed_result != '正常' AND m.sex = '男' THEN r.phone END) AS male_comorbidity_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result != '正常' AND r.depressed_result != '正常' AND m.sex = '女' THEN r.phone END) AS female_comorbidity_total
                    FROM (
                        SELECT * FROM report 
                        WHERE id IN (
                            SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                        ) 
                        ORDER BY id DESC
                    ) r
                    INNER JOIN medical_records m 
                    ON r.phone = m.phone
                    WHERE 1=1
                  """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果
            comorbidity_total = result[0]  # 焦虑抑郁共病总人数
            male_comorbidity_total = result[1]  # 男性焦虑抑郁共病人数
            female_comorbidity_total = result[2]  # 女性焦虑抑郁共病人数

            return True, {
                "comorbidity_total": comorbidity_total,
                "male_comorbidity_total": male_comorbidity_total,
                "female_comorbidity_total": female_comorbidity_total
            }

        except Exception as ex:
            err_info = str(ex)
            logger.error('data_sqlite/get_anxiety_depression_comorbidity_result/%s', err_info)
            return False, err_info

        finally:
            conn.close()

    #焦虑轻 中 重 人数
    def is_anxiety_statistics(self, school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询，统计不同焦虑程度的人数，以及按性别分类
            sql = """
                    SELECT 
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' THEN r.phone END) AS mild_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' THEN r.phone END) AS moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' THEN r.phone END) AS severe_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND m.sex = '男' THEN r.phone END) AS male_mild_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND m.sex = '男' THEN r.phone END) AS male_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND m.sex = '男' THEN r.phone END) AS male_severe_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND m.sex = '女' THEN r.phone END) AS female_mild_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND m.sex = '女' THEN r.phone END) AS female_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND m.sex = '女' THEN r.phone END) AS female_severe_total
                    FROM (
                        SELECT * FROM report 
                        WHERE id IN (
                            SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                        ) 
                        ORDER BY id DESC
                    ) r
                    INNER JOIN medical_records m 
                    ON r.phone = m.phone
                    WHERE 1=1
                  """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果
            anxiety_statistics = {
                "mild_total": result[0],  # 轻度焦虑总人数
                "moderate_total": result[1],  # 中度焦虑总人数
                "severe_total": result[2],  # 重度焦虑总人数

                "male_mild_total": result[3],  # 男性轻度焦虑人数
                "male_moderate_total": result[4],  # 男性中度焦虑人数
                "male_severe_total": result[5],  # 男性重度焦虑人数

                "female_mild_total": result[6],  # 女性轻度焦虑人数
                "female_moderate_total": result[7],  # 女性中度焦虑人数
                "female_severe_total": result[8]  # 女性重度焦虑人数
            }

            return True, anxiety_statistics

        except Exception as ex:
            err_info = str(ex)
            logger.error('data_sqlite/get_anxiety_statistics/%s', err_info)
            return False, err_info

        finally:
            conn.close()

    #抑郁 轻 中 重
    def is_depression_statistics(self, school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询，统计不同抑郁程度的人数，以及按性别分类
            sql = """
                    SELECT 
                        COUNT(DISTINCT CASE WHEN r.depressed_result = '轻度' THEN r.phone END) AS mild_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result = '中度' THEN r.phone END) AS moderate_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result = '重度' THEN r.phone END) AS severe_total,

                        COUNT(DISTINCT CASE WHEN r.depressed_result = '轻度' AND m.sex = '男' THEN r.phone END) AS male_mild_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result = '中度' AND m.sex = '男' THEN r.phone END) AS male_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result = '重度' AND m.sex = '男' THEN r.phone END) AS male_severe_total,

                        COUNT(DISTINCT CASE WHEN r.depressed_result = '轻度' AND m.sex = '女' THEN r.phone END) AS female_mild_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result = '中度' AND m.sex = '女' THEN r.phone END) AS female_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.depressed_result = '重度' AND m.sex = '女' THEN r.phone END) AS female_severe_total
                    FROM (
                        SELECT * FROM report 
                        WHERE id IN (
                            SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                        ) 
                        ORDER BY id DESC
                    ) r
                    INNER JOIN medical_records m 
                    ON r.phone = m.phone
                    WHERE 1=1
                  """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果
            depression_statistics = {
                "mild_total": result[0],  # 轻度抑郁总人数
                "moderate_total": result[1],  # 中度抑郁总人数
                "severe_total": result[2],  # 重度抑郁总人数

                "male_mild_total": result[3],  # 男性轻度抑郁人数
                "male_moderate_total": result[4],  # 男性中度抑郁人数
                "male_severe_total": result[5],  # 男性重度抑郁人数

                "female_mild_total": result[6],  # 女性轻度抑郁人数
                "female_moderate_total": result[7],  # 女性中度抑郁人数
                "female_severe_total": result[8]  # 女性重度抑郁人数
            }

            return True, depression_statistics

        except Exception as ex:
            err_info = str(ex)
            logger.error('data_sqlite/get_depression_statistics/%s', err_info)
            return False, err_info

        finally:
            conn.close()

    #共病种类  轻 中 重
    def is_anxiety_depression_statistics(self, school=None, grade=None,Class=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 基础SQL查询，统计不同焦虑和抑郁组合的人数，并按性别分类
            sql = """
                    SELECT 
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '轻度' THEN r.phone END) AS mild_light_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '轻度' THEN r.phone END) AS moderate_light_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '轻度' THEN r.phone END) AS severe_light_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '中度' THEN r.phone END) AS mild_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '中度' THEN r.phone END) AS moderate_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '中度' THEN r.phone END) AS severe_moderate_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '重度' THEN r.phone END) AS mild_severe_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '重度' THEN r.phone END) AS moderate_severe_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '重度' THEN r.phone END) AS severe_severe_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '轻度' AND m.sex = '男' THEN r.phone END) AS male_mild_light_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '轻度' AND m.sex = '男' THEN r.phone END) AS male_moderate_light_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '轻度' AND m.sex = '男' THEN r.phone END) AS male_severe_light_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '中度' AND m.sex = '男' THEN r.phone END) AS male_mild_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '中度' AND m.sex = '男' THEN r.phone END) AS male_moderate_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '中度' AND m.sex = '男' THEN r.phone END) AS male_severe_moderate_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '重度' AND m.sex = '男' THEN r.phone END) AS male_mild_severe_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '重度' AND m.sex = '男' THEN r.phone END) AS male_moderate_severe_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '重度' AND m.sex = '男' THEN r.phone END) AS male_severe_severe_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '轻度' AND m.sex = '女' THEN r.phone END) AS female_mild_light_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '轻度' AND m.sex = '女' THEN r.phone END) AS female_moderate_light_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '轻度' AND m.sex = '女' THEN r.phone END) AS female_severe_light_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '中度' AND m.sex = '女' THEN r.phone END) AS female_mild_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '中度' AND m.sex = '女' THEN r.phone END) AS female_moderate_moderate_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '中度' AND m.sex = '女' THEN r.phone END) AS female_severe_moderate_total,

                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '轻度' AND r.depressed_result = '重度' AND m.sex = '女' THEN r.phone END) AS female_mild_severe_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '中度' AND r.depressed_result = '重度' AND m.sex = '女' THEN r.phone END) AS female_moderate_severe_total,
                        COUNT(DISTINCT CASE WHEN r.anxiety_result = '重度' AND r.depressed_result = '重度' AND m.sex = '女' THEN r.phone END) AS female_severe_severe_total
                    FROM (
                        SELECT * FROM report 
                        WHERE id IN (
                            SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone
                        ) 
                        ORDER BY id DESC
                    ) r
                    INNER JOIN medical_records m 
                    ON r.phone = m.phone
                    WHERE 1=1
                  """

            # 动态添加条件
            params = []
            if school:
                sql += " AND m.school = ?"
                params.append(school)
            if grade:
                sql += " AND m.grade = ?"
                params.append(grade)
            if Class:
                sql += " AND m.class = ?"
                params.append(Class)

            # 执行查询
            res = cursor.execute(sql, params)
            result = cursor.fetchone()  # 获取一条记录

            # 解析结果
            statistics = {
                "mild_light_total": result[0],  # 轻抑轻焦总人数
                "moderate_light_total": result[1],  # 轻抑中焦总人数
                "severe_light_total": result[2],  # 轻抑重焦总人数

                "mild_moderate_total": result[3],  # 中抑轻焦总人数
                "moderate_moderate_total": result[4],  # 中抑中焦总人数
                "severe_moderate_total": result[5],  # 中抑重焦总人数

                "mild_severe_total": result[6],  # 重抑轻焦总人数
                "moderate_severe_total": result[7],  # 重抑中焦总人数
                "severe_severe_total": result[8],  # 重抑重焦总人数

                "male_mild_light_total": result[9],  # 男性轻抑轻焦总人数
                "male_moderate_light_total": result[10],  # 男性轻抑中焦总人数
                "male_severe_light_total": result[11],  # 男性轻抑重焦总人数

                "male_mild_moderate_total": result[12],  # 男性中抑轻焦总人数
                "male_moderate_moderate_total": result[13],  # 男性中抑中焦总人数
                "male_severe_moderate_total": result[14],  # 男性中抑重焦总人数

                "male_mild_severe_total": result[15],  # 男性重抑轻焦总人数
                "male_moderate_severe_total": result[16],  # 男性重抑中焦总人数
                "male_severe_severe_total": result[17],  # 男性重抑重焦总人数

                "female_mild_light_total": result[18],  # 女性轻抑轻焦总人数
                "female_moderate_light_total": result[19],  # 女性轻抑中焦总人数
                "female_severe_light_total": result[20],  # 女性轻抑重焦总人数

                "female_mild_moderate_total": result[21],  # 女性中抑轻焦总人数
                "female_moderate_moderate_total": result[22],  # 女性中抑中焦总人数
                "female_severe_moderate_total": result[23],  # 女性中抑重焦总人数

                "female_mild_severe_total": result[24],  # 女性重抑轻焦总人数
                "female_moderate_severe_total": result[25],  # 女性重抑中焦总人数
                "female_severe_severe_total": result[26]  # 女性重抑重焦总人数
            }

            return True,statistics

        finally:
            conn.close()

    def get_anxiety_depressed_result(self):
        '''
           数据分析焦虑和抑郁的数据结果
        '''
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            result = []
            sql = f'SELECT * FROM report WHERE id IN (SELECT MAX(id) FROM report WHERE is_delete = 1 GROUP BY phone) order BY id DESC;'
            res = cursor.execute(sql)
            for i in res:
                res_dict = {}  # 单个检材信息
                res_dict['phone'] = i[1]
                res_dict['anxiety_score'] = i[3]
                res_dict["depressed_score"] = i[4]
                result.append(res_dict)

            index_list = []
            for item in range(0, len(result)):
                if result[item]["phone"] is not None:
                    sql = f'SELECT * FROM medical_records where phone="{result[item]["phone"]}";'
                elif result[item]["phone"] is None:
                    sql = f'SELECT * FROM medical_records WHERE phone IS NULL;'

                res = cursor.execute(sql)
                flag = False
                for i in res:
                    flag = True
                    break
                if not flag:
                    index_list.append(result[item])

            for i in index_list:
                result.remove(i)
            conn.close()
            return True, result


        except Exception as ex:
            err_info = str(ex)
            logger.error('data_sqlite/get_anxiety_depressed_result/%s', str(ex))
            conn.close()
            return False, err_info

    def update_medical_records(self,phone,is_active):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        sql_select = "SELECT COUNT(*) FROM medical_records WHERE phone = ?"
        cursor.execute(sql_select, (phone,))

        result = cursor.fetchone()[0]
        if result > 0:
            sql_update = '''UPDATE medical_records
                                        SET is_active=?
                                        WHERE phone=?'''
            cursor.execute(sql_update, (is_active,phone,))

        conn.commit()
        conn.close()
        return True

    def insert_medical_records(self,phone,name,sex,age,school,grade,Class,is_active):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            sql_select = "SELECT COUNT(*) FROM medical_records WHERE phone = ?"
            cursor.execute(sql_select, (phone,))

            result = cursor.fetchone()[0]
            if result > 0:
                sql_select = "SELECT COUNT(*) FROM medical_records WHERE phone = ? and name=?"
                cursor.execute(sql_select, (phone,name))

                result_1 = cursor.fetchone()[0]
                if result_1>0:
                    sql_update = '''UPDATE medical_records
                                                        SET age=?
                                                        WHERE phone=?'''
                else:
                    return False,"该学号已存在,请重新输入"

                cursor.execute(sql_update, (age, phone,))
            else:
                sql_insert = '''INSERT INTO medical_records (phone, name, sex, age, school, grade, class,is_active) 
                                VALUES (?, ?, ?, ?, ?, ?, ?,?)'''
                cursor.execute(sql_insert, (phone, name, sex, age, school, grade, Class,is_active))
            conn.commit()
            conn.close()
            return True,""
        except sqlite3.Error as e:
            logger.error('%s', str(e))
            return False,""

    def insert_localAnaly_records(self,depressed_score,anxiety_score,phone,name,count,csv_file,csv_file_s,com_name=None):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        sql_select = "SELECT * FROM report WHERE phone = ? AND name = ? AND count = ? AND is_delete=?"
        cursor.execute(sql_select, (phone, name, count,1))
        result = cursor.fetchone()

        if -1 <= depressed_score <50:
            depressed_result = "正常"
        elif 50 <= depressed_score <65:
            depressed_result = "轻度"
        elif 65 <= depressed_score <75:
            depressed_result = "中度"
        elif 75 <= depressed_score <= 100:
            depressed_result = "重度"
        else:
            depressed_result = "正常"

        if -1 <= anxiety_score <50:
            anxiety_result = "正常"
        elif 50 <= anxiety_score <65:
            anxiety_result = "轻度"
        elif 65 <= anxiety_score <75:
            anxiety_result = "中度"
        elif 75 <= anxiety_score <= 100:
            anxiety_result = "重度"
        else:
            anxiety_result = "正常"
        # 确认查询结果是否存在
        if result:
            conn.close()
            return False

        # 获取当前时间
        createtime = datetime.now()

        # # Adding one year using timedelta (considering leap year possibility)
        # next_year_time = createtime.replace(year=createtime.year + 1)

        # Formatting as string
        createtime =  createtime.strftime("%Y-%m-%d %H:%M:%S")

        is_delete = 1
        is_localAnaly = 1
        cursor.execute(
            "INSERT INTO report (phone,name,count,depressed_score,depressed_result,anxiety_score, anxiety_result,createtime,is_delete,is_localAnaly,com,save_path,save_path_s) VALUES "
            "(?,?,?, ?, ?, ?,?, ?,?,?,?,?,?)",
            (phone,name, count, depressed_score, depressed_result,anxiety_score, anxiety_result, createtime, is_delete, is_localAnaly,com_name,csv_file,csv_file_s
             ))
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        return True

    def get_user_count_page(self,page_count,school,name,phone,grade,Class,check):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        # 构建基础查询语句
        if school != "请选择":
            query_base = "SELECT COUNT(*) FROM medical_records WHERE school = ?"
            params = [school]
        else:
            query_base = "SELECT COUNT(*) FROM medical_records WHERE 1 = ?"
            params = [1]

        # 动态添加其他条件
        if phone:
            query_base += ' AND phone LIKE ?'
            params.append(phone + '%')
        if name:
            query_base += ' AND name LIKE ?'
            params.append('%' + name + '%')
        if grade:
            query_base += ' AND grade LIKE ?'
            params.append('%' + grade + '%')
        if Class:
            query_base += ' AND class LIKE ?'
            params.append('%' + Class + '%')
        if check==0 or check==1:
            query_base += ' AND is_active = ?'
            params.append(check)
        # 执行查询
        cursor.execute(query_base, params)
        count = cursor.fetchone()[0]


        # 计算总页数
        total_page = (count + page_count - 1) // page_count

        cursor.close()
        conn.close()
        return True, total_page,count
        # 关闭连接


    def get_count_page(self,phone,name,time,time_suffix,grade,Class,level,page_count):

        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # 构建基础查询语句
            query_base = '''
                    SELECT COUNT(*)
                    FROM report r
                    INNER JOIN medical_records m ON r.phone = m.phone
                    WHERE r.is_delete = 1
                '''
            params = []

            # 动态添加 report 表的查询条件
            if phone:
                query_base += ' AND r.phone LIKE ?'
                params.append(phone + '%')
            if name:
                query_base += ' AND r.name LIKE ?'
                params.append('%' + name + '%')
            if time:
                query_base += ' AND r.createtime LIKE ?'
                params.append(time + '%')

            # 添加 level 的条件（如果有）
            if level:
                query_base += ' AND (r.anxiety_result = ? OR r.depressed_result = ?)'
                params.extend([level, level])

            # 添加 medical_records 表的查询条件
            if grade:
                query_base += ' AND m.grade = ?'
                params.append(grade)
            if Class:
                query_base += ' AND m.class = ?'
                params.append(Class)

            if time and time_suffix:
                query_base += ' AND r.createtime BETWEEN ? AND ?'
                time_prefix_full = f"{time} 00:00:00"
                time_suffix_full = f"{time_suffix} 23:59:59"
                params.extend([time_prefix_full, time_suffix_full])
            # 获取总记录数
            cursor.execute(query_base, params)
            total_records = cursor.fetchone()[0]

            # 计算总页数
            total_page = (total_records + page_count - 1) // page_count
            if total_page==0:
                total_page =1
            return True, total_page,total_records


        except sqlite3.Error as e:
            logger.error('data_sqlite/get_count_page/%s', str(e))
            conn.close()
            return False, e,0

    def get_page_user_count_data(self,page_count, current_page, school,phone=None,name=None,grade=None,Class=None,check=None):
        conn = sqlite3.connect(self.database_path)
        '''获取所有用户的检测情况'''
        try:
            cursor = conn.cursor()

            # 基础查询语句，从 medical_records 表中选择所有字段
            query_base = 'SELECT * FROM medical_records WHERE 1=1'
            params = []

            # 如果 school 不是 "请选择"，添加学校条件
            if school != "请选择":
                query_base += ' AND school = ?'
                params.append(school)

            # 动态添加条件
            if phone:
                query_base += ' AND phone LIKE ?'
                params.append(phone + '%')
            if name:
                query_base += ' AND name LIKE ?'
                params.append('%' + name + '%')
            if grade:
                query_base += ' AND grade LIKE ?'
                params.append('%' + grade + '%')
            if Class:
                query_base += ' AND Class LIKE ?'
                params.append('%' + Class + '%')
            if check==1 or check==0:
                query_base += ' AND is_active = ?'
                params.append(check)
            # 执行查询

            query_base += ' ORDER BY id DESC LIMIT ?, ?'
            params.extend([page_count * current_page - page_count, page_count])

            res = cursor.execute(query_base, params)

            res_list = []

            for row in res:
                res_dict = {
                    'phone': row[1],
                    'name': row[2],
                    'sex': row[3],
                    'age': row[4],
                    'school': row[5],
                    'grade': row[6],
                    'class': row[7],
                    'is_active': row[8],
                }
                res_list.append(res_dict)
            return True, res_list
        except Exception as ex:
            logger.error('data_sqlite/get_page_user_count_data/%s', str(ex))
            return False, ""
        finally:
            conn.close()

    def get_page_count_data(self, page_count, current_page, phone=None, name=None, time=None, grade=None, Class=None,
                            level=None,time_suffix=None):
        """
        Retrieves paginated report data with additional information from the medical_records table.
        Only includes records where matching phone values are found in both tables.
        """
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            # Base query using INNER JOIN
            query_base = '''
                SELECT 
                    r.phone, r.name, r.anxiety_score, r.depressed_score, r.anxiety_result, r.depressed_result, 
                    r.createtime, r.count, r.save_path, r.save_path_s, 
                    mr.sex, mr.age, mr.grade, mr.class
                FROM 
                    report r
                INNER JOIN 
                    medical_records mr ON r.phone = mr.phone
                WHERE 
                    r.is_delete = ?
            '''
            params = [1]

            # Dynamic conditions
            if phone:
                query_base += ' AND r.phone LIKE ?'
                params.append(phone + '%')
            if name:
                query_base += ' AND r.name LIKE ?'
                params.append('%' + name + '%')
            if grade:
                query_base += ' AND mr.grade = ?'
                params.append(grade)
            if Class:
                query_base += ' AND mr.class = ?'
                params.append(Class)

            if time and time_suffix:
                query_base += ' AND r.createtime BETWEEN ? AND ?'
                time_prefix_full = f"{time} 00:00:00"
                time_suffix_full = f"{time_suffix} 23:59:59"
                params.extend([time_prefix_full, time_suffix_full])

            # Level conditions (for anxiety_result and depressed_result)
            level_conditions = []
            if level:
                level_conditions.append('r.anxiety_result = ?')
                params.append(level)
                level_conditions.append('r.depressed_result = ?')
                params.append(level)

            if level_conditions:
                query_base += ' AND (' + ' OR '.join(level_conditions) + ')'

            query_base += ' ORDER BY r.id DESC LIMIT ?, ?'
            params.extend([page_count * current_page - page_count, page_count])

            # Execute query
            res = cursor.execute(query_base, params)
            res_list = []

            for row in res:
                res_dict = {
                    'phone': row[0],
                    'name': row[1],
                    'anxiety_score': row[2],
                    'depressed_score': row[3],
                    'anxiety_result': row[4],
                    'depressed_result': row[5],
                    'createtime': row[6],
                    'count': row[7],
                    'save_path': row[8],
                    'save_path_s': row[9],
                    'sex': row[10] if row[10] else "",
                    'age': row[11] if row[11] else "",
                    'grade': row[12] if row[12] else grade,
                    'class': row[13] if row[13] else Class
                }
                res_list.append(res_dict)
            return True, res_list

        except Exception as e:
            print(f"An error occurred: {e}")
            return False, []
        finally:
            conn.close()

    def delete_medical_data(self, phone,count,time):
        '''
        假删,删除患者
        '''
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            if time is None:
                sql = f'UPDATE report SET is_delete = 0 WHERE createtime is NULL and phone="{phone}";'
            else:
                sql = f'UPDATE report SET is_delete = 0 WHERE createtime="{time}" and phone="{phone}";'
            cursor = cursor.execute(sql)
            conn.commit()
            conn.close()
            return True
        except Exception as ex:
            logger.error('data_sqlite/get_page_count_data/%s', str(ex))
            conn.close()
            return False

    def query_phone_name_count_exist(self,phone,name,sex,age):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            # sql = 'SELECT * FROM report WHERE is_delete = ? and phone=? and name=? and count=?;'
            # cursor.execute(sql, (1,phone,name,count))
            # res = cursor.fetchone()
            #
            # if res is None:
            #     insert_sql = 'INSERT INTO report (phone, name, count, is_delete) VALUES (?, ?, ?, ?);'
            #     cursor.execute(insert_sql, (phone, name, count, 1))


            sql = 'SELECT * FROM medical_records WHERE phone=? and name=?;'
            cursor.execute(sql, (phone, name,))
            res = cursor.fetchone()
            if res is None:
                insert_sql = 'INSERT INTO medical_records (phone, name,sex,age,school) VALUES (?, ?,?,?,?);'
                cursor.execute(insert_sql, (phone, name,"","",""))

            conn.commit()
            conn.close()
        except Exception as ex:
            logger.error('data_sqlite/query_phone_name_count_exist/%s', str(ex))

    def get_report_tab_data(self, phone, count=None):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            if count is not None:  # 1 2
                sql = 'SELECT * FROM report WHERE is_delete = ? and phone = ? and count = ?;'
                res = cursor.execute(sql, (1, phone, count))
            else:
                sql = 'SELECT * FROM report WHERE is_delete = ? and phone = ?;'
                res = cursor.execute(sql, (1, phone))


            res_list=[]
            for row in res:
                res_dict = {}  # 单个检材信息
                res_dict['phone'] = row[1]
                res_dict['name'] = row[2]
                res_dict['anxiety_score'] = row[3]
                res_dict["depressed_score"] = row[4]
                res_dict['anxiety_result'] = row[5]
                res_dict['depressed_result'] = row[6]
                res_dict['createtime'] = row[8]
                res_dict['count'] = row[7]
                res_dict['com'] = row[11]
                res_dict['save_path'] = row[12]
                res_dict['save_path_s'] = row[13]
                res_list.append(res_dict)


            for i in range(0, len(res_list)):
                if res_list[i]['phone'] is not None:
                    sql = f'SELECT * FROM medical_records where phone="{res_list[i]["phone"]}";'
                elif res_list[i]['phone'] is None:
                    sql = f'SELECT * FROM medical_records WHERE phone IS NULL;'
                res = cursor.execute(sql)
                if res:
                    for row in res:
                        res_list[i]['sex'] = row[3]
                        res_list[i]['age'] = row[4]
                        res_list[i]['school'] = row[5]
                        res_list[i]['grade'] = row[6]
                        res_list[i]['class'] = row[7]
                        break
            return True, res_list

        except Exception as ex:
            logger.error('data_sqlite/get_report_tab_data/%s', str(ex))
            return False, ""
        finally:
            conn.close()

    def insert_csv(self, file_name, file_path):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # sql_select = "SELECT COUNT(*) FROM add_csv_path WHERE csv_name = ?"
            # cursor.execute(sql_select, (file_name,))
            #
            # result = cursor.fetchone()[0]
            # if result > 0:
            #     pass
            # else:

            sql_insert = '''INSERT INTO add_csv_path (csv_name, save_path) 
                            VALUES (?, ?)'''
            cursor.execute(sql_insert, (file_name, file_path))

            conn.commit()
            conn.close()
            return True
        except Exception as ex:
            logger.error('insert_csv：%s', str(ex))
            conn.close()
            return False


    def get_csv_data(self):
        """获取csv路径
        返回:
            列表嵌套字典
        """
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()

            sql = 'SELECT * FROM add_csv_path ORDER BY id DESC;'
            res = cursor.execute(sql)
            csv_list = []  # 当前案件对应的所有dbs

            for row in res:
                csv_info = {}  # 单个实例信息
                csv_info['csv_name'] = row[1]
                csv_info['save_path'] = row[2]

                csv_list.append(csv_info)
            return True, csv_list
        except Exception as ex:
            logger.error('data_sqlite/get_csv_data/%s', str(ex))
            return False, "查询系统数据库错误"
        finally:
            conn.close()

    def get_template_data(self):
        """获取模板
        返回:
            列表嵌套字典
        """
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            sql = f'select * from template where is_delete=1 order by school, grade, class;'
            res = cursor.execute(sql)
            template_list = []  # 当前案件对应的所有dbs
            for row in res:
                user_info = {}  # 单个实例信息
                user_info['school'] = row[1]
                user_info['grade'] = row[2]
                user_info['class'] = row[3]

                template_list.append(user_info)
            return True, template_list
        except Exception as ex:
            logger.error('data_sqlite/get_template_data/%s', str(ex))
            return False, "查询系统数据库错误"
        finally:
            conn.close()

    def create_template(self,school_text,grade_text,class_text):
        '''
        创建模板
        '''
        conn = sqlite3.connect(self.database_path)

        try:
            cursor = conn.cursor()

            # 添加之前先判断名称是否有重名的
            sql = f'SELECT * FROM template WHERE school = "{school_text}" and grade="{grade_text}" and class="{class_text}" and is_delete=1;'
            cursor.execute(sql)
            res = cursor.fetchone()
            if res:
                return False, "有重复名称"

            sql = f'''INSERT INTO template(school,grade,class,is_delete) VALUES("{school_text}",
                              "{grade_text}","{class_text}",1)'''
            cursor = cursor.execute(sql)
            conn.commit()
            conn.close()  # 最终关闭数据库连接
            return True, ""
        except Exception as ex:
            logger.error('data_sqlite/create_template/%s', str(ex))
            conn.close()
            return False, "添加失败"

    def update_template(self, school, school_text, grade, grade_text, Class, Class_text):
        '''
        修改模板
        '''
        conn = sqlite3.connect(self.database_path)

        try:
            cursor = conn.cursor()
            # 编辑病灶之前先判断名称是否有重名的

            sql = f'SELECT * FROM template WHERE school = "{school_text}" and grade="{grade_text}" and class="{Class_text}" and is_delete=1;'
            cursor.execute(sql)
            res = cursor.fetchone()
            if res:
                return False, "有重复名称"

            sql = f'UPDATE template SET school = "{school_text}",grade="{grade_text}",class="{Class_text}" WHERE school = "{school}" and grade ="{grade}" and class="{Class}" and is_delete=1;'
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return True, ""

        except Exception as ex:
            logger.error('data_sqlite/update_template/%s', str(ex))
            conn.close()
            return False, ""

    def delete_csv(self, save_path):
        '''
        假删csv文件，并删除信息录入表已经导入的数据
        '''
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            if os.path.exists(save_path):
                if save_path.endswith('.csv'):
                    df = pd.read_csv(save_path, header=None, usecols=[0, 1, 4, 5, 6])
                elif save_path.endswith('.xls') or save_path.endswith('.xlsx'):
                    engine = 'xlrd' if save_path.endswith('.xls') else 'openpyxl'
                    df = pd.read_excel(save_path, header=None, engine=engine, usecols=[0, 1, 4, 5, 6])
                else:
                    raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
                data_as_list = df.values.tolist()
            else:
                data_as_list = []

            # 删除 add_csv_path 表中的记录
            cursor.execute('DELETE FROM add_csv_path WHERE save_path = ?', (save_path,))
            print(data_as_list)
            # 遍历数据列表，删除 medical_records 表中的对应记录
            for i in data_as_list:
                if i[0] == "学号":  # 跳过表头
                    continue
                    # 假删 report 表中的记录

                cursor.execute("""
                            UPDATE report 
                            SET is_delete = 0 
                            WHERE phone IN (
                                SELECT phone FROM medical_records 
                                WHERE school = ? AND grade = ? AND class = ?)""", (i[2], i[3], i[4]))

                cursor.execute('DELETE FROM medical_records WHERE school = ? AND grade = ? AND class = ?',
                               (i[2], i[3], i[4]))
                cursor.execute('DELETE FROM template WHERE school = ? AND grade = ? AND class = ?', (i[2], i[3], i[4]))


                # cursor.execute('UPDATE report SET is_delete = 0 WHERE phone = ?', (i[0],))  # 修正参数数量

            conn.commit()
            conn.close()
            return True
        except Exception as ex:
            logger.error('data_sqlite/delete_csv/%s', str(ex))
            conn.close()
            return False

    def delete_template(self, school, grade, Class):
        '''
        假删模板
        '''
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # 假删 report 表中的记录
            cursor.execute("""
                                    UPDATE report 
                                    SET is_delete = 0 
                                    WHERE phone IN (
                                        SELECT phone FROM medical_records 
                                        WHERE school = ? AND grade = ? AND class = ?
                                    )
                                """, (school, grade, Class))

            # 更新 template 表
            cursor.execute("""
                UPDATE template 
                SET is_delete = 0 
                WHERE school = ? AND grade = ? AND class = ? AND is_delete = 1
            """, (school, grade, Class))

            # 删除 medical_records 中的数据
            cursor.execute("""
                DELETE FROM medical_records 
                WHERE school = ? AND grade = ? AND class = ?
            """, (school, grade, Class))

            conn.commit()
            return True
        except Exception as ex:
            logger.error('data_sqlite/delete_template/%s', str(ex))
            return False
        finally:
            # 确保在异常后关闭连接
            if conn:
                conn.close()

    def get_school_order_by(self):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            school_list = []
            sql = 'SELECT school FROM template WHERE is_delete = 1 GROUP BY school ORDER BY school DESC;'
            res = cursor.execute(sql)
            for row in res:
                school_list.append(row[0])

            # # 从 medical_records 表中获取 school 列的唯一值，并排除已经存在的学校
            # sql = 'SELECT school FROM medical_records GROUP BY school ORDER BY school DESC;'
            # res = cursor.execute(sql)
            # for row in res:
            #     if row[0] not in school_list:
            #         school_list.append(row[0])

            conn.commit()
            conn.close()
            return True,school_list
        except Exception as ex:
            logger.error('data_sqlite/get_school_order_by/%s', str(ex))
            conn.close()
            return False,""

    def get_grade_order_by(self, school):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            gtade_list = []

            query_base = '''
                                       SELECT grade FROM template WHERE is_delete = ?
                                   '''
            params = [1]
            if school:
                query_base += ' AND school = ?'
                params.append(school)

            query_base += ' GROUP BY grade ORDER BY grade DESC'
            res = cursor.execute(query_base, params)

            for row in res:
                gtade_list.append(row[0])


            conn.commit()
            conn.close()
            return True, gtade_list
        except Exception as ex:
            logger.error('data_sqlite/get_grade_order_by/%s', str(ex))
            conn.close()
            return False, ""

    def get_class_order_by(self,school,grade):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            class_list = []

            query_base = '''
                            SELECT class FROM template WHERE is_delete = ?
                        '''
            params = [1]
            if school:
                query_base += ' AND school = ?'
                params.append(school)

            if grade:
                query_base += ' AND grade = ?'
                params.append(grade)

            query_base += ' GROUP BY class ORDER BY class DESC'

            res = cursor.execute(query_base, params)

            for row in res:
                class_list.append(row[0])


            conn.commit()
            conn.close()
            return True, class_list
        except Exception as ex:
            logger.error('data_sqlite/get_class_order_by/%s', str(ex))
            conn.close()
            return False, ""

    def medical_records_phone_data_exists(self,phone):
        try:
            if not phone:
                return False
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            sql_select = "SELECT COUNT(*) FROM medical_records WHERE phone = ?"
            cursor.execute(sql_select, (phone,))
            result = cursor.fetchone()[0]
            conn.commit()
            conn.close()

            if result > 0:
                return True
            else:
                return False

        except Exception as ex:
            logger.error('data_sqlite/medical_records_phone_data_exists/%s', str(ex))
            conn.close()
            return False, ""



    def fuzzy_query_phone_data(self, text):
        '''
        模糊查询
        '''
        conn = sqlite3.connect(self.database_path)
        try:

            cursor = conn.cursor()
            edit_list = []
            cursor.execute(
                'SELECT phone FROM medical_records WHERE phone LIKE ?',
                ('%' + text + '%',))
            results = cursor.fetchall()
            for row in results:
                if text in row[0]:
                    edit_list.append(row[0])

            return True, edit_list

        except Exception as ex:
            err_info = str(ex)
            return False, err_info
        finally:
            conn.close()

    def search_anxiety_depressed_result(self,time_prefix,time_suffix,grade,Class):
        '''
           数据分析焦虑和抑郁的数据结果
        '''
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            result = []
            if time_prefix=="" and time_suffix=="":
                sql = f'select * from report WHERE is_delete = 1 order by id DESC;'
            else:
                time_prefix_full = f"{time_prefix} 00:00:00"
                time_suffix_full = f"{time_suffix} 23:59:59"

                sql = f'select * from report WHERE is_delete = 1 AND createtime BETWEEN "{time_prefix_full}" AND "{time_suffix_full}" order by id DESC;'

            res = cursor.execute(sql)
            phone="True"
            for i in res:
                res_dict = {}  # 单个检材信息
                if phone==i[1]:
                    continue
                res_dict['phone'] = i[1]
                phone=res_dict['phone']
                res_dict['anxiety_score'] = i[3]
                res_dict["depressed_score"] = i[4]
                result.append(res_dict)

            index_list=[]
            for item in range(0, len(result)):
                if result[item]["phone"] is not None:
                    if grade=="" and Class=="":
                        sql = f'SELECT * FROM medical_records where phone="{result[item]["phone"]}";'
                    elif grade!="" and Class=="":
                        sql = f'SELECT * FROM medical_records where phone="{result[item]["phone"]}" and grade="{grade}";'

                    elif grade!="" and Class!="":
                        sql = f'SELECT * FROM medical_records where phone="{result[item]["phone"]}" and grade="{grade}" and class="{Class}";'
                elif result[item]["phone"] is None:
                    if grade=="" and Class=="":
                        sql = f'SELECT * FROM medical_records WHERE phone IS NULL;'
                    elif grade!="" and Class == "":
                        sql = f'SELECT * FROM medical_records WHERE phone IS NULL and grade="{grade}";'
                    elif grade != "" and Class != "":
                        sql = f'SELECT * FROM medical_records WHERE phone IS NULL and grade="{grade}" and class="{Class}";'

                res = cursor.execute(sql)
                flag = False
                for i in res:
                    flag = True
                    break
                if not flag:
                    index_list.append(result[item])

            for i in index_list:
                result.remove(i)


            conn.close()
            return True, result

        except Exception as ex:
            err_info = str(ex)
            logger.error('data_sqlite/search_anxiety_depressed_result/%s', str(ex))
            conn.close()
            return False, err_info

    def get_medical_records_data(self,phone):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            # 参数化查询以防止SQL注入
            sql = 'SELECT * FROM medical_records WHERE name=?;'
            cursor.execute(sql, (phone,))
            results = cursor.fetchall()

            user_info = {}  # 单个实例信息

            for row in results:
                user_info['phone'] = row[1]
                user_info['name'] = row[2]
                user_info['sex'] = row[3]
                user_info['age'] = row[4]

                user_info['school'] = row[5]
                user_info['grade'] = row[6]
                user_info['class'] = row[7]
                break
            conn.close()
            return True,user_info
        except Exception as ex:
            logger.error('data_sqlite/get_medical_records_data/%s', str(ex))
            conn.close()
            return False,""

    def get_medical_records_phone_data(self, phone):
        conn = sqlite3.connect(self.database_path)
        try:
            cursor = conn.cursor()
            # 参数化查询以防止SQL注入
            sql = 'SELECT * FROM medical_records WHERE phone=?;'
            cursor.execute(sql, (phone,))
            results = cursor.fetchall()

            user_info = {}  # 单个实例信息

            for row in results:
                user_info['phone'] = row[1]
                user_info['name'] = row[2]
                user_info['sex'] = row[3]
                user_info['age'] = row[4]

                user_info['school'] = row[5]
                user_info['grade'] = row[6]
                user_info['class'] = row[7]
                break
            conn.close()
            return True, user_info
        except Exception as ex:
            logger.error('data_sqlite/get_medical_records_data/%s', str(ex))
            conn.close()
            return False, ""


    def get_report_count(self, phone):


        conn = sqlite3.connect(self.database_path)
        try:

            cursor = conn.cursor()
            # 参数化查询以防止SQL注入
            sql = 'SELECT count FROM report WHERE phone=? AND is_delete=? ORDER BY id DESC LIMIT 1;'
            cursor.execute(sql, (phone,1,))

            # 获取最新的一条结果
            row = cursor.fetchone()

            if row:
                count = row[0]
                return True, count+1
            else:
                return True, 1


        except Exception as ex:
            logger.error('data_sqlite/get_report_count/%s', str(ex))
            conn.close()
            return False,""


