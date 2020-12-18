# -*- coding: utf-8 -*-
import scrapy
from viagens.items import BookingHotelItem
from viagens.items import SchedulingHotelItem
from datetime import date
import os
import pandas
from viagens.sqlite import Sqlite


class BookingSpider(scrapy.Spider):

    name = "BookingDB"

    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Language': 'pt-BR,en;q=0.9',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
    }

    domain = 'https://www.booking.com'
    TABLENAME = "rooms_occupation"

    def __init__(self, city='-634196', checkin_year='2020', checkin_month='12', checkin_monthday='10', checkout_year='2020', checkout_month='12', checkout_monthday='18', group_adults='2', group_children='0', no_rooms='1'):
        self.is_ski_area = '0'
        self.city = city
        self.checkin_year = checkin_year
        self.checkin_month = checkin_month
        self.checkin_monthday = checkin_monthday
        self.checkout_year = checkout_year
        self.checkout_month = checkout_month
        self.checkout_monthday = checkout_monthday
        self.group_adults = group_adults
        self.group_children = group_children
        self.no_rooms = no_rooms
        self.from_sf = '1'
        self.total_rooms = {}
        self.db = Sqlite("Booking.db")
        self.db.create_database()
        columns = '''
        room_code INTEGER PRIMARY KEY,
        qty INTEGER NOT NULL
        '''
        self.db.create_table(self.TABLENAME, columns)

    def start_requests(self):

        url = self.domain+'/searchresults.html?is_ski_area={}&city={}&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&group_children={}&no_rooms={}&from_sf={}'.format(
            self.is_ski_area, self.city, self.checkin_year, self.checkin_month, self.checkin_monthday, self.checkout_year, self.checkout_month, self.checkout_monthday, self.group_adults, self.group_children, self.no_rooms, self.from_sf)

        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        text_result = response.css('h1::text').get()

        if(text_result != ''):
            qty_hotels = int(text_result.split(': ')[1].split(' ')[0])

        hotels_page = response.css('.sr_item')

        number_of_elements_page = len(hotels_page)
        for hotel in hotels_page:
            hotel_page = self.domain + \
                hotel.css('.hotel_name_link::attr(href)').get()
            hotel_page = hotel_page.replace('\n', '')
            yield scrapy.Request(url=hotel_page, headers=self.headers, callback=self.query_rooms)

        if qty_hotels > number_of_elements_page:
            request = response.css('.paging-next::attr(href)').get()
            if request is not None:
                url = self.domain+request
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def query_rooms(self, response):
        rooms_table = response.css('.hprt-table').css('tr')[1:]
        for row in rooms_table:
            room_code = row.css('::attr(data-block-id)').get().split('_')[0]
            room_qtd = len(row.css('.hprt-nos-select > option').getall()) - 1
            total_rooms = self.get_total_rooms(room_code, room_qtd)

    def get_total_rooms(self, room_code, room_qtd):
        room_code = "\'{}\'".format(room_code)
        result = self.db.read_table(
            self.TABLENAME, column_identify="room_code", value_column_identify=room_code)
        total_rooms = self.sinc_db(result, room_code, room_qtd)
        return total_rooms

    def sinc_db(self, result, room_code, room_qtd):
        max_rooms = room_qtd
        if len(result) > 0:
            qty = result[0][1]
            if(int(qty) < int(room_qtd)):
                self.db.update_element(
                    self.TABLENAME, "qty", room_qtd, "room_code", room_code)
            else:
                max_rooms = qty
        else:
            struct = "room_code,qty"
            values = "{},{}".format(room_code, room_qtd)
            self.db.insert_element(self.TABLENAME, struct, values)

        return max_rooms
