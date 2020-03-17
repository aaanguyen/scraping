# -*- coding: utf-8 -*-
import scrapy, json, re
from unidecode import unidecode


class SoundcloudNewAndHotUSSpider(scrapy.Spider):
    name = 'soundcloud_newandhotUS'
    start_urls = ['https://soundcloud.com/charts/new?genre=all-music&country=US']
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'api-v2.soundcloud.com',
        'Origin': 'https://soundcloud.com',
        'Pragma': 'no-cache',
        'Referer': 'https://soundcloud.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
    }

    def parse(self, response):
        url = 'https://api-v2.soundcloud.com/charts?kind=trending&genre=soundcloud%3Agenres%3Aall-music&region=soundcloud%3Aregions%3AUS&high_tier_only=false&client_id=TyQAtemcOqFFQTCV2qqy3rmP9cOn066j&limit=50&offset=0&linked_partitioning=1&app_version=1584447615&app_locale=en'
        yield scrapy.Request(url, callback=self.parse_api, headers=self.headers)

    def parse_api(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        replacements = [" \(remix\)", " [\(\[].*?[\)\]]", " ft.*", " aka.*", " feat.*", " 🤷🏽‍♂️", " x ", " #.*", "&"]

        for item in data['collection']:
            parsed_title = unidecode(item['track']['title'].lower())
            publisher_metadata = item['track']['publisher_metadata']
            for r in replacements:
                if r == " \(remix\)":
                    parsed_title = re.sub(r, " remix", parsed_title)
                else:
                    parsed_title = re.sub(r, " ", parsed_title)
            if " - " in parsed_title:
                yield {
                    'title': parsed_title,
                    'artist': ""
                }
                continue
            if publisher_metadata and 'artist' in publisher_metadata and publisher_metadata['artist']:
                artist = publisher_metadata['artist'].strip(" ")
            elif item['track']['user']['username']:
                artist = item['track']['user']['username']
            else:
                artist = ""
            yield {
                'title': parsed_title,
                'artist': artist
            }