import mysql.connector
from mysql.connector import Error

class shift_details_controller:
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
        """Lấy danh sách tất cả chi tiết ca làm việc"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT sd.id, sd.shift_id, sd.animal_id, sd.quantity,
                           ws.shift_number, a.type_name
                    FROM shift_details sd
                    JOIN work_shifts ws ON sd.shift_id = ws.id
                    JOIN animals a ON sd.animal_id = a.id
                """)
                shift_details = cursor.fetchall()
                return shift_details
        except Error as e:
            print(f"Error fetching shift details: {e}")
            return []

    def add_shift_detail(self, shift_id, animal_id, quantity):
        """Thêm một chi tiết ca làm việc mới"""
        try:
            with self.conn.cursor() as cursor:
                sql = """
                    INSERT INTO shift_details (shift_id, animal_id, quantity)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (shift_id, animal_id, quantity))
                self.conn.commit()
        except Error as e:
            print(f"Error adding shift detail: {e}")
            raise

    def update_shift_detail(self, id, shift_id, animal_id, quantity):
        """Cập nhật thông tin chi tiết ca làm việc"""
        try:
            with self.conn.cursor() as cursor:
                sql = """
                    UPDATE shift_details 
                    SET shift_id = %s, animal_id = %s, quantity = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (shift_id, animal_id, quantity, id))
                self.conn.commit()
        except Error as e:
            print(f"Error updating shift detail: {e}")
            raise

    def delete_shift_detail(self, id):
        """Xóa một chi tiết ca làm việc"""
        try:
            with self.conn.cursor() as cursor:
                sql = "DELETE FROM shift_details WHERE id = %s"
                cursor.execute(sql, (id,))
                self.conn.commit()
        except Error as e:
            print(f"Error deleting shift detail: {e}")
            raise

    def search_shift_details(self, search_term):
        """Tìm kiếm chi tiết ca làm việc theo shift_id hoặc animal_id"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT sd.id, sd.shift_id, sd.animal_id, sd.quantity,
                           ws.shift_number, a.type_name
                    FROM shift_details sd
                    JOIN work_shifts ws ON sd.shift_id = ws.id
                    JOIN animals a ON sd.animal_id = a.id
                    WHERE CAST(sd.shift_id AS CHAR) LIKE %s 
                       OR CAST(sd.animal_id AS CHAR) LIKE %s
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(sql, (search_pattern, search_pattern))
                shift_details = cursor.fetchall()
                return shift_details
        except Error as e:
            print(f"Error searching shift details: {e}")
            return []