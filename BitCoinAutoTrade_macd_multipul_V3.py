import time
import pyupbit
import datetime
import sys
import numpy

access = "KVnT9WKXqSPXW78McpUrBErHxbOeCR9v9XZGOAzE"# 본인 값으로 변경
secret = "SmBGJ9EiYAKoqDQx7VAnnhxqJz9YHygZJyNnKfHJ"# 본인 값으로 변경

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    #2일치 데이터 조회
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    #df.iloc[0]['close'] : 다음날 싯가
    #(df.iloc[0]['high'] - df.iloc[0]['low']) * k : 변동폭
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

#로그인
upbit = pyupbit.Upbit(access, secret)
#INPUT 값 받기
coin = sys.argv[1]
#coin = "DOGE"
file_name = "multipul_log-"+coin+".txt"
file = open(file_name, 'w')
file.write("autotrade start \n")
file.flush()

#my_money = 0
#my_money = get_balance("KRW")
buy_money = 0
krw = 0
rsi_gubun = 0
data = "coin : %s \n" % coin
file.write(data)
file.flush()

KRW_coin = "KRW-"+coin
data = "KRW_coin : %s \n" % KRW_coin
file.write(data)
file.flush()

#2차원 배열 선얼 [14][30]
#당일 - 전일 상승분 배열
up_arr   = numpy.zeros((30, 14))
#당일 - 전일 하락분 배열
down_arr = numpy.zeros((30, 14))
#1차 배열
#상승분 평균
avg_up   = numpy.zeros((30))
#하락분 평균
avg_down = numpy.zeros((30))
#rsi 상승분 기초데이터
rsi_base_up   = numpy.zeros((30))
#rsi 하락분 기초데이터
rsi_base_down = numpy.zeros((30))
#rsi 계산 최종 데이터
rsi_arr = numpy.zeros(30)

#cci
avg_HLC   = numpy.zeros((43))
sum_avg_HLC = numpy.zeros((43))
sum_avg_cal = numpy.zeros((43))
avg_sum_avg_cal = numpy.zeros((43))
cci_price = numpy.zeros((43))

#macd
avg_12day   = numpy.zeros((43))
avg_26day   = numpy.zeros((43))
dnag_jang   = numpy.zeros((43))
signal9     = numpy.zeros((43))
macd_signal = numpy.zeros((43))

# 자동매매 시작
while True:
    try:
        

        #2차원 배열 선얼 [14][30]
        #당일 - 전일 상승분 배열
        up_arr   = numpy.zeros((30, 14))
        #당일 - 전일 하락분 배열
        down_arr = numpy.zeros((30, 14))
        #1차 배열
        #상승분 평균
        avg_up   = numpy.zeros((30))
        #하락분 평균
        avg_down = numpy.zeros((30))
        #rsi 상승분 기초데이터
        rsi_base_up   = numpy.zeros((30))
        #rsi 하락분 기초데이터
        rsi_base_down = numpy.zeros((30))
        #rsi 계산 최종 데이터
        rsi_arr = numpy.zeros(30)

        #cci
        avg_HLC   = numpy.zeros((43))
        sum_avg_HLC = numpy.zeros((43))
        sum_avg_cal = numpy.zeros((43))
        avg_sum_avg_cal = numpy.zeros((43))
        cci_price = numpy.zeros((43))

        #macd
        avg_12day   = numpy.zeros((43))
        avg_26day   = numpy.zeros((43))
        dnag_jang   = numpy.zeros((43))
        signal9     = numpy.zeros((43))
        macd_signal = numpy.zeros((43))
            
        #1분봉 43개 가지고오기
        minute_ohlcv = pyupbit.get_ohlcv(KRW_coin, interval="minute1", count=43)

        i = 0
        j = 0
        ##########################################################################
        #rsi start                                                               #
        ##########################################################################
        for i in range(0,30):
            sum_up = 0
            sum_down = 0

            for j in range(0,14):

                if i == 0 and j == 0:
                    up_arr[0][0]   = 0
                    down_arr[0][0] = 0
                else:
                    #등락 계산(T분 종가- T-1분 종가) 배열에 저장
                    if (minute_ohlcv.close[i+j] - minute_ohlcv.close[i+j-1]) >= 0:
                        up_arr[i][j]   =  (minute_ohlcv.close[i+j] - minute_ohlcv.close[i+j-1])
                        down_arr[i][j] = 0
                    else:
                        up_arr[i][j]   = 0
                        down_arr[i][j] = ((minute_ohlcv.close[i+j] - minute_ohlcv.close[i+j-1]) * -1)


                sum_up   += up_arr[i][j]
                sum_down += down_arr[i][j]
            
            #등락 평균
            avg_up[i]    = (sum_up / 14)
            avg_down[i]  = (sum_down / 14)

        for i in range(0,30):
            if i == 0:
                rsi_base_up[i]   = avg_up[i]
                rsi_base_down[i] = avg_down[i]
            else:
                rsi_base_up[i]   = (((rsi_base_up[i-1] * 13  ) + up_arr[i][13]  ) / 14)
                rsi_base_down[i] = (((rsi_base_down[i-1] * 13) + down_arr[i][13]) / 14)

            #RSI = 상승폭 총합 / (상승폭 총합 + 하락폭 총합)
            rsi_arr[i] = (100 * rsi_base_up[i]) /(rsi_base_up[i] + rsi_base_down[i])
        ##########################################################################
        #rsi end                                                                 #
        ##########################################################################


        i = 0
        j = 0
        ##########################################################################
        #cci start                                                               #
        ##########################################################################
        for i in range(0,43):
            avg_HLC[i] = ((minute_ohlcv.high[i] + minute_ohlcv.low[i] + minute_ohlcv.close[i] ) / 3)
            #print("avg_HLC : %f" % avg_HLC[i])

            if i > 12:
                for j in range(0,14):
                    #print("avg_HLC[i - j] : %f" % avg_HLC[i - j])
                    sum_avg_HLC[i] += avg_HLC[i - j]
                
            sum_avg_HLC[i] = (sum_avg_HLC[i] / 14)
            #print("sum_avg_HLC : %f" % sum_avg_HLC[i])
            sum_avg_cal[i] = (avg_HLC[i] - sum_avg_HLC[i])
            if sum_avg_cal[i] < 0:
                sum_avg_cal[i] = (sum_avg_cal[i] * -1)
            #print("sum_avg_cal : %f" % sum_avg_cal[i])
            
            if i > 26:
                for j in range(0,14):
                    #print("avg_HLC[i - j] : %f" % avg_HLC[i - j])
                    avg_sum_avg_cal[i] += sum_avg_cal[i - j]
            
            avg_sum_avg_cal[i] = (avg_sum_avg_cal[i] / 14)
            #print("avg_sum_avg_cal : %f" % avg_sum_avg_cal[i])


            if i > 26:
                cci_price[i] = ((avg_HLC[i] - sum_avg_HLC[i])/(avg_sum_avg_cal[i] * 0.015))
            #print("cci_price : %f" % cci_price[i])
        ##########################################################################
        #cci end                                                                 #
        ##########################################################################


        i = 0
        j = 0
        ##########################################################################
        #macd start                                                              #
        ##########################################################################
        for i in range(0,43):
            
            if i > 11:
                for j in range(0,12):
                    avg_12day[i] += minute_ohlcv.close[i - j]
                
            avg_12day[i] = (avg_12day[i] / 12)
            #print("avg_12day[i] : %f" % avg_12day[i])


            if i > 25:
                for j in range(0,26):
                    avg_26day[i] += minute_ohlcv.close[i - j]
                
            avg_26day[i] = (avg_26day[i] / 26)
            #print("avg_26day[i] : %f" % avg_26day[i])


            dnag_jang[i] = (avg_12day[i] - avg_26day[i])
            #print("dnag_jang[i] : %f" % dnag_jang[i])

            if i > 33:
                for j in range(0,9):
                    signal9[i] += dnag_jang[i - j]
            
            signal9[i] = (signal9[i] / 9)
            #print("signal9[i] : %f" % signal9[i])

            macd_signal[i] = (dnag_jang[i] - signal9[i])
            #print("macd_signal[i] : %f" % macd_signal[i])
        ##########################################################################
        #macd start                                                              #
        ##########################################################################


        # 현재가
        current_price = get_current_price(KRW_coin)
        # 평균단가
        avg_price = upbit.get_avg_buy_price(KRW_coin)
        # 원화잔고
        current_krw = get_balance("KRW")
        


        
        if krw == 0:
            if (dnag_jang[42] - dnag_jang[41]) >= 0 and (dnag_jang[41] - dnag_jang[40]) < 0 and macd_signal[42] < 0 and cci_price[42] < -100 and rsi_arr[29] < 40:
                #krw = current_krw / 100
                krw = 10000
                buy_money = current_price
                #if krw > 5000:
                if current_krw >= krw:
                    #upbit.buy_market_order(KRW_coin, krw*0.9995) # 비트코인 매수
                    data = "BUY_COIN!  : %f \n" % current_price
                    file.write(data)
                    file.flush()
                    rsi_gubun = -1

        if krw != 0:
            #rsi 60이상(과매수시) 매도
            if dnag_jang[42] - dnag_jang[41] <= 0 or cci_price[42] > 100:
                coin_price = get_balance(coin)
                #upbit.sell_market_order(KRW_coin, coin_price) # 비트코인 전량 매도
                data = "SELL_COIN! : %f \n" % current_price
                file.write(data)
                file.flush()
                buy_money = 0
                krw = 0
                rsi_gubun = 0
        
        
        #추가매수 비법?
        #if rsi_gubun == -1:
        #    if rsi_arr[29] > 35 or cci_price[42] > -100 or macd_signal[42] >= 0:
        #        rsi_gubun = 1
        #elif rsi_gubun == 1:
        #    if rsi_arr[29] < 35 and cci_price[42] < -100 and macd_signal[42] < 0:
        #        #krw = current_krw / 100
        #        if current_price > avg_price:
        #            krw = 9000
        #        elif current_price == avg_price:
        #            krw = 10000
        #        else:
        #            krw = 11000
        #            
        #        buy_money = current_price
        #        #if krw > 5000:
        #        if current_krw >= krw:
        #            #upbit.buy_market_order(KRW_coin, krw*0.9995) # 비트코인 매수
        #            data = "BUY_COIN2!  : %f \n" % current_price
        #            file.write(data)
        #            file.flush()
        #
        #            rsi_gubun = -1


        
        #rsi 매매 기법
        ##rsi +됐다가 다시 35미만(과매도시) 분할 매수
        #if rsi_gubun == -1:
        #    if rsi_arr[29] > 35 or cci_price[42] > -100 or macd_signal[42] >= 0:
        #        rsi_gubun = 1
        #elif rsi_gubun == 1:
        #    if rsi_arr[29] < 35 and cci_price[42] < -100 and macd_signal[42] < 0:
        #        #krw = current_krw / 100
        #        if current_price > avg_price:
        #            krw = 9000
        #        elif current_price == avg_price:
        #            krw = 10000
        #        else:
        #            krw = 11000
        #            
        #        buy_money = current_price
        #        #if krw > 5000:
        #        if current_krw >= krw:
        #            #upbit.buy_market_order(KRW_coin, krw*0.9995) # 비트코인 매수
        #            data = "BUY_COIN2!  : %f \n" % current_price
        #            file.write(data)
        #            file.flush()
        #
        #            rsi_gubun = -1
        #
        #
        #if krw == 0:
        #    #rsi 35미만(과매도시) 매수
        #    if rsi_arr[29] < 35 and cci_price[42] < -100 and macd_signal[42] < 0:
        #        #krw = current_krw / 100
        #        krw = 10000
        #        buy_money = current_price
        #        #if krw > 5000:
        #        if current_krw >= krw:
        #            #upbit.buy_market_order(KRW_coin, krw*0.9995) # 비트코인 매수
        #            data = "BUY_COIN!  : %f \n" % current_price
        #            file.write(data)
        #            file.flush()
        #            rsi_gubun = -1
        #
        #if krw != 0:
        #    #rsi 60이상(과매수시) 매도
        #    if rsi_arr[29] >= 60:
        #        coin_price = get_balance(coin)
        #        #upbit.sell_market_order(KRW_coin, coin_price) # 비트코인 전량 매도
        #        data = "SELL_COIN! : %f \n" % current_price
        #        file.write(data)
        #        file.flush()
        #        buy_money = 0
        #        krw = 0
        #        rsi_gubun = 0

        time.sleep(3)
    except Exception as e:
        print(e)
        file.close()
        time.sleep(3)