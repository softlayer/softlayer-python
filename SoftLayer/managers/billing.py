"""
    SoftLayer.billing
    ~~~~~~~~~~~~
    Billing Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import calendar
import datetime

from SoftLayer import utils

import math
import time


class BillingManager(object):
    """Manages Billing details.

    :param SoftLayer.managers.orderingManager
    """

    def _format_date(self, date):
        """format  date.

        :param dt: YY-MM-DD
        """
        result = date.replace('T', ' ')
        return result[0:10]

    def _get_month_delta(self, date1, date2):
        """get month

        :param date1: YY-MM-DD
        :param date2: YY-MM-DD
        :return: delta
        """
        delta = 0
        while True:
            mdays = calendar.monthrange(date1.year, date1.month)[1]
            date1 += datetime.timedelta(days=mdays)
            if date1 <= date2:
                delta += 1
            else:
                break
        return delta

    def __init__(self, client):
        """init

        :param client
        :return: billing account info
        """
        self.client = client
        self.account = self.client['Account']
        self.billing_order = self.client['Billing_Order']

    def get_info(self):
        """get info

        :return: billing account info
        """
        result = self.account.getBillingInfo()
        return result

    def get_balance(self):
        """get balance

        :return: billing account info
        """
        result = self.account.getBalance()
        return result

    def get_next_balance(self):
        """get next balance

        :return: billing account info
        """
        result = self.account.getNextInvoiceTotalAmount()
        return result

    def get_latest_bill_date(self):
        """get latest balance

        :return: billing account info
        """
        result = self.account.getLatestBillDate()
        return result

    def get_next_bill_items(self):
        """get next bill items

        :return: billing account info
        """
        result = self.account.getAllBillingItems()
        return result

    def list_resources(self, from_date=None, to_date=None, **kwargs):
        """Retrieve a list of all ordered resources along with their costing.

        :param dict \\*\\*kwargs: response-level option (limit)
        :returns: Returns a list of dictionaries representing the
        matching ordered resorces by a user along with their costing
        """
        params = {}
        if 'mask' not in kwargs:
            items = set([
                'order[items[description,billingItem[id,hostName,'
                'hourlyRecurringFee,cancellationDate,createDate,'
                'laborFee,oneTimeFee,setupFee]]]'
            ])
            params['mask'] = "mask[%s]" % ','.join(items)

        _filter = utils.NestedDict({})
        user = self.account.getCurrentUser(mask='mask[id]')
        _filter['orders']['userRecordId'] = utils.query_filter(user['id'])
        date_format = '%Y-%m-%d'

        if from_date and to_date:
            _filter['orders']['createDate'] = utils.query_filter_date(
                from_date, to_date)
        elif from_date:
            from_date_filter = '>=' + ' ' + from_date
            _filter['orders']['createDate'] = utils.query_filter(
                from_date_filter)
        elif to_date:
            to_date_filter = '<=' + ' ' + to_date
            _filter['orders']['createDate'] = utils.query_filter(
                to_date_filter)
        orders = self.account.getOrders(filter=_filter.to_dict())
        result = []

        for order in orders:
            billing_order = self.client['Billing_Order']
            params['id'] = order_id = order['id']
            items = billing_order.getItems(**params)
            cost = float(0.0)
            resource_type = ''
            flag = 1
            hostname = ''
            creation_date = ''

            for item in items:
                if flag == 1:
                    resource_type = item['description']

                if 'Core' in resource_type and flag == 1:
                    hostname = item['billingItem']['hostName']
                flag = 0
                usedmonths = 1

                creation_date = item['billingItem']['createDate']
                cancellation_date = item['billingItem']['cancellationDate']

                if 'hourlyRecurringFee' not in item['billingItem']:
                    create_date = datetime.datetime.strptime(
                        self._format_date(
                            item['billingItem']['createDate']), date_format)
                    if cancellation_date:
                        cancel_date = datetime.datetime.strptime(
                            self._format_date(
                                item['billingItem']['cancellationDate']),
                            date_format)
                        usedmonths = self._get_month_delta(create_date,
                                                           cancel_date)
                    else:
                        now = datetime.datetime.strptime(
                            self._format_date(str(datetime.datetime.now())),
                            date_format)
                        usedmonths = self._get_month_delta(create_date, now)

                    usedmonths += 1

                    cost += float(
                        billing_order.getOrderTotalOneTime(
                            id=order['id']
                        ) + billing_order.getOrderTotalRecurring(
                            id=order['id']
                        ) * usedmonths
                    )

                elif not cancellation_date:
                    virtual_guest = self.account.getHourlyVirtualGuests(
                        filter={
                            'hourlyVirtualGuests': {
                                'hourlyVirtualGuests': {
                                    'billingItem': {
                                        'id': {
                                            'operation':
                                                item['billingItem']['id']}}}}})
                    if virtual_guest:
                        cost = virtual_guest[0]['billingItem']
                        ['currentHourlyCharge']

                else:
                    create_date = datetime.datetime.strptime(
                        self._format_date(creation_date), date_format)
                    cancel_date = datetime.datetime.strptime(
                        self._format_date(cancellation_date), date_format)
                    d1_ts = time.mktime(create_date.timetuple())
                    d2_ts = time.mktime(cancel_date.timetuple())
                    usedhours = math.ceil(d2_ts - d1_ts)/3600
                    cost += usedhours * float(
                        item['billingItem']['hourlyRecurringFee']
                    ) + float(
                        item['billingItem']['laborFee']
                    ) + float(
                        item['billingItem']['oneTimeFee']
                    ) + float(
                        item['billingItem']['setupFee'])
            resource = {
                'id': order_id,
                'resourceType': resource_type,
                'hostName': hostname,
                'createDate': creation_date,
                'cost': cost
            }
            result.append(resource)
        return result
