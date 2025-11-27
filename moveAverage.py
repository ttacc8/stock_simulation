## this file contains methods related to stock management

import pandas as pd
import numpy as np

def calculate_bollinger_bands(df: pd, nday: int, num_std_dev: float = 2.0):
    """Calculate Bollinger Bands for stock prices."""
    rolling_mean = df['Value'].rolling(window=nday).mean()
    rolling_std = df['Value'].rolling(window=nday).std()

    df[f"{nday}_BB_upper"] = rolling_mean + (rolling_std * num_std_dev)
    df[f"{nday}_BB_lower"] = rolling_mean - (rolling_std * num_std_dev)
    return df[[f"{nday}_BB_upper", f"{nday}_BB_lower"]]
    
def calculate_rsi(df: pd, nday: int):
    """Calculate the Relative Strength Index (RSI) for stock prices."""
    delta = df['Value'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=nday).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=nday).mean()
    rs = gain / loss
    df[f"{nday}_RSI"] = 100 - (100 / (1 + rs))
    return df[f"{nday}_RSI"]
    
def calculate_macd(df: pd, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
    """Calculate the Moving Average Convergence Divergence (MACD) for stock prices."""
    exp1 = df['Value'].ewm(span=short_window, adjust=False).mean()
    exp2 = df['Value'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    return df[['MACD', 'MACD_signal']]
    
def calculate_stochastic_oscillator(df: pd, k_window: int = 14, d_window: int = 3):
    """Calculate the Stochastic Oscillator for stock prices."""
    low_min = df['Low'].rolling(window=k_window).min()
    high_max = df['High'].rolling(window=k_window).max()
    df['%K'] = 100 * ((df['Value'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=d_window).mean()
    return df[['%K', '%D']]

def calculate_atr(df: pd, nday: int):
    """Calculate the Average True Range (ATR) for stock prices."""
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Value'].shift()).abs()
    low_close = (df['Low'] - df['Value'].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df[f"{nday}_ATR"] = true_range.rolling(window=nday).mean()
    return df[f"{nday}_ATR"]
    
def calculate_obv(df: pd):
    """Calculate the On-Balance Volume (OBV) for stock prices."""
    obv = [0]
    for i in range(1, len(df)):
        if df['Value'][i] > df['Value'][i - 1]:
            obv.append(obv[-1] + df['Volume'][i])
        elif df['Value'][i] < df['Value'][i - 1]:
            obv.append(obv[-1] - df['Volume'][i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    return df['OBV']
    
def calculate_cci(df: pd, nday: int):
    """Calculate the Commodity Channel Index (CCI) for stock prices."""
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    sma = tp.rolling(window=nday).mean()
    # pandas.Series.mad() was removed/unsupported in newer pandas versions.
    # Compute mean absolute deviation (MAD) using numpy on the rolling window.
    mad = tp.rolling(window=nday).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    # avoid division by zero
    mad = mad.replace(0, np.nan)
    df[f"{nday}_CCI"] = (tp - sma) / (0.015 * mad)
    return df[f"{nday}_CCI"]
    
def calculate_adx(df: pd, nday: int):
    """Calculate the Average Directional Index (ADX) for stock prices."""
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff().abs()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Value'].shift()).abs()
    tr3 = (df['Low'] - df['Value'].shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.rolling(window=nday).mean()
    plus_di = 100 * (plus_dm.rolling(window=nday).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=nday).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df[f"{nday}_ADX"] = dx.rolling(window=nday).mean()
    return df[f"{nday}_ADX"]

def calculate_vwap(df: pd):
    """Calculate the Volume Weighted Average Price (VWAP) for stock prices."""
    cum_vol = df['Volume'].cumsum()
    cum_vol_price = (df['Value'] * df['Volume']).cumsum()
    df['VWAP'] = cum_vol_price / cum_vol
    return df['VWAP']

def calculate_sar(df: pd, step: float = 0.02, max_step: float = 0.2):
    """Calculate the Stop and Reverse (SAR) for stock prices."""
    sar = df['Value'].astype(float).copy()
    sar[:] = 0.0
    up_trend = True
    af = step
    ep = df['Low'][0]

    for i in range(1, len(df)):
        if up_trend:
            sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
            if df['Low'][i] < sar[i]:
                up_trend = False
                sar[i] = ep
                af = step
                ep = df['High'][i]
        else:
            sar[i] = sar[i - 1] - af * (sar[i - 1] - ep)
            if df['High'][i] > sar[i]:
                up_trend = True
                sar[i] = ep
                af = step
                ep = df['Low'][i]

        if up_trend:
            if df['High'][i] > ep:
                ep = df['High'][i]
                af = min(af + step, max_step)
        else:
            if df['Low'][i] < ep:
                ep = df['Low'][i]
                af = min(af + step, max_step)

    df['SAR'] = sar
    return df['SAR']

 
def calculate_momentum(df: pd, nday: int):
    """Calculate the Momentum for stock prices."""
    df[f"{nday}_Momentum"] = df['Value'] - df['Value'].shift(nday)
    return df[f"{nday}_Momentum"]

def calculate_rate_of_change(df: pd, nday: int):
    """Calculate the Rate of Change (ROC) for stock prices."""
    df[f"{nday}_ROC"] = ((df['Value'] - df['Value'].shift(nday)) / df['Value'].shift(nday)) * 100
    return df[f"{nday}_ROC"]
    
def calculate_sma(df: pd, nday: int):
    """Calculate the Simple Moving Average (SMA) for stock prices."""
    df[f"{nday}_SMA"] = df['Value'].rolling(window=nday).mean()
    return df[f"{nday}_SMA"]

def calculate_ema(df: pd, nday: int):
    """Calculate the Exponential Moving Average (EMA) for stock prices."""
    df[f"{nday}_EMA"] = df['Value'].ewm(span=nday, adjust=False).mean()
    return df[f"{nday}_EMA"]
    
def calculate_wma(df: pd, nday: int):
    """Calculate the Weighted Moving Average (WMA) for stock prices."""
    weights = pd.Series(range(1, nday + 1))
    df[f"{nday}_WMA"] = df['Value'].rolling(window=nday).apply(lambda x: (x * weights).sum() / weights.sum(), raw=True)
    return df[f"{nday}_WMA"]

def calculate_hma(df: pd, nday: int):
    """Calculate the Hull Moving Average (HMA) for stock prices."""
    half_length = int(nday / 2)
    sqrt_length = int(nday ** 0.5)

    wma_half = calculate_wma(df, half_length)
    wma_full = calculate_wma(df, nday)
    diff_wma = 2 * wma_half - wma_full
    df[f"{nday}_HMA"] = diff_wma.rolling(window=sqrt_length).apply(lambda x: (x * pd.Series(range(1, sqrt_length + 1))).sum() / pd.Series(range(1, sqrt_length + 1)).sum(), raw=True)
    return df[f"{nday}_HMA"]
    
def calculate_keltner_channels(df: pd, nday: int, multiplier: float = 2.0):
    """Calculate Keltner Channels for stock prices."""
    ema = df['Value'].ewm(span=nday, adjust=False).mean()
    atr = calculate_atr(df, nday)
    df[f"{nday}_KC_upper"] = ema + (atr * multiplier)
    df[f"{nday}_KC_lower"] = ema - (atr * multiplier)
    return df[[f"{nday}_KC_upper", f"{nday}_KC_lower"]]
    
def calculate_paralolic_sar(df: pd, step: float = 0.02, max_step: float = 0.2):
    """Calculate the Parabolic SAR for stock prices."""
    psar = df['Value'].astype(float).copy()
    psar[:] = 0.0
    up_trend = True
    af = step
    ep = df['Low'][0]

    for i in range(1, len(df)):
        if up_trend:
            psar[i] = psar[i - 1] + af * (ep - psar[i - 1])
            if df['Low'][i] < psar[i]:
                up_trend = False
                psar[i] = ep
                af = step
                ep = df['High'][i]
        else:
            psar[i] = psar[i - 1] - af * (psar[i - 1] - ep)
            if df['High'][i] > psar[i]:
                up_trend = True
                psar[i] = ep
                af = step
                ep = df['Low'][i]

        if up_trend:
            if df['High'][i] > ep:
                ep = df['High'][i]
                af = min(af + step, max_step)
        else:
            if df['Low'][i] < ep:
                ep = df['Low'][i]
                af = min(af + step, max_step)

    df['PSAR'] = psar
    return df['PSAR']

def calculate_typical_price(df: pd):
    """Calculate the Typical Price for stock prices."""
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Value']) / 3
    return df['Typical_Price']
    
def calculate_weighted_close_price(df: pd):
    """Calculate the Weighted Close for stock prices."""
    df['Weighted_Close_Price'] = (df['High'] + df['Low'] + (2 * df['Value'])) / 4
    return df['Weighted_Close_Price']

def calculate_average_price(df: pd):
    """Calculate the Average Price for stock prices."""
    df['Average_Price'] = (df['High'] + df['Low'] + df['Value']) / 3
    return df['Average_Price']
    
def calculate_price_volume_trend(df: pd):
    """Calculate the Price Volume Trend (PVT) for stock prices."""
    pvt = [0]
    for i in range(1, len(df)):
        pvt_value = pvt[-1] + ((df['Value'][i] - df['Value'][i - 1]) / df['Value'][i - 1]) * df['Volume'][i]
        pvt.append(pvt_value)
    df['PVT'] = pvt
    return df['PVT']

def calculate_vortex_indicator(df: pd, nday: int):
    """Calculate the Vortex Indicator for stock prices."""
    tr = pd.concat([df['High'] - df['Low'], 
                    (df['High'] - df['Value'].shift()).abs(), 
                    (df['Low'] - df['Value'].shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(window=nday).sum()

    vmp = (df['High'] - df['High'].shift()).abs()
    vmm = (df['Low'] - df['Low'].shift()).abs()

    vip = vmp.rolling(window=nday).sum() / atr
    vin = vmm.rolling(window=nday).sum() / atr

    df[f"{nday}_Vortex_Pos"] = vip
    df[f"{nday}_Vortex_Neg"] = vin
    return df[[f"{nday}_Vortex_Pos", f"{nday}_Vortex_Neg"]]
    
def calculate_ultimate_oscillator(df: pd, short_window: int = 7, mid_window: int = 14, long_window: int = 28):
    """Calculate the Ultimate Oscillator for stock prices."""
    bp = df['Value'] - df['Low'].shift()
    tr = pd.concat([df['High'] - df['Low'], 
                    (df['High'] - df['Value'].shift()).abs(), 
                    (df['Low'] - df['Value'].shift()).abs()], axis=1).max(axis=1)

    avg7 = bp.rolling(window=short_window).sum() / tr.rolling(window=short_window).sum()
    avg14 = bp.rolling(window=mid_window).sum() / tr.rolling(window=mid_window).sum()
    avg28 = bp.rolling(window=long_window).sum() / tr.rolling(window=long_window).sum()

    df['Ultimate_Oscillator'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / (4 + 2 + 1)
    return df['Ultimate_Oscillator']
    
def calculate_chande_momentum_oscillator(df: pd, nday: int):
    """Calculate the Chande Momentum Oscillator (CMO) for stock prices."""
    delta = df['Value'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=nday).sum()
    loss = -delta.where(delta < 0, 0).rolling(window=nday).sum()
    df[f"{nday}_CMO"] = 100 * (gain - loss) / (gain + loss)
    return df[f"{nday}_CMO"]
    
def calculate_donchian_channels(df: pd, nday: int):
    """Calculate Donchian Channels for stock prices."""
    df[f"{nday}_DC_upper"] = df['High'].rolling(window=nday).max()
    df[f"{nday}_DC_lower"] = df['Low'].rolling(window=nday).min()
    return df[[f"{nday}_DC_upper", f"{nday}_DC_lower"]]
    
def calculate_price_channel_index(df: pd, nday: int):
    """Calculate the Price Channel Index (PCI) for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PCI"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"{nday}_PCI"]
    
def calculate_price_channel_breakout(df: pd, nday: int):
    """Calculate the Price Channel Breakout for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Breakout"] = 0
    df.loc[df['Value'] > highest_high.shift(), f"{nday}_PC_Breakout"] = 1
    df.loc[df['Value'] < lowest_low.shift(), f"{nday}_PC_Breakout"] = -1
    return df[f"{nday}_PC_Breakout"]
    
def calculate_price_channel_trend(df: pd, nday: int):
    """Calculate the Price Channel Trend for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Trend"] = 0
    df.loc[df['Value'] > highest_high.shift(), f"{nday}_PC_Trend"] = 1
    df.loc[df['Value'] < lowest_low.shift(), f"{nday}_PC_Trend"] = -1
    return df[f"{nday}_PC_Trend"]
    
def calculate_price_channel_strength(df: pd, nday: int):
    """Calculate the Price Channel Strength for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Strength"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"{nday}_PC_Strength"]

def calculate_price_channel_momentum(df: pd, nday: int):
    """Calculate the Price Channel Momentum for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Momentum"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"{nday}_PC_Momentum"]
    
def calculate_price_channel_volatility(df: pd, nday: int):
    """Calculate the Price Channel Volatility for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Volatility"] = (highest_high - lowest_low) / lowest_low * 100
    return df[f"{nday}_PC_Volatility"]
    
def calculate_price_channel_average(df: pd, nday: int):
    """Calculate the Price Channel Average for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Average"] = (highest_high + lowest_low) / 2
    return df[f"{nday}_PC_Average"]
    
def calculate_price_channel_range(df: pd, nday: int):
    """Calculate the Price Channel Range for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Range"] = highest_high - lowest_low
    return df[f"{nday}_PC_Range"]
    
def calculate_price_channel_width(df: pd, nday: int):
    """Calculate the Price Channel Width for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Width"] = (highest_high - lowest_low) / lowest_low * 100
    return df[f"{nday}_PC_Width"]
    
def calculate_price_channel_breakdown(df: pd, nday: int):
    """Calculate the Price Channel Breakdown for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Breakdown"] = 0
    df.loc[df['Value'] < lowest_low.shift(), f"{nday}_PC_Breakdown"] = -1
    return df[f"{nday}_PC_Breakdown"]

def calculate_price_channel_pullback(df: pd, nday: int):
    """Calculate the Price Channel Pullback for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Pullback"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"{nday}_PC_Pullback"]

def calculate_price_channel_reversal(df: pd, nday: int):
    """Calculate the Price Channel Reversal for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_PC_Reversal"] = 0
    df.loc[df['Value'] < lowest_low.shift(), f"{nday}_PC_Reversal"] = -1
    df.loc[df['Value'] > highest_high.shift(), f"{nday}_PC_Reversal"] = 1
    return df[f"{nday}_PC_Reversal"]
    
def calculate_coppock_curve(df: pd, nday1: int = 14, nday2: int = 11, nday3: int = 10):
    """Calculate the Coppock Curve for stock prices."""
    roc1 = calculate_rate_of_change(df, nday1)
    roc2 = calculate_rate_of_change(df, nday2)
    coppock = roc1 + roc2
    df['Coppock_Curve'] = coppock.rolling(window=nday3).mean()
    return df['Coppock_Curve']
    
def calculate_price_oscillator(df: pd, short_window: int = 12, long_window: int = 26):
    """Calculate the Price Oscillator for stock prices."""
    ema_short = df['Value'].ewm(span=short_window, adjust=False).mean()
    ema_long = df['Value'].ewm(span=long_window, adjust=False).mean()
    df['Price_Oscillator'] = ema_short - ema_long
    return df['Price_Oscillator']
    
def calculate_price_chanbdons(df: pd, nday: int):
    """Calculate the Price Chanbdons for stock prices."""
    rolling_mean = df['Value'].rolling(window=nday).mean()
    rolling_std = df['Value'].rolling(window=nday).std()

    df[f"{nday}_PCD_upper"] = rolling_mean + (rolling_std * 2)
    df[f"{nday}_PCD_lower"] = rolling_mean - (rolling_std * 2)
    return df[[f"{nday}_PCD_upper", f"{nday}_PCD_lower"]]
    
def calculate_chaikin_oscillator(df: pd, short_window: int = 3, long_window: int = 10):
    """Calculate the Chaikin Oscillator for stock prices."""
    adl = ((df['Value'] - df['Low']) - (df['High'] - df['Value'])) / (df['High'] - df['Low']) * df['Volume']
    adl = adl.cumsum()
    ema_short = adl.ewm(span=short_window, adjust=False).mean()
    ema_long = adl.ewm(span=long_window, adjust=False).mean()
    df['Chaikin_Oscillator'] = ema_short - ema_long
    return df['Chaikin_Oscillator']
    
def calculate_aroon_indicator(df: pd, nday: int):
    """Calculate the Aroon Indicator for stock prices."""
    rolling_max = df['High'].rolling(window=nday).apply(lambda x: x.argmax(), raw=True)
    rolling_min = df['Low'].rolling(window=nday).apply(lambda x: x.argmin(), raw=True)

    df[f"{nday}_Aroon_Up"] = 100 * (nday - rolling_max) / nday
    df[f"{nday}_Aroon_Down"] = 100 * (nday - rolling_min) / nday
    return df[[f"{nday}_Aroon_Up", f"{nday}_Aroon_Down"]]
    
def calculate_money_flow_index(df: pd, nday: int):
    """Calculate the Money Flow Index (MFI) for stock prices."""
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    money_flow = tp * df['Volume']
    positive_flow = money_flow.where(tp > tp.shift(), 0).rolling(window=nday).sum()
    negative_flow = money_flow.where(tp < tp.shift(), 0).rolling(window=nday).sum()
    money_ratio = positive_flow / negative_flow
    df[f"{nday}_MFI"] = 100 - (100 / (1 + money_ratio))
    return df[f"{nday}_MFI"]
    
def calculate_force_index(df: pd, nday: int):
    """Calculate the Force Index for stock prices."""
    fi = (df['Value'] - df['Value'].shift()) * df['Volume']
    df[f"{nday}_Force_Index"] = fi.rolling(window=nday).mean()
    return df[f"{nday}_Force_Index"]
    
def calculate_ease_of_movement(df: pd, nday: int):
    """Calculate the Ease of Movement (EOM) for stock prices."""
    distance_moved = ((df['High'] + df['Low']) / 2) - ((df['High'].shift() + df['Low'].shift()) / 2)
    box_ratio = df['Volume'] / (df['High'] - df['Low'])
    eom = distance_moved / box_ratio
    df[f"{nday}_EOM"] = eom.rolling(window=nday).mean()
    return df[f"{nday}_EOM"]

def calculate_volume_price_trend(df: pd):
    """Calculate the Volume Price Trend (VPT) for stock prices."""
    vpt = [0]
    for i in range(1, len(df)):
        vpt_value = vpt[-1] + ((df['Value'][i] - df['Value'][i - 1]) / df['Value'][i - 1]) * df['Volume'][i]
        vpt.append(vpt_value)
    df['VPT'] = vpt
    return df['VPT']

def calculate_on_balance_volume(df: pd):
    """Calculate the On-Balance Volume (OBV) for stock prices."""
    obv = [0]
    for i in range(1, len(df)):
        if df['Value'][i] > df['Value'][i - 1]:
            obv.append(obv[-1] + df['Volume'][i])
        elif df['Value'][i] < df['Value'][i - 1]:
            obv.append(obv[-1] - df['Volume'][i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    return df['OBV']

def calculate_volume_rate_of_change(df: pd, nday: int):
    """Calculate the Volume Rate of Change (VROC) for stock prices."""
    df[f"{nday}_VROC"] = ((df['Volume'] - df['Volume'].shift(nday)) / df['Volume'].shift(nday)) * 100
    return df[f"{nday}_VROC"]
    
def calculate_money_flow_volume(df: pd, nday: int):
    """Calculate the Money Flow Volume (MFV) for stock prices."""
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    mfv = tp * df['Volume']
    df[f"{nday}_MFV"] = mfv.rolling(window=nday).sum()
    return df[f"{nday}_MFV"]

def calculate_accumulation_distribution(df: pd):
    """Calculate the Accumulation/Distribution Line for stock prices."""
    mfm = ((df['Value'] - df['Low']) - (df['High'] - df['Value'])) / (df['High'] - df['Low'])
    mfv = mfm * df['Volume']
    df['A/D_Line'] = mfv.cumsum()
    return df['A/D_Line']

def calculate_mass_index(df: pd, nday: int = 25, ema_period: int = 9):
    """Calculate the Mass Index for stock prices."""
    high_low_diff = df['High'] - df['Low']
    ema1 = high_low_diff.ewm(span=ema_period, adjust=False).mean()
    ema2 = ema1.ewm(span=ema_period, adjust=False).mean()
    mass_index = ema1 / ema2
    df[f"Mass_Index"] = mass_index.rolling(window=nday).sum()
    return df[f"Mass_Index"]

def calculate_intraday_momentum_index(df: pd, nday: int = 14):
    """Calculate the Intraday Momentum Index (IMI) for stock prices."""
    up_close = df['Value'] > df['Value'].shift()
    down_close = df['Value'] < df['Value'].shift()

    up_gain = df['Value'].diff().where(up_close, 0)
    down_loss = -df['Value'].diff().where(down_close, 0)

    avg_up_gain = up_gain.rolling(window=nday).mean()
    avg_down_loss = down_loss.rolling(window=nday).mean()

    imi = 100 * (avg_up_gain / (avg_up_gain + avg_down_loss))
    df[f"{nday}_IMI"] = imi
    return df[f"{nday}_IMI"]

def calculate_true_strength_index(df: pd, short_window: int = 25, long_window: int = 13):
    """Calculate the True Strength Index (TSI) for stock prices."""
    delta = df['Value'].diff()
    abs_delta = delta.abs()

    ema1 = delta.ewm(span=long_window, adjust=False).mean()
    ema2 = ema1.ewm(span=short_window, adjust=False).mean()

    abs_ema1 = abs_delta.ewm(span=long_window, adjust=False).mean()
    abs_ema2 = abs_ema1.ewm(span=short_window, adjust=False).mean()

    df['TSI'] = 100 * (ema2 / abs_ema2)
    return df['TSI']
    
def calculate_dpo(df: pd, nday: int):
    """Calculate the Detrended Price Oscillator (DPO) for stock prices."""
    sma = df['Value'].rolling(window=nday).mean()
    df[f"{nday}_DPO"] = df['Value'] - sma.shift(int(nday / 2) + 1)
    return df[f"{nday}_DPO"]
    
def calculate_klinger_oscillator(df: pd, short_window: int = 34, long_window: int = 55, signal_window: int = 13):
    """Calculate the Klinger Oscillator for stock prices."""
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    vol = df['Volume']
    cf = ((tp - tp.shift()) * vol).fillna(0)

    df['KVO'] = cf.ewm(span=short_window, adjust=False).mean() - cf.ewm(span=long_window, adjust=False).mean()
    df['KVO_signal'] = df['KVO'].ewm(span=signal_window, adjust=False).mean()
    return df[['KVO', 'KVO_signal']]

def calculate_ulcer_index(df: pd, nday: int):
    """Calculate the Ulcer Index for stock prices."""
    rolling_max = df['Value'].rolling(window=nday).max()
    drawdown = (df['Value'] - rolling_max) / rolling_max * 100
    squared_drawdown = drawdown ** 2
    df[f"{nday}_Ulcer_Index"] = (squared_drawdown.rolling(window=nday).mean()) ** 0.5
    return df[f"{nday}_Ulcer_Index"]
    
def calculate_choppiness_index(df: pd, nday: int):
    """Calculate the Choppiness Index for stock prices."""
    tr = pd.concat([df['High'] - df['Low'], 
                    (df['High'] - df['Value'].shift()).abs(), 
                    (df['Low'] - df['Value'].shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(window=nday).sum()
    high_low_range = df['High'].rolling(window=nday).max() - df['Low'].rolling(window=nday).min()
    ci = 100 * np.log10(atr / high_low_range) / np.log10(nday)
    df[f"{nday}_Choppiness_Index"] = ci
    return df[f"{nday}_Choppiness_Index"]
    
def calculate_gopalakrishnan_range_index(df: pd, nday: int):
    """Calculate the Gopalakrishnan Range Index (GAPO) for stock prices."""
    high_low_range = df['High'].rolling(window=nday).max() - df['Low'].rolling(window=nday).min()
    gapo = np.log10(high_low_range) / np.log10(nday)
    df[f"{nday}_GAPO"] = gapo
    return df[f"{nday}_GAPO"]

def calculate_hurst_exponent(df: pd, max_lag: int = 20):
    """Calculate the Hurst Exponent for stock prices."""
    lags = range(2, max_lag)
    tau = [np.std(df['Value'].diff(lag).dropna()) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    hurst_exponent = poly[0] * 2.0
    df['Hurst_Exponent'] = hurst_exponent
    return df['Hurst_Exponent']

def calculate_fractal_dimension(df: pd, nday: int):
    """Calculate the Fractal Dimension for stock prices."""
    high_low_range = df['High'].rolling(window=nday).max() - df['Low'].rolling(window=nday).min()
    length = np.log(high_low_range).rolling(window=nday).sum()
    fd = 2 - (length / np.log(nday))
    df[f"{nday}_Fractal_Dimension"] = fd
    return df[f"{nday}_Fractal_Dimension"]

def calculate_fibonacci_retracement_levels(df: pd):
    """Calculate Fibonacci Retracement Levels for stock prices."""
    max_price = df['High'].max()
    min_price = df['Low'].min()
    diff = max_price - min_price

    levels = {
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50.0%': max_price - 0.500 * diff,
        '61.8%': max_price - 0.618 * diff,
        '78.6%': max_price - 0.786 * diff,
    }
    return levels

def calculate_pivot_points(df: pd):
    """Calculate Pivot Points for stock prices."""
    pivot_points = []
    for i in range(len(df)):
        high = df['High'][i]
        low = df['Low'][i]
        close = df['Value'][i]
        pp = (high + low + close) / 3
        r1 = (2 * pp) - low
        s1 = (2 * pp) - high
        r2 = pp + (high - low)
        s2 = pp - (high - low)
        pivot_points.append({
            'PP': pp,
            'R1': r1,
            'S1': s1,
            'R2': r2,
            'S2': s2
        })
    return pd.DataFrame(pivot_points)
    
def calculate_trix(df: pd, nday: int):
    """Calculate the TRIX indicator for stock prices."""
    ema1 = df['Value'].ewm(span=nday, adjust=False).mean()
    ema2 = ema1.ewm(span=nday, adjust=False).mean()
    ema3 = ema2.ewm(span=nday, adjust=False).mean()
    df[f"{nday}_TRIX"] = ema3.pct_change() * 100
    return df[f"{nday}_TRIX"]

def calculate_dmi(df: pd, nday: int):
    """Calculate the Directional Movement Index (DMI) for stock prices."""
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff().abs()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Value'].shift()).abs()
    tr3 = (df['Low'] - df['Value'].shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.rolling(window=nday).mean()
    plus_di = 100 * (plus_dm.rolling(window=nday).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=nday).mean() / atr)
    df[f"{nday}_DMI_Plus"] = plus_di
    df[f"{nday}_DMI_Minus"] = minus_di
    return df[[f"{nday}_DMI_Plus", f"{nday}_DMI_Minus"]]

def calculate_sumation_of_obv(df: pd):
    """Calculate the Summation of On-Balance Volume (OBV) for stock prices."""
    obv = [0]
    for i in range(1, len(df)):
        if df['Value'][i] > df['Value'][i - 1]:
            obv.append(obv[-1] + df['Volume'][i])
        elif df['Value'][i] < df['Value'][i - 1]:
            obv.append(obv[-1] - df['Volume'][i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    df['Sumation_OBV'] = df['OBV'].cumsum()
    return df['Sumation_OBV']
def calculate_supertrend_indicator(df: pd, nday: int = 10, multiplier: float = 3.0):
    """Calculate the Supertrend Indicator for stock prices."""
    atr = calculate_atr(df, nday)
    hl2 = (df['High'] + df['Low']) / 2

    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index)
    direction = pd.Series(index=df.index)

    for i in range(len(df)):
        if i == 0:
            supertrend[i] = upperband[i]
            direction[i] = 1.0  # True를 1.0으로 변환
        else:
            if df['Value'][i] > supertrend[i - 1]:
                direction[i] = 1.0  # True를 1.0으로 변환
            elif df['Value'][i] < supertrend[i - 1]:
                direction[i] = 0.0  # False를 0.0으로 변환
            else:
                direction[i] = direction[i - 1]

            if direction[i]:
                supertrend[i] = lowerband[i] if lowerband[i] > supertrend[i - 1] else supertrend[i - 1]
            else:
                supertrend[i] = upperband[i] if upperband[i] < supertrend[i - 1] else supertrend[i - 1]

    df[f"{nday}_Supertrend"] = supertrend
    return df[f"{nday}_Supertrend"]

def calculate_williams_percent_r(df: pd, nday: int):
    """Calculate the Williams %R for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_Williams_%R"] = -100 * (highest_high - df['Value']) / (highest_high - lowest_low)
    return df[f"{nday}_Williams_%R"]

def calculate_elder_ray_index(df: pd, nday: int):
    """Calculate the Elder-Ray Index for stock prices."""
    ema = df['Value'].ewm(span=nday, adjust=False).mean()
    bull_power = df['High'] - ema
    bear_power = df['Low'] - ema
    df[f"{nday}_Elder_Bull_Power"] = bull_power
    df[f"{nday}_Elder_Bear_Power"] = bear_power
    return df[[f"{nday}_Elder_Bull_Power", f"{nday}_Elder_Bear_Power"]]

def calculate_ichimoku_cloud(df: pd):
    """Calculate the Ichimoku Cloud for stock prices."""
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Tenkan_Sen'] = (high_9 + low_9) / 2

    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Kijun_Sen'] = (high_26 + low_26) / 2

    df['Senkou_Span_A'] = ((df['Tenkan_Sen'] + df['Kijun_Sen']) / 2).shift(26)

    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Senkou_Span_B'] = ((high_52 + low_52) / 2).shift(26)

    df['Chikou_Span'] = df['Value'].shift(-26)

    return df[['Tenkan_Sen', 'Kijun_Sen', 'Senkou_Span_A', 'Senkou_Span_B', 'Chikou_Span']]

def calculate_price_envelope(df: pd, nday: int, percent: float = 0.025):
    """Calculate Price Envelopes for stock prices."""
    sma = df['Value'].rolling(window=nday).mean()
    df[f"{nday}_Price_Envelope_Upper"] = sma * (1 + percent)
    df[f"{nday}_Price_Envelope_Lower"] = sma * (1 - percent)
    return df[[f"{nday}_Price_Envelope_Upper", f"{nday}_Price_Envelope_Lower"]]

def calculate_gann_fan(df: pd):
    """Calculate Gann Fan lines for stock prices."""
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low

    gann_lines = {
        '1x1': (high - diff, low + diff),
        '1x2': (high - diff / 2, low + diff / 2),
        '2x1': (high - 2 * diff, low + 2 * diff),
        '3x1': (high - 3 * diff, low + 3 * diff),
        '4x1': (high - 4 * diff, low + 4 * diff),
        '8x1': (high - 8 * diff, low + 8 * diff),
    }
    return gann_lines

def calculate_gann_square(df: pd):
    """Calculate Gann Square levels for stock prices."""
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low

    gann_levels = {
        '0%': low,
        '25%': low + 0.25 * diff,
        '50%': low + 0.50 * diff,
        '75%': low + 0.75 * diff,
        '100%': high,
    }
    return gann_levels

def calculate_gann_grid(df: pd):
    """Calculate Gann Grid levels for stock prices."""
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low

    gann_grid_levels = {
        '0%': low,
        '20%': low + 0.20 * diff,
        '40%': low + 0.40 * diff,
        '60%': low + 0.60 * diff,
        '80%': low + 0.80 * diff,
        '100%': high,
    }
    return gann_grid_levels

def calculate_gann_box(df: pd, box_size: float):
    """Calculate Gann Box levels for stock prices."""
    high = df['High'].max()
    low = df['Low'].min()

    gann_box_levels = {
        'Top': high,
        'Bottom': low,
        'Box_Size': box_size,
        'Boxes': [(low + i * box_size, low + (i + 1) * box_size) for i in range(int((high - low) / box_size) + 1)]
    }
    return gann_box_levels

def calculate_gann_time_cycles(df: pd, cycle_length: int):
    """Calculate Gann Time Cycles for stock prices."""
    time_cycles = []
    for i in range(0, len(df), cycle_length):
        time_cycles.append(df.index[i])
    return time_cycles

def calculate_gann_angles(df: pd, angle_degrees: float):
    """Calculate Gann Angles for stock prices."""
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low

    angle_radians = np.radians(angle_degrees)
    gann_angle_levels = {
        'Angle_Level': (high - diff * np.tan(angle_radians), low + diff * np.tan(angle_radians))
    }
    return gann_angle_levels

def calculate_gann_high_low_oscillator(df: pd, nday: int):
    """Calculate the Gann High-Low Oscillator for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"{nday}_Gann_HL_Oscillator"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"{nday}_Gann_HL_Oscillator"]

def calculate_hull_moving_average(df: pd, nday: int):
    """Calculate the Hull Moving Average (HMA) for stock prices."""
    half_length = int(nday / 2)
    sqrt_length = int(np.sqrt(nday))

    wma_half = df['Value'].rolling(window=half_length).apply(lambda x: np.sum((np.arange(1, half_length + 1) * x)) / np.sum(np.arange(1, half_length + 1)), raw=True)
    wma_full = df['Value'].rolling(window=nday).apply(lambda x: np.sum((np.arange(1, nday + 1) * x)) / np.sum(np.arange(1, nday + 1)), raw=True)

    hma = (2 * wma_half) - wma_full
    df[f"{nday}_HMA"] = hma.rolling(window=sqrt_length).apply(lambda x: np.sum((np.arange(1, sqrt_length + 1) * x)) / np.sum(np.arange(1, sqrt_length + 1)), raw=True)
    return df[f"{nday}_HMA"]
    

def calculate_all_indicators(df: pd):
    """Calculate all technical indicators for stock prices."""
    indicators = {}
    indicators['SMA5'] = calculate_sma(df, nday=5)
    indicators['SMA20'] = calculate_sma(df, nday=20)
    indicators['SMA60'] = calculate_sma(df, nday=60)
    indicators['SMA120'] = calculate_sma(df, nday=120)
    indicators['EMA'] = calculate_ema(df, nday=20)
    indicators['WMA'] = calculate_wma(df, nday=20)
    indicators['RSI'] = calculate_rsi(df, nday=14)
    indicators['VWAP'] = calculate_vwap(df)
    indicators['MACD'] = calculate_macd(df)
    indicators['Bollinger_Bands'] = calculate_bollinger_bands(df, nday=20)
    indicators['Keltener_Channels'] = calculate_keltner_channels(df, nday=20)   
    indicators['ATR'] = calculate_atr(df, nday=14)
    indicators['Stochastic_Oscillator'] = calculate_stochastic_oscillator(df, k_window=14, d_window=3)
    indicators['CCI'] = calculate_cci(df, nday=20)
    indicators['ADX'] = calculate_adx(df, nday=14)
    indicators['SAR'] = calculate_sar(df)
    indicators['Parabolic_SAR'] = calculate_paralolic_sar(df)
    indicators['Momentum'] = calculate_momentum(df, nday=10)
    indicators['Vortex'] = calculate_vortex_indicator(df, nday=14)
    indicators['Ultimate_Oscillator'] = calculate_ultimate_oscillator(df)
    indicators['Chande_Momentum_Oscillator'] = calculate_chande_momentum_oscillator(df, nday=14)
    indicators['Donchian_Channels'] = calculate_donchian_channels(df, nday=20)
    indicators['Price_Channel_Index'] = calculate_price_channel_index(df, nday=20)
    indicators['Price_Channel_Breakout'] = calculate_price_channel_breakout(df, nday=20)
    indicators['Price_Channel_Trend'] = calculate_price_channel_trend(df, nday=20)
    indicators['Price_Channel_Strength'] = calculate_price_channel_strength(df, nday=20)
    indicators['Price_Channel_Momentum'] = calculate_price_channel_momentum(df, nday=20)
    indicators['Price_Channel_Volatility'] = calculate_price_channel_volatility(df, nday=20)
    indicators['Price_Channel_Average'] = calculate_price_channel_average(df, nday=20)
    indicators['Price_Channel_Range'] = calculate_price_channel_range(df, nday=20)
    indicators['Price_Channel_Width'] = calculate_price_channel_width(df, nday=20)
    indicators['Price_Channel_Breakdown'] = calculate_price_channel_breakdown(df, nday=20)
    indicators['Price_Channel_Pullback'] = calculate_price_channel_pullback(df, nday=20)
    indicators['Price_Channel_Reversal'] = calculate_price_channel_reversal(df, nday=20)
    indicators['Coppock_Curve'] = calculate_coppock_curve(df)
    indicators['Price_Oscillator'] = calculate_price_oscillator(df)
    indicators['Price_Chanbdons'] = calculate_price_chanbdons(df, nday=20)
    indicators['Chaikin_Oscillator'] = calculate_chaikin_oscillator(df)
    indicators['Aroon_Indicator'] = calculate_aroon_indicator(df, nday=14)
    indicators['Money_Flow_Index'] = calculate_money_flow_index(df, nday=14)
    indicators['Force_Index'] = calculate_force_index(df, nday=13)
    indicators['Ease_of_Movement'] = calculate_ease_of_movement(df, nday=14)
    indicators['Volume_Price_Trend'] = calculate_price_volume_trend(df)
    indicators['On_Balance_Volume'] = calculate_on_balance_volume(df)
    indicators['Volume_Rate_of_Change'] = calculate_volume_rate_of_change(df, nday=12)
    indicators['Money_Flow_Volume'] = calculate_money_flow_volume(df, nday=14)
    indicators['Accumulation_Distribution'] = calculate_accumulation_distribution(df)
    indicators['Mass_Index'] = calculate_mass_index(df)
    indicators['Intraday_Momentum_Index'] = calculate_intraday_momentum_index(df)
    indicators['True_Strength_Index'] = calculate_true_strength_index(df)
    indicators['DPO'] = calculate_dpo(df, nday=20)
    indicators['Klinger_Oscillator'] = calculate_klinger_oscillator(df)
    indicators['Ulcer_Index'] = calculate_ulcer_index(df, nday=14)
    indicators['Choppiness_Index'] = calculate_choppiness_index(df, nday=14)
    indicators['GAPO'] = calculate_gopalakrishnan_range_index(df, nday=14)
    indicators['Hurst_Exponent'] = calculate_hurst_exponent(df)
    indicators['Fractal_Dimension'] = calculate_fractal_dimension(df, nday=14)
    indicators['Fibonacci_Retracement_Levels'] = calculate_fibonacci_retracement_levels(df)
    indicators['Pivot_Points'] = calculate_pivot_points(df)
    indicators['TRIX'] = calculate_trix(df, nday=15)
    indicators['DMI'] = calculate_dmi(df, nday=14)
    indicators['Sumation_of_OBV'] = calculate_sumation_of_obv(df)
    indicators['Supertrend_Indicator'] = calculate_supertrend_indicator(df, nday=10, multiplier=3.0)
    indicators['Williams_%R'] = calculate_williams_percent_r(df, nday=14)
    indicators['Elder_Ray_Index'] = calculate_elder_ray_index(df, nday=13)
    indicators['Ichimoku_Cloud'] = calculate_ichimoku_cloud(df)
    indicators['Price_Envelope'] = calculate_price_envelope(df, nday=20, percent=0.025)
    indicators['Gann_Fan'] = calculate_gann_fan(df)
    indicators['Gann_Square'] = calculate_gann_square(df)
    indicators['Gann_Grid'] = calculate_gann_grid(df)
    indicators['Gann_Box'] = calculate_gann_box(df, box_size=5.0)
    indicators['Gann_Time_Cycles'] = calculate_gann_time_cycles(df, cycle_length=30)
    indicators['Gann_Angles'] = calculate_gann_angles(df, angle_degrees=45)
    indicators['Gann_High_Low_Oscillator'] = calculate_gann_high_low_oscillator(df, nday=14)
    indicators['Hull_Moving_Average'] = calculate_hull_moving_average(df, nday=21)
    indicators['HMA'] = calculate_hull_moving_average(df, nday=21)
    indicators['Typical_Price'] = calculate_typical_price(df)
    indicators['Weighted_Close_Price'] = calculate_weighted_close_price(df)
    indicators['Average_Price'] = calculate_average_price(df)

    return indicators
