import mysql.connector
from mysql.connector import Error
import requests
class environment_controller:
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
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT record_date, record_time, temperature, humidity, rainfall FROM environment")
                env_list = cursor.fetchall()
                return env_list
        except Error as e:
            print(f"Error fetching environment data: {e}")
            return []

    def add_enviroment(self, record_date, record_time, temperature, humidity, rainfall):
        try:
            with self.conn.cursor() as cursor:
                sql = """INSERT INTO environment (record_date, record_time, temperature, humidity, rainfall)
                         VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (record_date, record_time, temperature, humidity, rainfall))
                self.conn.commit()
        except Error as e:
            print(f"Error adding environment record: {e}")
            raise

    def delete_enviroment(self, record_date, record_time):
        try:
            with self.conn.cursor() as cursor:
                sql = "DELETE FROM environment WHERE record_date = %s AND record_time = %s"
                cursor.execute(sql, (record_date, record_time))
                self.conn.commit()
        except Error as e:
            print(f"Error deleting environment record: {e}")
            raise
    def get_info_env():
        params = {
        'id': 1566083 ,  # Tên thành phố
        'appid': 'cfb56ad07272046760411444f50fb23f', 
        'units': 'metric',  # Đơn vị: Celsius
        'lang': 'vi'  # Ngôn ngữ: Tiếng Việt
        }
        response = requests.get('http://api.openweathermap.org/data/2.5/weather?app', params=params)
        if response.status_code == 200:
            data = response.json()
            name = data.get('name')
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            rain = data.get('rain', {}).get('1h', 0)  # mm trong 1 giờ
            return [name,temp,humidity,description,rain]
        else:
            print("Lỗi: Không thể lấy dữ liệu thời tiết.")
            return "lôi"
    