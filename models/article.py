class Article:
    def __init__(
        self,
        id=None,
        title=None,
        url=None,
        description=None,
        content=None,
        source_id=None,
        category_id=None,
        status="pending",
        created_at=None,
        updated_at=None,
        deleted_at=None,
        slug=None
    ):
        self.id = id
        self.title = title
        self.url = url
        self.description = description
        self.content = content
        self.source_id = source_id
        self.category_id = category_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.slug = slug

    def __str__(self):
        return f"{self.id} - {self.title} - {self.status}"
