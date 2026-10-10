import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

from models.article import Article


class CrawlerService:

    def __init__(self, article_repository):
        self.article_repo = article_repository

    def get_html(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as error:
            print(f"Loi tai website {url}: {error}")
            return None

    def crawl_source(self, source):
        if source.status != "active":
            print("Nguon khong hoat dong.")
            return 0

        domain = (source.domain or "").rstrip("/") + "/"
        base_url = urljoin(domain, (source.path or "").lstrip("/"))
        soup = self.get_html(base_url)

        if soup is None:
            return 0

        if not source.link_selector or not source.title_selector or not source.content_selector:
            print("Nguon tin thieu CSS selector.")
            return 0

        try:
            links = soup.select(source.link_selector)
        except Exception as error:
            print(f"Link selector khong hop le: {error}")
            return 0

        count = 0
        visited = set()
        base_host = urlparse(base_url).hostname

        for element in links:
            if len(visited) >= 30:
                break

            href = element.get("href")
            if not href:
                continue

            url = urldefrag(urljoin(base_url, href))[0]
            parsed = urlparse(url)

            if parsed.scheme not in ("http", "https") or parsed.hostname != base_host:
                continue

            if not re.search(r"-\d+\.chn$", parsed.path, flags=re.IGNORECASE):
                continue

            url = parsed._replace(query="", fragment="").geturl()

            if url in visited:
                continue
            visited.add(url)

            try:
                if self.article_repo.find_by_url(url) is not None:
                    print(f"Bo qua bai da ton tai: {url}")
                    continue
            except Exception as error:
                print(f"Loi kiem tra URL {url}: {error}")
                continue

            detail = self.get_html(url)
            if detail is None:
                continue

            try:
                title_element = detail.select_one(source.title_selector)
                description_element = (
                    detail.select_one(source.description_selector)
                    if source.description_selector else None
                )
                content_elements = detail.select(source.content_selector)
            except Exception as error:
                print(f"CSS selector khong hop le tai {url}: {error}")
                continue

            if title_element is None:
                continue

            title = title_element.get_text(" ", strip=True)
            description = (
                description_element.get_text(" ", strip=True)
                if description_element else ""
            )
            paragraphs = [
                item.get_text(" ", strip=True)
                for item in content_elements
            ]
            content = "\n".join(text for text in paragraphs if text)

            if not title or not content:
                print(f"Bo qua bai thieu noi dung: {url}")
                continue

            article = Article(
                title=title,
                url=url,
                description=description,
                content=content,
                source_id=source.id,
                category_id=source.category_id,
                status="completed"
            )

            article_id = self.article_repo.save(article)
            if article_id:
                count += 1
                print(f"Da luu [{article_id}]: {title}")

        return count
