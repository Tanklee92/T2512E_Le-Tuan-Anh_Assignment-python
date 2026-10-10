from models.category import Category
from repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository):

    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, category: Category):
        query = """
            INSERT INTO categories (name, slug)
            VALUES (%s, %s)
        """
        params = (category.name, category.slug)

        conn = self.db.get_connection()
        if not conn:
            return None

        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
                    category.id = cursor.lastrowid
                    return category.id
        except Exception as e:
            print(f"Lỗi thêm Category: {e}")
            return None

    def update(self, category: Category):
        query = """
            UPDATE categories
            SET name = %s, slug = %s
            WHERE id = %s AND deleted_at IS NULL
        """
        params = (category.name, category.slug, category.id)

        conn = self.db.get_connection()
        if not conn:
            return False

        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Lỗi cập nhật Category: {e}")
            return False

    def find_all(self):
        query = """
            SELECT * FROM categories
            WHERE deleted_at IS NULL
        """
        conn = self.db.get_connection()
        if not conn:
            return []

        try:
            with conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    return [
                        Category(**row)
                        for row in rows
                    ]
        except Exception as e:
            print(f"Lỗi lấy Category: {e}")
            return []

    def find_by_id(self, category_id):
        query = """
            SELECT * FROM categories
            WHERE id = %s AND deleted_at IS NULL
        """
        conn = self.db.get_connection()
        if not conn:
            return None

        try:
            with conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (category_id,))
                    row = cursor.fetchone()

                    if row:
                        return Category(**row)
                    return None
        except Exception as e:
            print(f"Lỗi tìm Category: {e}")
            return None

    def delete_by_id(self, category_id):
        query = """
            UPDATE categories
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = %s AND deleted_at IS NULL
        """
        conn = self.db.get_connection()
        if not conn:
            return False

        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (category_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Lỗi xóa Category: {e}")
            return False
