from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os

class AccountController:
    def __init__(self, user_id, username=None, password=None, activity=None):
        self.user_id = user_id
        self._username = username
        self._password = password
        self._activity = activity

    def _get_connection(self):
        """Tạo kết nối cơ sở dữ liệu với thông tin bảo mật"""
        try:
            return mysql.connector.connect(
                user='root',
                password=os.getenv('DB_PASSWORD', ''),
                host='localhost',
                database='animals_management'
            )
        except Error as e:
            raise Exception(f"Lỗi kết nối cơ sở dữ liệu: {e}")

    def get_user_info(self):
        """Lấy thông tin người dùng dựa trên user_id"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT u.id, u.first_name, u.last_name, u.gender, u.phone_number, u.email, u.birth_year, u.role, u.joined_date, a.username, a.activity
                FROM users u
                LEFT JOIN accounts a ON u.id = a.user_id
                WHERE u.id = %s
            """
            cursor.execute(query, (self.user_id,))
            user = cursor.fetchone()
            return user if user else None
        except Error as e:
            raise Exception(f"Lỗi khi lấy thông tin người dùng: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_all_accounts(self):
        """Lấy danh sách tất cả tài khoản"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT u.id, u.first_name, u.last_name, u.gender, u.phone_number, u.email, u.birth_year, u.role, u.joined_date, a.username, a.activity
                FROM users u
                LEFT JOIN accounts a ON u.id = a.user_id
            """
            cursor.execute(query)
            accounts = cursor.fetchall()
            return accounts
        except Error as e:
            raise Exception(f"Lỗi khi lấy danh sách tài khoản: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_account(self, username, password, first_name, last_name, gender, phone_number, email, birth_year, role, activity='active'):
        """Thêm tài khoản mới vào cả users và accounts"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Thêm vào bảng users
            query_users = """
                INSERT INTO users (first_name, last_name, gender, phone_number, email, birth_year, role, joined_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_users, (
                first_name, last_name, gender, phone_number, email, birth_year, role, datetime.now().date()
            ))
            user_id = cursor.lastrowid  # Lấy ID của bản ghi vừa thêm

            # Thêm vào bảng accounts
            query_accounts = """
                INSERT INTO accounts (username, password, activity, user_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_accounts, (username, password, activity, user_id))

            conn.commit()
            self._username = username
            self._password = password
            self._activity = activity
            self.user_id = user_id
        except Error as e:
            raise Exception(f"Lỗi khi thêm tài khoản: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_account(self, first_name, last_name, gender, birth_year, phone_number, email):
        """Cập nhật thông tin tài khoản trong cả users và accounts""" 
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Cập nhật bảng users
            query_users = """
                UPDATE users
                SET first_name = %s, last_name = %s, gender = %s,birth_year = %s, phone_number = %s, email = %s
                WHERE id = %s
            """
            cursor.execute(query_users, (
                first_name, last_name, gender, birth_year, phone_number, email, self.user_id
            ))

        
            conn.commit()
        
        except Error as e:
            raise Exception(f"Lỗi khi cập nhật tài khoản: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_account(self):
        """Xóa tài khoản từ cả users và accounts"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Xóa từ bảng accounts trước (vì có khóa ngoại)
            query_accounts = "DELETE FROM accounts WHERE user_id = %s"
            cursor.execute(query_accounts, (self.user_id,))

            # Xóa từ bảng users
            query_users = "DELETE FROM users WHERE id = %s"
            cursor.execute(query_users, (self.user_id,))

            conn.commit()
        except Error as e:
            raise Exception(f"Lỗi khi xóa tài khoản: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def change_password(self, new_password):
        """Đổi mật khẩu trong bảng accounts"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "UPDATE accounts SET password = %s WHERE user_id = %s"
            cursor.execute(query, (new_password, self.user_id))
            conn.commit()
            self._password = new_password
        except Error as e:
            raise Exception(f"Lỗi khi đổi mật khẩu: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Getter và Setter cho username
    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    # Getter và Setter cho password
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    # Getter và Setter cho activity
    @property
    def activity(self):
        return self._activity

    @activity.setter
    def activity(self, value):
        self._activity = value