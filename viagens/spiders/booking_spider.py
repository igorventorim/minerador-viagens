# -*- coding: utf-8 -*-
import scrapy
from viagens.items import BookingHotelItem
from viagens.items import SchedulingHotelItem
from datetime import date
import os
import pandas


class BookingSpider(scrapy.Spider):

    name = "Booking"

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

    def start_requests(self):

        # accept_language = 'pt-BR,pt;q=0.9,pt;q=0.8'
        url = self.domain+'/searchresults.html?is_ski_area={}&city={}&checkin_year={}&checkin_month={}&checkin_monthday={}&checkout_year={}&checkout_month={}&checkout_monthday={}&group_adults={}&group_children={}&no_rooms={}&from_sf={}'.format(
            self.is_ski_area, self.city, self.checkin_year, self.checkin_month, self.checkin_monthday, self.checkout_year, self.checkout_month, self.checkout_monthday, self.group_adults, self.group_children, self.no_rooms, self.from_sf)

        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):

        text_result = response.css('h1::text').get()

        if(text_result != ''):
            qty_hotels = int(text_result.split(': ')[1].split(' ')[0])

        print(response.css('h1::text').get())
        hotels_page = response.css('.sr_item')

        number_of_elements_page = len(hotels_page)
        for hotel in hotels_page:
            name = hotel.css('.sr-hotel__name::text').get().replace('\n', '')
            grade = hotel.css('.bui-review-score__badge::text').get() if hotel.css('.bui-review-score__badge::text').get(
            ) is not None else ""
            hotel_page = self.domain + \
                hotel.css('.hotel_name_link::attr(href)').get()
            hotel_page = hotel_page.replace('\n', '')
            best_price = hotel.css('.bui-price-display__value::text').get()
            best_price = best_price.replace(
                '\n', '').replace('\xa0', ' ') if best_price is not None else best_price
            yield scrapy.Request(url=hotel_page.split('?')[0], headers=self.headers, callback=self.insert_total_rooms)
            yield scrapy.Request(url=hotel_page, headers=self.headers, callback=self.query_rooms)

        if qty_hotels > number_of_elements_page:
            request = response.css('.paging-next::attr(href)').get()
            if request is not None:
                url = self.domain+request
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def query_rooms(self, response):

        today = date.today().strftime("%d-%m-%y")
        hotel_name = response.css('.hp__hotel-name::text').getall()[1]
        hotel_name = hotel_name.replace('\n', '') if hotel_name else hotel_name
        rooms_table = response.css('.hprt-table').css('tr')[1:]
        address = response.css(
            '#showMap2 > span::text').get().replace('\n', '')

        check_in_date = date(
            int(self.checkin_year), int(self.checkin_month), int(self.checkin_monthday))
        check_out_date = date(int(self.checkout_year),
                              int(self.checkout_month), int(self.checkout_monthday))

        self.fix_dates()
        check_in_room = '{}-{}-{}'.format(self.checkin_monthday,
                                          self.checkin_month, self.checkin_year)
        check_out_room = '{}-{}-{}'.format(self.checkout_monthday,
                                           self.checkout_month, self.checkout_year)

        for row in rooms_table:
            room_code = row.css('::attr(data-block-id)').get().split('_')[0]
            hotel_code = row.css('::attr(data-block-id)').get().split('_')[1]
            room_name = row.css(
                '.hprt-roomtype-link').css('.hprt-roomtype-icon-link::text').get()
            room_price = row.css(
                '.bui-price-display__value::text').get()
            room_qtd = len(row.css('.hprt-nos-select > option').getall()) - 1
            room_limit = len(row.css('.bicon-occupancy').getall())
            room_name = room_name.replace('\n', '') if room_name else room_name
            room_price = room_price.replace(
                '\n', '') if room_price else room_price

            total_rooms = self.get_total_rooms(room_code)
            price_by_day = self.get_price_by_day(
                room_price, check_in_date, check_out_date)

            # yield SchedulingHotelItem(room_code=room_code, hotel_code=hotel_code, available=room_qtd, price=room_price,  limit=room_limit, hotel_name=hotel_name, search_date=today, room_name=room_name,  check_in_date=check_in_room, check_out_date=check_out_room, people=self.group_adults, address=address, price_by_day=price_by_day, url=response.url)

            yield SchedulingHotelItem(room_code=room_code, hotel_code=hotel_code, available=room_qtd, price=room_price,  limit=room_limit, hotel_name=hotel_name, search_date=today, room_name=room_name,  check_in_date=check_in_room, check_out_date=check_out_room, people=self.group_adults, address=address, total_rooms=total_rooms, price_by_day=price_by_day, url=response.url)

    def get_total_rooms(self, room_code):
        if room_code in self.total_rooms.keys():
            return self.total_rooms[room_code]
        else:
            return "Indefinido"

    def insert_total_rooms(self, response):
        rooms_table = response.css('.hprt-table').css('tr')[1:]
        for row in rooms_table:
            room_code = row.css('::attr(data-block-id)').get().split('_')[0]
            room_qtd = len(row.css('.hprt-nos-select > option').getall()) - 1
            self.total_rooms['room_code'] = room_qtd

    def get_price_by_day(self, room_price, check_in_date, check_out_date):
        delta = check_out_date - check_in_date
        price = ''
        room_price = room_price.replace(
            '\xa0', '').replace('.', '').replace(',', '.')
        if room_price != '':
            price_splited = room_price.split("R$")
            if len(price_splited) > 1:
                price = float(price_splited[1]) / float(delta.days)
        return str(price)

    def fix_dates(self):
        self.checkin_monthday = self.checkin_monthday if len(
            self.checkin_monthday) > 1 else '0'+self.checkin_monthday
        self.checkout_monthday = self.checkout_monthday if len(
            self.checkout_monthday) > 1 else '0'+self.checkout_monthday
        self.checkin_month = self.checkin_month if len(
            self.checkin_month) > 1 else '0'+self.checkin_month
        self.checkout_month = self.checkout_month if len(
            self.checkout_month) > 1 else '0'+self.checkout_month
