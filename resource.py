import aiohttp
import asyncio
from typing import Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin


@dataclass
class Resource:
    def __init__(self, url: str):
        self._url = url
        self._links = []
        self._name = None
        self._desc = None
        self._title = None
        self._site_url = None
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

    @property
    def site_url(self):
        return self._site_url

    def format(self, netloc=False):
        """Format url"""
        if not netloc:
            if not self._url.startswith('http'):
                self._url = f'http://{self._url}'
            self._url = self._url.replace('https://', 'http://')
        parsed_uri = urlparse(self._url)
        self._site_url = f'{parsed_uri.scheme}://{parsed_uri.netloc}'
        self._url = urljoin(self._site_url, parsed_uri.path)

    @staticmethod
    async def get_page(url, headers=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
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
                if not href.startswith('http'):
                    href = urljoin(self._site_url, href)
                href = urljoin(self._site_url, urlparse(href).path)
                self._links.append(href)
            except Exception as exc:
                print(exc)
                pass

    async def parse(self):
        """Parse URL."""
        try:
            page, self._url = await self.get_page(self._url, headers={'User-Agent': 'Mozilla/6.0'})
            self.format(True)
            soup = BeautifulSoup(page, 'html.parser')
            self.meta(soup)
            self.children(soup)
        except BrokenPipeError:
            # DDOS protection
            print('cooldown')
            await asyncio.sleep(1)
            await self.parse()
        except Exception as exc:
            raise exc

