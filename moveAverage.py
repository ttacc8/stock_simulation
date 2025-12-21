## this file contains methods related to stock management

import pandas as pd
import numpy as np
import warnings

# Warning 메시지 억제
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

def calculate_bollinger_bands(df: pd, nday: int, num_std_dev: float = 2.0):
    """Calculate Bollinger Bands for stock prices."""
    rolling_mean = df['Value'].rolling(window=nday).mean()
    rolling_std = df['Value'].rolling(window=nday).std()

    df[f"BB_upper_{nday}"] = rolling_mean + (rolling_std * num_std_dev)
    df[f"BB_lower_{nday}"] = rolling_mean - (rolling_std * num_std_dev)
    return df[[f"BB_upper_{nday}", f"BB_lower_{nday}"]]
    
def calculate_rsi(df: pd, nday: int):
    """Calculate the Relative Strength Index (RSI) for stock prices."""
    delta = df['Value'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=nday).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=nday).mean()
    rs = gain / loss
    df[f"RSI_{nday}"] = 100 - (100 / (1 + rs))
    return df[f"RSI_{nday}"]
    
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
    df[f"ATR_{nday}"] = true_range.rolling(window=nday).mean()
    return df[f"ATR_{nday}"]
    
def calculate_obv(df: pd, nday: int = 20):
    """Calculate the On-Balance Volume (OBV) for stock prices."""
    obv = [0]
    for i in range(1, nday):
        if len(df) < nday:
            break
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
    df[f"CCI_{nday}"] = (tp - sma) / (0.015 * mad)
    return df[f"CCI_{nday}"]
    
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
    df[f"ADX_{nday}"] = dx.rolling(window=nday).mean()
    return df[f"ADX_{nday}"]

def calculate_vwap(df: pd):
    """Calculate the Volume Weighted Average Price (VWAP) for stock prices."""
    cum_vol = df['Volume'].cumsum()
    cum_vol_price = (df['Value'] * df['Volume']).cumsum()
    df['VWAP'] = cum_vol_price / cum_vol
    return df['VWAP']


def calculate_parabolic_sar(df: pd, step: float = 0.02, max_step: float = 0.2):
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
 
def calculate_momentum(df: pd, nday: int):
    """Calculate the Momentum for stock prices."""
    df[f"Momentum_{nday}"] = df['Value'] - df['Value'].shift(nday)
    return df[f"Momentum_{nday}"]

def calculate_rate_of_change(df: pd, nday: int):
    """Calculate the Rate of Change (ROC) for stock prices."""
    df[f"ROC_{nday}"] = ((df['Value'] - df['Value'].shift(nday)) / df['Value'].shift(nday)) * 100
    return df[f"ROC_{nday}"]
    
def calculate_sma(df: pd, nday: int):
    """Calculate the Simple Moving Average (SMA) for stock prices."""
    df[f"SMA_{nday}"] = df['Value'].rolling(window=nday).mean()
    return df[f"SMA_{nday}"]

def calculate_ema(df: pd, nday: int):
    """Calculate the Exponential Moving Average (EMA) for stock prices."""
    df[f"EMA_{nday}"] = df['Value'].ewm(span=nday, adjust=False).mean()
    return df[f"EMA_{nday}"]
    
def calculate_wma(df: pd, nday: int):
    """Calculate the Weighted Moving Average (WMA) for stock prices."""
    weights = pd.Series(range(1, nday + 1))
    df[f"WMA_{nday}"] = df['Value'].rolling(window=nday).apply(lambda x: (x * weights).sum() / weights.sum(), raw=True)
    return df[f"WMA_{nday}"]

def calculate_hma(df: pd, nday: int):
    """Calculate the Hull Moving Average (HMA) for stock prices."""
    half_length = int(nday / 2)
    sqrt_length = int(nday ** 0.5)

    wma_half = calculate_wma(df, half_length)
    wma_full = calculate_wma(df, nday)
    diff_wma = 2 * wma_half - wma_full
    df[f"HMA_{nday}"] = diff_wma.rolling(window=sqrt_length).apply(lambda x: (x * pd.Series(range(1, sqrt_length + 1))).sum() / pd.Series(range(1, sqrt_length + 1)).sum(), raw=True)
    return df[f"HMA_{nday}"]
    
def calculate_keltner_channels(df: pd, nday: int, multiplier: float = 2.0):
    """Calculate Keltner Channels for stock prices."""
    ema = df['Value'].ewm(span=nday, adjust=False).mean()
    atr = calculate_atr(df, nday)
    df[f"KC_upper_{nday}"] = ema + (atr * multiplier)
    df[f"KC_lower_{nday}"] = ema - (atr * multiplier)
    return df[[f"KC_upper_{nday}", f"KC_lower_{nday}"]]
    


def calculate_typical_price(df: pd):
    """Calculate the Typical Price for stock prices."""
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Value']) / 3
    return df['Typical_Price']
    
def calculate_weighted_close_price(df: pd):
    """Calculate the Weighted Close for stock prices."""
    df['Weighted_Close_Price'] = (df['High'] + df['Low'] + (2 * df['Value'])) / 4
    return df['Weighted_Close_Price']

def calculate_price_volume_trend(df: pd):
    """Calculate the Price Volume Trend (PVT) for stock prices."""
    pvt = [0]
    for i in range(1, len(df)):
        pvt_value = pvt[i-1] + ((df['Value'][i] - df['Value'][i - 1]) / df['Value'][i - 1]) * df['Volume'][i]
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

    df[f"Vortex_Pos_{nday}"] = vip
    df[f"Vortex_Neg_{nday}"] = vin
    return df[[f"Vortex_Pos_{nday}", f"Vortex_Neg_{nday}"]]
    
def calculate_ultimate_oscillator(df: pd, short_window: int = 7, mid_window: int = 14, long_window: int = 28):
    """Calculate the Ultimate Oscillator for stock prices."""
    bp = df['Value'] - df['Low'].shift()
    tr = pd.concat([df['High'] - df['Low'], 
                    (df['High'] - df['Value'].shift()).abs(), 
                    (df['Low'] - df['Value'].shift()).abs()], axis=1).max(axis=1)

    avg7 = bp.rolling(window=short_window).sum() / tr.rolling(window=short_window).sum()
    avg14 = bp.rolling(window=mid_window).sum() / tr.rolling(window=mid_window).sum()
    avg28 = bp.rolling(window=long_window).sum() / tr.rolling(window=long_window).sum()

    df[f"Ultimate_Oscillator_{short_window}_{mid_window}_{long_window}"] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / (4 + 2 + 1)
    return df[f"Ultimate_Oscillator_{short_window}_{mid_window}_{long_window}"]
    
def calculate_chande_momentum_oscillator(df: pd, nday: int):
    """Calculate the Chande Momentum Oscillator (CMO) for stock prices."""
    delta = df['Value'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=nday).sum()
    loss = -delta.where(delta < 0, 0).rolling(window=nday).sum()
    df[f"CMO_{nday}"] = 100 * (gain - loss) / (gain + loss)
    return df[f"CMO_{nday}"]
    
def calculate_donchian_channels(df: pd, nday: int):
    """Calculate Donchian Channels for stock prices."""
    df[f"DC_upper_{nday}"] = df['High'].rolling(window=nday).max()
    df[f"DC_lower_{nday}"] = df['Low'].rolling(window=nday).min()
    return df[[f"DC_upper_{nday}", f"DC_lower_{nday}"]]
    
def calculate_price_channel_index(df: pd, nday: int):
    """Calculate the Price Channel Index (PCI) for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PCI_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"PCI_{nday}"]
    
def calculate_price_channel_breakout(df: pd, nday: int):
    """Calculate the Price Channel Breakout for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Breakout_{nday}"] = 0
    df.loc[df['Value'] > highest_high.shift(), f"PC_Breakout_{nday}"] = 1
    df.loc[df['Value'] < lowest_low.shift(), f"PC_Breakout_{nday}"] = -1
    return df[f"PC_Breakout_{nday}"]
    
def calculate_price_channel_trend(df: pd, nday: int):
    """Calculate the Price Channel Trend for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Trend_{nday}"] = 0
    df.loc[df['Value'] > highest_high.shift(), f"PC_Trend_{nday}"] = 1
    df.loc[df['Value'] < lowest_low.shift(), f"PC_Trend_{nday}"] = -1
    return df[f"PC_Trend_{nday}"]
    
def calculate_price_channel_strength(df: pd, nday: int):
    """Calculate the Price Channel Strength for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Strength_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"PC_Strength_{nday}"]

def calculate_price_channel_momentum(df: pd, nday: int):
    """Calculate the Price Channel Momentum for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Momentum_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"PC_Momentum_{nday}"]
    
def calculate_price_channel_volatility(df: pd, nday: int):
    """Calculate the Price Channel Volatility for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Volatility_{nday}"] = (highest_high - lowest_low) / lowest_low * 100
    return df[f"PC_Volatility_{nday}"]
    
def calculate_price_channel_average(df: pd, nday: int):
    """Calculate the Price Channel Average for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Average_{nday}"] = (highest_high + lowest_low) / 2
    return df[f"PC_Average_{nday}"]
    
def calculate_price_channel_range(df: pd, nday: int):
    """Calculate the Price Channel Range for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Range_{nday}"] = highest_high - lowest_low
    return df[f"PC_Range_{nday}"]
    
def calculate_price_channel_width(df: pd, nday: int):
    """Calculate the Price Channel Width for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Width_{nday}"] = (highest_high - lowest_low) / lowest_low * 100
    return df[f"PC_Width_{nday}"]
    
def calculate_price_channel_breakdown(df: pd, nday: int):
    """Calculate the Price Channel Breakdown for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Breakdown_{nday}"] = 0
    df.loc[df['Value'] < lowest_low.shift(), f"PC_Breakdown_{nday}"] = -1
    return df[f"PC_Breakdown_{nday}"]

def calculate_price_channel_pullback(df: pd, nday: int):
    """Calculate the Price Channel Pullback for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Pullback_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"PC_Pullback_{nday}"]

def calculate_price_channel_reversal(df: pd, nday: int):
    """Calculate the Price Channel Reversal for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Reversal_{nday}"] = 0
    df.loc[df['Value'] < lowest_low.shift(), f"PC_Reversal_{nday}"] = -1
    df.loc[df['Value'] > highest_high.shift(), f"PC_Reversal_{nday}"] = 1
    return df[f"PC_Reversal_{nday}"]
    
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

    df[f"PCD_upper_{nday}"] = rolling_mean + (rolling_std * 2)
    df[f"PCD_lower_{nday}"] = rolling_mean - (rolling_std * 2)
    return df[[f"PCD_upper_{nday}", f"PCD_lower_{nday}"]]
    
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

    df[f"Aroon_Up_{nday}"] = 100 * (nday - rolling_max) / nday
    df[f"Aroon_Down_{nday}"] = 100 * (nday - rolling_min) / nday
    return df[[f"Aroon_Up_{nday}", f"Aroon_Down_{nday}"]]
    
def calculate_money_flow_index(df: pd, nday: int):
    """Calculate the Money Flow Index (MFI) for stock prices."""
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    money_flow = tp * df['Volume']
    positive_flow = money_flow.where(tp > tp.shift(), 0).rolling(window=nday).sum()
    negative_flow = money_flow.where(tp < tp.shift(), 0).rolling(window=nday).sum()
    money_ratio = positive_flow / negative_flow
    df[f"MFI_{nday}"] = 100 - (100 / (1 + money_ratio))
    return df[f"MFI_{nday}"]
    
def calculate_force_index(df: pd, nday: int):
    """Calculate the Force Index for stock prices."""
    fi = (df['Value'] - df['Value'].shift()) * df['Volume']
    df[f"FI_{nday}"] = fi.rolling(window=nday).mean()
    return df[f"FI_{nday}"]
    
def calculate_ease_of_movement(df: pd, nday: int):
    """Calculate the Ease of Movement (EOM) for stock prices."""
    distance_moved = ((df['High'] + df['Low']) / 2) - ((df['High'].shift() + df['Low'].shift()) / 2)
    box_ratio = df['Volume'] / (df['High'] - df['Low'])
    eom = distance_moved / box_ratio
    df[f"EOM_{nday}"] = eom.rolling(window=nday).mean()
    return df[f"EOM_{nday}"]

def calculate_volume_rate_of_change(df: pd, nday: int):
    """Calculate the Volume Rate of Change (VROC) for stock prices."""
    df[f"VROC_{nday}"] = ((df['Volume'] - df['Volume'].shift(nday)) / df['Volume'].shift(nday)) * 100
    return df[f"VROC_{nday}"]
    
def calculate_money_flow_volume(df: pd, nday: int):
    """Calculate the Money Flow Volume (MFV) for stock prices."""
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    mfv = tp * df['Volume']
    df[f"MFV_{nday}"] = mfv.rolling(window=nday).sum()
    return df[f"MFV_{nday}"]

def calculate_accumulation_distribution(df: pd):
    """Calculate the Accumulation/Distribution Line for stock prices."""
    mfm = ((df['Value'] - df['Low']) - (df['High'] - df['Value'])) / (df['High'] - df['Low'])
    mfv = mfm * df['Volume']
    df['A/D_Line'] = mfv.cumsum()
    return df['A/D_Line']

def calculate_accumulation_distribution_oscillator(df: pd, short_window: int = 3, long_window: int = 10):
    """Calculate the Accumulation/Distribution Oscillator for stock prices."""
    adl = calculate_accumulation_distribution(df)
    ema_short = adl.ewm(span=short_window, adjust=False).mean()
    ema_long = adl.ewm(span=long_window, adjust=False).mean()
    df['A/D_Oscillator'] = ema_short - ema_long
    return df['A/D_Oscillator']

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
    df[f"IMI_{nday}"] = imi
    return df[f"IMI_{nday}"]

def calculate_true_strength_index(df: pd, short_window: int = 13, long_window: int = 25, signal_window: int = 7):
    """Calculate the True Strength Index (TSI) for stock prices."""
    delta = df['Value'].diff()
    abs_delta = delta.abs()

    ema1 = delta.ewm(span=long_window, adjust=False).mean()
    ema2 = ema1.ewm(span=short_window, adjust=False).mean()

    abs_ema1 = abs_delta.ewm(span=long_window, adjust=False).mean()
    abs_ema2 = abs_ema1.ewm(span=short_window, adjust=False).mean()

    df['TSI'] = 100 * (ema2 / abs_ema2)
    df['TSI_signal'] = df['TSI'].ewm(span=signal_window, adjust=False).mean()
    return df[['TSI', 'TSI_signal']]
    
def calculate_dpo(df: pd, nday: int):
    """Calculate the Detrended Price Oscillator (DPO) for stock prices."""
    sma = df['Value'].rolling(window=nday).mean()
    df[f"DPO_{nday}"] = df['Value'] - sma.shift(int(nday / 2) + 1)
    return df[f"DPO_{nday}"]
    
def calculate_klinger_oscillator(df: pd, short_window: int = 34, long_window: int = 55, signal_window: int = 13):
    """Calculate the Klinger Oscillator for stock prices."""
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    vol = df['Volume']
    cf = ((tp - tp.shift()) * vol).fillna(0)

    df['Klinger_OC'] = cf.ewm(span=short_window, adjust=False).mean() - cf.ewm(span=long_window, adjust=False).mean()
    df['Klinger_OC_signal'] = df['Klinger_OC'].ewm(span=signal_window, adjust=False).mean()
    return df[['Klinger_OC', 'Klinger_OC_signal']]


'''
Choppiness Index Trading의 핵심 활용법
1.추세 매매 필터 (가장 중요)
CHO < 38.2
→ 추세 전략 허용 (돌파, 눌림)
CHO > 61.8
→ 추세 전략 중단
손실의 상당 부분은 횡보장에서 발생
→ 이를 걸러내는 데 최적

2. 횡보 → 추세 전환 탐지
CHO가 고점(>61.8)에서 하락 전환
→ 에너지 축적 후 추세 시작 가능성

이때 가격 돌파와 결합하면 신뢰도 상승
'''
def calculate_choppiness_index(df: pd, nday: int):
    """Calculate the Choppiness Index for stock prices."""
    tr = pd.concat([df['High'] - df['Low'], 
                    (df['High'] - df['Value'].shift()).abs(), 
                    (df['Low'] - df['Value'].shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(window=nday).sum()
    high_low_range = df['High'].rolling(window=nday).max() - df['Low'].rolling(window=nday).min()
    ci = 100 * np.log10(atr / high_low_range) / np.log10(nday)
    df[f"Choppiness_Index_{nday}"] = ci
    return df[f"Choppiness_Index_{nday}"]
    
'''
Gopalakrishnan Range Index Trading의 활용법
① 추세 품질 평가

가격 상승 + GRI 완만
→ 건강한 추세

가격 상승 + GRI 급등
→ 과열 가능성

② 돌파 필터

장기간 낮은 GRI
→ 에너지 축적

이후 GRI 상승 + 가격 돌파
→ 신뢰도 높은 브레이크아웃

③ 리스크 관리

GRI 급등 구간
→ 포지션 축소

변동성 폭발 구간 회피
'''
def calculate_gopalakrishnan_range_index(df: pd, nday: int):
    """Calculate the Gopalakrishnan Range Index (GAPO) for stock prices."""
    high_low_range = df['High'].rolling(window=nday).max() - df['Low'].rolling(window=nday).min()
    gapo = np.log10(high_low_range) / np.log10(nday)
    df[f"GAPO_{nday}"] = gapo
    return df[f"GAPO_{nday}"]


'''
3. Hurst Exponent Trading의 핵심 활용
① 전략 선택 필터 (가장 중요)

H > 0.55
→ 추세 추종, 돌파, 모멘텀 전략

H < 0.45
→ 평균회귀, 밴드 트레이딩

0.45 ~ 0.55
→ 관망 또는 포지션 축소

👉 잘못된 전략을 쓰는 것 자체를 방지

② 국면 전환 탐지

H가 0.5 아래 → 위로 상승
→ 횡보/회귀 → 추세 국면 진입 가능

H가 0.5 위 → 아래로 하락
→ 추세 소멸

③ 다중 타임프레임

장기 H > 0.5, 단기 H < 0.5
→ 조정 후 재추세 가능성
'''
def calculate_hurst_exponent(df: pd, max_lag: int = 20):
    """Calculate the Hurst Exponent for stock prices."""
    lags = range(2, max_lag)
    tau = [np.std(df['Value'].diff(lag).dropna()) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    hurst_exponent = poly[0] * 2.0
    df['Hurst_Exponent'] = hurst_exponent
    return df['Hurst_Exponent']

'''
3. Fractal Dimension Trading의 핵심 활용
① 전략 선택 필터 (가장 중요)
FD 값	시장 성격	적합 전략
FD < 1.3	강한 추세	추세 추종
1.3 ~ 1.5	약한 추세	신중
FD > 1.5	횡보·혼돈	평균회귀
FD > 1.7	무작위	관망
② 국면 전환 탐지

FD 하락 → 질서 증가 → 추세 형성

FD 상승 → 추세 붕괴 → 횡보

③ 포지션 사이징

FD 낮음 → 공격적

FD 높음 → 축소
'''
def calculate_fractal_dimension(df: pd, nday: int):
    """Calculate the Fractal Dimension for stock prices."""
    high_low_range = df['High'].rolling(window=nday).max() - df['Low'].rolling(window=nday).min()
    length = np.log(high_low_range).rolling(window=nday).sum()
    fd = 2 - (length / np.log(nday))
    df[f"Fractal_Dimension_{nday}"] = fd
    return df[f"Fractal_Dimension_{nday}"]

def calculate_polarized_fractal_efficiency_index(df: pd, nday: int):
    """Calculate the Polarized Fractal Efficiency Index (PFE) for stock prices."""
    direction = df['Value'] - df['Value'].shift(nday)
    distance = np.sqrt((df['Value'] - df['Value'].shift(nday))**2 + (nday)**2)
    pfe = (direction / distance) * 100
    df[f"PFE_{nday}"] = pfe
    return df[f"PFE_{nday}"]

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
    df[f"TRIX_{nday}"] = ema3.pct_change() * 100
    return df[f"TRIX_{nday}"]

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
    df[f"DMI_Plus_{nday}"] = plus_di
    df[f"DMI_Minus_{nday}"] = minus_di
    return df[[f"DMI_Plus_{nday}", f"DMI_Minus_{nday}"]]


'''
3. 핵심 해석 방법
① SOBV의 기울기(slope)

상승 기울기
→ 장기 자금 유입 (매집 국면)

하락 기울기
→ 장기 자금 유출 (분배 국면)

👉 값의 절대 수준보다 방향과 곡률이 중요

② 가격과의 구조적 괴리

가격 횡보 + SOBV 상승
→ 보이지 않는 매집

가격 상승 + SOBV 하락
→ 분배 가능성

③ 장기 다이버전스

가격 신고가 + SOBV 저점 하락
→ 중·장기 약세 경고

가격 신저가 + SOBV 상승
→ 장기 바닥 형성 가능성

4. 실전 매매에서의 활용 방식
① 방향 필터 (가장 중요)

SOBV 상승 구간에서만 매수 전략

SOBV 하락 구간에서만 매도/관망
'''
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

    df[f"Supertrend_{nday}"] = supertrend
    return df[f"Supertrend_{nday}"]

def calculate_williams_percent_r(df: pd, nday: int):
    """Calculate the Williams %R for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"WPR_{nday}"] = -100 * (highest_high - df['Value']) / (highest_high - lowest_low)
    return df[f"WPR_{nday}"]

def calculate_elder_ray_index(df: pd, nday: int):
    """Calculate the Elder-Ray Index for stock prices."""
    ema = df['Value'].ewm(span=nday, adjust=False).mean()
    bull_power = df['High'] - ema
    bear_power = df['Low'] - ema
    df[f"ERay_Bull_{nday}"] = bull_power
    df[f"ERay_Bear_{nday}"] = bear_power
    return df[[f"ERay_Bull_{nday}", f"ERay_Bear_{nday}"]]

def calculate_ichimoku_cloud(df: pd):
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
    df['Chikou_Span'] = df['Value'].shift(26)

    return df[['Tenkan_Sen', 'Kijun_Sen', 'Senkou_Span_A', 'Senkou_Span_B', 'Chikou_Span']]


'''
how to set the parmeters for Price Envelopes Trading
이동 평균은 13을 권장
5분 차트 기준 : envelope 퍼센트 0.3% 권장
1시간 차트 기준 : envelope 퍼센트 0.8% 권장
1일 차트 기준 : envelope 퍼센트 2.0% 권장
1주 차트 기준 : envelope 퍼센트 10% 권장
'''
def calculate_price_envelope(df: pd, nday: int, percent: float = 0.02):
    sma = df['Value'].rolling(window=nday).mean()
    df[f"Envelope_Upper_{nday}"] = sma * (1 + percent)
    df[f"Envelope_Lower_{nday}"] = sma * (1 - percent)
    return df[[f"Envelope_Upper_{nday}", f"Envelope_Lower_{nday}"]]

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
    df[f"Gann_HL_Oscillator_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"Gann_HL_Oscillator_{nday}"]

def calculate_Smoothed_Moving_Average(df: pd, nday: int):
    """Calculate the Smoothed Moving Average (SMMA) for stock prices."""
    smma = df['Value'].astype(float).copy()
    for i in range(1, len(df)):
        smma[i] = (smma[i - 1] * (nday - 1) + df['Value'][i]) / nday
    df[f"SMMA_{nday}"] = smma
    return df[f"SMMA_{nday}"]

def calculate_Kaufman_Adaptive_Moving_Average(df: pd, nday: int = 10, fast_ema: int = 2, slow_ema: int = 30):
    """Calculate the Kaufman Adaptive Moving Average (KAMA) for stock prices."""
    change = df['Value'].diff().abs()
    volatility = df['Value'].diff().abs().rolling(window=nday).sum()

    efficiency_ratio = change / volatility
    smoothing_constant = (efficiency_ratio * (2 / (fast_ema + 1) - 2 / (slow_ema + 1)) + 2 / (slow_ema + 1)) ** 2

    kama = df['Value'].astype(float).copy()
    for i in range(1, len(df)):
        if i < nday:
            continue
        kama[i] = kama[i - 1] + smoothing_constant[i] * (df['Value'][i] - kama[i - 1])
    df[f"KAMA_{nday}"] = kama
    return df[f"KAMA_{nday}"]

def calculate_Tema(df: pd, nday: int = 20):
    """Calculate the Triple Exponential Moving Average (TEMA) for stock prices."""
    ema1 = df['Value'].ewm(span=nday, adjust=False).mean()
    ema2 = ema1.ewm(span=nday, adjust=False).mean()
    ema3 = ema2.ewm(span=nday, adjust=False).mean()
    df[f"TEMA_{nday}"] = (3 * ema1) - (3 * ema2) + ema3
    return df[f"TEMA_{nday}"]

def calculate_vidya(df: pd, nday: int = 9, fast_ema: int = 2, slow_ema: int = 30):
    """Calculate the Variable Index Dynamic Average (VIDYA) for stock prices using CMO-based smoothing."""
    values = df['Value'].astype(float).values
    vidya = np.full_like(values, np.nan, dtype=float)
    cmo = np.zeros_like(values, dtype=float)
    n = nday
    base_smoothing = 2 / (n + 1)
    
    if len(values) < n:
        return pd.Series(vidya, index=df.index, name=f"VIDYA_{nday}")

    # CMO 계산
    for i in range(n, len(values)):
        up = 0.0
        down = 0.0
        for j in range(i - n + 1, i + 1):
            diff = values[j] - values[j - 1]
            if diff > 0:
                up += diff
            else:
                down -= diff
        denom = up + down
        cmo[i] = ((up - down) / denom) * 100 if denom != 0 else 0.0

    # VIDYA 계산
    vidya[n - 1] = np.mean(values[:n])  # 초기값: n일 SMA
    for i in range(n, len(values)):
        alpha = base_smoothing * abs(cmo[i]) / 100
        vidya[i] = (1 - alpha) * vidya[i - 1] + alpha * values[i]

    df[f"VIDYA_{nday}"] = vidya
    return df[f"VIDYA_{nday}"]

def calculate_all_indicators(df: pd):
    """Calculate all technical indicators for stock prices."""
    indicators = {}
    indicators['SMA5'] = calculate_sma(df, nday=5)
    indicators['SMA20'] = calculate_sma(df, nday=20)
    indicators['SMA30'] = calculate_sma(df, nday=30)
    indicators['SMA60'] = calculate_sma(df, nday=60)
    indicators['SMA120'] = calculate_sma(df, nday=120)
    indicators['SMA200'] = calculate_sma(df, nday=200)
    indicators['EMA5'] = calculate_ema(df, nday=5)
    indicators['EMA20'] = calculate_ema(df, nday=20)
    indicators['EMA60'] = calculate_ema(df, nday=60)
    indicators['EMA200'] = calculate_ema(df, nday=200)
    indicators['EMA12'] = calculate_ema(df, nday=12)
    indicators['EMA26'] = calculate_ema(df, nday=26)
    indicators['WMA5'] = calculate_wma(df, nday=5)
    indicators['WMA14'] = calculate_wma(df, nday=14)
    indicators['WMA20'] = calculate_wma(df, nday=20)
    indicators['RSI'] = calculate_rsi(df, nday=14)
    indicators['VWAP'] = calculate_vwap(df)
    indicators['MACD'] = calculate_macd(df)
    indicators['Bollinger_Bands20'] = calculate_bollinger_bands(df, nday=20)
    indicators['Bollinger_Bands30'] = calculate_bollinger_bands(df, nday=30)
    indicators['Keltner_Channels20'] = calculate_keltner_channels(df, nday=20)
    indicators['Keltner_Channels30'] = calculate_keltner_channels(df, nday=30)   
    indicators['ATR14'] = calculate_atr(df, nday=14)
    indicators['Stochastic_Oscillator'] = calculate_stochastic_oscillator(df, k_window=14, d_window=3)
    indicators['CCI'] = calculate_cci(df, nday=20)
    indicators['ADX'] = calculate_adx(df, nday=14)
    indicators['PSAR'] = calculate_parabolic_sar(df)
    indicators['Momentum'] = calculate_momentum(df, nday=10)
    indicators['ROC'] = calculate_rate_of_change(df, nday=12)
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
    indicators['FI_7'] = calculate_force_index(df, nday=7)
    indicators['FI_13'] = calculate_force_index(df, nday=13)
    indicators['FI_14'] = calculate_force_index(df, nday=14)
    indicators['Ease_of_Movement'] = calculate_ease_of_movement(df, nday=14)
    indicators['VROC_7'] = calculate_volume_rate_of_change(df, nday=7)
    indicators['VROC_12'] = calculate_volume_rate_of_change(df, nday=12)
    indicators['VROC_14'] = calculate_volume_rate_of_change(df, nday=14)
    indicators['MFV_7'] = calculate_money_flow_volume(df, nday=7)
    indicators['MFV_14'] = calculate_money_flow_volume(df, nday=14)
    indicators['AD_Oscillator_3_10'] = calculate_accumulation_distribution_oscillator(df, short_window=3, long_window=10)
    indicators['Mass_Index'] = calculate_mass_index(df)
    indicators['Intraday_Momentum_Index'] = calculate_intraday_momentum_index(df)
    indicators['True_Strength_Index'] = calculate_true_strength_index(df)
    indicators['DPO'] = calculate_dpo(df, nday=20)
    indicators['Klinger_Oscillator'] = calculate_klinger_oscillator(df)
    indicators['Choppiness_Index'] = calculate_choppiness_index(df, nday=14)
    indicators['GAPO'] = calculate_gopalakrishnan_range_index(df, nday=14)
    indicators['Hurst_Exponent'] = calculate_hurst_exponent(df)
    indicators['Fractal_Dimension'] = calculate_fractal_dimension(df, nday=14)
    indicators['PFE'] = calculate_polarized_fractal_efficiency_index(df, nday=10)
    indicators['Fibonacci_Retracement_Levels'] = calculate_fibonacci_retracement_levels(df)
    indicators['Pivot_Points'] = calculate_pivot_points(df)
    indicators['TRIX'] = calculate_trix(df, nday=12)
    indicators['DMI'] = calculate_dmi(df, nday=14)
    indicators['Sumation_of_OBV'] = calculate_sumation_of_obv(df)
    indicators['Supertrend_Indicator'] = calculate_supertrend_indicator(df, nday=10, multiplier=3.0)
    indicators['Williams_PR'] = calculate_williams_percent_r(df, nday=14)
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
    indicators['HMA'] = calculate_hma(df, nday=21)
    indicators['Typical_Price'] = calculate_typical_price(df)
    indicators['PVT'] = calculate_price_volume_trend(df)
    indicators['Weighted_Close_Price'] = calculate_weighted_close_price(df)
    indicators['SMMA5'] = calculate_Smoothed_Moving_Average(df, nday=5)
    indicators['SMMA8'] = calculate_Smoothed_Moving_Average(df, nday=8)
    indicators['SMMA13'] = calculate_Smoothed_Moving_Average(df, nday=13)
    indicators['KAMA10'] = calculate_Kaufman_Adaptive_Moving_Average(df, nday=10)
    indicators['TEMA5'] = calculate_Tema(df, nday=5)
    indicators['TEMA20'] = calculate_Tema(df, nday=20)
    indicators['VIDYA9'] = calculate_vidya(df, nday=9)
 
    return indicators
