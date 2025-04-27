# model.py
from datetime import datetime
import mysql.connector

class LoginController:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="",  # Chỉnh sửa mật khẩu nếu có
            database="animals_management"  # Tên cơ sở dữ liệu của bạn
        )
        self.cursor = self.conn.cursor()

    def check_login(self, username, password):
        """Kiểm tra thông tin đăng nhập từ cơ sở dữ liệu"""
        query = "SELECT * FROM accounts WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        if result:  # Nếu tìm thấy người dùng
            if result[2] == 0: # NẾU TÀI KHOẢN CHƯA ĐƯỢC DUYỆT
                return False
            else:
                 return True
        else:
            return False
    def check_id(self, username):
        """Kiểm tra thông tin đăng nhập từ cơ sở dữ liệu"""
        query = "SELECT * FROM accounts WHERE username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result[3]
    def register_user(self, first_name, last_name, gender,phone_number, email,  birth_year, role, username, password):
        """Đăng ký người dùng mới"""
        try:

            # Thêm vào bảng users
            user_query = """
            INSERT INTO users (first_name, last_name, gender, phone_number, email, birth_year, role, joined_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            joined_date = datetime.now().date()
            self.cursor.execute(user_query, (first_name, last_name, gender, phone_number, email, birth_year, role, joined_date))
            # Thêm vào bảng accounts
            user_id = self.cursor.lastrowid
            account_query = "INSERT INTO accounts (user_id, username, password) VALUES (%s, %s, %s)"
            self.cursor.execute(account_query, (user_id, username, password))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.conn.rollback()
            return False
