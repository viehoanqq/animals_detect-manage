import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional
from datetime import date

class VaccinationController:
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

    def get_vaccinations_list(self) -> List[Dict]:
        """Lấy danh sách tất cả các bản ghi tiêm phòng từ bảng vaccinations"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT vaccination_id, batch_id, vaccine_name, vaccination_date, notes
                    FROM vaccinations
                    ORDER BY vaccination_date DESC
                """
                cursor.execute(query)
                vaccinations_list = cursor.fetchall()
                return vaccinations_list
        except Error as e:
            print(f"Error fetching vaccinations: {e}")
            return []

    def get_vaccination_by_id(self, vaccination_id: int) -> Optional[Dict]:
        """Lấy thông tin một bản ghi tiêm phòng theo vaccination_id"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT vaccination_id, batch_id, vaccine_name, vaccination_date, notes
                    FROM vaccinations
                    WHERE vaccination_id = %s
                """
                cursor.execute(query, (vaccination_id,))
                vaccination = cursor.fetchone()
                return vaccination
        except Error as e:
            print(f"Error fetching vaccination: {e}")
            return None

    def add_vaccination(self, batch_id: str, vaccine_name: str, vaccination_date: date, notes: Optional[str] = None) -> None:
        """Thêm một bản ghi tiêm phòng mới vào bảng vaccinations"""
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO vaccinations (batch_id, vaccine_name, vaccination_date, notes)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (batch_id, vaccine_name, vaccination_date, notes))
                self.conn.commit()
        except Error as e:
            print(f"Error adding vaccination: {e}")
            self.conn.rollback()

    def update_vaccination(self, vaccination_id: int, batch_id: str, vaccine_name: str, vaccination_date: date, notes: Optional[str] = None) -> None:
        """Cập nhật thông tin một bản ghi tiêm phòng"""
        try:
            with self.conn.cursor() as cursor:
                query = """
                    UPDATE vaccinations
                    SET batch_id=%s, vaccine_name=%s, vaccination_date=%s, notes=%s
                    WHERE vaccination_id=%s
                """
                cursor.execute(query, (batch_id, vaccine_name, vaccination_date, notes, vaccination_id))
                self.conn.commit()
        except Error as e:
            print(f"Error updating vaccination: {e}")
            self.conn.rollback()

    def delete_vaccination(self, vaccination_id: int) -> None:
        """Xóa một bản ghi tiêm phòng"""
        try:
            with self.conn.cursor() as cursor:
                query = "DELETE FROM vaccinations WHERE vaccination_id=%s"
                cursor.execute(query, (vaccination_id,))
                self.conn.commit()
        except Error as e:
            print(f"Error deleting vaccination: {e}")
            self.conn.rollback()

    def __del__(self):
        """Đóng kết nối khi đối tượng bị hủy"""
        try:
            if self.conn.is_connected():
                self.conn.close()
        except Error as e:
            print(f"Error closing connection: {e}")