import time
import random
import pymysql
import os
import pandas as pd
import numpy as np

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.optimizers import SGD, Adam


class PyMySQL:
    # 获取当前时间
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
        # 数据库初始化

    def _init_(self, host, user, passwd, db, port=3306, charset='utf8'):
        pymysql.install_as_MySQLdb()
        try:
            self.db = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=3306, charset='utf8')
            # self.db = pymysql.connect(ip, username, pwd, schema,port)
            self.db.ping(True)  # 使用mysql ping来检查连接,实现超时自动重新连接
            print(self.getCurrentTime(), u"MySQL DB Connect Success:", user + '@' + host + ':' + str(port) + '/' + db)
            self.cur = self.db.cursor()
        except  Exception as e:
            print(self.getCurrentTime(), u"MySQL DB Connect Error :%d: %s" % (e.args[0], e.args[1]))
            # 插入数据

    def insertData(self, table, my_dict):
        try:
            # self.db.set_character_set('utf8')
            cols = ', '.join(my_dict.keys())
            values = '"," '.join(my_dict.values())
            sql = "replace into %s (%s) values (%s)" % (table, cols, '"' + values + '"')
            # print (sql)
            try:
                result = self.cur.execute(sql)
                insert_id = self.db.insert_id()
                self.db.commit()
                # 判断是否执行成功
                if result:
                    # print (self.getCurrentTime(), u"Data Insert Sucess")
                    return insert_id
                else:
                    return 0
            except Exception as e:
                # 发生错误时回滚
                self.db.rollback()
                print(self.getCurrentTime(), u"Data Insert Failed: %s" % (e))
                return 0
        except Exception as e:
            print(self.getCurrentTime(), u"MySQLdb Error: %s" % (e))
            return 0

    def getdata(self, items, table, condition):
        sql = "select %s from %s where %s" % (items, table, condition)

        try:
            print(self.cur.execute(sql))
            result = self.cur.fetchall()
            print(result,type(result))
            # for nav in result:
            #     print(nav)
            return result
        except Exception as e:
            # 发生错误时回滚
            self.db.rollback()
            print(self.getCurrentTime(), u"Data Insert Failed: %s" % (e))
            return 0

def load_data(seq_len):
    global mySQL
    mySQL = PyMySQL()
    mySQL._init_('localhost', 'root', 'mysql', 'invest')


    try:
        data = mySQL.getdata('nav', 'fund_nav', 'fund_code="160222"')
        data = list(data)

        sequence_length = seq_len + 1
        result = []
        for index in range(len(data) - sequence_length):
            result.append(data[index: index + sequence_length])



        result = np.array(result)

        row = round(0.9 * result.shape[0])
        train = result[:int(row), :]
        np.random.shuffle(train)
        x_train = train[:, :-1]
        y_train = train[:, -1]
        x_test = result[int(row):, :-1]
        y_test = result[int(row):, -1]

        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

        return [x_train, y_train, x_test, y_test]



    except Exception as e:
        print(e)


def build_model(layers):
    model = Sequential()

    model.add(LSTM(
        input_shape=(layers[1], layers[0]),
        # input_dim=layers[0],
        output_dim=layers[1],
        return_sequences=True))
    model.add(Dropout(0.1))

    model.add(LSTM(
        layers[2],
        return_sequences=False))
    model.add(Dropout(0.1))

    model.add(Dense(
        output_dim=layers[3]))
    model.add(Activation("linear"))

    start = time.time()
    model.compile(loss="mae", optimizer=Adam(lr=0.01))
    print("> Compilation Time : ", time.time() - start)
    return model

def predict_point_by_point(model, data):

    #Predict each timestep given the last sequence of true data, in effect only predicting 1 step ahead each time
    predicted = model.predict(data)
    predicted = np.reshape(predicted, (predicted.size))
    return predicted