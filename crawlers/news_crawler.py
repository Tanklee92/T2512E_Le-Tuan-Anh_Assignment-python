import time
import requests
from BS4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

class NewsCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent":"Mozilla/5.0 (compatible; EducationalNewsCrawler/1.0)"})

    def fetch(self, url):
        response = self.session.get(url,timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content,"html.parser")

    def links(self, source, limit=15):
        base = urljoin(source.domain.rstrip('/')+'/',source.path.lstrip('/'))
        soup = self.fetch(base)
        urls=[]
        host=urlparse(source.domain).netloc.lower()
        for node in soup.select(source.link_selector):
            href=node.get('href')
            if not href:
                a=node.find('a',href=True)
                href=a.get('href') if a else None
            if not href:
                continue
            url=urljoin(base,href).split('#')[0]
            if urlparse(url).scheme in ('http','https') and urlparse(url).netloc.lower()==host and url not in urls:
                urls.append(url)
            if len(urls)>=limit:
                break
        return urls

    def detail(self, source, url):
        soup=self.fetch(url)
        def get_text(selector):
            if not selector:
                return ''
            node=soup.select_one(selector)
            return node.get_text(' ',strip=True) if node else ''
        title=get_text(source.title_selector)
        description=get_text(source.description_selector)
        content='\n'.join(n.get_text(' ',strip=True) for n in soup.select(source.content_selector))
        if not title or not content:
            raise ValueError('Không tìm được title/content; kiểm tra CSS selector')
        published=None
        if source.date_selector:
            node=soup.select_one(source.date_selector)
            if node:
                raw=node.get('datetime','')
                if raw:
                    try:
                        published=datetime.fromisoformat(raw.replace('Z','+00:00')).replace(tzinfo=None)
                    except ValueError:
                        pass
        return title,description,content,published
