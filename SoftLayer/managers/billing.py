"""
    SoftLayer.cci
    ~~~~~~~~~~~~~
    Billing Manager/helpers
            
    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.utils import NestedDict, query_filter, query_filter_date, IdentifierMixin, lookup
import SoftLayer
from calendar import monthrange
from datetime import datetime, date, timedelta
import math
import time



class BillingManager(object):

    def _format_date(self, dt):
        a = dt.replace('T', ' ')
        return a[0:10]

    def _get_month_delta(self, d1, d2):
        delta = 0
        while True:
            mdays = monthrange(d1.year, d1.month)[1]
            d1 += timedelta(days=mdays)
            if d1 <= d2:
                delta += 1
            else:
                break
        return delta

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.billing_order = self.client['Billing_Order']

    def get_info(self):
        result = self.account.getBillingInfo()
        return result


    def list_resources(self, from_date=None, to_date=None, **kwargs):
        """ Retrieve a list of all ordered resources along with their costing.

        :param dict \\*\\*kwargs: response-level option (limit)
        :returns: Returns a list of dictionaries representing the matching ordered resorces by a user along with their costing

        ::

           # Print out a list of all hourly CCIs in the DAL05 data center.
           # env variables
           # SL_USERNAME = YOUR_USERNAME
           # SL_API_KEY = YOUR_API_KEY
           import SoftLayer
           client = SoftLayer.Client()

           kwargs['from_date'] = '2014-04*'
           mgr = SoftLayer.BillingManager(client)
           for resource in mgr.list_resources(**kwargs):
               print resource['description'], resource['cost']

    """

        params = {}
        if 'mask' not in kwargs:
            items = set([
                'order[items[description,billingItem[id,hostName,hourlyRecurringFee,cancellationDate,createDate,laborFee,oneTimeFee,setupFee]]]'
            ])
            params['mask'] = "mask[%s]" % ','.join(items)

        _filter = NestedDict({})
        user = self.account.getCurrentUser(mask='mask[id]')
        _filter['orders']['userRecordId'] = query_filter(user['id'])
        date_format = '%Y-%m-%d'

        if from_date and to_date:
            _filter['orders']['createDate'] = query_filter_date(from_date, to_date)
        elif from_date:
            from_date_filter = '>=' + ' ' + from_date
            _filter['orders']['createDate'] = query_filter(from_date_filter)
        elif to_date:
            to_date_filter = '<=' + ' ' + to_date
            _filter['orders']['createDate'] = query_filter(to_date_filter)
        print  _filter['orders']['createDate']
        orders = self.account.getOrders(filter=_filter.to_dict())
        total = 0.0
        result = []

        for order in orders:
            print order
            print order['id'], order['orderTypeId']
            billing_order = self.client['Billing_Order']

            params['id'] = order_id = order['id']
            items = billing_order.getItems(**params)
            cost = float(0.0)
            resource_type = ''
            flag = 1
            hostName = ''
            resource = {}
            creation_date = ''
            cancellation_date = ''

            for item in items:
                #print item
                if flag == 1:
                    resource_type = item['description']

                if 'Core' in resource_type and flag == 1:
                    hostName = item['billingItem']['hostName']
                flag = 0
                usedMonths = 1

                creation_date = item['billingItem']['createDate']
                cancellation_date = item['billingItem']['cancellationDate']

                if not 'hourlyRecurringFee' in item['billingItem']:
                    create_date = datetime.strptime(
                        self._format_date(
                            item['billingItem']['createDate']), date_format)
                    if cancellation_date:
                        cancel_date = datetime.strptime(
                            self._format_date(
                                item['billingItem']['cancellationDate']), date_format)
                        usedMonths = self._get_month_delta(create_date, cancel_date)
                    else:
                        NOW = datetime.strptime(
                            self._format_date(str(datetime.now())), date_format)
                        usedMonths = self._get_month_delta(create_date, NOW)

                    usedMonths += 1

                    cost += float(billing_order.getOrderTotalOneTime(
                        id=order['id']) + billing_order.getOrderTotalRecurring(id=order['id']) * usedMonths)

                elif not cancellation_date:
                    virtual_guest = self.account.getHourlyVirtualGuests(
                        filter={
                            'hourlyVirtualGuests': {
                                'hourlyVirtualGuests': {
                                    'billingItem': {
                                        'id': {
                                            'operation': item['billingItem']['id']}}}}})
                    if virtual_guest:
                        cost = virtual_guest[0]['billingItem']['currentHourlyCharge']

                else:
                    create_date = datetime.strptime(
                        self._format_date(
                            creation_date), date_format)
                    cancel_date = datetime.strptime(
                        self._format_date(
                            cancellation_date), date_format)

                    d1_ts = time.mktime(create_date.timetuple())
                    d2_ts = time.mktime(cancel_date.timetuple())

                    usedHours = math.ceil(d2_ts - d1_ts) / 3600

                    cost += usedHours * float(item['billingItem']['hourlyRecurringFee']) + float(item['billingItem']
                                                                                             ['laborFee']) + float(item['billingItem']['oneTimeFee']) + float(item['billingItem']['setupFee'])
            resource = {'id': order_id,
                'resourceType': resource_type,
                'hostName': hostName,
                'createDate': creation_date,
                'cost': cost
            }
            result.append(resource)

        return result