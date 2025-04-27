import mysql.connector
from mysql.connector import Error

class AnimalsController:
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

    def get_species_list(self):
        """Lấy danh sách các loài vật từ bảng animals"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT animal_id, species, description FROM animals")
                species_list = cursor.fetchall()
                return species_list
        except Error as e:
            print(f"Error fetching species: {e}")
            return []

    def add_species(self, species, description=None):
        """Thêm loài vật mới vào bảng animals"""
        try:
            with self.conn.cursor() as cursor:
                query = "INSERT INTO animals (species, description) VALUES (%s, %s)"
                cursor.execute(query, (species, description))
                self.conn.commit()
        except Error as e:
            print(f"Error adding species: {e}")
            self.conn.rollback()

    def get_batches_list(self):
        """Lấy danh sách các bầy vật nuôi từ bảng animal_batches"""
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT b.batch_id, b.animal_id, a.species, b.import_date, b.export_date, 
                           b.quantity, b.average_weight
                    FROM animal_batches b
                    JOIN animals a ON b.animal_id = a.animal_id
                    ORDER BY b.import_date DESC
                """
                cursor.execute(query)
                batches_list = cursor.fetchall()
                return batches_list
        except Error as e:
            print(f"Error fetching batches: {e}")
            return []

    def add_batch(self, animal_id, import_date, quantity, average_weight, export_date=None):
        """Thêm một bầy vật nuôi mới vào bảng animal_batches"""
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO animal_batches (animal_id, import_date, export_date, quantity, average_weight)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (animal_id, import_date, export_date, quantity, average_weight))
                self.conn.commit()
        except Error as e:
            print(f"Error adding batch: {e}")
            self.conn.rollback()

    def update_batch(self, batch_id, import_date, quantity, average_weight, export_date):
        """Cập nhật thông tin một bầy vật nuôi"""
        try:
            with self.conn.cursor() as cursor:
                query = """
                    UPDATE animal_batches
                    SET import_date=%s, quantity=%s, average_weight=%s, export_date=%s
                    WHERE batch_id=%s
                """
                cursor.execute(query, (import_date, quantity, average_weight, export_date, batch_id))
                self.conn.commit()
        except Error as e:
            print(f"Error updating batch: {e}")
            self.conn.rollback()

    def delete_batch(self, batch_id):
        """Xóa một bầy vật nuôi"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM animal_batches WHERE batch_id=%s", (batch_id,))
                self.conn.commit()
        except Error as e:
            print(f"Error deleting batch: {e}")
            self.conn.rollback()

    def __del__(self):
        """Đóng kết nối khi đối tượng bị hủy"""
        try:
            if self.conn.is_connected():
                self.conn.close()
        except Error as e:
            print(f"Error closing connection: {e}")
