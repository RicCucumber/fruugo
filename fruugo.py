from collections import namedtuple
import requests
import configparser
from pathlib import Path
import base64
import xml.etree.ElementTree as ET
import re

class Fruugo:
    def __init__(self, account):
        def generate_token():
            #base64 token generation
            user, password = self.config[self.account]['user'], self.config[self.account]['password']
            return base64.b64encode(f'{user}:{password}'.encode()).decode()

        self.base_path = Path(__file__).parent
        self.account = account
        self.config = configparser.ConfigParser()
        self.config.read(str(self.base_path / 'fruugo.ini'))
        user, password = self.config[self.account]['user'], self.config[self.account]['password']
        self.url = 'https://www.fruugo.com/'
        self.headers = {
            'Authorization': f'Basic {generate_token()}'
        }

    def send_request(self, params=''):
        return requests.get(url=self.url+self.api_call, headers=self.headers, params=params)



class FruugoGetOrders(Fruugo):

    def __init__(self, user, params=''):

        columns = [
            'customer_order_id',
            'order_id',
            'order_date',
            'order_release_date',
            'order_status',
            'customer_language_code',
            'shipping_first_name',
            'shipping_last_name',
            'shipping_street_address',
            'shipping_city',
            'shipping_province',
            'shipping_postal_code',
            'shipping_country_code',
            'shipping_phone_number',
            'shipping_method',
            'shipping_cost_incl_vat',
            'shipping_cost_vat',
            'product_id',
            'sku_id',
            'fruugo_product_id',
            'fruugo_sku_id',
            'currency_code',
            'item_price_incl_vat',
            'item_vat',
            'total_price_incl_vat',
            'total_vat',
            'vat_percentage',
            'total_number_of_items',
            'pending_items',
            'confirmed_items',
            'shipped_items',
            'cancelled_items',
            'return_announced_items',
            'returned_items',
            'items_with_exceptions'
        ]

        super().__init__(user)
        self.api_call = 'orders/download'
        self.params = params
        self.order_tuple = namedtuple('Order', field_names=self.columns)


    def get(self):
        return self.get_request(params=self.params)


    def parse_xml(self, xml_string):
        result = []
        #replace xmlns value on " " for more pretty parsing code
        xml_string = re.sub(pattern='(?<=xmlns:o=)"[^"]+"', repl='" "', string=xml_string)
        root = ET.fromstring(xml_string)
        for order in root:
            for line in order.find('.//{ }orderLines'):
                result.append(self.order_tuple(
                        order.find('.//{ }customerOrderId').text,
                        order.find('.//{ }orderId').text,
                        order.find('.//{ }orderDate').text,
                        order.find('.//{ }orderReleaseDate').text,
                        order.find('.//{ }orderStatus').text,
                        order.find('.//{ }customerLanguageCode').text,
                        order.find('.//{ }shippingAddress/{ }firstName').text,
                        order.find('.//{ }shippingAddress/{ }lastName').text,
                        order.find('.//{ }shippingAddress/{ }streetAddress').text,
                        order.find('.//{ }shippingAddress/{ }city').text,
                        order.find('.//{ }shippingAddress/{ }province').text,
                        order.find('.//{ }shippingAddress/{ }postalCode').text,
                        order.find('.//{ }shippingAddress/{ }countryCode').text,
                        order.find('.//{ }shippingAddress/{ }phoneNumber').text,
                        order.find('.//{ }shippingMethod').text,
                        order.find('.//{ }shippingCostInclVAT').text,
                        order.find('.//{ }shippingCostVAT').text,
                        line.find('.//{ }productId').text,
                        line.find('.//{ }skuId').text,
                        line.find('.//{ }skuName').text,
                        line.find('.//{ }fruugoProductId').text,
                        line.find('.//{ }fruugoSkuId').text,
                        line.find('.//{ }currencyCode').text,
                        line.find('.//{ }itemPriceInclVat').text,
                        line.find('.//{ }itemVat').text,
                        line.find('.//{ }totalPriceInclVat').text,
                        line.find('.//{ }totalVat').text,
                        line.find('.//{ }vatPercentage').text,
                        line.find('.//{ }totalNumberOfItems').text,
                        line.find('.//{ }confirmedItems').text,
                        line.find('.//{ }shippedItems').text,
                        line.find('.//{ }cancelledItems').text,
                        line.find('.//{ }returnAnnouncedItems').text,
                        line.find('.//{ }returnedItems').text,
                        line.find('.//{ }itemsWithException').text,
                    )
                )

        return result
