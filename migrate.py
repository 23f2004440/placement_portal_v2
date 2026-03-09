import sqlite3

def migrate():
    conn = sqlite3.connect('backend/ppa.db')
    cursor = conn.cursor()
    
    queries = [
        "ALTER TABLE user ADD COLUMN email VARCHAR(120);",
        "ALTER TABLE student_profile ADD COLUMN resume_path VARCHAR(255);",
        "ALTER TABLE application ADD COLUMN interview_datetime DATETIME;",
        "ALTER TABLE application ADD COLUMN interview_link VARCHAR(255);"
    ]
    
    for q in queries:
        try:
            cursor.execute(q)
            print(f"Executed: {q}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Skipping (already exists): {q}")
            else:
                print(f"Error on {q}: {e}")
                
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    migrate()
