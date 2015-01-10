__author__ = 'joseph kodjo-kuma Djomeda'

from suds.client import Client
from suds.sax.element import Element

class Integrator:



    def __init__(self,nspace, wsdl, api_version, merchant_email, merchant_secret_key, service_type, integration_mode):

        self.iwl = Client(wsdl)

        #this method equally works as well. it's a matter of preference
        # namespace = (None,nspace)
        # apiVersion = Element('APIVersion').setText(api_version)
        # merchantEmail = Element('MerchantEmail').setText(merchant_email)
        # merchantKey = Element('MerchantKey').setText(merchant_secret_key)
        # serviceType = Element('SvcType').setText(service_type)
        # integrationMode = Element("UseIntMode").setText(integration_mode)
        #
        # paymentHeader = Element('PaymentHeader',ns = namespace).append(apiVersion).append(merchantEmail).append(merchantKey).append(serviceType).append(integrationMode)


        paymentHeader = self.iwl.factory.create('PaymentHeader')
        paymentHeader.APIVersion = api_version
        paymentHeader.MerchantKey = merchant_secret_key
        paymentHeader.MerchantEmail = merchant_email
        paymentHeader.SvcType = service_type
        paymentHeader.UseIntMode = integration_mode
        #
        self.iwl.set_options(soapheaders=paymentHeader)
        # print self.iwl



    def mobilePaymentOrder(self, orderId, subtotal, shippingCost, taxAmount,  total,comment1, comment2, orderItems):
        paymentResult = self.iwl.service.mobilePaymentOrder(orderId, subtotal,  shippingCost, taxAmount,  total, comment1,  comment2, orderItems )
        return paymentResult


    def processPaymentOrder(self, orderId, subtotal, shippingCost,  taxAmount,  total, comment1,  comment2, orderItems):
        paymentResult = self.iwl.service.ProcessPaymentOrder(orderId,subtotal,shippingCost,taxAmount,total,comment1,comment2,orderItems)
        return paymentResult

    def processPaymentJSON(self, orderId,  amount, comment1, comment2,  orderItems) :
        paymentResult = self.iwl.service.processPaymentJSON(self,orderId,amount,comment1,comment2,orderItems)
        return paymentResult

    def confirmTransaction(self, payToken,  transactionId):
        paymentResult = self.iwl.service.ConfirmTransaction(payToken,transactionId)
        return paymentResult

    def generatePaymentCode(self, orderId, subtotal, shippingCost,  taxAmount,  total, comment1,  comment2,  orderItems,payerName,  payerMobile, providerName, providerType):
        paymentResult = self.iwl.service.generatePaymentCode(orderId,subtotal,shippingCost,taxAmount,total,comment1,comment2,orderItems,payerName,payerMobile,providerName, providerType)
        return paymentResult

    def verifyMobilePayment(self, orderId):
        paymentResult = self.iwl.service.verifyMobilePayment(orderId)
        return paymentResult

    def cancelTransaction(self, payToken,  transactionId):
        paymentResult = self.iwl.service.cancelTransaction(payToken,transactionId)
        return paymentResult

    def checkPaymentStatus(self, orderId,  providerName,providerType):
        paymentResult = self.iwl.service.checkPaymentStatus(orderId,providerName,providerType)
        return paymentResult

    def processOrder(self,amount,custRef, comment1, comment2, unitPrice, quantity, item, useToken,  useIntMode):
        paymentResult = self.iwl.service.processOrder(custRef,comment1,comment2,unitPrice,quantity,item,useToken,useIntMode)
        return paymentResult

    def buildOrderItem(self,item_code, item_name, unit_price, quantity, sub_total):

        orderItem = self.iwl.factory.create('OrderItem')
        orderItem.ItemCode = item_code
        orderItem.ItemName = item_name
        orderItem.UnitPrice = unit_price
        orderItem.Quantity = quantity
        orderItem.SubTotal = sub_total
        # print orderItem
        return orderItem

    def buildAPIObject(self,objectname):
        object = self.iwl.factory.create(objectname)
        return object