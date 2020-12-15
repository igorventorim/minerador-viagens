# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookingHotelItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    grade = scrapy.Field()
    url = scrapy.Field()
    query_date = scrapy.Field()
    best_price = scrapy.Field()
    # pass


class SchedulingHotelItem(scrapy.Item):
    # INPUT FIELDS
    search_date = scrapy.Field()
    check_in_date = scrapy.Field()
    check_out_date = scrapy.Field()
    people = scrapy.Field()
    # EXTRACT FIELDS
    price = scrapy.Field()
    available = scrapy.Field()
    # name = scrapy.Field()
    room_code = scrapy.Field()
    hotel_code = scrapy.Field()
    limit = scrapy.Field()
    room_name = scrapy.Field()
    hotel_name = scrapy.Field()
    address = scrapy.Field()
    url = scrapy.Field()
    price_by_day = scrapy.Field()
    total_rooms = scrapy.Field()
