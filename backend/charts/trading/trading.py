import ta
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
from ta.trend import ADXIndicator
from tradingview_ta import TA_Handler,Exchange
from tradingview_ta import Interval as tvtaInterval
import sqlite3, os
import numpy as np
from add import coins_dict
from datetime import datetime, timedelta
from fvg import find_fvg_levels


tv = TvDatafeed()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "papers.sqlite3")
conn = sqlite3.connect(db_path)

interval_dict = {
    '1m' : Interval.in_1_minute,
    '5m' : Interval.in_5_minute,
    '15m': Interval.in_15_minute,
    '30m': Interval.in_30_minute,
    '1h' : Interval.in_1_hour,
    '4h' : Interval.in_4_hour,
    '1d' : Interval.in_daily,
    '1w' : Interval.in_weekly,
    '1mo': Interval.in_monthly
}
interval_mapping = {
    "1h": 60,
    "4h": 240,
    "1d": 1440
}


def rational_quadratic_kernel(x, y, h, alpha):
    n = len(x)
    y_hat = np.zeros(n)

    for i in range(n):
        weights = (1 + ((x[i] - x) ** 2) / (alpha * h ** 2)) ** (-alpha)
        weights /= np.sum(weights)
        y_hat[i] = np.sum(weights * y)

    return y_hat

# ATR Hesaplama
def compute_atr(high, low, close, length=60):
    tr = np.maximum(high - low, np.maximum(abs(high - np.roll(close, 1)), abs(low - np.roll(close, 1))))
    tr[0] = np.nan  
    atr = pd.Series(tr).rolling(window=length, min_periods=1).mean().to_numpy()
    return atr

def compute_bounds(yhat, atr, near_factor=1.85, far_factor=5.9, top_factor=10):
    upper_near = yhat + near_factor * atr
    upper_far = yhat + far_factor * atr
    upper_top = yhat + top_factor *atr 
    lower_near = yhat - near_factor * atr
    lower_far = yhat - far_factor * atr
    lower_top = yhat - top_factor *atr 
    return upper_near, upper_far, upper_top, lower_near, lower_far, lower_top


def update(SYMBOL, EXCHANGE, INTERVAL, BAR_COUNT):
    data = tv.get_hist(symbol=SYMBOL, exchange=EXCHANGE, interval=interval_dict.get(INTERVAL), n_bars=BAR_COUNT+28)
    data = add_indicators(data)
    return data

def calculate_bar_count_for_paper(PAPER_NAME , INTERVAL):
    current_data = tv.get_hist(symbol='BTCUSDT', exchange='BINANCE', interval=interval_dict.get(INTERVAL),n_bars=1)
    current_data = current_data.reset_index()
    current_datetime = str(current_data['datetime'].iloc[-1])
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {PAPER_NAME}on{INTERVAL} ORDER BY rowid DESC LIMIT 1;')
    last_row = cursor.fetchone()
    last_datetime = str(last_row[0])

    last_datetime = datetime.strptime(last_datetime, "%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
    time_difference = current_datetime-last_datetime
    print("Fark:", time_difference)

    interval_minutes = interval_mapping["4h"]
    missing_bar_count = time_difference.total_seconds() / (interval_minutes * 60)

    return missing_bar_count

def get_data(SYMBOL, EXCHANGE, INTERVAL):
    data = tv.get_hist(symbol=SYMBOL, exchange=EXCHANGE, interval=interval_dict.get(INTERVAL), n_bars=3000)
    return add_indicators(data)


def add_indicators(data):
    data['rsi_14'] = ta.momentum.RSIIndicator(data['close'], window=14).rsi()

    macd = ta.trend.MACD(data['close'])
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()

    stoch = ta.momentum.StochasticOscillator(data['high'], data['low'], data['close'], window=14, smooth_window=3)
    data['stoch_k'] = stoch.stoch()
    data['stoch_d'] = stoch.stoch_signal()

    # CMF
    data['cmf'] = ta.volume.ChaikinMoneyFlowIndicator(data['high'], data['low'], data['close'], data['volume'], window=21).chaikin_money_flow()

    # CCI
    data['cci'] = ta.trend.CCIIndicator(data['high'], data['low'], data['close'], window=10).cci()

    # MFI
    data['mfi'] = ta.volume.MFIIndicator(data['high'], data['low'], data['close'], data['volume'], window=14).money_flow_index()

    # OBV
    data['obv'] = ta.volume.OnBalanceVolumeIndicator(data['close'], data['volume']).on_balance_volume()

    # DIOSC (ADX based on directional movement index)
    adx = ADXIndicator(high=data['high'], low=data['low'], close=data['close'], window=14)
    data['dmi_positive'] = adx.adx_pos()
    data['dmi_negative'] = adx.adx_neg()
    data['adx'] = adx.adx()

    short_ema_volume = data['volume'].ewm(span=12, adjust=False).mean()  # Short EMA of volume
    long_ema_volume = data['volume'].ewm(span=26, adjust=False).mean()  # Long EMA of volume
    data['v_macd'] = short_ema_volume - long_ema_volume  # VMACD line
    data['v_macd_signal'] = data['v_macd'].ewm(span=9, adjust=False).mean()

    data = data.reset_index(drop=False)

    return add_divergences(data)

def add_divergences(data):
    
    def bearish_rsi_divergence(data, lookback=24):
        rsi_values = data['rsi_14']
        divergence_points = []

        for i in range(lookback, len(data)-1):
            recent_rsi_values = rsi_values[i-lookback:i]
            recent_price_values = data['high'].iloc[i-lookback:i]

            if data['high'].iloc[i] > max(recent_price_values) and rsi_values[i] <= max(recent_rsi_values):
                divergence_points.append(i)
        
        data['Bearish_RSI_Divergence'] = False
        data.loc[divergence_points, 'Bearish_RSI_Divergence'] = True
        return data

    def bearish_cmf_divergence(data, lookback_per=24):
        cmf_values = data['cmf']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_cmf_values = cmf_values[i-lookback_per:i]
            recent_price_values = data['high'].iloc[i-lookback_per:i]

            if (data['high'].iloc[i] > max(recent_price_values) and cmf_values[i] <= max(recent_cmf_values)):
                divergence_points.append(i)

        data['Bear_Divergence_CMF'] = False
        data.loc[divergence_points, 'Bear_Divergence_CMF'] = True
        return data

    def bearish_macd_divergence(data, lookback_per=24):
        macd_values = data['macd']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_macd_values = macd_values[i-lookback_per:i]
            recent_price_values = data['high'].iloc[i-lookback_per:i]

            if (data['high'].iloc[i] > max(recent_price_values) and macd_values[i] <= max(recent_macd_values)):
                divergence_points.append(i)

        data['Bear_Divergence_MACD'] = False
        data.loc[divergence_points, 'Bear_Divergence_MACD'] = True
        return data

    def bearish_stoch_divergence(data, lookback=24):
        stoch_values = data['stoch_k']
        divergence_points = []

        for i in range(lookback, len(data)-1):
            recent_stoch_values = stoch_values[i-lookback:i]
            recent_price_values = data['high'].iloc[i-lookback:i]

            if data['high'].iloc[i] > max(recent_price_values) and stoch_values[i] <= max(recent_stoch_values):
                divergence_points.append(i)

        data['Bearish_Stoch_Divergence'] = False
        data.loc[divergence_points, 'Bearish_Stoch_Divergence'] = True
        return data

    def bearish_cci_divergence(data, lookback_per=24):
        cci_values = data['cci']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_cci_values = cci_values[i-lookback_per:i]
            recent_price_values = data['high'].iloc[i-lookback_per:i]

            if (data['high'].iloc[i] > max(recent_price_values) and cci_values[i] <= max(recent_cci_values)):
                divergence_points.append(i)

        data['Bear_Divergence_CCI'] = False
        data.loc[divergence_points, 'Bear_Divergence_CCI'] = True
        return data

    def bearish_mfi_divergence(data, lookback_per=24):
        mfi_values = data['mfi']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_mfi_values = mfi_values[i-lookback_per:i]
            recent_price_values = data['high'].iloc[i-lookback_per:i]

            if (data['high'].iloc[i] > max(recent_price_values) and mfi_values[i] <= max(recent_mfi_values)):
                divergence_points.append(i)

        data['Bear_Divergence_MFI'] = False
        data.loc[divergence_points, 'Bear_Divergence_MFI'] = True
        return data

    def bearish_obv_divergence(data, lookback_per=24):
        obv_values = data['obv']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_obv_values = obv_values[i-lookback_per:i]
            recent_price_values = data['high'].iloc[i-lookback_per:i]

            if (data['high'].iloc[i] > max(recent_price_values) and obv_values[i] <= max(recent_obv_values)):
                divergence_points.append(i)

        data['Bear_Divergence_OBV'] = False
        data.loc[divergence_points, 'Bear_Divergence_OBV'] = True
        return data

    def bearish_diosc_divergence(data, lookback_per=24):
        dmi_positive = data['dmi_positive']
        dmi_negative = data['dmi_negative']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_dmi_values = dmi_positive[i-lookback_per:i]
            recent_price_values = data['high'].iloc[i-lookback_per:i]

            # Bearish divergence: Higher highs in price, but lower or equal DMI+
            if (data['high'].iloc[i] > max(recent_price_values) and dmi_positive[i] <= max(recent_dmi_values)):
                divergence_points.append(i)

        data['Bear_DIOSC_Divergence'] = False
        data.loc[divergence_points, 'Bear_DIOSC_Divergence'] = True

        return data

    def bearish_vmacd_divergence(data, lookback_per=24):
        v_macd_values = data['v_macd']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_v_macd_values = v_macd_values[i-lookback_per:i]
            recent_price_values = data['high'].iloc[i-lookback_per:i]

            # Bearish divergence: Price makes higher highs, VMACD makes lower highs
            if (data['high'].iloc[i] > max(recent_price_values) and v_macd_values[i] <= max(recent_v_macd_values)):
                divergence_points.append(i)

        data['Bear_VMACD_Divergence'] = False
        data.loc[divergence_points, 'Bear_VMACD_Divergence'] = True

        return data


    def bullish_rsi_divergence(data, lookback_per=24):
        rsi_values = data['rsi_14']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_rsi_values = rsi_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and rsi_values[i] >= min(recent_rsi_values)):
                divergence_points.append(i)

        data['Bull_Divergence'] = False
        data.loc[divergence_points, 'Bull_Divergence'] = True

        return data

    def bullish_macd_divergence(data, lookback_per=24):
        macd_values = data['macd']
        macd_signal = data['macd_signal']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_macd_values = macd_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and macd_values[i] >= min(recent_macd_values)):
                divergence_points.append(i)

        data['Bull_MACD_Divergence'] = False
        data.loc[divergence_points, 'Bull_MACD_Divergence'] = True

        return data

    def bullish_stochastic_divergence(data, lookback_per=24):
        stoch_k_values = data['stoch_k']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_stoch_k = stoch_k_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and stoch_k_values[i] >= min(recent_stoch_k)):
                divergence_points.append(i)

        data['Bull_Stoch_Divergence'] = False
        data.loc[divergence_points, 'Bull_Stoch_Divergence'] = True

        return data

    def bullish_cci_divergence(data, lookback_per=24):
        cci_values = data['cci']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_cci_values = cci_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and cci_values[i] >= min(recent_cci_values)):
                divergence_points.append(i)

        data['Bull_CCI_Divergence'] = False
        data.loc[divergence_points, 'Bull_CCI_Divergence'] = True

        return data

    def bullish_mfi_divergence(data, lookback_per=24):
        mfi_values = data['mfi']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_mfi_values = mfi_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and mfi_values[i] >= min(recent_mfi_values)):
                divergence_points.append(i)

        data['Bull_MFI_Divergence'] = False
        data.loc[divergence_points, 'Bull_MFI_Divergence'] = True

        return data

    def bullish_obv_divergence(data, lookback_per=24):
        obv_values = data['obv']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_obv_values = obv_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and obv_values[i] >= min(recent_obv_values)):
                divergence_points.append(i)

        data['Bull_OBV_Divergence'] = False
        data.loc[divergence_points, 'Bull_OBV_Divergence'] = True

        return data

    def bullish_diosc_divergence(data, lookback_per=24):
        dmi_positive = data['dmi_positive']
        dmi_negative = data['dmi_negative']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_dmi_values = dmi_positive[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and dmi_positive[i] >= min(recent_dmi_values)):
                divergence_points.append(i)

        data['Bull_DIOSC_Divergence'] = False
        data.loc[divergence_points, 'Bull_DIOSC_Divergence'] = True

        return data

    def bullish_vmacd_divergence(data, lookback_per=24):
        vmacd_values = data['v_macd']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_vmacd_values = vmacd_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and vmacd_values[i] >= min(recent_vmacd_values)):
                divergence_points.append(i)

        data['Bull_VMACD_Divergence'] = False
        data.loc[divergence_points, 'Bull_VMACD_Divergence'] = True

        return data

    def bullish_cmf_divergence(data, lookback_per=24):
        cmf_values = data['cmf']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_cmf_values = cmf_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] < min(recent_price_values) and cmf_values[i] >= min(recent_cmf_values)):
                divergence_points.append(i)

        data['Bull_CMF_Divergence'] = False
        data.loc[divergence_points, 'Bull_CMF_Divergence'] = True

        return data


    def hidden_bullish_divergence_rsi(data, lookback_per=24):
        rsi_values = data['rsi_14']
        divergence_points = []

        for i in range(lookback_per, len(data)-1):
            recent_rsi_values = rsi_values[i-lookback_per:i]
            recent_price_values = data['low'].iloc[i-lookback_per:i]

            if (data['low'].iloc[i] > min(recent_price_values)) and rsi_values[i] <= min(recent_rsi_values):
                divergence_points.append(i)

        data['Hidden_Bull_RSI_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bull_RSI_Divergence'] = True

        return data

    def hidden_bearish_divergence_rsi(data, lookback_per=24):
        rsi_values = data['rsi_14']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_rsi_values = rsi_values[i - lookback_per:i]
            recent_price_values = data['high'].iloc[i - lookback_per:i]

            if (data['high'].iloc[i] < max(recent_price_values) and
                    rsi_values[i] >= max(recent_rsi_values)):
                divergence_points.append(i)

        data['Hidden_Bear_RSI_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bear_RSI_Divergence'] = True

        return data


    def hidden_bullish_divergence_macd(data, lookback_per=24):
        macd_values = data['macd']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_macd_values = macd_values[i - lookback_per:i]
            recent_price_values = data['low'].iloc[i - lookback_per:i]

            if (data['low'].iloc[i] > min(recent_price_values) and
                    macd_values[i] <= min(recent_macd_values)):
                divergence_points.append(i)

        data['Hidden_Bull_MACD_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bull_MACD_Divergence'] = True

        return data


    def hidden_bearish_divergence_macd(data, lookback_per=24):
        macd_values = data['macd']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_macd_values = macd_values[i - lookback_per:i]
            recent_price_values = data['high'].iloc[i - lookback_per:i]

            if (data['high'].iloc[i] < max(recent_price_values) and
                    macd_values[i] >= max(recent_macd_values)):
                divergence_points.append(i)

        data['Hidden_Bear_MACD_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bear_MACD_Divergence'] = True

        return data


    def hidden_bullish_divergence_vmacd(data, lookback_per=24):
        vmacd_values = data['v_macd']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_vmacd_values = vmacd_values[i - lookback_per:i]
            recent_price_values = data['low'].iloc[i - lookback_per:i]

            if (data['low'].iloc[i] > min(recent_price_values) and
                    vmacd_values[i] <= min(recent_vmacd_values)):
                divergence_points.append(i)

        data['Hidden_Bull_VMACD_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bull_VMACD_Divergence'] = True

        return data


    def hidden_bearish_divergence_vmacd(data, lookback_per=24):
        vmacd_values = data['v_macd']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_vmacd_values = vmacd_values[i - lookback_per:i]
            recent_price_values = data['high'].iloc[i - lookback_per:i]

            if (data['high'].iloc[i] < max(recent_price_values) and
                    vmacd_values[i] >= max(recent_vmacd_values)):
                divergence_points.append(i)

        data['Hidden_Bear_VMACD_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bear_VMACD_Divergence'] = True

        return data


    def hidden_bullish_divergence_obv(data, lookback_per=24):
        obv_values = data['obv']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_obv_values = obv_values[i - lookback_per:i]
            recent_price_values = data['low'].iloc[i - lookback_per:i]

            if (data['low'].iloc[i] > min(recent_price_values) and
                    obv_values[i] <= min(recent_obv_values)):
                divergence_points.append(i)

        data['Hidden_Bull_OBV_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bull_OBV_Divergence'] = True

        return data


    def hidden_bearish_divergence_obv(data, lookback_per=24):
        obv_values = data['obv']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_obv_values = obv_values[i - lookback_per:i]
            recent_price_values = data['high'].iloc[i - lookback_per:i]

            if (data['high'].iloc[i] < max(recent_price_values) and
                    obv_values[i] >= max(recent_obv_values)):
                divergence_points.append(i)

        data['Hidden_Bear_OBV_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bear_OBV_Divergence'] = True

        return data


    def hidden_bullish_divergence_mfi(data, lookback_per=24):
        mfi_values = data['mfi']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_mfi_values = mfi_values[i - lookback_per:i]
            recent_price_values = data['low'].iloc[i - lookback_per:i]

            if (data['low'].iloc[i] > min(recent_price_values) and
                    mfi_values[i] <= min(recent_mfi_values)):
                divergence_points.append(i)

        data['Hidden_Bull_MFI_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bull_MFI_Divergence'] = True

        return data


    def hidden_bearish_divergence_mfi(data, lookback_per=24):
        mfi_values = data['mfi']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_mfi_values = mfi_values[i - lookback_per:i]
            recent_price_values = data['high'].iloc[i - lookback_per:i]

            if (data['high'].iloc[i] < max(recent_price_values) and
                    mfi_values[i] >= max(recent_mfi_values)):
                divergence_points.append(i)

        data['Hidden_Bear_MFI_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bear_MFI_Divergence'] = True

        return data


    def hidden_bullish_divergence_cmf(data, lookback_per=24):
        cmf_values = data['cmf']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_cmf_values = cmf_values[i - lookback_per:i]
            recent_price_values = data['low'].iloc[i - lookback_per:i]

            if (data['low'].iloc[i] > min(recent_price_values) and
                    cmf_values[i] <= min(recent_cmf_values)):
                divergence_points.append(i)

        data['Hidden_Bull_CMF_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bull_CMF_Divergence'] = True

        return data


    def hidden_bearish_divergence_cmf(data, lookback_per=24):
        cmf_values = data['cmf']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_cmf_values = cmf_values[i - lookback_per:i]
            recent_price_values = data['high'].iloc[i - lookback_per:i]

            if (data['high'].iloc[i] < max(recent_price_values) and
                    cmf_values[i] >= max(recent_cmf_values)):
                divergence_points.append(i)

        data['Hidden_Bear_CMF_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bear_CMF_Divergence'] = True

        return data


    def hidden_bullish_divergence_cci(data, lookback_per=24):
        cci_values = data['cci']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_cci_values = cci_values[i - lookback_per:i]
            recent_price_values = data['low'].iloc[i - lookback_per:i]

            if (data['low'].iloc[i] > min(recent_price_values) and
                    cci_values[i] <= min(recent_cci_values)):
                divergence_points.append(i)

        data['Hidden_Bull_CCI_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bull_CCI_Divergence'] = True

        return data


    def hidden_bearish_divergence_cci(data, lookback_per=24):
        cci_values = data['cci']
        divergence_points = []

        for i in range(lookback_per, len(data) - 1):
            recent_cci_values = cci_values[i - lookback_per:i]
            recent_price_values = data['high'].iloc[i - lookback_per:i]

            if (data['high'].iloc[i] < max(recent_price_values) and
                    cci_values[i] >= max(recent_cci_values)):
                divergence_points.append(i)

        data['Hidden_Bear_CCI_Divergence'] = False
        data.loc[divergence_points, 'Hidden_Bear_CCI_Divergence'] = True

        return data





    data = bearish_rsi_divergence(data)
    data = bearish_cmf_divergence(data)
    data = bearish_macd_divergence(data)
    data = bearish_cci_divergence(data)
    data = bearish_mfi_divergence(data)
    data = bearish_obv_divergence(data)
    data = bearish_diosc_divergence(data)
    data = bearish_vmacd_divergence(data)


    data = bullish_rsi_divergence(data)
    data = bullish_cmf_divergence(data)
    data = bullish_macd_divergence(data)
    data = bullish_cci_divergence(data)
    data = bullish_mfi_divergence(data)
    data = bullish_obv_divergence(data)
    data = bullish_diosc_divergence(data)
    data = bullish_vmacd_divergence(data)

    data = hidden_bearish_divergence_rsi(data)
    data = hidden_bearish_divergence_mfi(data)
    data = hidden_bearish_divergence_macd(data)
    data = hidden_bearish_divergence_cci(data)
    
    data = hidden_bearish_divergence_obv(data)
    #data = hidden_bearish_divergence_diosc(data)
    data = hidden_bearish_divergence_vmacd(data)

    data = hidden_bullish_divergence_rsi(data)
    data = hidden_bullish_divergence_mfi(data)
    data = hidden_bullish_divergence_macd(data)
    data = hidden_bullish_divergence_cci(data)
    
    data = hidden_bullish_divergence_obv(data)
    data = hidden_bullish_divergence_vmacd(data)

    bear_columns = [col for col in data.columns if col.lower().startswith("bear_") and not col.lower().startswith("hidden_bear")]


    bull_columns = [col for col in data.columns if col.lower().startswith("bull_") and not col.lower().startswith("hidden_bull")]

    # Hidden Bear sütunlarını seç
    hidden_bear_columns = [col for col in data.columns if col.lower().startswith("hidden_bear")]

    # Hidden Bull sütunlarını seç
    hidden_bull_columns = [col for col in data.columns if col.lower().startswith("hidden_bull")]

    # Yeni sütunları oluştur ve uyumsuzluk sayılarını hesapla
    data['Bearish_Total'] = data[bear_columns].sum(axis=1)
    data['Bull_Total'] = data[bull_columns].sum(axis=1)
    data['Hidden_Bear_Total'] = data[hidden_bear_columns].sum(axis=1)
    data['Hidden_Bull_Total'] = data[hidden_bull_columns].sum(axis=1)

    return add_nadaraya_watson(data)

def add_nadaraya_watson(df):    
    h, alpha = 8, 8  
    df["yhat"] = rational_quadratic_kernel(np.arange(len(df)), df["close"].values, h, alpha)

    df["atr"] = compute_atr(df["high"].values, df["low"].values, df["close"].values)

    df["upper_near"], df["upper_far"], df["upper_top"], df["lower_near"], df["lower_far"], df["lower_top"] = compute_bounds(df["yhat"], df["atr"])

    return df
     

def create_table(table_name, cursor: sqlite3.Cursor):
   
    query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            datetime TEXT,
            symbol TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            rsi_14 REAL,
            macd REAL,
            macd_signal REAL,
            stoch_k REAL,
            stoch_d REAL,
            cmf REAL,
            cci REAL,
            mfi REAL,
            obv REAL,
            dmi_positive REAL,
            dmi_negative REAL,
            adx REAL,
            v_macd REAL,
            v_macd_signal REAL,
            Bearish_RSI_Divergence BOOLEAN,
            Bear_Divergence_CMF BOOLEAN,
            Bear_Divergence_MACD BOOLEAN,
            Bear_Divergence_CCI BOOLEAN,
            Bear_Divergence_MFI BOOLEAN,
            Bear_Divergence_OBV BOOLEAN,
            Bear_DIOSC_Divergence BOOLEAN,
            Bear_VMACD_Divergence BOOLEAN,
            Bull_Divergence BOOLEAN,
            Bull_CMF_Divergence BOOLEAN,
            Bull_MACD_Divergence BOOLEAN,
            Bull_CCI_Divergence BOOLEAN,
            Bull_MFI_Divergence BOOLEAN,
            Bull_OBV_Divergence BOOLEAN,
            Bull_DIOSC_Divergence BOOLEAN,
            Bull_VMACD_Divergence BOOLEAN,
            Hidden_Bear_RSI_Divergence BOOLEAN,
            Hidden_Bear_MFI_Divergence BOOLEAN,
            Hidden_Bear_MACD_Divergence BOOLEAN,
            Hidden_Bear_CCI_Divergence BOOLEAN,
            Hidden_Bear_OBV_Divergence BOOLEAN,
            Hidden_Bear_VMACD_Divergence BOOLEAN,
            Hidden_Bull_RSI_Divergence BOOLEAN,
            Hidden_Bull_MFI_Divergence BOOLEAN,
            Hidden_Bull_MACD_Divergence BOOLEAN,
            Hidden_Bull_CCI_Divergence BOOLEAN,
            Hidden_Bull_OBV_Divergence BOOLEAN,
            Hidden_Bull_VMACD_Divergence BOOLEAN,
            Bearish_Total NUMBER,
            Bull_Total NUMBER,
            Hidden_Bear_Total NUMBER,
            Hidden_Bull_Total NUMBER,
            yhat REAL,
            upper_near REAL,
            upper_far REAL,
            upper_top REAL,
            lower_near REAL,
            lower_far REAL,
            lower_top REAL,
            
            UNIQUE(datetime, symbol) ON CONFLICT IGNORE
        )
    """
    cursor.execute(query)

                
def saveToDatabase(symbol_dict: dict, INTERVAL):
    

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "papers.sqlite3")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    
    for symbol, exchange in symbol_dict.items():
        try:
            
            data = get_data(symbol, exchange, INTERVAL)
            data.drop(columns=["atr"], inplace=True)

            data = data.astype({
                'datetime': 'str',
                'open': 'float',
                'high': 'float',
                'low': 'float',
                'close': 'float',
                'volume': 'float',
                'rsi_14': 'float',
                'macd': 'float',
                'macd_signal': 'float',
                'stoch_k': 'float',
                'stoch_d': 'float',
                'cmf': 'float',
                'cci': 'float',
                'mfi': 'float',
                'obv': 'float',
                'dmi_positive': 'float',
                'dmi_negative': 'float',
                'adx': 'float',
                'v_macd': 'float',
                'v_macd_signal': 'float',
                # Divergence sütunları
                'Bearish_RSI_Divergence': 'bool',
                'Bear_Divergence_CMF': 'bool',
                'Bear_Divergence_MACD': 'bool',
                'Bear_Divergence_CCI': 'bool',
                'Bear_Divergence_MFI': 'bool',
                'Bear_Divergence_OBV': 'bool',
                'Bear_DIOSC_Divergence': 'bool',
                'Bear_VMACD_Divergence': 'bool',
                'Bull_Divergence': 'bool',
                'Bull_CMF_Divergence': 'bool',
                'Bull_MACD_Divergence': 'bool',
                'Bull_CCI_Divergence': 'bool',
                'Bull_MFI_Divergence': 'bool',
                'Bull_OBV_Divergence': 'bool',
                'Bull_DIOSC_Divergence': 'bool',
                'Bull_VMACD_Divergence': 'bool',
                'Hidden_Bear_RSI_Divergence': 'bool',
                'Hidden_Bear_MFI_Divergence': 'bool',
                'Hidden_Bear_MACD_Divergence': 'bool',
                'Hidden_Bear_CCI_Divergence': 'bool',
                'Hidden_Bear_OBV_Divergence': 'bool',
                'Hidden_Bear_VMACD_Divergence': 'bool',
                'Hidden_Bull_RSI_Divergence': 'bool',
                'Hidden_Bull_MFI_Divergence': 'bool',
                'Hidden_Bull_MACD_Divergence': 'bool',
                'Hidden_Bull_CCI_Divergence': 'bool',
                'Hidden_Bull_OBV_Divergence': 'bool',
                'Hidden_Bull_VMACD_Divergence': 'bool',
                'Bearish_Total': 'int',
                'Bull_Total': 'int',
                'Hidden_Bear_Total': 'int',
                'Hidden_Bull_Total': 'int',
                'yhat' : 'float',
                "upper_near" : 'float',
                "upper_far" : 'float',
                "upper_top" : 'float',
                "lower_near" : 'float',
                "lower_far" : 'float',
                "lower_top" : 'float',
                
                
            })

            if data is not None:  
                data['symbol'] = symbol
                name = (f"{symbol}on{INTERVAL}")

                create_table(name, cursor)
               
                data = data.replace({np.nan: None})

                for _, row in data.iterrows():
                    print(row)
                    print(row.dtypes)

             
                for _, row in data.iterrows():
                    row_data = tuple(row[col] for col in data.columns)
                    try:
                        cursor.execute(f"""
                            INSERT INTO {name} ({", ".join(data.columns)})
                            VALUES ({", ".join(["?"] * len(data.columns))})
                        """, row_data)
                        conn.commit() 
                    except Exception as e:
                        print(f"Veri eklenirken hata oluştu: {e}")

                 
            else:
                print(f"Symbol {symbol} için veri alınamadı.")
        except Exception as e:
            print(f"Veri alınırken hata oluştu: {e}")

    conn.close()

def updateDatabase(symbol_dict: dict, INTERVAL):
    cursor = conn.cursor()
    

    for symbol, exchange in symbol_dict.items():
        try:
            name = symbol
            bar_count = int(calculate_bar_count_for_paper(name, INTERVAL))         
            data = update(symbol, exchange, INTERVAL, bar_count)
            if data is not None:  
                data['symbol'] = symbol
                


                data = data.astype({
                'datetime': 'str',
                'open': 'float',
                'high': 'float',
                'low': 'float',
                'close': 'float',
                'volume': 'float',
                'rsi_14': 'float',
                'macd': 'float',
                'macd_signal': 'float',
                'stoch_k': 'float',
                'stoch_d': 'float',
                'cmf': 'float',
                'cci': 'float',
                'mfi': 'float',
                'obv': 'float',
                'dmi_positive': 'float',
                'dmi_negative': 'float',
                'adx': 'float',
                'v_macd': 'float',
                'v_macd_signal': 'float',
                # Divergence sütunları
                'Bearish_RSI_Divergence': 'bool',
                'Bear_Divergence_CMF': 'bool',
                'Bear_Divergence_MACD': 'bool',
                'Bear_Divergence_CCI': 'bool',
                'Bear_Divergence_MFI': 'bool',
                'Bear_Divergence_OBV': 'bool',
                'Bear_DIOSC_Divergence': 'bool',
                'Bear_VMACD_Divergence': 'bool',
                'Bull_Divergence': 'bool',
                'Bull_CMF_Divergence': 'bool',
                'Bull_MACD_Divergence': 'bool',
                'Bull_CCI_Divergence': 'bool',
                'Bull_MFI_Divergence': 'bool',
                'Bull_OBV_Divergence': 'bool',
                'Bull_DIOSC_Divergence': 'bool',
                'Bull_VMACD_Divergence': 'bool',
                'Hidden_Bear_RSI_Divergence': 'bool',
                'Hidden_Bear_MFI_Divergence': 'bool',
                'Hidden_Bear_MACD_Divergence': 'bool',
                'Hidden_Bear_CCI_Divergence': 'bool',
                'Hidden_Bear_OBV_Divergence': 'bool',
                'Hidden_Bear_VMACD_Divergence': 'bool',
                'Hidden_Bull_RSI_Divergence': 'bool',
                'Hidden_Bull_MFI_Divergence': 'bool',
                'Hidden_Bull_MACD_Divergence': 'bool',
                'Hidden_Bull_CCI_Divergence': 'bool',
                'Hidden_Bull_OBV_Divergence': 'bool',
                'Hidden_Bull_VMACD_Divergence': 'bool',
                'Bearish_Total': 'int',
                'Bull_Total': 'int',
                'Hidden_Bear_Total': 'int',
                'Hidden_Bull_Total': 'int',
            })

                           
                for _, row in data.iterrows():
                    row_data = tuple(row[col] for col in data.columns)
                    try:
                        cursor.execute(f"""
                            INSERT INTO {name}on{INTERVAL} ({", ".join(data.columns)})
                            VALUES ({", ".join(["?"] * len(data.columns))})
                        """, row_data)
                        conn.commit() 
                    except Exception as e:
                        print(f"Veri eklenirken hata oluştu: {e}")

                    
                    conn.commit()
                    print("Yeni veri eklendi.")
                


                 
            else:
                print(f"Symbol {symbol} için veri alınamadı.")
        except Exception as e:
            print(f"Veri alınırken hata oluştu: {e}")

    conn.close()

def new_updateDatabase(symbol_dict: dict):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "papers.sqlite3")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    
    for symbol, exchange in symbol_dict.items():
        try:         
            data = update(symbol, exchange)
            if data is not None:  
                data['symbol'] = symbol
                name = symbol


                data = data.astype({
                'datetime': 'str',
                'open': 'float',
                'high': 'float',
                'low': 'float',
                'close': 'float',
                'volume': 'float',
                'rsi_14': 'float',
                'macd': 'float',
                'macd_signal': 'float',
                'stoch_k': 'float',
                'stoch_d': 'float',
                'cmf': 'float',
                'cci': 'float',
                'mfi': 'float',
                'obv': 'float',
                'dmi_positive': 'float',
                'dmi_negative': 'float',
                'adx': 'float',
                'v_macd': 'float',
                'v_macd_signal': 'float',
                # Divergence sütunları
                'Bearish_RSI_Divergence': 'bool',
                'Bear_Divergence_CMF': 'bool',
                'Bear_Divergence_MACD': 'bool',
                'Bear_Divergence_CCI': 'bool',
                'Bear_Divergence_MFI': 'bool',
                'Bear_Divergence_OBV': 'bool',
                'Bear_DIOSC_Divergence': 'bool',
                'Bear_VMACD_Divergence': 'bool',
                'Bull_Divergence': 'bool',
                'Bull_CMF_Divergence': 'bool',
                'Bull_MACD_Divergence': 'bool',
                'Bull_CCI_Divergence': 'bool',
                'Bull_MFI_Divergence': 'bool',
                'Bull_OBV_Divergence': 'bool',
                'Bull_DIOSC_Divergence': 'bool',
                'Bull_VMACD_Divergence': 'bool',
                'Hidden_Bear_RSI_Divergence': 'bool',
                'Hidden_Bear_MFI_Divergence': 'bool',
                'Hidden_Bear_MACD_Divergence': 'bool',
                'Hidden_Bear_CCI_Divergence': 'bool',
                'Hidden_Bear_OBV_Divergence': 'bool',
                'Hidden_Bear_VMACD_Divergence': 'bool',
                'Hidden_Bull_RSI_Divergence': 'bool',
                'Hidden_Bull_MFI_Divergence': 'bool',
                'Hidden_Bull_MACD_Divergence': 'bool',
                'Hidden_Bull_CCI_Divergence': 'bool',
                'Hidden_Bull_OBV_Divergence': 'bool',
                'Hidden_Bull_VMACD_Divergence': 'bool',
                'Bearish_Total': 'int',
                'Bull_Total': 'int',
                'Hidden_Bear_Total': 'int',
                'Hidden_Bull_Total': 'int',
            })

                last_row_df = data.tail(1)  

                last_row_datetime = last_row_df['datetime'].iloc[0]

                cursor.execute(f"""
                    SELECT COUNT(*) FROM {name}
                    WHERE datetime = ?
                """, (last_row_datetime,))

                
                if cursor.fetchone()[0] == 0:
                    
                    row_data = tuple(last_row_df.iloc[0])

                    
                    cursor.execute(f"""
                        INSERT INTO {name} ({', '.join(last_row_df.columns)})
                        VALUES ({', '.join(['?'] * len(last_row_df.columns))})
                    """, row_data)

                    
                    conn.commit()
                    print("Yeni veri eklendi.")
                else:
                    print(f"Veri zaten mevcut: {last_row_datetime}")


                 
            else:
                print(f"Symbol {symbol} için veri alınamadı.")
        except Exception as e:
            print(f"Veri alınırken hata oluştu: {e}")

    conn.close()
