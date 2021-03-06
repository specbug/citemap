import aiohttp
import asyncio
from typing import Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
from asyncio.exceptions import TimeoutError
from aiohttp.client_exceptions import ClientOSError

from exceptions import DDoSException


@dataclass
class Resource:
    def __init__(self, url: str, base_url: Optional[str] = None, site_url: Optional[str] = None):
        self._url = url
        self._links = []
        self._name = None
        self._desc = None
        self._title = None
        self._base_url = base_url
        self._site_url = site_url
        self.format()

    @property
    def url(self):
        return self._url

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    @property
    def desc(self):
        return self._desc

    @property
    def links(self):
        return self._links

    @links.setter
    def links(self, links):
        self._links = links

    @property
    def base_url(self):
        return self._base_url

    @property
    def site_url(self):
        return self._site_url

    def format(self, netloc=False):
        """Format url"""
        if not netloc:
            if not self._url.startswith('http'):
                self._url = f'http://{self._url}'
            self._url = self._url.replace('https://', 'http://')
        else:
            parsed_uri = urlparse(self._url)
            if not self._site_url:
                self._site_url = f'{parsed_uri.scheme}://{parsed_uri.netloc}/'
                self._base_url = urljoin(f'{parsed_uri.scheme}://{parsed_uri.netloc}', parsed_uri.path)
            self._url = urljoin(self._base_url, parsed_uri.path)

    @staticmethod
    async def get_page(url, headers=None, connector=None):
        """Get page from url"""
        async with aiohttp.request('GET', url, headers=headers, connector=connector) as response:
            return await response.text(), str(response.url)

    def meta(self, soup: BeautifulSoup):
        """Get name, title, & description of a page"""
        title, desc, name = None, None, None
        try:
            title = soup.find('title').text
            desc = soup.find('meta', {'name': 'description'})
            name = soup.find('meta', {'name': 'name'})
        except Exception:
            pass
        finally:
            self._title = title or ''
            self._desc = desc['content'] if desc else ''
            self._name = name['content'] if name else ''

    def children(self, soup: BeautifulSoup):
        """Get all links from a page"""
        for link in soup.find_all('a', href=True):
            try:
                href = link['href']
                if href.startswith('mailto:'):
                    continue
                if href.startswith('http') and not href.startswith(self._site_url):
                    continue
                if href.startswith('#'):
                    continue
                # TODO: check for MIME type
                if href.endswith(('.jpg', '.png', '.gif', '.jpeg', '.svg', '.ico',
                                  '.css', '.js', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.pdf')):
                    continue
                if not href.startswith('http'):
                    href = urljoin(self._site_url, href)
                href = urljoin(self._base_url, urlparse(href).path)
                self._links.append(href)
            except Exception:
                pass

    async def parse(self, connector=None):
        """Parse URL."""
        try:
            page, self._url = await self.get_page(self._url, headers={'User-Agent': 'Mozilla/6.0'}, connector=connector)
            self.format(True)
            soup = BeautifulSoup(page, 'html.parser')
            self.meta(soup)
            self.children(soup)
        except (TimeoutError, BrokenPipeError, ClientOSError, aiohttp.ServerDisconnectedError) as exc:
            # DDOS protection
            raise DDoSException(exc) from exc
        except Exception as exc:
            raise exc

