import scrapy
from viagens.items import SchedulingHotelItem
from datetime import date
# from scrapy_splash import SplashRequest


class AirbnbSpider(scrapy.Spider):
    name = 'Airbnb'
    allowed_domains = ['airbnb.com.br']

    domain = 'https://airbnb.com.br'

    checkin = '2020-12-12'
    checkout = '2020-12-20'
    adults = '2'
    query = 'Campos do Jordão - SP'

    def start_requests(self):
        url = 'https://www.airbnb.com.br/s/Campos-do-Jord%C3%A3o-~-SP/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&query=Campos%20do%20Jord%C3%A3o%20-%20SP&place_id=ChIJff6EvbiIzJQRXrpQN8sjgDQ&checkin={}&checkout={}&adults={}&source=structured_search_input_header&search_type=autocomplete_click'.format(
            self.checkin, self.checkout, self.adults)

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        print(response.css('._14i3z6h::text').get())
        print(response.css('._1snxcqc::text').get())

        hotels_page = response.css('._gig1e7')

        number_of_elements_page = len(hotels_page)
        for hotel in hotels_page:
            hotel_page = self.domain + \
                hotel.css('._gjfol0').css('::attr(href)').get()

            today = date.today().strftime("%d-%m-%y")
            room_price = hotel.css('._ebe4pze::text').get()

            if room_price:
                room_price = room_price.replace('Total de ', '')

            hotel_name = hotel.css('._1c2n35az::text').get()
            room_code = hotel_page.split('/rooms/')[1].split('?')[0]

            yield SchedulingHotelItem(code=room_code, price=room_price, hotel_name=hotel_name, search_date=today, check_in_date=self.checkin, check_out_date=self.checkout, people=self.adults, url=hotel_page)

        arrow_next = response.css('._i66xk8d')
        if arrow_next:
            url = self.domain + arrow_next.css('::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.parse)
