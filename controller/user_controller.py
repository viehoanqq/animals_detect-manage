import mysql.connector

def get_user_info(user_id):
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='animals_management')
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user
