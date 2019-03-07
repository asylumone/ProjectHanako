from urllib.parse import urlencode
from urllib import request
from bs4 import BeautifulSoup

genre_code = {
    'business': {
        'finance': 'banking',
        'marketing': 'org_behavior',
        'career': 'popular_business',
        'business': 'business',
        'economics': 'economics_ref,economics'
    },
    'detective': {
        'classic': 'det_classic',
        'police': 'det_police',
        'action': 'det_action',
        'ironic': 'det_irony',
        'historic': 'det_history',
        'spy': ',det_espionage',
        'criminal': 'det_crime',
        'political': 'det_political',
        'maniac': 'det_maniac',
        'cool': 'det_hard',
        'thriller': 'thriller',
        'detective': 'detective',
        'soviet': 'det_su'

    },
    'documentary': {
        'bio': 'nonf_biography',
        'publicistics': 'nonf_publicism',
        'documentary': 'nonfiction',
        'miltary and analitics': 'nonf_military',
        'military': 'military_special',
        'geography': 'travel_notes'
    },
    'home': {
        'cuisine': 'home_cooking',
        'pets': 'home_pets',
        'hobby': 'home_crafts',
        'entertain': 'home_entertain',
        'health': 'home_health',
        'garden': 'home_garden',
        'diy': 'home_diy',
        'sport': 'home_sport',
        'sex': 'home_sex',
        'home': 'home',
        'child upraising': 'sci_pedagogy',
        'automobile': 'auto_regulations',
        'collecting': 'home_collecting',
        'family relations': 'family'
    },
    'drama': {
        'dramaturgy': 'dramaturgy',
        'comedy': 'comedy',
        'tragedy': 'tragedy',
    }
}


def remove_empty(d: dict):
    empty_keys = []
    for k in d.keys():
        if not d[k]:
            empty_keys.append(k)
    for i in empty_keys:
        del d[i]
    return d


class Book(dict):
    def get_title(self):
        return self['title']

    def get_authors(self):
        authors = ''
        for a in self['author']:
            authors += a['name']
            if a != self['author'][-1]:
                authors += ', '
        return authors

    def get_genres(self):
        genres = ''
        for g in self['genre']:
            genres += g['name']
            if g != self['genre'][-1]:
                genres += ', '
        return genres

    def _construct_refs(self):
        links = self['links']
        links_str = ''
        for k in links.keys():
            if k == 'read':
                name = 'читать'
            else:
                name = k
            links_str += f'    {name} - {links[k]}\n'

        return links_str

    def make_string(self):
        genres = self.get_genres()

        authors = self.get_authors()

        string = '''{0} ({2})
    Жанр: {1}
    ________________________
    {4}
    ________________________
{3}'''.format(self['title'], genres, authors, self._construct_refs(),self['description'])
        return string

    def load_book(self, form, filename):
        link = None
        possible = ['fb2', 'epub', 'mobi', 'download']
        link = self['links'].get(form)
        while link is None:
            for form in possible:
                link = self['links'].get(form)
                if not link is None:
                    if form == 'download':
                        form = 'djvu'
                    break

        print(f'loading {link}')
        if link is None:
            return False
        else:
            request.urlretrieve(link, filename+'.'+form)
            return filename+'.'+form

    def get_page(self):
        return self['links'].get('page')

    def get_read(self):
        return self['links'].get('read')

    def get_mobi(self):
        return self['links'].get('mobi')

    def get_epub(self):
        return self['links'].get('epub')

    def get_fb2(self):
        return self['links'].get('fb2')

    @staticmethod
    def _find_decription(l):
        dscr = l[1].text
        return dscr

    def get_description(self):
        if self.get('description') is None:
            url = self['links']['page']
            if not isinstance(self.fb_inst, Flibusta):
                self.fb_inst = Flibusta()
            data = BeautifulSoup(self.fb_inst._perform_request(url), features='html.parser')
            descr = self._find_decription(data.find_all('p'))
            return descr
        else:
            return self.get('description')

    def __init__(self, title=None, genre=None, author=None, description=None, links=None, fb_inst=None):
        super().__init__()
        self.fb_inst = fb_inst
        self['title'] = title
        self['genre'] = genre
        self['author'] = author
        self['links'] = links
        self['description'] = self.get_description()


class Flibusta:
    def __init__(self, web_domains=('http://flibusta.site/', 'http://flibusta.is/'),
                 local_catalogue=None,
                 proxies=None, force_proxy=False):

        self.web_domains = web_domains
        self.local_catalogue = local_catalogue
        self.proxies = proxies
        self.force_proxy = force_proxy
        self.proxy_index = -1
        self.domain_index = 0

    @staticmethod
    def _pack_params(params):
        if isinstance(params['s1'], tuple) or isinstance(params['s1'], list):
            if len(params['s1']) > 1:
                params['s2'] = params['s1'][1]
                params['s1'] = params['s1'][0]
            else:
                params['s2'] = params['s1'][0]
                params['s1'] = None
        else:
            params['s1'] = None
            params['s2'] = None

        if isinstance(params['issueYearMin'], tuple) or isinstance(params['issueYearMin'], list):
            if len(params['issueYearMin']) > 1:
                params['issueYearMax'] = params['issueYearMin'][1]
                params['issueYearMin'] = params['issueYearMin'][0]
            else:
                params['issueYearMax'] = params['issueYearMin'][0]
                params['issueYearMin'] = None
        else:
            params['issueYearMin'] = None
            params['issueYearMax'] = None

        params = urlencode(remove_empty(params))

        return params

    def _perform_request(self, url):
        req = request.Request(url)
        if self.proxies and self.force_proxy:
            print('proxy pass')

        if self.proxy_index != -1:
            req.set_proxy(self.proxies[self.proxy_index], 'http')

        response = request.urlopen(req)

        def out_of_reach(d):
            try:
                page_title = BeautifulSoup(d, features='html.parser')('title', limit=1)[0]
            except IndexError:
                page_title = ''
            cant_get_to_site = ('Ресурс заблокирован' in page_title or response.getcode() != 200)
            return cant_get_to_site

        data = response.read().decode()
        # Local blocking bypass
        while out_of_reach(data):
            self.proxy_index += 1

            if isinstance(self.proxies, list) or isinstance(self.proxies, tuple):
                if self.proxy_index < len(self.proxies):
                    req.set_proxy(self.proxies[self.proxy_index], 'http')
                    print(f'Trying proxy {self.proxies[self.proxy_index]}')
                else:
                    print('Unfortunately, no proxy worked')
                    self.proxy_index = -1
                    break
            elif isinstance(self.proxies, str):
                req.set_proxy(self.proxies, 'http')
                print(f'Trying proxy {self.proxies}')

            else:
                print('Try specify proxies in Flibusta instance, like folows:')
                print('Flibusta(proxies=[\'ip:port\',\'ip2:potr2\'])')
                break
            response = request.urlopen(req)
            data = response.read().decode()
            out_of_reach(data)
        else:
            return data

        if response.getcode() == 200:
            return data
        else:
            return Exception(f'Could not access data. Server returned code {response.getcode()}')

    def _parse_book_list_result(self, html):
        books = []
        soup = BeautifulSoup(html, features='html.parser')
        if soup.form is None:
            return books
        container = soup.form.extract()
        book_htmls = container('div')
        old_genre = []

        for item in book_htmls:
            raw_genre = item.find_all('a', {'class': 'genre'})
            genre = []
            all_refs = item.find_all('a')
            book_links = []
            author_links = []

            for i in all_refs:
                if '/b/' in i['href']:
                    book_links.append(i)

            for i in all_refs:
                if '/a/' in i['href']:
                    author_links.append(i)

            title = book_links[0].text
            book_addr = book_links.pop(0)['href']
            download_links = {}
            authors = []

            download_links['page'] = self.web_domains[self.domain_index] + book_addr[1:]
            for link in book_links:
                download_links[link['href'][link['href'].rfind('/') + 1:]] = self.web_domains[self.domain_index] \
                                                                             + link['href'][1:]

            for aut in author_links:
                authors.append({'name': aut.text, 'link': aut['href']})

            for i in raw_genre:  # Genre parsing
                genre.append({'name': i.text, 'link': i['href']})

            if len(genre) == 0:
                genre = old_genre
            old_genre = genre

            books.append(Book(title=title,
                              genre=genre,
                              author=authors,
                              links=download_links,
                              fb_inst=self))
        return books

    def make_book_list(self, **kwargs):
        """Standard Flibusta search query.
        takes:
            title - Book title
            genre - Book genre
            lastname - author lastname
            firstname - author firstname
            patronymic - author patronymic
            filesize - min/max file size(tuple or list)
            years - years of issue, oldest/newest(tuple or list)

        returns list of books object(inherited from dict)
        if no books were found, returns empty list
        """

        method = 'makebooklist?'

        params = {'ab': kwargs.get('ab', 'ab1'),  # have no idea what that is
                  't': kwargs.get('title'),  # book Title
                  'sort': kwargs.get('sort', 'sd1'),  # Sorting. By title (st1,st2), By date (sd1, sd2)
                  'ln': kwargs.get('lastname'),  # author Lastname
                  'fn': kwargs.get('firstname'),  # author Firstname
                  'mn': kwargs.get('patronymic'),  # author OTCHESTVO
                  'g': kwargs.get('genre'),  # Genre
                  's1': kwargs.get('filesize'),  # min filesize
                  's2': '',  # max filesize
                  'issueYearMin': kwargs.get('years'),  # Years
                  'issueYearMax': ''
                  }
        params = self._pack_params(params)

        req_url = self.web_domains[self.domain_index] + method + params
        data = self._perform_request(req_url)
        answer = []
        if data != 'Не нашлось ни единой книги, удовлетворяющей вашим требованиям.':
            answer = self._parse_book_list_result(data)

        return answer
