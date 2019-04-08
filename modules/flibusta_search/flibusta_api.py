import socket
import json
from threading import Thread
import logging

from urllib.parse import urlencode
from urllib import request
from urllib.error import URLError
from bs4 import BeautifulSoup
import socks
from sockshandler import SocksiPyHandler

logging.basicConfig(filename='flibusta_api.log', level=logging.NOTSET)


def remove_empty(d: dict):
    empty_keys = []
    for k in d.keys():
        if not d[k]:
            empty_keys.append(k)
    for i in empty_keys:
        del d[i]
    return d


def load_genres_list(gf_name='flibusta_genre_codes.json'):
    try:
        with open(gf_name, 'r') as genres_file:
            genres = json.load(genres_file)
        return genres
    except FileNotFoundError:
        logging.error(f'File {gf_name} wasn\'t found')
        return None


def load_config(config_name='config.txt'):
    try:
        with open(config_name, 'r') as config_file:
            lines = config_file.read().split('\n')
            params = {}
            for line in lines:
                if line.strip().startswith('#'):
                    continue
                while '  ' in line:
                    line = line.replace('  ', ' ')
                if '#' in line:
                    line = line[:line.find('#')]
                p_v = line.strip().split('=')
                while '' in p_v:
                    p_v.remove('')

                if len(p_v) == 1:
                    continue
                elif len(p_v) == 0:
                    continue
                else:
                    param = p_v[0].strip()
                    value = p_v[1].strip()

                    while True:  # my crappy autotyping
                        if value.isdigit():
                            value = int(value)
                            break
                        if '.' in value and value.replace('.', '').isdigit():
                            value = float(value)
                            break
                        if value in ['None', 'none']:
                            value = None
                            break
                        if value in ['True', 'true']:
                            value = True
                            break
                        if value in ['False', 'false']:
                            value = False
                            break
                        break
                    params[param] = value

            if len(params) == 0:
                return None
            else:
                return params
    except FileNotFoundError:
        return None


def load_proxy_list(list_filename='proxy_list.txt'):
    if list_filename is None:
        return None
    try:
        with open(list_filename, 'r') as list_file:
            lines = list_file.read().split('\n')
            proxy_list = []
            for line in lines:
                if line.strip().startswith('#'):
                    continue
                while '  ' in line:
                    line = line.replace('  ', ' ')
                ip_type = line.strip().split(' ')
                while '' in ip_type:
                    ip_type.remove('')

                if len(ip_type) == 1:
                    logging.warn(f'Proxy type not defined for {ip_type[0]}')
                    continue
                elif len(ip_type) == 0:
                    continue
                else:
                    address = ip_type[0].strip()
                    t = ip_type[1].strip()
                    proxy_list.append((address, t))

            if len(proxy_list) == 0:
                return None
            else:
                return proxy_list
    except FileNotFoundError:
        return None


def split_list(l: list, n: int):
    rev = False
    if 0 < n > len(l):
        n = len(l)
    elif n < 0:
        n = abs(n)
        if n > len(l):
            n = len(l)
        rev = True
    elif n == 0:
        raise ZeroDivisionError
    new_list_len = (round(len(l) / n))
    odd = len(l) % n
    list_of_lists = []
    for k in range(n):
        new_list = []
        list_len = new_list_len
        if odd != 0 and odd == len(l) % n:
            list_len += 1
        for i in range(list_len):
            try:
                item = l.pop(0)
                new_list.append(item)
            except IndexError:
                break
        list_of_lists.append(new_list)
    while len(l) != 0:
        new_list = []
        for i in range(new_list_len):
            try:
                item = l.pop(0)
                new_list.append(item)
            except IndexError:
                break
        list_of_lists.append(new_list)
    while [] in list_of_lists:
        list_of_lists.remove([])
    if rev:
        list_of_lists.reverse()
    return list_of_lists


class ThreadedParse:
    def __init__(self, fb_inst, book_htmls, force_description=False):
        self.fb_inst = fb_inst
        self.book_htmls = book_htmls
        self.parse_thread = Thread(target=self.process_books,
                                   args=[force_description])
        self.result_list = []

    def start_parse(self):
        self.parse_thread.start()

    def process_books(self, force_description):
        old_genre = []
        for item in self.book_htmls:
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
            domain = self.fb_inst.web_domains[self.fb_inst.domain_index]
            download_links['page'] = domain + book_addr[1:]
            for link in book_links:
                download_links[link['href'][link['href'].rfind('/') + 1:]] = domain + link['href'][1:]

            for aut in author_links:
                authors.append({'name': aut.text, 'link': aut['href']})

            for i in raw_genre:  # Genre parsing
                genre.append({'name': i.text, 'link': i['href']})

            if len(genre) == 0:
                genre = old_genre
            old_genre = genre

            self.result_list.append(Book(title=title,
                                         genre=genre,
                                         author=authors,
                                         links=download_links,
                                         fb_inst=self.fb_inst,
                                         force_load_description=force_description))

    def get_result(self):
        self.parse_thread.join()
        return self.result_list


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
        for linkformat in links.keys():
            if linkformat == 'read':
                name = 'читать'
            else:
                name = linkformat
            links_str += f'    {name} - {links[linkformat]}\n'

        return links_str

    def make_string(self):
        genres = self.get_genres()

        authors = self.get_authors()

        string = '''{0} ({2})
    Жанр: {1}
    ________________________
    {4}
    ________________________
{3}'''.format(self['title'], genres, authors, self._construct_refs(), self['description'])
        return string

    def load_book(self, filename, form=None):
        link, form = self.get_download_link(form)
        if link is None:
            logging.error('Loading failed. No valid link found for given format.')
            return False
        else:
            req = request.Request(link)
            pindex = self.fb_inst.proxy_index
            if pindex > -1 and self.fb_inst.proxies[pindex][1] not in ['socks4', 'socks5']:
                proxy = self.fb_inst.proxies[self.fb_inst.proxy_index]
                req.set_proxy(proxy[0], proxy[1])
            try:
                data = request.urlopen(req, timeout=self.fb_inst.file_timeout).read()
                if b'<!DOCTYPE html>' in data:
                    logging.error(' got html for some reason.. Most probalby it is provider plug.')
                    return None
                if 'Доступ к книге ограничен'.encode() in data:
                    return 'book blocked'
                else:
                    with open(filename + "." + form, 'wb') as book_file:
                        book_file.write(data)
            except socket.timeout:
                logging.error(f' Could not get file in {self.fb_inst.file_timeout} seconds')
                return None

            logging.info(f'File {filename+"."+form} loaded')
            return filename + '.' + form

    def get_download_link(self, f=None, invalid=None):
        """returns download link and format to file of given format(f) string or list
        if no format given, returns first existing link in ['fb2', 'epub', 'mobi', 'djvu'] format list"""

        if f is None:
            format_list = ['fb2', 'epub', 'mobi', 'djvu']
        elif isinstance(f, list) or isinstance(f, tuple):
            format_list = f
        elif isinstance(f, str):
            format_list = [f]
        else:
            raise TypeError(f"expected type list, tuple or str, got {type(f)}")

        for i in format_list:
            if i == 'djvu':
                return self['links'].get('download'), i  # Download links doesnt work fo some reason so always fail
            link = self['links'].get(i)  # Maybe cause my provider has a very good DPI
            if link is not None:
                return link, i
        return None

    def get_page(self):
        return self['links'].get('page')

    def get_read(self):
        return self['links'].get('read')

    @staticmethod
    def _find_decription(l):
        dscr = l[1].text
        return dscr

    def get_description(self):
        if self.get('description') is None or self.get('description') == '':
            url = self['links']['page']
            if not isinstance(self.fb_inst, Flibusta):
                self.fb_inst = Flibusta()
            data = BeautifulSoup(self.fb_inst._perform_request(url), features='html.parser')
            descr = self._find_decription(data.find_all('p'))
            return descr
        else:
            return self.get('description')

    def __init__(self, title=None, genre=None, author=None, force_load_description=False, links=None, fb_inst=None):
        super().__init__()
        self.fb_inst = fb_inst
        self['title'] = title
        self['genre'] = genre
        self['author'] = author
        self['links'] = links
        if force_load_description:
            self['description'] = self.get_description()
        else:
            self['description'] = ''


class Flibusta:
    """Class for handling Flibusta queries.
    Constructor optional:
        web_domains - iterable containg str links to flibusta
        local_catalogue - local flibusta catalogue(NOT YET IMPLEMENTED)
        proxies - list of proxies to use if cant reach flibusta directly, like follows:
            [('proxy_ip:proxy_port', 'type')]
        force_proxy - boolean, if this is False proxy will be used only when cant access site directly
        file_timeout - timeout for file downloading attempt in secodns
        threaded_parse - int, number of threads used for book data parsing 0(and 1 too) mean single thread parse
        WARNING: dont ever use force_description with threaded parse, it'll make a mess. Better get description,
        after you have a full book list.

    methods:
        make_book_list - standard flibusta query
        """
    genre_codes = load_genres_list()
    web_domains = ('http://flibusta.site/', 'http://flibusta.is/')

    def __init__(self, local_catalog=None,
                 proxies=None, force_proxy=False, file_timeout=10,
                 threaded_parse=0, config=None):
        self.config = config
        if config is None:
            self.local_catalog = local_catalog
            self.proxies = proxies
            self.force_proxy = force_proxy
            self.proxy_index = -1
            self.domain_index = 0
            self.file_timeout = file_timeout
            self.threaded_parse = threaded_parse
        else:
            self.local_catalog = config.get('local_catalog')
            self.proxies = load_proxy_list(config.get('proxy_list_filename'))
            self.force_proxy = config.get('force_proxy', False)
            self.proxy_index = -1
            self.domain_index = 0
            self.file_timeout = config.get('file_timeout')
            self.threaded_parse = config.get('threaded_parse')

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

    @staticmethod
    def set_current_proxy(req_obj: request.Request, proxy: tuple):
        if proxy[1] == 'socks5':
            opener = request.build_opener(
                SocksiPyHandler(socks.PROXY_TYPE_SOCKS5,
                                proxy[0].split(':')[0],
                                int(proxy[0].split(':')[1])))
            request.install_opener(opener)
        elif proxy[1] == 'socks4':
            opener = request.build_opener(
                SocksiPyHandler(socks.PROXY_TYPE_SOCKS4,
                                proxy[0].split(':')[0],
                                int(proxy[0].split(':')[1])))
            request.install_opener(opener)
        else:
            proxy_handler = request.ProxyHandler({proxy[1]: proxy[0]})
            opener = request.build_opener(proxy_handler)
            request.install_opener(opener)
        logging.info(f'proxy set to {proxy}')

    def _perform_request(self, url, required_part=None):

        req = request.Request(url)
        # Setting up a proxy if needed
        try:
            if len(self.proxies) > self.proxy_index != -1:
                self.set_current_proxy(req, self.proxies[self.proxy_index])
            elif self.proxy_index >= len(self.proxies):
                return 'noway'
            elif self.proxies and self.force_proxy:
                while self.proxy_index <= -1:
                    self.proxy_index += 1
                self.set_current_proxy(req, self.proxies[self.proxy_index])
        except TypeError:
            pass

        # Getting data
        logging.info(f'loading {url}')
        try:
            response = request.urlopen(req)
        except URLError as err:
            logging.error(err)
            self.proxy_index += 1
            return None
        if response.getcode() == 200:
            data = response.read().decode()
            if required_part is None or 'Не нашлось ни единой книги, удовлетворяющей вашим требованиям.' in data:
                return data
            elif isinstance(required_part, str):  # Response validation by content
                if required_part in data:
                    return data
                else:
                    self.proxy_index += 1
                    return None
            elif isinstance(required_part, list):
                for i in required_part:
                    if i not in data:
                        self.proxy_index += 1
                        return None
        elif response.getcode() == 404:
            self.domain_index += 1
            return None
        else:
            return Exception(f'Could not access data. Server returned code {response.getcode()}')

    def _parse_book_list_result(self, html, limit=0, force_description=False):
        books = []
        soup = BeautifulSoup(html, features='html.parser')
        if soup.form is None:
            return books
        container = soup.form.extract()
        book_htmls = container('div')

        while len(book_htmls) > limit > 0:
            book_htmls.pop()

        if self.threaded_parse > 1:
            parse_data_sets = split_list(book_htmls, self.threaded_parse)
            parsers = []
            for i in parse_data_sets:
                parsers.append(ThreadedParse(self, i, force_description))
            for p in parsers:
                p.start_parse()

            for parser in parsers:
                books.extend(parser.get_result())
            return books
        else:
            p = ThreadedParse(self, book_htmls, force_description)
            p.start_parse()
            books = p.get_result()

        return books

    def make_book_list(self, **kwargs):
        """Standard Flibusta search query.
        takes(optional):
            title - Book title
            genre - Book genre
            lastname - author lastname
            firstname - author firstname
            patronymic - author patronymic
            filesize - min/max file size(tuple or list)
            years - years of issue, oldest/newest(tuple or list)
            limit - maximum amount of books to be returned

        returns list of books object(inherited from dict)
        if no books were found, returns empty list
        """
        answer = []
        if self.local_catalog is None:
            method = 'makebooklist?'

            # Cooking parameters for url
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

            if isinstance(self.config, dict):
                limit = self.config.get('book_limit', 0)
            else:
                limit = kwargs.get('limit', 0)

            # Fetching data
            data = None
            if not Flibusta.web_domains and not self.local_catalog:
                logging.error('No data source defined')
                return []

            # Check if site can be found
            while data is None and self.domain_index < len(Flibusta.web_domains) and data != 'noway':
                req_url = Flibusta.web_domains[self.domain_index] + method + params
                data = self._perform_request(req_url, '<form name="bk" action="#">')
            else:
                if data is None:
                    logging.error('Could not recieve data')
                    return []
            if data != 'Не нашлось ни единой книги, удовлетворяющей вашим требованиям.':
                answer = self._parse_book_list_result(html=data,
                                                      limit=limit,
                                                      force_description=kwargs.get('force_description', False))
        else:
            raise NotImplementedError("Local catalogue is not implenented yet.")
        logging.info(f'returned {len(answer)} books')
        return answer
