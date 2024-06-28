import mysql.connector
import config

db_config = {
    'user': config.DB_USER,
    'password': config.DB_PASSWORD,
    'host': config.DB_HOST,
    'database': config.DB_NAME
}
conn = mysql.connector.connect(**db_config)

def fetch_data():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, price, employment, experience, requirements FROM vacancies")
    rows = cursor.fetchall()
    cursor.close()
    return rows

def fetch_profile(user_phone):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM profiles WHERE phone = %s", (user_phone,))
    profile = cursor.fetchone()
    cursor.close()
    return profile

def read_profile(p_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM profiles WHERE id = %s", (p_id,))
    p = cursor.fetchone()
    cursor.close()
    return p

def read_vacancy(v_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vacancies WHERE id = %s", (v_id,))
    v = cursor.fetchone()
    cursor.close()
    return v

def read_candidates():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, profile_id, job_id FROM candidates")
    candidates = cursor.fetchall()
    cursor.close()
    return candidates

def del_candidate(profile_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM candidates WHERE profile_id = %s", (profile_id,))
    conn.commit()
    cursor.close()

def edit_vacancy(vacancy_id, field, value):
    cursor = conn.cursor()
    query = f"UPDATE vacancies SET {field} = %s WHERE id = %s"
    cursor.execute(query, (value, vacancy_id))
    conn.commit()
    cursor.close()

def del_vacancy(vacancy_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM vacancies WHERE id = %s", (vacancy_id,))
    conn.commit()
    cursor.close()