# -*- coding: utf-8 -*-
import scrapy, json, re


class ShazamDiscoveryCanadaSpider(scrapy.Spider):
    name = 'shazam_discovery_xanada'
    start_urls = ['https://www.shazam.com/gb/charts/discovery/canada']
    headers = {
        'authority': 'www.shazam.com',
        'method': 'GET',
        'path': '/shazam/v2/en/CA/web/-/tracks/risers-country-chart-CA?pageSize=20&startFrom=0',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'cookie': 'geoip_country=CA; geoip_lat=49.273; geoip_long=-123.012; _ga=GA1.2.523067025.1581555067; _gid=GA1.2.2013236128.1581752813',
        'pragma': 'no-cache',
        'referer': 'https://www.shazam.com/gb/charts/discovery/canada',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }

    def parse(self, response):
        url = 'https://www.shazam.com/shazam/v2/en/CA/web/-/tracks/risers-country-chart-CA?pageSize=20&startFrom=0'
        yield scrapy.Request(url, callback=self.parse_api, headers=self.headers)

    def parse_api(self,response):
        raw_data = response.body
        data = json.loads(raw_data)
        replacements = [" \(Remix\)", " [\(\[].*?[\)\]]", " ft.*", " Aka.*", " feat.*", " FT.*", ",.*"]
        for item in data['chart']:
            parsed_title = item['heading']['title']
            for r in replacements:
                if r == " \(Remix\)":
                    parsed_title = re.sub(r, " Remix", parsed_title)
                else:
                    parsed_title = re.sub(r, "", parsed_title)
            yield {
                'title': parsed_title,
                'artist': item['heading']['subtitle']
            }
