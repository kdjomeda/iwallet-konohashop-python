from flask import Flask, request, session, g, redirect, url_for, abort, render_template
from classes.DbLayer import DbLayer
import uuid,decimal
from classes.Integrator import Integrator


app = Flask(__name__)
app.config.from_pyfile("config/config.py")
db = DbLayer(app.config['USERNAME'],app.config['PASSWORD'],app.config['HOST'],app.config['DBNAME'])
iWallet = Integrator(app.config["API_IWALLET_NAMESPACE"], app.config["API_IWALLET_WSDL"], app.config["API_IWALLET_VERSION"], app.config["API_IWALLET_MERCHANT_EMAIL"], app.config["API_IWALLET_MERCHANT_KEY"], app.config["API_IWALLET_SERVICE_TYPE"], app.config["API_IWALLET_INTEGRATION_MODE"])

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/viewitems')
def showitems():
    items = db.getAllItems()
    return render_template("viewitems.html",rows=items)

@app.route("/checkout", methods=['POST'])
def processCheckout():


    listOfIds = request.form.getlist("orderItems")
    result = doWork(listOfIds)

    if ' ' in result:
        return result
    else:
        return redirect(result,302)

@app.route('/fixtures')
def runfixtures():
    db.tearDown()
    db.setFixtures()
    return "Fixures run"


@app.route('/receivecallback')
def parsecallback():

    status_code = request.args.get("status")
    transaction_id = request.args.get("transac_id")
    order_id = request.args.get("cust_ref")
    payment_token = request.args.get("pay_token")

    if None == status_code or None == order_id  or None == payment_token:
        return "Not good, details are missing or someone is messing with you"

    payment_status = parseTransactionStatusCode(status_code)

    if None == transaction_id or len(transaction_id) == 0:
        db.updateOrder(order_id,"","FAILED")
        return "Empty or Null Transaction Id"

    if not checkValidity(payment_token,order_id):
        return "There is no transaction corresponding to the received payment token. Please contact iWallet support"

    order_result = iWallet.verifyMobilePayment(order_id)

    if order_result.success:
        db.updateOrder(order_id,transaction_id,payment_status)
        iWallet.confirmTransaction(payment_token,transaction_id)
        return "Yatta!! Your order is on the way"
    else:
        iWallet.cancelTransaction(payment_token,transaction_id)
        return "Something seems to be wrong with your order, Kindly start afresh"

    return "{0}".format(order_result.success)



def doWork(listOfProductIds):

    arrayOfOrderItem = iWallet.buildAPIObject('ArrayOfOrderItem')

    for productId in listOfProductIds:
        dbProducts = db.getProductById(productId)
        fetchedItem = dbProducts[0]
        orderItem = iWallet.buildOrderItem(fetchedItem[2],fetchedItem[3],fetchedItem[4],1,fetchedItem[4])
        arrayOfOrderItem.OrderItem.append(orderItem)

    return proccessIwalletOrder(listOfProductIds,arrayOfOrderItem)
    #return redirect("http://www.google.com",code=302)


def proccessIwalletOrder(productIds, arrayOfOrderItems):

    order_id= uuid.uuid1()
    grandSubTotal = grandSubTotalCalculator(arrayOfOrderItems)
    flatShippingCost = app.config["SHIPPINGCOST"]
    tax = app.config["TAXES"]
    taxAmount = grandSubTotal * tax/100
    D = decimal.Decimal

    total = grandSubTotal+ D(taxAmount)+D(flatShippingCost)
    result = iWallet.processPaymentOrder(order_id,grandSubTotal,flatShippingCost,taxAmount,total,"konohashop items","Tutorial shop",arrayOfOrderItems)
    paymentToken = result

    if ' ' in paymentToken:
       message = "Payment Not Successful !"
       return message
    else:
        db.createOrder(order_id,paymentToken,productIds)
        redirectUrl = "{0}{1}".format(app.config["API_IWALLET_REDIRECT_URL"],paymentToken)
        return redirectUrl


def grandSubTotalCalculator(arrayOfOrderItems):
    subtotal = 0
    for orderItem in arrayOfOrderItems.OrderItem:
        subtotal += orderItem.SubTotal
    return subtotal


def parseTransactionStatusCode(status_code):

     status_code = int(status_code)

     if status_code == 0:
         return "success"
     elif status_code == -2:
         return "cancelled"
     elif status_code == -1:
         return "error"
     else:
         return "unknown"


def checkValidity(paymentToken,orderId):

    savedOrderIdString = db.countValidTransaction(paymentToken)
    if None == savedOrderIdString or len(savedOrderIdString[0]) == 0:
        return False
    if orderId != savedOrderIdString[0]:
        return False

    return  True

if __name__ == '__main__':
    app.run(debug=True)
