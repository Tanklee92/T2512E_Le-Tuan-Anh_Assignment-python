from models.source import Source
from repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def _to_source(self, row):
        if row is None:
            return None
        try:
            return Source(**row)
        except TypeError:
            fields = (
                "id", "name", "domain", "path", "category_id", "description",
                "link_selector", "title_selector", "description_selector", "content_selector"
            )
            source = Source(**{key: row[key] for key in fields if key in row})
            if "status" in row:
                source.status = row["status"]
            return source

    def save(self, source: Source):
        query = """
            INSERT INTO sources
            (name, domain, path, category_id, description,
             link_selector, title_selector, description_selector,
             content_selector, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            source.name, source.domain, source.path,
            source.category_id, source.description,
            source.link_selector, source.title_selector,
            source.description_selector, source.content_selector,
            getattr(source, "status", "active")
        )
        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            if conn is None:
                print("Khong the ket noi database.")
                return None
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            source.id = cursor.lastrowid
            return source.id
        except Exception as e:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"Loi them Source: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def update(self, source: Source):
        query = """
            UPDATE sources
            SET name=%s, domain=%s, path=%s, category_id=%s,
                description=%s, link_selector=%s, title_selector=%s,
                description_selector=%s, content_selector=%s, status=%s
            WHERE id=%s
        """
        params = (
            source.name, source.domain, source.path,
            source.category_id, source.description,
            source.link_selector, source.title_selector,
            source.description_selector, source.content_selector,
            getattr(source, "status", "active"), source.id
        )
        return self._write(query, params)

    def _write(self, query, params):
        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            if conn is None:
                print("Khong the ket noi database.")
                return False
            cursor = conn.cursor()
            cursor.execute(query, params)
            affected = cursor.rowcount
            conn.commit()
            return affected > 0
        except Exception as e:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"Loi cap nhat database: {e}")
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def _read(self, query, params=(), many=False):
        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            if conn is None:
                print("Khong the ket noi database.")
                return [] if many else None
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if many:
                return [self._to_source(row) for row in cursor.fetchall()]
            return self._to_source(cursor.fetchone())
        except Exception as e:
            print(f"Loi truy van Source: {e}")
            return [] if many else None
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def find_all(self):
        return self._read("SELECT * FROM sources ORDER BY id", many=True)

    def find_by_id(self, source_id):
        return self._read("SELECT * FROM sources WHERE id=%s", (source_id,))

    def delete_by_id(self, source_id):
        return self._write("DELETE FROM sources WHERE id=%s", (source_id,))

    def find_active(self):
        return self._read(
            "SELECT * FROM sources WHERE status=%s ORDER BY id",
            ("active",), many=True
        )

    def update_status(self, source_id, status):
        if status not in ("active", "inactive"):
            return False
        return self._write(
            "UPDATE sources SET status=%s WHERE id=%s",
            (status, source_id)
        )
