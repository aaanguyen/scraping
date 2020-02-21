# -*- coding: utf-8 -*-
import scrapy, json, re


class SoundcloudTop50usSpider(scrapy.Spider):
    name = 'soundcloud_top50us'
    start_urls = ['https://soundcloud.com/charts/top?genre=all-music&country=US']
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }

    def parse(self, response):
        url = 'https://api-v2.soundcloud.com/charts?kind=top&genre=soundcloud%3Agenres%3Aall-music&region=soundcloud%3Aregions%3AUS&high_tier_only=false&client_id=qeWb21nmKO1VUDsY88W1341i7kO1JXeK&limit=50&offset=0&linked_partitioning=1&app_version=1581677269&app_locale=en'
        yield scrapy.Request(url, callback=self.parse_api, headers=self.headers)

    def parse_api(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        replacements = [" \(Remix\)", " [\(\[].*?[\)\]]", " ft.*", " Aka.*", " feat.*", " FT.*", ",.*"]

        for item in data['collection']:
            parsed_title = item['track']['title'].split(" - ")[-1]
            if r == " \(Remix\)":
                    parsed_title = re.sub(r, " Remix", parsed_title)
                else:
                    parsed_title = re.sub(r, "", parsed_title)
            if 'artist' in item['track']['publisher_metadata'] and item['track']['publisher_metadata']['artist']:
                artist = item['track']['publisher_metadata']['artist']
            elif item['track']['user']['username']:
                artist = item['track']['user']['username']
            else:
                artist = ""
            yield {
                'title': parsed_title,
                'artist': artist
            }