import hashlib

from models.article import Article
from repositories.base_repository import BaseRepository


class ArticleRepository(BaseRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def _map_to_article(self, row):
        return Article(**row) if row is not None else None

    def _read(self, query, params=(), many=False):
        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            if conn is None:
                return [] if many else None
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if many:
                return [self._map_to_article(row) for row in cursor.fetchall()]
            return self._map_to_article(cursor.fetchone())
        except Exception as e:
            print(f"Loi truy van Article: {e}")
            return [] if many else None
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def _write(self, query, params):
        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            if conn is None:
                return False
            cursor = conn.cursor()
            cursor.execute(query, params)
            affected = cursor.rowcount
            conn.commit()
            return affected > 0
        except Exception as e:
            if conn is not None:
                conn.rollback()
            print(f"Loi cap nhat Article: {e}")
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def save(self, article: Article):
        if not article.url:
            print("Loi them Article: URL khong duoc de trong")
            return None

        slug = hashlib.sha256(article.url.encode("utf-8")).hexdigest()
        query = """
            INSERT INTO articles
            (title, url, description, content, source_id, category_id, status, slug)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            article.title, article.url, article.description, article.content,
            article.source_id, article.category_id, article.status, slug
        )
        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            article.id = cursor.lastrowid
            article.slug = slug
            return article.id
        except Exception as e:
            if conn is not None:
                conn.rollback()
            if getattr(e, "errno", None) == 1062:
                print(f"Bo qua bai viet da ton tai: {article.url}")
            else:
                print(f"Loi them Article: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def update(self, article: Article):
        query = """
            UPDATE articles
            SET title=%s, url=%s, description=%s, content=%s,
                source_id=%s, category_id=%s, status=%s, slug=%s
            WHERE id=%s
        """
        slug = hashlib.sha256(article.url.encode("utf-8")).hexdigest()
        params = (
            article.title, article.url, article.description, article.content,
            article.source_id, article.category_id, article.status, slug, article.id
        )
        result = self._write(query, params)
        if result:
            article.slug = slug
        return result

    def find_all(self):
        return self._read("SELECT * FROM articles ORDER BY id DESC", many=True)

    def find_by_id(self, article_id):
        return self._read("SELECT * FROM articles WHERE id=%s", (article_id,))

    def delete_by_id(self, article_id):
        return self._write("DELETE FROM articles WHERE id=%s", (article_id,))

    def search(self, keyword):
        query = """
            SELECT * FROM articles
            WHERE title LIKE %s OR url LIKE %s OR description LIKE %s
            ORDER BY id DESC
        """
        value = f"%{keyword}%"
        return self._read(query, (value, value, value), many=True)

    def find_by_source(self, source_id):
        return self._read(
            "SELECT * FROM articles WHERE source_id=%s ORDER BY id DESC",
            (source_id,), many=True
        )

    def find_by_url(self, url):
        return self._read("SELECT * FROM articles WHERE url=%s LIMIT 1", (url,))
