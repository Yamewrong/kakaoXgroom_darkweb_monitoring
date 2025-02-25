import sqlite3

db_file = "test.db"  # 올바른 파일 경로 설정

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()
    print("DB 무결성 검사 결과:", result)
except Exception as e:
    print("DB 오류 발생:", e)
finally:
    conn.close()
