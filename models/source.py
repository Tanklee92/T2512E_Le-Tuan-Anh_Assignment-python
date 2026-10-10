
class Source:
    def __init__(
        self,
        id=None,
        name=None,
        domain=None,
        path=None,
        category_id=None,
        description=None,
        link_selector=None,
        title_selector=None,
        description_selector=None,
        content_selector=None,
        status="active"
    ):
        self.id = id
        self.name = name
        self.domain = domain
        self.path = path
        self.category_id = category_id
        self.description = description
        self.link_selector = link_selector
        self.title_selector = title_selector
        self.description_selector = description_selector
        self.content_selector = content_selector
        self.status = status

    def __str__(self):
        return f"{self.id} - {self.name} - {self.status}"
