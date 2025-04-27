import mysql.connector
from mysql.connector import Error

class work_shifts_controller:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                user='root',
                password='',
                host='localhost',
                database='animals_management'
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def get_list(self):
        """Lấy danh sách tất cả ca làm việc"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT id, shift_number, start_time, end_time, total_animals, username 
                    FROM work_shifts
                """)
                shifts = cursor.fetchall()
                return shifts
        except Error as e:
            print(f"Error fetching work shifts: {e}")
            return []

    def add_shift(self, shift_number, start_time, end_time, total_animals, username):
        """Thêm một ca làm việc mới"""
        try:
            with self.conn.cursor() as cursor:
                sql = """
                    INSERT INTO work_shifts (shift_number, start_time, end_time, total_animals, username)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (shift_number, start_time, end_time, total_animals, username))
                self.conn.commit()
        except Error as e:
            print(f"Error adding work shift: {e}")
            raise

    def update_shift(self, id, shift_number, start_time, end_time, total_animals, username):
        """Cập nhật thông tin ca làm việc"""
        try:
            with self.conn.cursor() as cursor:
                sql = """
                    UPDATE work_shifts 
                    SET shift_number = %s, start_time = %s, end_time = %s, 
                        total_animals = %s, username = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (shift_number, start_time, end_time, total_animals, username, id))
                self.conn.commit()
        except Error as e:
            print(f"Error updating work shift: {e}")
            raise

    def delete_shift(self, id):
        """Xóa một ca làm việc"""
        try:
            with self.conn.cursor() as cursor:
                sql = "DELETE FROM work_shifts WHERE id = %s"
                cursor.execute(sql, (id,))
                self.conn.commit()
        except Error as e:
            print(f"Error deleting work shift: {e}")
            raise

    def search_shifts(self, search_term):
        """Tìm kiếm ca làm việc theo số ca hoặc username"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT id, shift_number, start_time, end_time, total_animals, username 
                    FROM work_shifts 
                    WHERE shift_number LIKE %s OR username LIKE %s
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(sql, (search_pattern, search_pattern))
                shifts = cursor.fetchall()
                return shifts
        except Error as e:
            print(f"Error searching work shifts: {e}")
            return []