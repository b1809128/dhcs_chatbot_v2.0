from db.mysql import get_connection


def get_lich_hoc_by_lop(lop):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT mon_hoc, thu, gio_bat_dau, gio_ket_thuc, phong
                FROM lich_hoc
                WHERE lop = %s
                ORDER BY thu, gio_bat_dau
            """
            cursor.execute(sql, (lop,))
            return cursor.fetchall()
    finally:
        conn.close()
