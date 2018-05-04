# fund

the spider.py cited from https://blog.csdn.net/yuzhucu/article/details/55261024  by yuzhucu

This Project use the 'Spider.py' to get the specific funds' information which's fund_code is in 'fund.csv'.
Then save the data into Mysql DB, the code to the table was writed in 'Create invest'.
In the 'prepare.py' I read and preprocessing the data from Mysql，and build up a model of lstm to predict 
the nav of the fund based on the last N-days nav data.
