__author__ = 'joseph kodjo-kuma Djomeda'

import MySQLdb
import datetime

class DbLayer:

    def __init__(self, username, password,host, database):

        self.username = username
        self.password = password
        self.host = host
        self.database = database
        self.db = self.getConnection()


    def getConnection(self):
        return MySQLdb.connect(self.host, self.username, self.password, self.database)


    def setFixtures(self):

        self.db = self.getConnection()
        cursor = self.db.cursor()

        cursor.execute("insert into category(id,name,description) values(1,'food','all sort of comestible item'),(2,'ninja tools','any sort of tool according to konoha classifications')")
        cursor.execute("insert into product(id,category_id,product_id,name,price,in_stock,comment) values(1,1,'ra_0001','ramen',30,20,''),(2,2,'we_0001','shuriken',120,100,''),(3,2,'we_0002','kunai',62,95,'')")

        self.db.commit()
        self.db.close()


    def tearDown(self):

        self.db = self.getConnection()
        cursor = self.db.cursor()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("truncate table product")
        cursor.execute("truncate table category")
        cursor.execute("truncate table order_product_map")
        cursor.execute("truncate table `order`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        self.db.commit()
        self.db.close()

    def getAllItems(self):
        # if(not self.db):

        self.db = self.getConnection()

        cursor = self.db.cursor()
        cursor.execute("select c.name as category_name, p.name ,p.id, p.price,p.product_id ,p.comment from product p inner join category c on c.id = p.category_id where in_stock <> 0")
        result = cursor.fetchall()

        self.db.close()
        return result

    def getProductById(self, productId):
        self.db = self.getConnection()

        cursor = self.db.cursor()
        cursor.execute("select * from product where id=%s" ,(productId))
        result = cursor.fetchall()
        self.db.close()
        return result


    def updateOrder(self, orderId, paymentTransactionId, paymentStatus):
        self.db = self.getConnection()

        cursor = self.db.cursor()
        cursor.execute("update `order` set payment_common_id='{0}', order_status='{1}', date_modified='{2}' where order_id='{3}'".format(paymentTransactionId,paymentStatus,datetime.datetime.now(),orderId))
        self.db.commit()
        self.db.close()

    def createOrder(self,orderId, paymentToken, productIdList):

        self.db = self.getConnection()
        cursor = self.db.cursor()
        self.db.autocommit(False)
        order_product_map_query = self.orderProductMapQueryBuilder(orderId,productIdList)
        try:
            cursor.execute("insert into `order`(order_id,payment_token) values ('{0}', '{1}')".format(orderId,paymentToken))
            cursor.execute("insert into order_product_map values" + order_product_map_query)
            self.db.commit()
        except:
            self.db.rollback()
            self.db.close()


    def orderProductMapQueryBuilder(self,orderId, productIdList):

        queryPartString = ""

        for id in productIdList:
            queryPartString +="('{0}',{1}),".format(orderId,id)

        if(queryPartString):
            queryPartString = queryPartString[:-1]

        return queryPartString


    def countValidTransaction(self,paymentToken):

        self.db = self.getConnection()
        cursor = self.db.cursor()
        cursor.execute("select order_id from `order` where payment_token= '{0}' and order_status='PENDING'".format(paymentToken))
        result = cursor.fetchone()
        self.db.close()
        return result

