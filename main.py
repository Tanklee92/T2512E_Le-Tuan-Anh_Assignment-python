from urllib.parse import urlparse

from database.connection import DatabaseConnection
from models.source import Source
from repositories.category_respository import CategoryRepository
from repositories.source_repository import SourceRepository
from repositories.article_repository import ArticleRepository
from services.crawler_service import CrawlerService


def source_menu(source_repo):
    def display_sources(sources):
        if not sources:
            print('Chua co nguon tin.')
            return
        print('\n' + '-' * 115)
        print(f"{'ID':<6} {'TEN NGUON':<26} {'URL TRANG CHU / CHUYEN MUC':<63} {'TRANG THAI':<12}")
        print('-' * 115)
        for source in sources:
            domain = (source.domain or '').rstrip('/')
            path = source.path or ''
            url = path if path.startswith(('http://', 'https://')) else domain + ('/' + path.lstrip('/') if path else '')
            status = getattr(source, 'status', 'inactive')
            print(f"{str(source.id):<6} {str(source.name or '')[:26]:<26} {url[:63]:<63} {status:<12}")
        print('-' * 115)

    def get_source_id():
        try:
            return int(input('Nhap ID nguon tin: ').strip())
        except ValueError:
            print('ID phai la so nguyen.')
            return None

    while True:
        print('\n--- QUAN LY NGUON TIN ---')
        print('1.1. Xem danh sach cac nguon tin')
        print('1.2. Them nguon tin moi')
        print('1.3. Cap nhat thong tin nguon tin')
        print('1.4. Xoa nguon tin (hoac doi trang thai Kich hoat/Bo kich hoat)')
        print('0. Quay lai Menu chinh')
        choice = input('Chon: ').strip()
        try:
            if choice in ('1', '1.1'):
                display_sources(source_repo.find_all())
            elif choice in ('2', '1.2'):
                print('\n--- THEM NGUON TIN MOI ---')
                name = input('Ten nguon: ').strip()
                domain = input('Domain: ').strip()
                path = input('Path: ').strip()
                link_selector = input('Link selector: ').strip()
                title_selector = input('Title selector: ').strip()
                description_selector = input('Description selector: ').strip()
                content_selector = input('Content selector: ').strip()
                if not name or not domain:
                    print('Ten nguon va Domain khong duoc de trong.')
                    continue
                if not domain.startswith(('http://', 'https://')):
                    domain = 'https://' + domain
                if path.startswith(('http://', 'https://')):
                    parsed = urlparse(path)
                    domain = f'{parsed.scheme}://{parsed.netloc}'
                    path = parsed.path
                elif path:
                    path = '/' + path.lstrip('./')
                source = Source(name=name, domain=domain, path=path, category_id=None,
                                description='', link_selector=link_selector,
                                title_selector=title_selector, description_selector=description_selector,
                                content_selector=content_selector, status='active')
                result = source_repo.save(source)
                if result is not None and result is not False:
                    print(f'Them nguon tin thanh cong! ID: {result}')
                else:
                    print('Them nguon tin that bai!')
            elif choice in ('3', '1.3'):
                print('\n--- CAP NHAT NGUON TIN ---')
                source_id = get_source_id()
                if source_id is None:
                    continue
                source = source_repo.find_by_id(source_id)
                if source is None:
                    print('Khong tim thay nguon tin.')
                    continue
                values = {
                    'name': input(f'Ten nguon [{source.name}]: ').strip(),
                    'domain': input(f'Domain [{source.domain}]: ').strip(),
                    'path': input(f'Path [{source.path}]: ').strip(),
                    'link_selector': input(f'Link selector [{source.link_selector}]: ').strip(),
                    'title_selector': input(f'Title selector [{source.title_selector}]: ').strip(),
                    'description_selector': input(f'Description selector [{source.description_selector}]: ').strip(),
                    'content_selector': input(f'Content selector [{source.content_selector}]: ').strip()
                }
                for key, value in values.items():
                    if not value:
                        continue
                    if key == 'domain' and not value.startswith(('http://', 'https://')):
                        value = 'https://' + value
                    if key == 'path':
                        if value.startswith(('http://', 'https://')):
                            parsed = urlparse(value)
                            source.domain = f'{parsed.scheme}://{parsed.netloc}'
                            value = parsed.path
                        else:
                            value = '/' + value.lstrip('./')
                    setattr(source, key, value)
                print('Cap nhat nguon tin thanh cong!' if source_repo.update(source) else 'Cap nhat that bai hoac du lieu khong thay doi.')
            elif choice in ('4', '1.4'):
                print('\n--- XOA / DOI TRANG THAI NGUON TIN ---')
                source_id = get_source_id()
                if source_id is None:
                    continue
                source = source_repo.find_by_id(source_id)
                if source is None:
                    print('Khong tim thay nguon tin.')
                    continue
                print(f'Nguon: {source.name} | Trang thai: {source.status}')
                print('1. Xoa nguon tin')
                print('2. Kich hoat nguon tin')
                print('3. Bo kich hoat nguon tin')
                print('0. Huy')
                action = input('Chon: ').strip()
                if action == '1':
                    if input('Xac nhan xoa? (y/n): ').strip().lower() == 'y':
                        print('Xoa nguon tin thanh cong!' if source_repo.delete_by_id(source_id) else 'Xoa that bai. Kiem tra rang buoc du lieu trong MySQL.')
                    else:
                        print('Da huy xoa.')
                elif action in ('2', '3'):
                    status = 'active' if action == '2' else 'inactive'
                    print('Cap nhat trang thai thanh cong!' if source_repo.update_status(source_id, status) else 'Cap nhat that bai hoac trang thai khong thay doi.')
                elif action != '0':
                    print('Lua chon khong hop le.')
            elif choice == '0':
                print('Quay lai Menu chinh.')
                break
            else:
                print('Lua chon khong hop le.')
        except Exception as error:
            print(f'Loi xu ly nguon tin: {error}')


def article_menu(article_repo):
    while True:
        print('\n========== QUAN LY BAI VIET ==========')
        print('1. Xem danh sach bai viet')
        print('2. Tim kiem bai viet')
        print('3. Loc bai viet theo nguon')
        print('4. Xem chi tiet bai viet')
        print('5. Xoa bai viet')
        print('0. Quay lai menu chinh')
        choice = input('Chon: ').strip()
        try:
            if choice == '1':
                articles = article_repo.find_all()
                if not articles:
                    print('Chua co bai viet nao.')
                else:
                    for article in articles:
                        print(f'ID: {article.id} | Tieu de: {article.title} | Nguon ID: {article.source_id}')
            elif choice == '2':
                print('\n--- TIM KIEM BAI VIET ---')
                keyword = input('Nhap tieu de, URL hoac tu khoa: ').strip()
                if not keyword:
                    print('Vui long nhap tu khoa.')
                    continue
                articles = article_repo.search(keyword)
                if not articles:
                    print('Khong tim thay bai viet trong database.')
                    print('Hay kiem tra Crawler da luu bai viet chua.')
                else:
                    print(f'\nTim thay {len(articles)} bai viet:')
                    for article in articles:
                        print('-' * 60)
                        print('ID:', article.id)
                        print('Tieu de:', article.title)
                        print('URL:', article.url)
                        print('Nguon ID:', article.source_id)
            elif choice == '3':
                source_id = int(input('Nhap Source ID: '))
                articles = article_repo.find_by_source(source_id)
                if not articles:
                    print('Khong co bai viet thuoc nguon nay.')
                else:
                    for article in articles:
                        print(f'ID: {article.id} | Tieu de: {article.title}')
            elif choice == '4':
                article_id = int(input('Nhap Article ID: '))
                article = article_repo.find_by_id(article_id)
                if article is None:
                    print('Khong tim thay bai viet.')
                else:
                    print('ID:', article.id)
                    print('Tieu de:', article.title)
                    print('URL:', article.url)
                    print('Mo ta:', article.description)
                    print('Noi dung:', article.content)
                    print('Source ID:', article.source_id)
                    print('Category ID:', article.category_id)
                    print('Trang thai:', article.status)
                    print('Ngay tao:', article.created_at)
                    print('Ngay cap nhat:', article.updated_at)
            elif choice == '5':
                article_id = int(input('Nhap Article ID can xoa: '))
                article = article_repo.find_by_id(article_id)
                if article is None:
                    print('Khong tim thay bai viet.')
                    continue
                print('Bai viet:', article.title)
                if input('Ban co chac muon xoa? (y/n): ').strip().lower() == 'y':
                    print('Xoa bai viet thanh cong!' if article_repo.delete_by_id(article_id) else 'Xoa bai viet that bai!')
                else:
                    print('Da huy xoa.')
            elif choice == '0':
                print('Quay lai menu chinh.')
                break
            else:
                print('Lua chon khong hop le.')
        except ValueError:
            print('ID phai la so nguyen.')
        except Exception as error:
            print(f'Loi khi quan ly bai viet: {error}')


def main():
    print('Dang khoi dong chuong trinh...')
    db = DatabaseConnection(host='127.0.0.1', user='root', password='', database='news', port=3306)
    category_repo = CategoryRepository(db)
    source_repo = SourceRepository(db)
    article_repo = ArticleRepository(db)
    crawler = CrawlerService(article_repo)
    while True:
        print('\n================================')
        print('   CHUONG TRINH NEWS CRAWLER')
        print('================================')
        print('1. Quan ly nguon tin')
        print('2. Quan ly bai viet')
        print('3. Chay Crawler')
        print('0. Thoat')
        choice = input('Nhap lua chon: ').strip()
        if choice == '1':
            source_menu(source_repo)
        elif choice == '2':
            article_menu(article_repo)
        elif choice == '3':
            print('\n--- CRAWLER ---')
            print('1. Crawl tat ca nguon')
            print('2. Crawl theo ID')
            print('0. Quay lai')
            option = input('Nhap lua chon: ').strip()
            try:
                if option == '1':
                    sources = source_repo.find_active()
                    if not sources:
                        print('Khong co nguon dang hoat dong.')
                    else:
                        for source in sources:
                            count = crawler.crawl_source(source)
                            print(f'{source.name}: {count} bai moi')
                elif option == '2':
                    source_id = int(input('Nhap Source ID: '))
                    source = source_repo.find_by_id(source_id)
                    if source:
                        count = crawler.crawl_source(source)
                        print(f'Da crawl {count} bai moi')
                    else:
                        print('Khong tim thay nguon')
                elif option != '0':
                    print('Lua chon khong hop le.')
            except ValueError:
                print('ID phai la so nguyen')
            except Exception as error:
                print(f'Loi khi chay crawler: {error}')
        elif choice == '0':
            print('Ket thuc chuong trinh!')
            break
        else:
            print('Lua chon khong hop le!')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Loi chuong trinh: {error}')
