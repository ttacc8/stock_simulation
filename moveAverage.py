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

    df[f"BB_middle_{nday}"] = rolling_mean
    df[f"BB_upper_{nday}"] = rolling_mean + (rolling_std * num_std_dev)
    df[f"BB_lower_{nday}"] = rolling_mean - (rolling_std * num_std_dev)
    return df[[f"BB_upper_{nday}", f"BB_lower_{nday}"]]
    
def calculate_rsi(df: pd, nday: int):
    """Calculate the Relative Strength Index (RSI) for stock prices using Wilder's smoothing method."""
    delta = df['Value'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Wilder's smoothing: EWM with alpha = 1/nday
    avg_gain = gain.ewm(alpha=1/nday, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/nday, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    df[f"RSI_{nday}"] = 100 - (100 / (1 + rs))
    return df[f"RSI_{nday}"]
    
def calculate_macd(df: pd, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
    """Calculate the Moving Average Convergence Divergence (MACD) for stock prices."""
    exp1 = df['Value'].ewm(span=short_window, adjust=False).mean()
    exp2 = df['Value'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
    return df[['MACD', 'MACD_signal', 'MACD_histogram']]
    
def calculate_stochastic_oscillator(df: pd, k_window: int = 14, d_window: int = 3, slow: bool = True):
    """Calculate the Stochastic Oscillator for stock prices.
    
    Args:
        k_window: Period for %K calculation (default: 14)
        d_window: Period for %D smoothing (default: 3)
        slow: If True, returns Slow Stochastic (default), if False returns Fast Stochastic
    """
    low_min = df['Low'].rolling(window=k_window).min()
    high_max = df['High'].rolling(window=k_window).max()
    
    # Fast %K
    fast_k = 100 * ((df['Value'] - low_min) / (high_max - low_min))
    
    if slow:
        # Slow Stochastic (more commonly used)
        df['%K'] = fast_k.rolling(window=d_window).mean()  # Slow %K = Fast %D
        df['%D'] = df['%K'].rolling(window=d_window).mean()  # Slow %D
    else:
        # Fast Stochastic
        df['%K'] = fast_k
        df['%D'] = fast_k.rolling(window=d_window).mean()
    
    return df[['%K', '%D']]

def calculate_atr(df: pd, nday: int = 14):
    """Calculate the Average True Range (ATR) for stock prices using Wilder's smoothing method."""
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Value'].shift()).abs()
    low_close = (df['Low'] - df['Value'].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Wilder's smoothing: EWM with alpha = 1/nday
    df[f"ATR_{nday}"] = true_range.ewm(alpha=1/nday, adjust=False).mean()
    return df[f"ATR_{nday}"]
    
def calculate_obv(df: pd):
    """Calculate the On-Balance Volume (OBV) for stock prices.
    
    OBV is a cumulative indicator with no period parameter.
    It measures buying/selling pressure by adding volume on up days and subtracting on down days.
    """
    obv = [0]
    for i in range(1, len(df)):
        if df['Value'].iloc[i] > df['Value'].iloc[i - 1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Value'].iloc[i] < df['Value'].iloc[i - 1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    return df['OBV']
    
def calculate_cci(df: pd, nday: int = 20):
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
    
def calculate_adx(df: pd, nday: int = 14):
    """Calculate the Average Directional Index (ADX) for stock prices using Wilder's smoothing method."""
    # Directional Movement calculation
    high_diff = df['High'].diff()
    low_diff = -df['Low'].diff()  # negative of low diff
    
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

    # True Range calculation
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Value'].shift()).abs()
    tr3 = (df['Low'] - df['Value'].shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Wilder's smoothing: EWM with alpha = 1/nday
    atr = true_range.ewm(alpha=1/nday, adjust=False).mean()
    plus_dm_smooth = plus_dm.ewm(alpha=1/nday, adjust=False).mean()
    minus_dm_smooth = minus_dm.ewm(alpha=1/nday, adjust=False).mean()
    
    # Directional Indicators
    plus_di = 100 * (plus_dm_smooth / atr)
    minus_di = 100 * (minus_dm_smooth / atr)
    
    # DX and ADX
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df[f"ADX_{nday}"] = dx.ewm(alpha=1/nday, adjust=False).mean()
    return df[f"ADX_{nday}"]

def calculate_vwap(df: pd):
    """Calculate the Volume Weighted Average Price (VWAP) for stock prices."""
    cum_vol = df['Volume'].cumsum()
    cum_vol_price = (df['Value'] * df['Volume']).cumsum()
    df['VWAP'] = cum_vol_price / cum_vol
    return df['VWAP']


def calculate_parabolic_sar(df: pd, step: float = 0.02, max_step: float = 0.2):
    """Calculate the Parabolic SAR for stock prices."""
    high = df['High'].values
    low = df['Low'].values
    close = df['Value'].values
    
    psar = np.zeros(len(df))
    up_trend = True
    af = step
    
    # 초기값 설정
    psar[0] = low[0]
    ep = high[0]

    for i in range(1, len(df)):
        # 이전 PSAR 저장
        prev_psar = psar[i - 1]
        
        # PSAR 계산
        psar[i] = prev_psar + af * (ep - prev_psar)
        
        # 추세 전환 체크 및 처리
        reverse = False
        
        if up_trend:
            # 상승 추세: SAR이 저가보다 높으면 추세 전환
            if low[i] < psar[i]:
                reverse = True
                up_trend = False
                psar[i] = ep
                ep = low[i]
                af = step
            else:
                # SAR 제약: 이전 2일의 저가보다 낮아야 함
                if i >= 1 and psar[i] > low[i - 1]:
                    psar[i] = low[i - 1]
                if i >= 2 and psar[i] > low[i - 2]:
                    psar[i] = low[i - 2]
                    
                # EP와 AF 업데이트 (추세 유지 시)
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + step, max_step)
        else:
            # 하락 추세: SAR이 고가보다 낮으면 추세 전환
            if high[i] > psar[i]:
                reverse = True
                up_trend = True
                psar[i] = ep
                ep = high[i]
                af = step
            else:
                # SAR 제약: 이전 2일의 고가보다 높아야 함
                if i >= 1 and psar[i] < high[i - 1]:
                    psar[i] = high[i - 1]
                if i >= 2 and psar[i] < high[i - 2]:
                    psar[i] = high[i - 2]
                    
                # EP와 AF 업데이트 (추세 유지 시)
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + step, max_step)

    df['PSAR'] = psar
    return df['PSAR']
 
def calculate_momentum(df: pd, nday: int = 10):
    """Calculate the Momentum for stock prices."""
    df[f"Momentum_{nday}"] = df['Value'] - df['Value'].shift(nday)
    return df[f"Momentum_{nday}"]

def calculate_rate_of_change(df: pd, nday: int = 12):
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

def calculate_hma(df: pd, nday: int = 21):  # TradingView 9일, Alan Hull은 16일, 일반적으로 21일 사용
    """Calculate the Hull Moving Average (HMA) for stock prices."""
    half_length = int(nday / 2)
    sqrt_length = int(nday ** 0.5)

    wma_half = calculate_wma(df, half_length)
    wma_full = calculate_wma(df, nday)
    diff_wma = 2 * wma_half - wma_full
    
    # Apply WMA to diff_wma with period sqrt_length
    weights = pd.Series(range(1, sqrt_length + 1))
    df[f"HMA_{nday}"] = diff_wma.rolling(window=sqrt_length).apply(
        lambda x: (x * weights).sum() / weights.sum(), raw=True
    )
    return df[f"HMA_{nday}"]
    
def calculate_keltner_channels(df: pd, nday: int = 20, multiplier: float = 2.0):
    """Calculate Keltner Channels for stock prices."""
    ema = df['Value'].ewm(span=nday, adjust=False).mean()
    atr = calculate_atr(df, nday)
    df[f"KC_middle_{nday}"] = ema
    df[f"KC_upper_{nday}"] = ema + (atr * multiplier)
    df[f"KC_lower_{nday}"] = ema - (atr * multiplier)
    return df[[f"KC_upper_{nday}", f"KC_middle_{nday}", f"KC_lower_{nday}"]]
    
def calculate_typical_price(df: pd):
    """Calculate the Typical Price for stock prices."""
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Value']) / 3
    return df['Typical_Price']
    
def calculate_weighted_close_price(df: pd):
    """Calculate the Weighted Close for stock prices."""
    df['Weighted_Close_Price'] = (df['High'] + df['Low'] + (2 * df['Value'])) / 4
    return df['Weighted_Close_Price']

def calculate_price_volume_trend(df: pd):
    """Calculate the Price Volume Trend (PVT) for stock prices.
    
    PVT is a cumulative indicator with no period parameter.
    It combines price momentum and volume to measure money flow.
    """
    pvt = [0]
    for i in range(1, len(df)):
        prev_price = df['Value'].iloc[i - 1]
        if prev_price != 0:  # Avoid division by zero
            price_change_pct = (df['Value'].iloc[i] - prev_price) / prev_price
            pvt_value = pvt[i-1] + (price_change_pct * df['Volume'].iloc[i])
        else:
            pvt_value = pvt[i-1]
        pvt.append(pvt_value)
    df['PVT'] = pvt
    return df['PVT']

def calculate_vortex_indicator(df: pd, nday: int = 14):
    """Calculate the Vortex Indicator for stock prices.
    
    VI+ and VI- measure upward and downward trend movement.
    Developed by Etienne Botes and Douglas Siepman (2010).
    """
    # True Range calculation
    tr = pd.concat([df['High'] - df['Low'], 
                    (df['High'] - df['Value'].shift()).abs(), 
                    (df['Low'] - df['Value'].shift()).abs()], axis=1).max(axis=1)
    
    # Vortex Movement: cross-over between current and previous extremes
    vmp = (df['High'] - df['Low'].shift()).abs()  # VM+: |High - Low[i-1]|
    vmm = (df['Low'] - df['High'].shift()).abs()  # VM-: |Low - High[i-1]|

    # Vortex Indicators
    vip = vmp.rolling(window=nday).sum() / tr.rolling(window=nday).sum()
    vin = vmm.rolling(window=nday).sum() / tr.rolling(window=nday).sum()

    df[f"Vortex_Pos_{nday}"] = vip
    df[f"Vortex_Neg_{nday}"] = vin
    return df[[f"Vortex_Pos_{nday}", f"Vortex_Neg_{nday}"]]
    
def calculate_ultimate_oscillator(df: pd, short_window: int = 7, mid_window: int = 14, long_window: int = 28):
    """Calculate the Ultimate Oscillator for stock prices.
    
    Developed by Larry Williams in 1976.
    Combines short, medium, and long-term momentum into one indicator.
    """
    close = df['Value']
    close_prev = close.shift()
    
    # Buying Pressure: Close - min(Low, Previous Close)
    bp = close - pd.concat([df['Low'], close_prev], axis=1).min(axis=1)
    
    # True Range for Ultimate Oscillator: max(High, Previous Close) - min(Low, Previous Close)
    tr = pd.concat([df['High'], close_prev], axis=1).max(axis=1) - pd.concat([df['Low'], close_prev], axis=1).min(axis=1)

    # Calculate averages for three periods
    avg_short = bp.rolling(window=short_window).sum() / tr.rolling(window=short_window).sum()
    avg_mid = bp.rolling(window=mid_window).sum() / tr.rolling(window=mid_window).sum()
    avg_long = bp.rolling(window=long_window).sum() / tr.rolling(window=long_window).sum()

    # Weighted average with weights 4:2:1
    df[f"Ultimate_Oscillator_{short_window}_{mid_window}_{long_window}"] = 100 * ((4 * avg_short) + (2 * avg_mid) + avg_long) / 7
    return df[f"Ultimate_Oscillator_{short_window}_{mid_window}_{long_window}"]
    
def calculate_chande_momentum_oscillator(df: pd, nday: int = 14):
    """Calculate the Chande Momentum Oscillator (CMO) for stock prices."""
    delta = df['Value'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=nday).sum()
    loss = -delta.where(delta < 0, 0).rolling(window=nday).sum()
    df[f"CMO_{nday}"] = 100 * (gain - loss) / (gain + loss)
    return df[f"CMO_{nday}"]
    
def calculate_donchian_channels(df: pd, nday: int = 20):
    """Calculate Donchian Channels for stock prices."""
    df[f"DC_upper_{nday}"] = df['High'].rolling(window=nday).max()
    df[f"DC_lower_{nday}"] = df['Low'].rolling(window=nday).min()
    df[f"DC_middle_{nday}"] = (df[f"DC_upper_{nday}"] + df[f"DC_lower_{nday}"]) / 2
    return df[[f"DC_upper_{nday}", f"DC_middle_{nday}", f"DC_lower_{nday}"]]
    
# 0 ~ 100 범위의 오실레이터
# 80 이상: 고가권 (과매수, 저항 근접)
# 20 이하: 저가권 (과매도, 지지 근접)
# 50: 채널 중간
def calculate_price_channel_index(df: pd, nday: int = 20):
    """Calculate the Price Channel Index (PCI) for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PCI_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"PCI_{nday}"]

# 활용법

# 반환값:
# +1: 상향 돌파 (매수 신호)
# -1: 하향 돌파 (매도 신호)
# 0: 돌파 없음 (대기)

# Turtle Trading 전략:
# 20일 채널 상향돌파 시 매수
# 20일 채널 하향돌파 시 매도
# 10일 채널로 청산    
def calculate_price_channel_breakout(df: pd, nday: int = 20):
    """Calculate the Price Channel Breakout for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Breakout_{nday}"] = 0
    df.loc[df['Value'] > highest_high.shift(), f"PC_Breakout_{nday}"] = 1
    df.loc[df['Value'] < lowest_low.shift(), f"PC_Breakout_{nday}"] = -1
    return df[f"PC_Breakout_{nday}"]

# PC_Trend vs PC_Breakout 차이
# 실제로 두 함수는 동일한 로직을 사용합니다:

# PC_Breakout: "돌파" 이벤트 감지 (일회성 신호)
# PC_Trend: "추세" 방향 표시 (지속 신호)
# 의미적으로는 다르지만 계산 방식은 같습니다.

# 활용법
# 반환값:

# +1: 상승 추세 (가격이 채널 상단 위)
# -1: 하락 추세 (가격이 채널 하단 아래)
# 0: 중립 (가격이 채널 내부)
# 채널 돌파 후 추세가 유지되는지 모니터링하는 데 사용됩니다.    
def calculate_price_channel_trend(df: pd, nday: int = 20):
    """Calculate the Price Channel Trend for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Trend_{nday}"] = 0
    df.loc[df['Value'] > highest_high.shift(), f"PC_Trend_{nday}"] = 1
    df.loc[df['Value'] < lowest_low.shift(), f"PC_Trend_{nday}"] = -1
    return df[f"PC_Trend_{nday}"]

# Price_Channel_Index와 유사 로직    
def calculate_price_channel_strength(df: pd, nday: int = 20):
    """Calculate the Price Channel Strength for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Strength_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"PC_Strength_{nday}"]

# Price_Channel_Index와 유사 로직
def calculate_price_channel_momentum(df: pd, nday: int):
    """Calculate the Price Channel Momentum for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Momentum_{nday}"] = (df['Value'] - lowest_low) / (highest_high - lowest_low) * 100
    return df[f"PC_Momentum_{nday}"]

# 특징:
# n일간 가격 변동폭을 채널 하단 기준 퍼센트로 표현
# 변동성이 클수록 값이 커짐
# 절대값 변동폭 → 상대 변동률로 정규화

# 해석:
# 낮은 값 (예: 5-10%): 저변동성, 횡보 또는 안정적 추세
# 높은 값 (예: 20-30%+): 고변동성, 급등락 또는 불안정
def calculate_price_channel_volatility(df: pd, nday: int = 20):
    """Calculate the Price Channel Volatility for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Volatility_{nday}"] = (highest_high - lowest_low) / lowest_low * 100
    return df[f"PC_Volatility_{nday}"]

# Donchian Channels Middle Line과 완전히 동일    
def calculate_price_channel_average(df: pd, nday: int):
    """Calculate the Price Channel Average for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Average_{nday}"] = (highest_high + lowest_low) / 2
    return df[f"PC_Average_{nday}"]

# Donchian Channels Range와 완전히 동일    
def calculate_price_channel_range(df: pd, nday: int):
    """Calculate the Price Channel Range for stock prices."""
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    df[f"PC_Range_{nday}"] = highest_high - lowest_low
    return df[f"PC_Range_{nday}"]

# Donchian Channels Width와 완전히 동일    
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
    """Calculate the Coppock Curve for stock prices.
    
    Original parameters (14, 11, 10) designed for monthly data.
    For daily data, consider using (22, 14, 10) or similar adjustments.
    Uses WMA (Weighted Moving Average) for smoothing, not SMA.
    """
    roc1 = calculate_rate_of_change(df, nday1)
    roc2 = calculate_rate_of_change(df, nday2)
    roc_sum = roc1 + roc2
    
    # Use WMA instead of SMA for proper Coppock Curve
    weights = pd.Series(range(1, nday3 + 1))
    df['Coppock_Curve'] = roc_sum.rolling(window=nday3).apply(
        lambda x: (x * weights).sum() / weights.sum(), raw=True
    )
    return df['Coppock_Curve']
    
def calculate_price_oscillator(df: pd, short_window: int = 12, long_window: int = 26, percentage: bool = False):
    """
    Calculate the Price Oscillator for stock prices.
    
    Price Oscillator는 두 개의 이동평균선(EMA) 차이를 이용한 모멘텀 지표입니다.
    MACD와 유사하지만 가격 자체의 EMA를 사용합니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'Value')
    short_window : int, default=12
        단기 EMA 기간 (표준: 12일)
    long_window : int, default=26
        장기 EMA 기간 (표준: 26일)
    percentage : bool, default=False
        True: PPO (Percentage Price Oscillator) 계산
        False: APO (Absolute Price Oscillator) 계산
    
    Returns:
    --------
    pd.Series
        Price Oscillator 값
    
    Formula:
    --------
    APO (Absolute): EMA(short) - EMA(long)
    PPO (Percentage): [(EMA(short) - EMA(long)) / EMA(long)] × 100
    
    Standard Parameters:
    -------------------
    - Short EMA: 12일 (주식), 9일 (선물/옵션)
    - Long EMA: 26일 (주식), 18일 (선물/옵션)
    - Signal Line: 9일 EMA (MACD와 동일)
    
    Trading Signals:
    ---------------
    1. Zero Cross:
       - PO > 0 → 상승 모멘텀 (매수 신호)
       - PO < 0 → 하락 모멘텀 (매도 신호)
    
    2. Signal Line Cross:
       - PO crosses above Signal → 매수 신호
       - PO crosses below Signal → 매도 신호
    
    3. Divergence:
       - 가격 신고점 vs PO 신저점 → 약세 다이버전스 (매도)
       - 가격 신저점 vs PO 신고점 → 강세 다이버전스 (매수)
    
    Notes:
    ------
    - MACD와 거의 동일한 지표 (MACD는 종가 EMA, PO는 가격 EMA)
    - PPO는 서로 다른 가격대의 종목 비교에 유용
    - APO는 절대적인 가격 변화 파악에 유용
    """
    # EMA 계산
    ema_short = df['Value'].ewm(span=short_window, adjust=False).mean()
    ema_long = df['Value'].ewm(span=long_window, adjust=False).mean()
    
    # Price Oscillator 계산
    if percentage:
        # PPO (Percentage Price Oscillator)
        df[f'PPO_{short_window}_{long_window}'] = ((ema_short - ema_long) / ema_long) * 100
        return df[f'PPO_{short_window}_{long_window}']
    else:
        # APO (Absolute Price Oscillator)
        df[f'APO_{short_window}_{long_window}'] = ema_short - ema_long
        # 하위 호환성을 위해 기존 컬럼명도 유지
        df['Price_Oscillator'] = df[f'APO_{short_window}_{long_window}']
        return df[f'APO_{short_window}_{long_window}']

# 여기까지 
    
    
def calculate_chaikin_oscillator(df: pd, short_window: int = 3, long_window: int = 10):
    """
    Calculate the Chaikin Oscillator for stock prices.
    
    Chaikin Oscillator는 Marc Chaikin이 개발한 모멘텀 지표로,
    ADL(Accumulation/Distribution Line)의 MACD 버전입니다.
    거래량과 가격의 관계를 분석하여 매수/매도 압력을 측정합니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'High', 'Low', 'Value', 'Volume')
    short_window : int, default=3
        단기 EMA 기간 (표준: 3일)
    long_window : int, default=10
        장기 EMA 기간 (표준: 10일)
    
    Returns:
    --------
    pd.Series
        Chaikin Oscillator 값
    
    Formula:
    --------
    1. Money Flow Multiplier (MFM):
       MFM = [(Close - Low) - (High - Close)] / (High - Low)
       
    2. Money Flow Volume (MFV):
       MFV = MFM × Volume
       
    3. Accumulation/Distribution Line (ADL):
       ADL = Cumulative Sum of MFV
       
    4. Chaikin Oscillator:
       Chaikin Oscillator = EMA(3, ADL) - EMA(10, ADL)
    
    Standard Parameters:
    -------------------
    - Short EMA: 3일 (표준)
    - Long EMA: 10일 (표준)
    - Alternative: (5, 20) - 느린 반응
    
    Trading Signals:
    ---------------
    1. Zero Cross:
       - Chaikin > 0 → 매수 압력 우세 (매수 신호)
       - Chaikin < 0 → 매도 압력 우세 (매도 신호)
    
    2. Divergence (중요):
       - 가격 신고점 + Chaikin 신저점 → 약세 다이버전스 (매도)
       - 가격 신저점 + Chaikin 신고점 → 강세 다이버전스 (매수)
    
    3. Trend Confirmation:
       - 가격 상승 + Chaikin 상승 → 상승 추세 확인
       - 가격 하락 + Chaikin 하락 → 하락 추세 확인
    
    Notes:
    ------
    - 거래량 정보를 활용하여 가격 움직임의 신뢰도 평가
    - MACD와 유사하지만 거래량 가중치 적용
    - 다이버전스가 가장 신뢰할 수 있는 신호
    - 횡보장에서는 신호 신뢰도 낮음
    """
    # 1. Money Flow Multiplier 계산
    # 분모가 0인 경우 처리 (High == Low인 경우)
    high_low_diff = df['High'] - df['Low']
    # 0으로 나누는 것을 방지하기 위해 매우 작은 값으로 대체
    high_low_diff = high_low_diff.replace(0, 0.0001)
    
    mfm = ((df['Value'] - df['Low']) - (df['High'] - df['Value'])) / high_low_diff
    
    # 2. Money Flow Volume 계산
    mfv = mfm * df['Volume']
    
    # 3. Accumulation/Distribution Line 계산 (누적합)
    adl = mfv.cumsum()
    
    # 4. Chaikin Oscillator 계산
    ema_short = adl.ewm(span=short_window, adjust=False).mean()
    ema_long = adl.ewm(span=long_window, adjust=False).mean()
    df['Chaikin_Oscillator'] = ema_short - ema_long
    
    # ADL도 DataFrame에 저장 (분석용)
    df['ADL'] = adl
    
    return df['Chaikin_Oscillator']
    
def calculate_aroon_indicator(df: pd, nday: int = 25):
    """
    Calculate the Aroon Indicator for stock prices.
    
    Aroon Indicator는 Tushar Chande가 개발한 추세 강도 지표로,
    일정 기간 동안 최고가/최저가가 발생한 이후 경과한 일수를 측정합니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'High', 'Low')
    nday : int, default=25
        Aroon 계산 기간 (표준: 25일)
        - 단기: 14일
        - 표준: 25일 (Tushar Chande 권장)
        - 장기: 50일
    
    Returns:
    --------
    pd.DataFrame
        Aroon Up, Aroon Down 값
    
    Formula:
    --------
    Aroon Up = [(N - Days Since N-day High) / N] × 100
    Aroon Down = [(N - Days Since N-day Low) / N] × 100
    
    예시 (N=25):
    - 25일 전에 최고가 발생 → Aroon Up = 0%
    - 오늘 최고가 발생 → Aroon Up = 100%
    - 12.5일 전에 최고가 발생 → Aroon Up = 50%
    
    Standard Parameters:
    -------------------
    - Short-term: 14일 (빠른 신호)
    - Standard: 25일 (Tushar Chande 권장)
    - Long-term: 50일 (장기 추세)
    
    Trading Signals:
    ---------------
    1. Trend Strength:
       - Aroon Up > 70 → 강한 상승 추세
       - Aroon Down > 70 → 강한 하락 추세
       - Both < 50 → 추세 없음 (횡보)
    
    2. Crossover:
       - Aroon Up crosses above Aroon Down → 매수 신호
       - Aroon Down crosses above Aroon Up → 매도 신호
    
    3. Extreme Levels:
       - Aroon Up = 100 → 새로운 고점 (강세)
       - Aroon Down = 100 → 새로운 저점 (약세)
    
    4. Aroon Oscillator:
       - Aroon Oscillator = Aroon Up - Aroon Down
       - > 0 → 상승 추세
       - < 0 → 하락 추세
    
    Notes:
    ------
    - 추세의 방향과 강도를 동시에 측정
    - 새로운 추세의 시작을 조기 감지
    - RSI, MACD와 달리 가격 변동폭이 아닌 시간에 기반
    - 횡보장에서는 신호 신뢰도 낮음
    """
    # 각 시점에서 최고가/최저가가 발생한 이후 경과 일수 계산
    # argmax/argmin은 윈도우 내에서 최댓값/최솟값의 인덱스를 반환
    # (nday - 1) - index = 경과 일수
    
    def days_since_high(window):
        """최고가 이후 경과 일수"""
        if len(window) == 0:
            return nday
        return len(window) - 1 - window.argmax()
    
    def days_since_low(window):
        """최저가 이후 경과 일수"""
        if len(window) == 0:
            return nday
        return len(window) - 1 - window.argmin()
    
    # N일 동안 최고가/최저가 이후 경과 일수
    days_since_high_series = df['High'].rolling(window=nday).apply(days_since_high, raw=True)
    days_since_low_series = df['Low'].rolling(window=nday).apply(days_since_low, raw=True)
    
    # Aroon Up/Down 계산
    # Aroon Up = [(N - 최고가 이후 경과일수) / N] × 100
    # Aroon Down = [(N - 최저가 이후 경과일수) / N] × 100
    df[f"Aroon_Up_{nday}"] = ((nday - days_since_high_series) / nday) * 100
    df[f"Aroon_Down_{nday}"] = ((nday - days_since_low_series) / nday) * 100
    
    # Aroon Oscillator 추가 (추세 방향 판단용)
    df[f"Aroon_Oscillator_{nday}"] = df[f"Aroon_Up_{nday}"] - df[f"Aroon_Down_{nday}"]
    
    return df[[f"Aroon_Up_{nday}", f"Aroon_Down_{nday}", f"Aroon_Oscillator_{nday}"]]
    
def calculate_money_flow_index(df: pd, nday: int = 14):
    """
    Calculate the Money Flow Index (MFI) for stock prices.
    
    MFI는 'Volume-weighted RSI'로 불리며, 가격과 거래량을 결합하여
    과매수/과매도 상태를 측정하는 모멘텀 오실레이터입니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'High', 'Low', 'Close' or 'Value', 'Volume')
    nday : int, default=14
        MFI 계산 기간 (표준: 14일)
        - 단기: 7일 (민감)
        - 표준: 14일 (Gene Quong & Avrum Soudack 권장)
        - 장기: 21일 (안정적)
    
    Returns:
    --------
    pd.Series
        Money Flow Index 값 (0~100)
    
    Formula:
    --------
    1. Typical Price = (High + Low + Close) / 3
    2. Raw Money Flow = Typical Price × Volume
    3. Money Flow Ratio = (14-period Positive MF) / (14-period Negative MF)
       - Positive MF: TP가 전일보다 상승한 날의 Raw Money Flow
       - Negative MF: TP가 전일보다 하락한 날의 Raw Money Flow
    4. MFI = 100 - [100 / (1 + Money Flow Ratio)]
    
    Standard Parameters:
    -------------------
    - Short-term: 7일 (빠른 신호)
    - Standard: 14일 (Gene Quong & Avrum Soudack 권장)
    - Long-term: 21일 (장기 추세)
    
    Trading Signals:
    ---------------
    1. Overbought/Oversold:
       - MFI > 80 → 과매수 (매도 고려)
       - MFI < 20 → 과매도 (매수 고려)
       - Conservative: 90/10 레벨 사용
    
    2. Divergence (강력한 신호):
       - Bullish: 가격 하락 but MFI 상승 → 반등 가능
       - Bearish: 가격 상승 but MFI 하락 → 조정 가능
    
    3. Failure Swing:
       - Top Failure: MFI가 80 위에서 고점 갱신 실패 → 매도
       - Bottom Failure: MFI가 20 아래에서 저점 갱신 실패 → 매수
    
    4. 50 레벨:
       - MFI > 50 → 매수 압력 우세
       - MFI < 50 → 매도 압력 우세
    
    Notes:
    ------
    - RSI와 유사하지만 거래량을 고려하여 더 신뢰성 높음
    - 거래량이 적은 종목에서는 신호 신뢰도 낮음
    - RSI와 함께 사용하여 확증 효과
    - 0으로 나누기 방지 필요 (Negative MF = 0인 경우)
    
    Developer: Gene Quong & Avrum Soudack (1989)
    """
    # Typical Price 계산
    # Close 컬럼이 없으면 Value 사용
    close_col = 'Close' if 'Close' in df.columns else 'Value'
    typical_price = (df['High'] + df['Low'] + df[close_col]) / 3
    
    # Raw Money Flow 계산
    raw_money_flow = typical_price * df['Volume']
    
    # Typical Price 변화 계산
    tp_change = typical_price.diff()
    
    # Positive/Negative Money Flow 분리
    # tp_change > 0: Positive, tp_change < 0: Negative
    # tp_change == 0인 경우는 둘 다 0으로 처리
    positive_flow = pd.Series(0.0, index=df.index)
    negative_flow = pd.Series(0.0, index=df.index)
    
    positive_flow[tp_change > 0] = raw_money_flow[tp_change > 0]
    negative_flow[tp_change < 0] = raw_money_flow[tp_change < 0]
    
    # N일 동안의 Positive/Negative Money Flow 합계
    positive_mf_sum = positive_flow.rolling(window=nday, min_periods=nday).sum()
    negative_mf_sum = negative_flow.rolling(window=nday, min_periods=nday).sum()
    
    # Money Flow Ratio 계산 (0으로 나누기 방지)
    # Negative MF가 0이면 MFI = 100
    money_flow_ratio = positive_mf_sum / negative_mf_sum.replace(0, 0.00001)
    
    # MFI 계산
    mfi = 100 - (100 / (1 + money_flow_ratio))
    
    df[f"MFI_{nday}"] = mfi
    
    # Raw Money Flow와 Typical Price도 저장 (분석용)
    df['Typical_Price'] = typical_price
    df['Raw_Money_Flow'] = raw_money_flow
    
    return df[f"MFI_{nday}"]

def calculate_force_index(df: pd, nday: int = 13, use_ema: bool = True):
    """
    Calculate the Force Index for stock prices.
    
    Force Index는 가격 변화, 거래량, 방향을 결합하여
    시장의 강도(힘)를 측정하는 지표입니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'Close' or 'Value', 'Volume')
    nday : int, default=13
        평활화 기간
        - 단기: 2일 (Raw Force Index, 매우 민감)
        - 표준: 13일 (Alexander Elder 권장, EMA 사용)
        - 장기: 100일 (장기 추세)
    use_ema : bool, default=True
        True: EMA 사용 (Elder 권장)
        False: SMA 사용
    
    Returns:
    --------
    pd.Series
        Force Index 값
    
    Formula:
    --------
    1. Raw Force Index = (Close - Close_previous) × Volume
    2. Force Index(N) = EMA(Raw Force Index, N)
       또는 SMA(Raw Force Index, N)
    
    Interpretation:
    ---------------
    - Positive FI: 상승 압력 (가격↑ + 거래량↑)
    - Negative FI: 하락 압력 (가격↓ + 거래량↑)
    - Zero 근처: 힘 없음 (낮은 거래량 또는 가격 변동 없음)
    
    Standard Parameters:
    -------------------
    - 2-period: Raw Force Index (노이즈 많음, 단기 신호)
    - 13-period EMA: 표준 (Alexander Elder 권장)
    - 100-period EMA: 장기 추세
    
    Trading Signals:
    ---------------
    1. Divergence (강력한 신호):
       - Bullish: 가격 하락 but FI 상승 → 매수
       - Bearish: 가격 상승 but FI 하락 → 매도
    
    2. Zero Cross:
       - FI > 0 → 상승 압력 (매수 고려)
       - FI < 0 → 하락 압력 (매도 고려)
    
    3. Extreme Values:
       - 극단적 양수: 과매수 (조정 가능)
       - 극단적 음수: 과매도 (반등 가능)
    
    4. Trend Confirmation:
       - 13-day FI와 100-day FI 같은 방향 → 강한 추세
       - 서로 다른 방향 → 추세 약화
    
    Notes:
    ------
    - 가격 변화와 거래량을 동시에 고려
    - 거래량이 많을수록 Force Index 절대값 증가
    - Elder는 13-day EMA 추천
    - 2-day FI는 단기 진입/청산 타이밍용
    
    Developer: Alexander Elder (1993)
    """
    # Close 컬럼 확인
    close_col = 'Close' if 'Close' in df.columns else 'Value'
    
    # Raw Force Index 계산
    # Force = (Close - Close_previous) × Volume
    price_change = df[close_col].diff()
    raw_force_index = price_change * df['Volume']
    
    # 평활화
    if use_ema:
        # EMA 사용 (Elder 권장)
        force_index = raw_force_index.ewm(span=nday, adjust=False).mean()
    else:
        # SMA 사용
        force_index = raw_force_index.rolling(window=nday).mean()
    
    df[f"FI_{nday}"] = force_index
    
    # Raw Force Index도 저장 (분석용)
    df['Raw_Force_Index'] = raw_force_index
    
    return df[f"FI_{nday}"]
    
def calculate_ease_of_movement(df: pd, nday: int = 14, scale_factor: float = 100000000):
    """
    Calculate the Ease of Movement (EOM) for stock prices.
    
    EOM은 가격이 얼마나 쉽게 움직이는지를 측정하는 지표로,
    거래량 대비 가격 변동폭을 계산합니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'High', 'Low', 'Volume')
    nday : int, default=14
        EOM 평활화 기간 (표준: 14일)
        - 단기: 7일
        - 표준: 14일 (Richard Arms 권장)
        - 장기: 20일
    scale_factor : float, default=100000000
        스케일링 팩터 (읽기 쉬운 값으로 변환)
        - 일반적으로 100,000,000 (1억) 사용
        - 거래량 단위에 따라 조정 가능
    
    Returns:
    --------
    pd.Series
        Ease of Movement 값
    
    Formula:
    --------
    1. Distance Moved = [(High + Low)/2 - (High_prev + Low_prev)/2]
    2. Box Ratio = (Volume / scale_factor) / (High - Low)
    3. EMV = Distance Moved / Box Ratio
    4. EOM = SMA(EMV, N)
    
    Interpretation:
    ---------------
    - Positive EOM: 상승이 쉬움 (적은 거래량으로 가격 상승)
    - Negative EOM: 하락이 쉬움 (적은 거래량으로 가격 하락)
    - Zero 근처: 움직임 어려움 (큰 거래량 필요)
    - High absolute value: 적은 거래량으로 큰 가격 변동
    
    Standard Parameters:
    -------------------
    - Short-term: 7일
    - Standard: 14일 (Richard Arms 권장)
    - Long-term: 20일
    - Scale Factor: 100,000,000 (1억)
    
    Trading Signals:
    ---------------
    1. Zero Cross:
       - EOM > 0 → 상승 추세 (매수 고려)
       - EOM < 0 → 하락 추세 (매도 고려)
    
    2. Extreme Values:
       - 매우 높은 양수: 과도한 상승 (조정 가능)
       - 매우 낮은 음수: 과도한 하락 (반등 가능)
    
    3. Divergence:
       - 가격 상승 but EOM 하락 → 약세 (거래량 증가)
       - 가격 하락 but EOM 상승 → 강세 (거래량 감소)
    
    4. Trend Confirmation:
       - EOM과 가격이 같은 방향 → 추세 강함
       - 반대 방향 → 추세 약함
    
    Notes:
    ------
    - 거래량이 적을수록 EOM 절대값 증가
    - 가격 변동폭(High-Low)이 작을수록 EOM 절대값 증가
    - 0으로 나누기 방지 필요 (High == Low)
    - Volume-by-Price 분석에 유용
    - Arms' Ease of Movement Value라고도 불림
    
    Developer: Richard W. Arms Jr. (1970)
    """
    # Distance Moved 계산 (중간 가격의 변화)
    midpoint = (df['High'] + df['Low']) / 2
    midpoint_prev = midpoint.shift()
    distance_moved = midpoint - midpoint_prev
    
    # High - Low (가격 변동 범위)
    price_range = df['High'] - df['Low']
    
    # 0으로 나누기 방지 (High == Low인 경우)
    # 가격 변동이 없으면 매우 작은 값으로 대체
    price_range_safe = price_range.replace(0, 0.0001)
    
    # Box Ratio 계산
    # Volume을 scale_factor로 나누어 적절한 스케일로 조정
    box_ratio = (df['Volume'] / scale_factor) / price_range_safe
    
    # 1-Period EMV (Ease of Movement Value)
    # Box Ratio가 0에 가까우면 EMV가 매우 커짐
    # 이는 적은 거래량으로 가격이 움직였다는 의미
    emv = distance_moved / box_ratio.replace(0, 0.0001)
    
    # N-day SMA로 평활화
    eom = emv.rolling(window=nday).mean()
    
    df[f"EOM_{nday}"] = eom
    
    # 1-Period EMV도 저장 (분석용)
    df['EMV_Raw'] = emv
    
    return df[f"EOM_{nday}"]

def calculate_volume_rate_of_change(df: pd, nday: int = 25):
    """
    Calculate the Volume Rate of Change (VROC) for stock prices.
    
    VROC는 일정 기간 동안 거래량의 변화율을 측정하는 지표로,
    거래량 추세의 강도를 파악하는 데 사용됩니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'Volume')
    nday : int, default=25
        VROC 계산 기간 (표준: 25일)
        - 단기: 12일
        - 표준: 25일 (가장 일반적)
        - 장기: 50일
    
    Returns:
    --------
    pd.Series
        Volume Rate of Change 값 (%)
    
    Formula:
    --------
    VROC = [(Volume - Volume_N_days_ago) / Volume_N_days_ago] × 100
    
    Interpretation:
    ---------------
    - Positive VROC: 거래량 증가 (관심도 증가)
    - Negative VROC: 거래량 감소 (관심도 감소)
    - Zero: 거래량 변화 없음
    - High absolute value: 급격한 거래량 변화
    
    Standard Parameters:
    -------------------
    - Short-term: 12일 (빠른 신호)
    - Standard: 25일 (가장 일반적)
    - Long-term: 50일 (장기 추세)
    
    Trading Signals:
    ---------------
    1. Trend Confirmation:
       - 가격 상승 + VROC 양수 → 강한 상승 추세 (확증)
       - 가격 하락 + VROC 양수 → 매도 압력 (주의)
       - 가격 상승 + VROC 음수 → 약한 상승 (의심)
       - 가격 하락 + VROC 음수 → 약한 하락
    
    2. Divergence (중요한 신호):
       - 가격 신고점 but VROC 하락 → 거래량 감소로 추세 약화
       - 가격 신저점 but VROC 상승 → 거래량 증가로 반등 가능
    
    3. Extreme Levels:
       - VROC > 100%: 거래량 폭발적 증가 (관심 급증)
       - VROC < -50%: 거래량 급감 (관심 소멸)
    
    4. Zero Cross:
       - VROC > 0 → 거래량 증가 추세
       - VROC < 0 → 거래량 감소 추세
    
    Notes:
    ------
    - Price ROC와 함께 사용하여 추세 강도 확인
    - 거래량 증가는 추세의 신뢰성을 높임
    - 거래량 감소는 추세 약화 신호
    - 급격한 거래량 변화는 반전 신호일 수 있음
    - 0으로 나누기 방지 필요 (Volume = 0인 경우)
    
    Related Indicators:
    ------------------
    - Price ROC: 가격 변화율
    - Volume: 절대 거래량
    - OBV: 누적 거래량
    """
    # N일 전 거래량
    volume_n_days_ago = df['Volume'].shift(nday)
    
    # 0으로 나누기 방지
    # 거래량이 0이면 매우 작은 값으로 대체
    volume_n_days_ago_safe = volume_n_days_ago.replace(0, 0.0001)
    
    # VROC 계산 (%)
    vroc = ((df['Volume'] - volume_n_days_ago) / volume_n_days_ago_safe) * 100
    
    df[f"VROC_{nday}"] = vroc
    
    return df[f"VROC_{nday}"]
    
def calculate_money_flow_volume(df: pd, nday: int = 20):
    """
    Calculate the Money Flow Volume (MFV) for stock prices.
    
    MFV는 Typical Price에 거래량을 곱한 값을 일정 기간 누적하여
    자금 흐름의 규모를 측정하는 지표입니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'High', 'Low', 'Close' or 'Value', 'Volume')
    nday : int, default=20
        MFV 누적 기간 (표준: 20일)
        - 단기: 10일
        - 표준: 20일 (가장 일반적)
        - 장기: 50일
    
    Returns:
    --------
    pd.Series
        Money Flow Volume 값
    
    Formula:
    --------
    1. Typical Price = (High + Low + Close) / 3
    2. Money Flow = Typical Price × Volume
    3. MFV = Sum(Money Flow, N periods)
    
    Interpretation:
    ---------------
    - Increasing MFV: 자금 유입 증가 (매수 압력)
    - Decreasing MFV: 자금 유출 증가 (매도 압력)
    - High MFV: 큰 규모의 자금 거래
    - Low MFV: 작은 규모의 자금 거래
    
    Standard Parameters:
    -------------------
    - Short-term: 10일
    - Standard: 20일 (가장 일반적)
    - Long-term: 50일
    
    Trading Signals:
    ---------------
    1. Trend Analysis:
       - Rising MFV + Rising Price → 강한 상승 (자금 유입)
       - Rising MFV + Falling Price → 바닥 형성 가능
       - Falling MFV + Rising Price → 약한 상승 (자금 유출)
       - Falling MFV + Falling Price → 강한 하락
    
    2. Divergence:
       - Price makes new high, MFV doesn't → 약세 (자금 감소)
       - Price makes new low, MFV doesn't → 강세 (자금 증가)
    
    3. Volume Confirmation:
       - High MFV with price breakout → 신뢰할 수 있는 돌파
       - Low MFV with price breakout → 약한 돌파 (의심)
    
    Notes:
    ------
    - Typical Price는 해당 기간의 평균 가격 수준 대표
    - 거래량과 가격을 모두 고려
    - 자금의 절대적 규모를 측정 (방향성은 2차 지표)
    - Money Flow Index(MFI)와는 다른 개념
      * MFI: 과매수/과매도 오실레이터 (0-100)
      * MFV: 자금 흐름의 절대 규모 측정
    
    Related Indicators:
    ------------------
    - Money Flow Index (MFI): 방향성을 포함한 오실레이터
    - On-Balance Volume (OBV): 방향성 거래량
    - Accumulation/Distribution: 자금 축적/분배
    """
    # Close 컬럼 확인
    close_col = 'Close' if 'Close' in df.columns else 'Value'
    
    # Typical Price 계산
    typical_price = (df['High'] + df['Low'] + df[close_col]) / 3
    
    # Money Flow 계산 (Typical Price × Volume)
    money_flow = typical_price * df['Volume']
    
    # N일 동안의 Money Flow 누적
    mfv = money_flow.rolling(window=nday).sum()
    
    df[f"MFV_{nday}"] = mfv
    
    # Typical Price와 Money Flow도 저장 (분석용)
    df['Typical_Price_MFV'] = typical_price
    df['Money_Flow'] = money_flow
    
    return df[f"MFV_{nday}"]

def calculate_accumulation_distribution(df: pd):
    """
    Calculate the Accumulation/Distribution Line for stock prices.
    
    A/D Line은 Marc Chaikin이 개발한 지표로, 거래량과 가격 위치를 결합하여
    자금의 축적(매수)과 분배(매도)를 측정합니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'High', 'Low', 'Close' or 'Value', 'Volume')
    
    Returns:
    --------
    pd.Series
        Accumulation/Distribution Line 값 (누적)
    
    Formula:
    --------
    1. Money Flow Multiplier (MFM) = [(Close - Low) - (High - Close)] / (High - Low)
       = (2×Close - High - Low) / (High - Low)
    2. Money Flow Volume = MFM × Volume
    3. A/D Line = Cumulative Sum of Money Flow Volume
    
    Money Flow Multiplier Range:
    ----------------------------
    - MFM = +1: Close = High (강한 매수)
    - MFM = 0: Close = (High + Low) / 2 (중립)
    - MFM = -1: Close = Low (강한 매도)
    
    Interpretation:
    ---------------
    - Rising A/D Line: 축적 (매수 압력, 자금 유입)
    - Falling A/D Line: 분배 (매도 압력, 자금 유출)
    - Flat A/D Line: 균형 (매수/매도 균형)
    
    Trading Signals:
    ---------------
    1. Trend Confirmation:
       - Price↑ + A/D↑ → 상승 추세 확증 (자금 유입)
       - Price↓ + A/D↓ → 하락 추세 확증 (자금 유출)
    
    2. Divergence (강력한 신호):
       - Bullish: Price makes new low, A/D doesn't → 매수 압력 증가
       - Bearish: Price makes new high, A/D doesn't → 매도 압력 증가
    
    3. Breakout Confirmation:
       - A/D breaks out before price → 조기 신호
       - A/D confirms price breakout → 신뢰할 수 있는 돌파
    
    Notes:
    ------
    - Marc Chaikin이 On-Balance Volume을 개선하여 개발
    - 종가 위치를 고려하여 더 정교함
    - 누적 지표이므로 절대값보다 추세가 중요
    - 다이버전스가 가장 강력한 신호
    - High == Low인 경우 처리 필요 (0으로 나누기)
    
    Developer: Marc Chaikin
    Related: Chaikin Oscillator, Chaikin Money Flow
    """
    # Close 컬럼 확인
    close_col = 'Close' if 'Close' in df.columns else 'Value'
    
    # High - Low (가격 범위)
    high_low_diff = df['High'] - df['Low']
    
    # 0으로 나누기 방지 (High == Low인 경우)
    # 가격 변동이 없으면 매우 작은 값으로 대체
    high_low_diff_safe = high_low_diff.replace(0, 0.0001)
    
    # Money Flow Multiplier 계산
    # MFM = [(Close - Low) - (High - Close)] / (High - Low)
    # = (2×Close - High - Low) / (High - Low)
    mfm = ((df[close_col] - df['Low']) - (df['High'] - df[close_col])) / high_low_diff_safe
    
    # Money Flow Volume 계산
    mfv = mfm * df['Volume']
    
    # A/D Line 계산 (누적)
    ad_line = mfv.cumsum()
    
    df['A/D_Line'] = ad_line
    
    # Money Flow Multiplier와 Money Flow Volume도 저장 (분석용)
    df['MFM'] = mfm
    df['MFV_AD'] = mfv
    
    return df['A/D_Line']

def calculate_accumulation_distribution_oscillator(df: pd.DataFrame, short_window: int = 3, long_window: int = 10):
    """
    Accumulation/Distribution Oscillator (Chaikin Oscillator) 계산
    
    A/D Line의 단기/장기 EMA 차이로 모멘텀을 측정하는 지표입니다.
    Marc Chaikin이 개발했으며, A/D Line의 추세 변화를 조기 감지합니다.
    
    Formula:
    --------
    1. A/D Line 계산 (먼저 calculate_accumulation_distribution 실행 필요)
    2. Short EMA = EMA(A/D Line, short_window)
    3. Long EMA = EMA(A/D Line, long_window)
    4. A/D Oscillator = Short EMA - Long EMA
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLCV 데이터를 포함한 DataFrame (A/D_Line 컬럼 필수)
    short_window : int, default=3
        단기 EMA 기간 (Chaikin 표준: 3일)
    long_window : int, default=10
        장기 EMA 기간 (Chaikin 표준: 10일)
    
    Returns:
    --------
    pd.Series
        A/D Oscillator 값
    
    Interpretation:
    ---------------
    - ADO > 0: 매수 압력 우세 (축적)
    - ADO < 0: 매도 압력 우세 (분배)
    - ADO 상승 중: 상승 모멘텀 강화
    - ADO 하락 중: 하락 모멘텀 강화
    - 0선 돌파: 추세 전환 신호
    
    Trading Signals:
    ----------------
    1. Zero Line Cross:
       - ADO가 0 돌파 상승 → BUY (자금 유입 시작)
       - ADO가 0 아래 하락 → SELL (자금 유출 시작)
    
    2. Divergence:
       - 가격 신고점 but ADO 낮아짐 → Bearish (약세 다이버전스)
       - 가격 신저점 but ADO 높아짐 → Bullish (강세 다이버전스)
    
    3. Trend Confirmation:
       - 가격 상승 + ADO 상승 → 강한 상승 추세
       - 가격 하락 + ADO 하락 → 강한 하락 추세
    
    Standard Parameters:
    --------------------
    - Marc Chaikin Original: (3, 10) ← 현재 기본값
    - Alternative Settings: (2, 5) - 더 민감한 반응
    - Conservative: (5, 20) - 노이즈 감소
    
    Notes:
    ------
    - A/D Line이 먼저 계산되어야 합니다
    - MACD와 유사한 형태이지만 거래량 정보 포함
    - 단기간 추세 변화 감지에 효과적
    - 중소형주에서 더 신뢰도 높음
    
    Developer:
    ----------
    Marc Chaikin (Chaikin Analytics)
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> calculate_accumulation_distribution(df)  # 먼저 A/D Line 계산
    >>> calculate_accumulation_distribution_oscillator(df, short_window=3, long_window=10)
    >>> # 매매 신호: df['A/D_Oscillator'] 0선 돌파 확인
    """
    # A/D Line 존재 확인
    if 'A/D_Line' not in df.columns:
        # A/D Line이 없으면 먼저 계산
        calculate_accumulation_distribution(df)
    
    if 'A/D_Line' not in df.columns:
        raise ValueError("A/D_Line column not found. Cannot calculate A/D Oscillator.")
    
    # A/D Line의 EMA 계산
    ad_line = df['A/D_Line']
    ema_short = ad_line.ewm(span=short_window, adjust=False).mean()
    ema_long = ad_line.ewm(span=long_window, adjust=False).mean()
    
    # Oscillator = Short EMA - Long EMA
    df['A/D_Oscillator'] = ema_short - ema_long
    
    # 추가 정보 저장 (분석용)
    df['A/D_EMA_Short'] = ema_short
    df['A/D_EMA_Long'] = ema_long
    
    return df['A/D_Oscillator']

def calculate_mass_index(df: pd.DataFrame, nday: int = 25, ema_period: int = 9):
    """
    Mass Index 계산 - 추세 반전을 감지하는 변동성 지표
    
    Donald Dorsey가 개발한 지표로, 가격 범위(High-Low)의 변동성을 측정하여
    추세 반전을 조기 경고합니다. 가격 방향과 무관하게 변동성만 측정합니다.
    
    Formula:
    --------
    1. Range = High - Low
    2. EMA1 = EMA(Range, ema_period)
    3. EMA2 = EMA(EMA1, ema_period)  ← Double EMA
    4. EMA Ratio = EMA1 / EMA2
    5. Mass Index = Sum(EMA Ratio, nday)
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLCV 데이터를 포함한 DataFrame
    nday : int, default=25
        EMA Ratio 합계 기간 (Dorsey 표준: 25일)
    ema_period : int, default=9
        EMA 기간 (Dorsey 표준: 9일)
    
    Returns:
    --------
    pd.Series
        Mass Index 값
    
    Interpretation:
    ---------------
    - MI > 27.0: Reversal Bulge (추세 반전 경고 - 매우 중요!)
    - MI < 26.5: Bulge 해제 (경고 해제)
    - MI 상승: 변동성 증가 (추세 약화 가능)
    - MI 하락: 변동성 감소 (추세 안정)
    - 일반 범위: 18~26
    
    Trading Signals:
    ----------------
    1. Reversal Bulge Setup:
       - MI가 27.0 돌파 → 반전 경고 활성화
       - MI가 26.5 아래로 하락 → 반전 신호 발생
       - 방향: 직전 9일 가격 추세의 반대 방향
    
    2. Signal Generation:
       Step 1: MI > 27.0 (Bulge 형성 - 경고 상태)
       Step 2: MI < 26.5 (Bulge 완료 - 반전 신호)
       Step 3: 가격 방향 확인
         - 직전 상승 → SELL (하락 반전)
         - 직전 하락 → BUY (상승 반전)
    
    3. Exit Signal:
       - 반전 후 MI가 다시 27.0 돌파 (새로운 반전 경고)
       - 또는 Stop Loss (3%)
    
    Standard Parameters:
    --------------------
    - Donald Dorsey Original: nday=25, ema_period=9 ← 현재 기본값
    - Alternative: nday=20, ema_period=9 (더 민감)
    - Thresholds:
      * Bulge Start: 27.0
      * Bulge End (Signal): 26.5
      * Normal Range: 18~26
    
    Notes:
    ------
    - 가격 방향과 무관하게 변동성만 측정
    - 27.0 돌파 = 반전 가능성 높음 (경고)
    - 26.5 하락 = 반전 확정 신호
    - 다른 지표와 조합 필수 (방향 확인용)
    - 모든 시장 환경에서 작동 (상승/하락/횡보)
    - False Signal 적음 (신뢰도 높음)
    
    Developer:
    ----------
    Donald Dorsey (1992)
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> calculate_mass_index(df, nday=25, ema_period=9)
    >>> # 매매 신호:
    >>> # 1. MI > 27.0 돌파 → 경고 (대기)
    >>> # 2. MI < 26.5 하락 → 반전 신호
    >>> # 3. 직전 9일 추세 반대로 진입
    """
    # High-Low Range 계산
    high_low_diff = df['High'] - df['Low']
    
    # Division by zero 방지
    high_low_diff = high_low_diff.replace(0, 0.0001)
    
    # Single EMA
    ema1 = high_low_diff.ewm(span=ema_period, adjust=False).mean()
    
    # Double EMA
    ema2 = ema1.ewm(span=ema_period, adjust=False).mean()
    
    # Division by zero 방지
    ema2 = ema2.replace(0, 0.0001)
    
    # EMA Ratio
    ema_ratio = ema1 / ema2
    
    # Mass Index = Sum of EMA Ratio over nday period
    mass_index = ema_ratio.rolling(window=nday).sum()
    
    df['Mass_Index'] = mass_index
    
    # 추가 정보 저장 (분석용)
    df['MI_EMA1'] = ema1
    df['MI_EMA2'] = ema2
    df['MI_Ratio'] = ema_ratio
    
    return df['Mass_Index']

def calculate_intraday_momentum_index(df: pd.DataFrame, nday: int = 14):
    """
    Intraday Momentum Index (IMI) 계산 - 일중 모멘텀 측정 지표
    
    RSI와 유사하지만 종가 간 변화 대신 일중(Open vs Close) 변화를 측정합니다.
    Tushar Chande가 개발했으며, 단기 과매수/과매도 상태를 더 민감하게 감지합니다.
    
    Formula:
    --------
    1. Up Day: Close > Open (일중 상승)
       Up Gain = Close - Open
    2. Down Day: Close < Open (일중 하락)
       Down Loss = Open - Close
    3. Sum of Up Gains (nday period)
    4. Sum of Down Losses (nday period)
    5. IMI = 100 × (Sum Up) / (Sum Up + Sum Down)
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLCV 데이터를 포함한 DataFrame (Open, Close 필수)
    nday : int, default=14
        IMI 계산 기간 (Chande 표준: 14일)
    
    Returns:
    --------
    pd.Series
        IMI 값 (0~100 범위)
    
    Interpretation:
    ---------------
    - IMI > 70: 과매수 (Overbought) - 매도 고려
    - IMI < 30: 과매도 (Oversold) - 매수 고려
    - IMI > 50: 상승 모멘텀 우세
    - IMI < 50: 하락 모멘텀 우세
    - IMI = 50: 중립 (균형)
    
    Trading Signals:
    ----------------
    1. Overbought/Oversold:
       - IMI > 70 → SELL (과매수)
       - IMI < 30 → BUY (과매도)
    
    2. Centerline Cross:
       - IMI 50 상향 돌파 → BUY (모멘텀 전환)
       - IMI 50 하향 돌파 → SELL (모멘텀 약화)
    
    3. Divergence:
       - 가격 신고점 but IMI 낮아짐 → Bearish (약세 다이버전스)
       - 가격 신저점 but IMI 높아짐 → Bullish (강세 다이버전스)
    
    4. Extreme Readings:
       - IMI > 80: 극단적 과매수 (강력한 매도 신호)
       - IMI < 20: 극단적 과매도 (강력한 매수 신호)
    
    Standard Parameters:
    --------------------
    - Tushar Chande Original: nday=14 ← 현재 기본값
    - Short-term: nday=7 (더 민감한 반응)
    - Long-term: nday=21 (더 안정적)
    - Thresholds: 
      * Overbought: 70
      * Oversold: 30
      * Extreme: 80/20
    
    Differences from RSI:
    ---------------------
    - RSI: Close vs Previous Close (종가 간 비교)
    - IMI: Close vs Open (일중 변화)
    - IMI가 더 민감하고 단기 신호에 적합
    - IMI는 갭 영향 받지 않음 (일중만 측정)
    
    Notes:
    ------
    - RSI보다 더 빠른 신호 제공
    - 단기 트레이딩에 적합
    - 일중 모멘텀 변화를 조기 감지
    - 갭 발생 시 RSI보다 안정적
    - Open 데이터 필수 (일봉 데이터에 적합)
    
    Developer:
    ----------
    Tushar Chande
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> calculate_intraday_momentum_index(df, nday=14)
    >>> # 매매 신호:
    >>> # IMI < 30 → BUY (과매도)
    >>> # IMI > 70 → SELL (과매수)
    """
    # Open과 Close 컬럼 확인
    if 'Open' not in df.columns:
        # Open이 없으면 Value를 사용 (Close의 대체)
        if 'Close' in df.columns:
            df['Open'] = df['Close'].shift(1)  # 전일 종가를 Open으로 근사
        else:
            raise ValueError("Neither 'Open' nor 'Close' column found in DataFrame")
    
    # Close 컬럼 확인 (Value 또는 Close)
    if 'Close' in df.columns:
        close = df['Close']
    elif 'Value' in df.columns:
        close = df['Value']
    else:
        raise ValueError("Neither 'Close' nor 'Value' column found in DataFrame")
    
    open_price = df['Open']
    
    # 일중 변화 계산 (Close - Open)
    intraday_change = close - open_price
    
    # Up Day와 Down Day 분리
    up_days = intraday_change > 0
    down_days = intraday_change < 0
    
    # Up Gains와 Down Losses
    up_gains = intraday_change.where(up_days, 0)
    down_losses = (-intraday_change).where(down_days, 0)  # 양수로 변환
    
    # nday 기간 합계
    sum_up_gains = up_gains.rolling(window=nday).sum()
    sum_down_losses = down_losses.rolling(window=nday).sum()
    
    # Division by zero 방지
    total = sum_up_gains + sum_down_losses
    total = total.replace(0, 0.0001)
    
    # IMI 계산
    imi = 100 * (sum_up_gains / total)
    
    df[f"IMI_{nday}"] = imi
    
    # 추가 정보 저장 (분석용)
    df[f"IMI_Up_Sum_{nday}"] = sum_up_gains
    df[f"IMI_Down_Sum_{nday}"] = sum_down_losses
    
    return df[f"IMI_{nday}"]

def calculate_true_strength_index(df: pd.DataFrame, long_window: int = 25, short_window: int = 13, signal_window: int = 7):
    """
    True Strength Index (TSI) 계산 - 이중 스무딩 모멘텀 오실레이터
    
    William Blau가 개발한 지표로, 가격 변화를 이중 EMA로 스무딩하여
    노이즈를 줄이고 추세와 모멘텀을 동시에 측정합니다.
    
    Formula:
    --------
    1. Price Change = Close - Previous Close
    2. Double Smoothed Price Change:
       - First EMA = EMA(Price Change, long_window)
       - Second EMA = EMA(First EMA, short_window)
    3. Double Smoothed Absolute Price Change:
       - First EMA = EMA(|Price Change|, long_window)
       - Second EMA = EMA(First EMA, short_window)
    4. TSI = 100 × (Double Smoothed Change / Double Smoothed Abs Change)
    5. Signal Line = EMA(TSI, signal_window)
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLCV 데이터를 포함한 DataFrame
    long_window : int, default=25
        첫 번째 EMA 기간 (Blau 표준: 25일)
    short_window : int, default=13
        두 번째 EMA 기간 (Blau 표준: 13일)
    signal_window : int, default=7
        신호선 EMA 기간 (Blau 표준: 7일)
    
    Returns:
    --------
    pd.DataFrame
        TSI와 TSI_signal 컬럼을 포함한 DataFrame
    
    Interpretation:
    ---------------
    - TSI > 0: 상승 모멘텀 (Bullish)
    - TSI < 0: 하락 모멘텀 (Bearish)
    - TSI > 25: 강한 상승 모멘텀
    - TSI < -25: 강한 하락 모멘텀
    - TSI 범위: -100 ~ +100
    
    Trading Signals:
    ----------------
    1. Zero Line Cross (가장 중요):
       - TSI > 0 돌파 → BUY (모멘텀 전환)
       - TSI < 0 하락 → SELL (모멘텀 약화)
    
    2. Signal Line Cross:
       - TSI > Signal → BUY (단기 모멘텀 강화)
       - TSI < Signal → SELL (단기 모멘텀 약화)
    
    3. Divergence:
       - 가격 신고점 but TSI 낮아짐 → Bearish (약세 다이버전스)
       - 가격 신저점 but TSI 높아짐 → Bullish (강세 다이버전스)
    
    4. Overbought/Oversold (보조적):
       - TSI > +25: 과매수 경향
       - TSI < -25: 과매도 경향
    
    Standard Parameters:
    --------------------
    - William Blau Original: (25, 13, 7) ← 현재 기본값
    - More Sensitive: (13, 7, 7) - 빠른 반응
    - More Stable: (40, 20, 10) - 노이즈 감소
    - Thresholds:
      * Strong Bull: TSI > +25
      * Strong Bear: TSI < -25
      * Neutral: -25 ~ +25
    
    Advantages:
    -----------
    - 이중 스무딩으로 노이즈 최소화
    - False Signal 적음
    - 추세와 모멘텀 동시 측정
    - 다이버전스 감지 우수
    - 모든 시장 환경에서 작동
    
    Notes:
    ------
    - MACD보다 더 스무딩됨 (신호 더 안정적)
    - RSI보다 추세 파악 우수
    - 0선 돌파가 가장 신뢰할 수 있는 신호
    - 신호선 교차로 진입/청산 타이밍 정밀화
    - 장기 투자보다 중단기 트레이딩에 적합
    
    Developer:
    ----------
    William Blau
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> calculate_true_strength_index(df, long_window=25, short_window=13, signal_window=7)
    >>> # 매매 신호:
    >>> # TSI > 0 AND TSI > Signal → BUY
    >>> # TSI < 0 OR TSI < Signal → SELL
    """
    # Close/Value 컬럼 확인
    if 'Close' in df.columns:
        price = df['Close']
    elif 'Value' in df.columns:
        price = df['Value']
    else:
        raise ValueError("Neither 'Close' nor 'Value' column found in DataFrame")
    
    # 가격 변화 (Momentum)
    delta = price.diff()
    abs_delta = delta.abs()
    
    # Double Smoothing of Price Change
    # 1st smoothing: long_window
    ema1 = delta.ewm(span=long_window, adjust=False).mean()
    # 2nd smoothing: short_window
    ema2 = ema1.ewm(span=short_window, adjust=False).mean()
    
    # Double Smoothing of Absolute Price Change
    # 1st smoothing: long_window
    abs_ema1 = abs_delta.ewm(span=long_window, adjust=False).mean()
    # 2nd smoothing: short_window
    abs_ema2 = abs_ema1.ewm(span=short_window, adjust=False).mean()
    
    # Division by zero 방지
    abs_ema2 = abs_ema2.replace(0, 0.0001)
    
    # TSI 계산
    tsi = 100 * (ema2 / abs_ema2)
    df['TSI'] = tsi
    
    # Signal Line (TSI의 EMA)
    df['TSI_Signal'] = tsi.ewm(span=signal_window, adjust=False).mean()
    
    # 추가 정보 저장 (분석용)
    df['TSI_Momentum'] = ema2  # Double smoothed momentum
    df['TSI_Abs_Momentum'] = abs_ema2  # Double smoothed absolute momentum
    
    return df[['TSI', 'TSI_Signal']]
    
def calculate_dpo(df: pd.DataFrame, nday: int = 20):
    """
    Detrended Price Oscillator (DPO) 계산 - 추세 제거 가격 오실레이터
    
    추세를 제거하여 가격의 사이클(주기)을 식별하는 지표입니다.
    장기 추세에 관계없이 단기 과매수/과매도와 사이클 패턴을 파악합니다.
    
    Formula:
    --------
    DPO = Price - SMA(Price, nday) [shifted (nday/2 + 1) periods ago]
    
    Note: SMA는 과거로 shift되어 중앙 정렬됩니다 (centered).
    이는 DPO를 비추세성(non-trending) 지표로 만듭니다.
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLCV 데이터를 포함한 DataFrame
    nday : int, default=20
        SMA 기간 (일반 표준: 20일)
        - 단기 사이클: 10~14일
        - 중기 사이클: 20~30일
        - 장기 사이클: 40~60일
    
    Returns:
    --------
    pd.Series
        DPO 값
    
    Interpretation:
    ---------------
    - DPO > 0: 가격이 과거 평균보다 높음 (과매수 경향)
    - DPO < 0: 가격이 과거 평균보다 낮음 (과매도 경향)
    - DPO는 추세 방향이 아닌 사이클을 측정
    - Zero Line Cross는 매매 신호가 아님 (사이클 파악용)
    
    Trading Signals:
    ----------------
    1. Cycle Peaks/Troughs (사이클 분석):
       - DPO Peak → 사이클 고점 (과매수)
       - DPO Trough → 사이클 저점 (과매도)
       - 사이클 간격 측정 → 다음 전환점 예측
    
    2. Overbought/Oversold (보조적):
       - DPO가 과거 최고점 근처 → 과매수
       - DPO가 과거 최저점 근처 → 과매도
    
    3. Zero Line (중립):
       - DPO > 0: 단기적으로 평균 이상
       - DPO < 0: 단기적으로 평균 이하
    
    Standard Parameters:
    --------------------
    - General Standard: nday=20 ← 현재 기본값
    - Short Cycle: nday=10~14
    - Medium Cycle: nday=20~30
    - Long Cycle: nday=40~60
    
    Important Notes:
    ----------------
    - DPO는 후행 지표가 아님 (centered SMA 사용)
    - 추세 지표가 아님 (사이클 식별용)
    - 매매 신호보다는 사이클 분석에 사용
    - 다른 추세 지표와 조합 필수
    - 과거 데이터를 기준으로 하므로 실시간 신호 부적합
    
    Use Cases:
    ----------
    1. 사이클 길이 측정 (peak to peak)
    2. 다음 사이클 전환점 예측
    3. 과매수/과매도 확인 (보조)
    4. 가격 패턴 분석
    
    Limitations:
    ------------
    - 추세 시장에서 효과 낮음
    - 실시간 매매 신호로 부적합
    - SMA가 shift되어 있어 최근 데이터 반영 안 됨
    - 주로 사후 분석용
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> calculate_dpo(df, nday=20)
    >>> # DPO 사이클 분석:
    >>> # Peak 간격 측정 → 사이클 주기 파악
    >>> # Trough에서 매수, Peak에서 매도 고려
    """
    # Close/Value 컬럼 확인
    if 'Close' in df.columns:
        price = df['Close']
    elif 'Value' in df.columns:
        price = df['Value']
    else:
        raise ValueError("Neither 'Close' nor 'Value' column found in DataFrame")
    
    # Simple Moving Average 계산
    sma = price.rolling(window=nday).mean()
    
    # DPO: 현재 가격 - Shifted SMA
    # Shift = (nday / 2) + 1 periods (중앙 정렬)
    shift_period = int(nday / 2) + 1
    dpo = price - sma.shift(shift_period)
    
    df[f"DPO_{nday}"] = dpo
    
    # 추가 정보 저장 (분석용)
    df[f"DPO_SMA_{nday}"] = sma
    df[f"DPO_Shift_{nday}"] = sma.shift(shift_period)
    
    return df[f"DPO_{nday}"]
    
def calculate_klinger_oscillator(df: pd.DataFrame, short: int = 34, long: int = 55, signal: int = 13):
    """
    Klinger Volume Oscillator (KVO) - 거래량과 가격의 누적 관계 분석
    
    Stephen J. Klinger가 개발한 지표로 단기/장기 거래량 추세를 비교하여
    가격 움직임의 지속성과 반전 신호를 감지합니다.
    
    Formula:
    --------
    1. Trend = +1 if (H+L+C) > (H+L+C)_prev, else -1
    2. DM = High - Low (Daily Movement)
    3. CM = CM_prev + DM (Cumulative Movement, if Trend continues)
           or DM (if Trend reverses)
    4. Volume Force (VF) = Volume × Trend × |2×((DM/CM)-1)| × 100
    5. KVO = EMA(VF, short) - EMA(VF, long)
    6. Signal = EMA(KVO, signal)
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLCV 데이터 (High, Low, Close, Volume 필수)
    short : int, default=34
        단기 EMA 기간 (Klinger 표준)
    long : int, default=55
        장기 EMA 기간 (Klinger 표준)
    signal : int, default=13
        신호선 EMA 기간 (Klinger 표준)
    
    Returns:
    --------
    pd.DataFrame
        KVO_{short}_{long} : Klinger Oscillator
        KVO_Signal_{short}_{long}_{signal} : Signal Line
    
    Trading Signals:
    ----------------
    1. **Zero Line Cross (주추세 전환)**:
       - KVO > 0: 매수 압력 우세 (상승 추세)
       - KVO < 0: 매도 압력 우세 (하락 추세)
    
    2. **Signal Line Cross (단기 전환)**:
       - KVO > Signal: 매수 신호
       - KVO < Signal: 매도 신호
    
    3. **Divergence (고급)**:
       - 가격 고점 상승 + KVO 고점 하락: 약세 다이버전스 (매도)
       - 가격 저점 하락 + KVO 저점 상승: 강세 다이버전스 (매수)
    
    4. **Trend Confirmation**:
       - 가격 상승 + KVO 상승: 거래량 뒷받침 (강한 추세)
       - 가격 상승 + KVO 하락: 거래량 약화 (추세 약함)
    
    Interpretation:
    ---------------
    - KVO > 0: 매수세 우세 (accumulation)
    - KVO < 0: 매도세 우세 (distribution)
    - KVO 극값: 과매수/과매도 (반전 가능)
    - KVO와 가격 다이버전스: 추세 전환 경고
    
    Use Cases:
    ----------
    1. 추세 확인: 가격 + KVO 동반 상승 시 신뢰도 ↑
    2. 진입 타이밍: Signal Line Cross로 단기 진입점
    3. 다이버전스: 추세 전환 조기 감지
    4. 거래량 분석: 가격 움직임의 거래량 뒷받침 확인
    
    Advantages:
    -----------
    - 거래량과 가격 추세를 동시 분석
    - 단기/장기 추세 비교로 전환점 감지
    - 다이버전스로 조기 경고
    - 누적 거래량 반영
    
    Limitations:
    ------------
    - 변동성 높은 시장에서 whipsaw 발생
    - 거래량 적은 종목에서 신뢰도 ↓
    - 파라미터 조정 필요 (시장/종목별)
    - 다른 지표와 병행 권장
    
    Best Practices:
    ---------------
    - Signal Line Cross를 주 신호로 사용
    - 가격 패턴과 병행 분석
    - 추세 지표(MA, MACD)와 조합
    - 거래량 지표(OBV, CMF)와 상호 검증
    - 다이버전스는 다른 확인 신호와 함께 사용
    
    Standard Parameters:
    --------------------
    - Short=34, Long=55, Signal=13 (Stephen Klinger 원저)
    - 변경 시: Short < Long 유지
    - 단기 트레이딩: (21, 34, 8)
    - 장기 투자: (55, 89, 21)
    
    Notes:
    ------
    - Volume Force는 가격 변동폭 대비 거래량 강도 측정
    - CM(Cumulative Movement)은 추세 지속 시 누적
    - Trend 전환 시 CM 리셋 → 새로운 사이클 시작
    - 0선은 매수/매도 균형점
    """
    # 필수 컬럼 확인
    required = ['High', 'Low', 'Value', 'Volume']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns for Klinger Oscillator: {missing}")
        return df[[]]
    
    # 1. Typical Price (HLC/3)
    tp = (df['High'] + df['Low'] + df['Value']) / 3
    
    # 2. Trend 결정 (+1 or -1)
    # Trend = +1 if TP > TP_prev, else -1
    trend = pd.Series(index=df.index, dtype=float)
    trend.iloc[0] = 1  # 첫날은 +1로 가정
    for i in range(1, len(df)):
        if tp.iloc[i] > tp.iloc[i-1]:
            trend.iloc[i] = 1
        else:
            trend.iloc[i] = -1
    
    # 3. Daily Movement (DM) = High - Low
    dm = df['High'] - df['Low']
    
    # 4. Cumulative Movement (CM)
    # Trend가 유지되면 누적, 전환되면 리셋
    cm = pd.Series(index=df.index, dtype=float)
    cm.iloc[0] = dm.iloc[0]
    
    for i in range(1, len(df)):
        if trend.iloc[i] == trend.iloc[i-1]:
            # Trend 지속 → 누적
            cm.iloc[i] = cm.iloc[i-1] + dm.iloc[i]
        else:
            # Trend 전환 → 리셋
            cm.iloc[i] = dm.iloc[i-1] + dm.iloc[i]
    
    # Division by zero 방지
    cm = cm.replace(0, np.nan)
    
    # 5. Volume Force (VF)
    # VF = Volume × Trend × |2×((DM/CM)-1)| × 100
    vf = df['Volume'] * trend * (2 * ((dm / cm) - 1)).abs() * 100
    vf = vf.fillna(0)
    
    # 6. Klinger Oscillator = EMA(VF, short) - EMA(VF, long)
    kvo_short = vf.ewm(span=short, adjust=False).mean()
    kvo_long = vf.ewm(span=long, adjust=False).mean()
    kvo = kvo_short - kvo_long
    
    # 7. Signal Line = EMA(KVO, signal)
    kvo_signal = kvo.ewm(span=signal, adjust=False).mean()
    
    # 결과 저장
    kvo_col = f'KVO_{short}_{long}'
    signal_col = f'KVO_Signal_{short}_{long}_{signal}'
    
    df[kvo_col] = kvo
    df[signal_col] = kvo_signal
    
    # 추가 분석 컬럼
    df[f'KVO_Trend_{short}_{long}'] = trend
    df[f'KVO_VF_{short}_{long}'] = vf
    
    return df[[kvo_col, signal_col]]


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
def calculate_choppiness_index(df: pd.DataFrame, nday: int = 14):
    """
    Choppiness Index (CHOP) - 시장의 추세/횡보 구분 지표
    
    E.W. Dreiss가 개발한 지표로 시장이 추세 중인지 횡보 중인지를 측정합니다.
    ATR과 가격 범위를 비교하여 시장의 방향성 강도를 0~100으로 표현합니다.
    
    Formula:
    --------
    CHOP = 100 × log10(Sum(ATR, n) / (Max(High, n) - Min(Low, n))) / log10(n)
    
    Where:
    - ATR = Average True Range (True Range의 합)
    - Max(High, n) = n일간 최고가
    - Min(Low, n) = n일간 최저가
    - n = 기간 (일반적으로 14일)
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLC 데이터 (High, Low, Close 필수)
    nday : int, default=14
        계산 기간 (일반 표준)
    
    Returns:
    --------
    pd.Series
        Choppiness_Index_{nday} 컬럼
    
    Interpretation:
    ---------------
    - **CHOP > 61.8**: 횡보장 (Choppy/Consolidation)
      → 추세 전략 중단, 관망 또는 레인지 전략
    
    - **CHOP < 38.2**: 추세장 (Trending)
      → 추세 추종 전략 허용 (돌파, 모멘텀)
    
    - **38.2 ≤ CHOP ≤ 61.8**: 중립 (Neutral)
      → 방향성 불분명, 신중한 접근
    
    Trading Signals:
    ----------------
    1. **추세 매매 필터 (핵심 용도)**:
       - CHOP < 38.2: 추세 전략 허용 (돌파, 추세 추종)
       - CHOP > 61.8: 추세 전략 중단 (손실 방지)
    
    2. **횡보 → 추세 전환 탐지**:
       - CHOP가 고점(>61.8)에서 하락 전환
       - → 에너지 축적 후 추세 시작 가능성
       - 가격 돌파와 결합 시 신뢰도 ↑
    
    3. **추세 → 횡보 전환 경고**:
       - CHOP가 저점(<38.2)에서 상승 전환
       - → 추세 약화, 포지션 축소
    
    Use Cases:
    ----------
    1. 추세 전략 필터: 횡보장에서 손실 방지
    2. 전환점 탐지: 횡보 → 추세 초기 진입
    3. 리스크 관리: 고 CHOP 구간 회피
    4. 전략 선택: 추세 vs 레인지 전략
    
    Advantages:
    -----------
    - 추세/횡보 명확히 구분
    - 손실 방지 (횡보장 필터링)
    - 추세 전환 조기 감지
    - 모든 시장에 적용 가능
    
    Limitations:
    ------------
    - 방향성 없음 (상승/하락 구분 못함)
    - 후행 지표 (전환 확인 늦음)
    - 단독 사용 불가 (필터로만 활용)
    - 다른 추세 지표 필수
    
    Best Practices:
    ---------------
    - 추세 지표(MA, ADX)와 조합
    - CHOP < 38.2에서만 추세 전략 사용
    - 횡보장(CHOP > 61.8)에서 관망
    - 돌파 신호와 결합 (CHOP 하락 + 가격 돌파)
    - 포지션 크기 조절 (CHOP 낮을수록 크게)
    
    Standard Parameters:
    --------------------
    - nday=14 (가장 일반적, E.W. Dreiss 권장)
    - Short-term: nday=10
    - Long-term: nday=20~30
    
    Critical Levels:
    ----------------
    - 61.8: 횡보/추세 경계 (상단)
    - 38.2: 추세/횡보 경계 (하단)
    - 이 값들은 피보나치 레벨에서 유래
    
    Notes:
    ------
    - CHOP는 방향이 아닌 "움직임의 질"을 측정
    - 높을수록 횡보 (가격이 작은 범위 내 왔다갔다)
    - 낮을수록 추세 (가격이 한 방향으로 지속 이동)
    - ADX와 반대 개념 (ADX 높음 = 추세, CHOP 낮음 = 추세)
    """
    # 필수 컬럼 확인
    required = ['High', 'Low', 'Value']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns for Choppiness Index: {missing}")
        return pd.Series(dtype=float)
    
    # True Range 계산
    # TR = max(H-L, |H-C_prev|, |L-C_prev|)
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Value'].shift()).abs()
    lc = (df['Low'] - df['Value'].shift()).abs()
    
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    
    # Sum of True Range over nday period
    atr_sum = tr.rolling(window=nday).sum()
    
    # High-Low Range over nday period
    high_max = df['High'].rolling(window=nday).max()
    low_min = df['Low'].rolling(window=nday).min()
    high_low_range = high_max - low_min
    
    # Division by zero 방지
    high_low_range = high_low_range.replace(0, np.nan)
    
    # Choppiness Index 계산
    # CHOP = 100 × log10(ATR_sum / Range) / log10(nday)
    ci = 100 * np.log10(atr_sum / high_low_range) / np.log10(nday)
    
    # 결과 저장
    col_name = f"Choppiness_Index_{nday}"
    df[col_name] = ci
    
    return df[col_name]
    
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
def calculate_gopalakrishnan_range_index(df: pd.DataFrame, nday: int = 5):
    """
    Gopalakrishnan Range Index (GAPO/GRI) - 변동성 및 추세 품질 측정 지표
    
    Jayanthi Gopalakrishnan이 개발한 지표로 가격 범위와 기간의 로그 관계를 통해
    시장의 변동성과 추세의 강도를 측정합니다.
    
    Formula:
    --------
    GAPO = log10(Max(High, n) - Min(Low, n)) / log10(n)
    
    Where:
    - Max(High, n) = n일간 최고가
    - Min(Low, n) = n일간 최저가
    - n = 기간 (일반적으로 5일)
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLC 데이터 (High, Low 필수)
    nday : int, default=5
        계산 기간 (Gopalakrishnan 표준)
    
    Returns:
    --------
    pd.Series
        GAPO_{nday} 컬럼
    
    Interpretation:
    ---------------
    - **GAPO 상승**: 변동성 증가, 가격 범위 확대
      → 추세 강화 또는 변동성 폭발
    
    - **GAPO 하락**: 변동성 감소, 가격 범위 축소
      → 횡보/수렴, 에너지 축적
    
    - **GAPO 완만**: 안정적 추세
      → 건강한 추세 지속
    
    - **GAPO 급등**: 변동성 급증
      → 과열/패닉, 주의 필요
    
    Trading Signals:
    ----------------
    1. **추세 품질 평가**:
       - 가격 상승 + GAPO 완만: 건강한 상승 추세
       - 가격 상승 + GAPO 급등: 과열 가능성 (주의)
    
    2. **돌파 필터 (브레이크아웃)**:
       - 장기간 낮은 GAPO: 에너지 축적 (수렴)
       - 이후 GAPO 상승 + 가격 돌파: 신뢰도 높은 브레이크아웃
    
    3. **리스크 관리**:
       - GAPO 급등 구간: 포지션 축소
       - 변동성 폭발 구간 회피
    
    4. **횡보 → 추세 전환**:
       - GAPO 저점 → 상승 전환: 추세 시작 가능
       - 가격 패턴과 결합 시 효과적
    
    Use Cases:
    ----------
    1. 변동성 모니터링: 시장 변동성 추적
    2. 추세 품질: 추세의 건강성 평가
    3. 브레이크아웃 확인: 돌파 신뢰도 검증
    4. 리스크 조절: 변동성 기반 포지션 조정
    
    Advantages:
    -----------
    - 변동성과 추세 동시 측정
    - 로그 스케일로 정규화
    - 브레이크아웃 필터로 유용
    - 간단한 계산
    
    Limitations:
    ------------
    - 방향성 없음 (상승/하락 구분 못함)
    - 단독 사용 불가
    - 해석이 상대적 (절대값 의미 약함)
    - 다른 지표와 조합 필수
    
    Best Practices:
    ---------------
    - ATR, Bollinger Bands와 조합
    - 추세 지표(MA, ADX)와 병행
    - 브레이크아웃 시 GAPO 상승 확인
    - 급등 구간에서 과열 경계
    - 다중 기간 분석 (5일, 10일, 20일)
    
    Standard Parameters:
    --------------------
    - nday=5 (Gopalakrishnan 원저, 단기 변동성)
    - Alternative: 10일 (중기), 20일 (장기)
    - 짧을수록 민감, 길수록 완만
    
    Comparison with Other Indicators:
    ----------------------------------
    - vs ATR: GAPO는 로그 스케일, ATR은 절대값
    - vs Choppiness: CHOP는 추세/횡보, GAPO는 변동성 강도
    - vs Bollinger Width: 유사하나 GAPO는 정규화됨
    
    Notes:
    ------
    - GAPO는 정규화된 변동성 지표
    - 기간이 길수록 값이 작아짐 (로그 분모 증가)
    - Range가 클수록 값이 커짐 (로그 분자 증가)
    - 절대값보다 추세(상승/하락)가 중요
    """
    # 필수 컬럼 확인
    required = ['High', 'Low']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns for GAPO: {missing}")
        return pd.Series(dtype=float)
    
    # High-Low Range over nday period
    high_max = df['High'].rolling(window=nday).max()
    low_min = df['Low'].rolling(window=nday).min()
    high_low_range = high_max - low_min
    
    # Division by zero 방지 (range가 0이면 log 계산 불가)
    high_low_range = high_low_range.replace(0, np.nan)
    
    # GAPO 계산
    # GAPO = log10(Range) / log10(nday)
    gapo = np.log10(high_low_range) / np.log10(nday)
    
    # 결과 저장
    col_name = f"GAPO_{nday}"
    df[col_name] = gapo
    
    return df[col_name]


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
def calculate_hurst_exponent(df: pd.DataFrame, window: int = 100, max_lag: int = 20):
    """
    Hurst Exponent - 시계열의 장기 기억성과 추세 지속성 측정
    
    H.E. Hurst가 개발한 지표로 시계열의 자기상관 구조를 분석하여
    추세 지속성, 평균 회귀성, 무작위성을 구분합니다.
    
    Formula:
    --------
    H = slope of log(tau) vs log(lag) / 2
    
    Where:
    - tau(lag) = Standard Deviation of price differences at each lag
    - lag = time lag (2 to max_lag)
    - Regression: log(tau) = a × log(lag) + b
    - H = a × 2.0 (slope × 2)
    
    Parameters:
    -----------
    df : pd.DataFrame
        가격 데이터 (Close 필수)
    window : int, default=100
        Hurst 계산을 위한 Rolling window 크기
        (충분한 데이터 필요, 최소 50~100)
    max_lag : int, default=20
        최대 lag 값 (일반적으로 window의 10~20%)
    
    Returns:
    --------
    pd.Series
        Hurst_Exponent_{window}_{max_lag} 컬럼
    
    Interpretation:
    ---------------
    - **H > 0.5**: 추세 지속 (Trending, Persistent)
      → 과거 방향이 미래에도 지속 가능
      → 추세 추종 전략 유리
    
    - **H = 0.5**: 무작위 보행 (Random Walk)
      → 과거가 미래에 영향 없음
      → 효율적 시장
    
    - **H < 0.5**: 평균 회귀 (Mean Reverting, Anti-persistent)
      → 과거 방향의 반대로 움직임 경향
      → 평균회귀 전략 유리
    
    Critical Levels:
    ----------------
    - **H > 0.55**: 강한 추세 성향
      → 추세 추종, 돌파, 모멘텀 전략
    
    - **0.45 ≤ H ≤ 0.55**: 중립/무작위
      → 관망 또는 포지션 축소
      → 잘못된 전략 사용 방지
    
    - **H < 0.45**: 강한 회귀 성향
      → 평균회귀, 밴드 트레이딩, 역추세
    
    Trading Signals:
    ----------------
    1. **전략 선택 필터 (핵심 용도)**:
       - H > 0.55: 추세 전략 사용
       - H < 0.45: 평균회귀 전략 사용
       - 0.45~0.55: 전략 효과 낮음, 관망
    
    2. **국면 전환 탐지**:
       - H: 0.5 이하 → 이상: 횡보 → 추세 전환 가능
       - H: 0.5 이상 → 이하: 추세 → 횡보 전환 가능
    
    3. **다중 타임프레임**:
       - 장기 H > 0.5, 단기 H < 0.5: 조정 후 재추세 가능
       - 장기 H < 0.5, 단기 H > 0.5: 일시적 추세, 주의
    
    Use Cases:
    ----------
    1. 전략 선택: 시장 성격에 맞는 전략 선택
    2. 리스크 관리: 부적합 전략 회피
    3. 국면 전환: 추세/횡보 전환 감지
    4. 포지션 크기: H 높을수록 추세 전략 비중 ↑
    
    Advantages:
    -----------
    - 시장의 근본 성격 파악
    - 전략 선택에 객관적 기준 제공
    - 잘못된 전략 사용 방지
    - 수학적으로 명확한 해석
    
    Limitations:
    ------------
    - 계산에 많은 데이터 필요 (최소 100개)
    - 후행 지표 (과거 데이터 기반)
    - 값 자체가 매매 신호 아님 (필터)
    - Rolling window로 계산 시 느림
    - 단기 변화 포착 어려움
    
    Best Practices:
    ---------------
    - 충분한 window 크기 사용 (100~250)
    - 추세 지표(ADX, MA)와 조합
    - H > 0.55일 때만 추세 전략 사용
    - H < 0.45일 때만 평균회귀 전략 사용
    - 다중 타임프레임 분석 (단기/장기)
    - 변화 추세 관찰 (상승/하락)
    
    Standard Parameters:
    --------------------
    - window=100 (일반적, 충분한 데이터)
    - max_lag=20 (window의 20%)
    - 장기: window=250, max_lag=50
    - 단기: window=50, max_lag=10 (신뢰도 낮음)
    
    Comparison:
    -----------
    - vs ADX: ADX는 추세 강도, Hurst는 지속성
    - vs Choppiness: CHOP는 추세/횡보, Hurst는 성격 분류
    - vs Fractal Dimension: FD = 2 - H (역관계)
    
    Notes:
    ------
    - Hurst는 R/S 분석에서 유래
    - Fractal Dimension과 밀접한 관계 (FD = 2 - H)
    - 금융 시계열에서 H는 0.4~0.6 범위가 일반적
    - H = 0.5은 기하 브라운 운동 (효율적 시장)
    - Rolling window로 계산하여 시간에 따른 변화 추적
    """
    # 필수 컬럼 확인
    if 'Value' not in df.columns:
        print("Error: 'Value' column required for Hurst Exponent")
        return pd.Series(dtype=float)
    
    # max_lag는 window보다 훨씬 작아야 함
    if max_lag >= window / 2:
        print(f"Warning: max_lag ({max_lag}) should be much smaller than window ({window})")
        max_lag = min(max_lag, int(window / 5))
    
    # Rolling window로 Hurst Exponent 계산
    def calculate_hurst(prices):
        """단일 window에 대한 Hurst Exponent 계산"""
        if len(prices) < max_lag + 2:
            return np.nan
        
        lags = range(2, max_lag + 1)
        tau = []
        
        for lag in lags:
            # lag 간격의 price difference의 표준편차
            diffs = prices.diff(lag).dropna()
            if len(diffs) < 2:
                return np.nan
            std = np.std(diffs)
            if std > 0:
                tau.append(std)
            else:
                return np.nan
        
        if len(tau) < 2:
            return np.nan
        
        # log(tau) vs log(lag) 선형 회귀
        try:
            log_lags = np.log(list(lags)[:len(tau)])
            log_tau = np.log(tau)
            
            # NaN이나 inf 체크
            if np.any(np.isnan(log_tau)) or np.any(np.isinf(log_tau)):
                return np.nan
            
            # 선형 회귀로 기울기 추정
            poly = np.polyfit(log_lags, log_tau, 1)
            hurst = poly[0] * 2.0
            
            # Hurst는 일반적으로 0~1 범위
            # 금융 데이터에서 0.3~0.7이 정상 범위
            if hurst < 0 or hurst > 1.5:
                return np.nan
            
            return hurst
        except:
            return np.nan
    
    # Rolling window 적용
    hurst_values = df['Value'].rolling(window=window).apply(calculate_hurst, raw=False)
    
    # 결과 저장
    col_name = f'Hurst_Exponent_{window}_{max_lag}'
    df[col_name] = hurst_values
    
    return df[col_name]

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
def calculate_fractal_dimension(df: pd.DataFrame, nday: int = 10):
    """
    Fractal Dimension (FD) - 가격 시계열의 복잡도와 불규칙성 측정
    
    Benoit Mandelbrot의 프랙탈 이론을 기반으로 가격 움직임의 복잡도를 측정합니다.
    Higuchi 방법을 사용하여 시계열의 프랙탈 차원을 계산합니다.
    
    Formula (Higuchi Method):
    -------------------------
    1. 각 k에 대해 k개의 부분 시계열 생성
    2. 각 부분 시계열의 길이 L_m(k) 계산
    3. 평균 길이 L(k) = mean(L_m(k))
    4. log(L(k)) vs log(1/k) 선형 회귀
    5. FD = -slope (기울기의 음수)
    
    Simplified Version (High-Low Range):
    ------------------------------------
    FD ≈ 2 - H (Hurst Exponent와 역관계)
    또는 Range-based 근사:
    FD = log(N) / (log(N) + log(Range/Sum_of_steps))
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLC 데이터 (High, Low 필수)
    nday : int, default=10
        계산 기간 (Rolling window)
    
    Returns:
    --------
    pd.Series
        Fractal_Dimension_{nday} 컬럼
    
    Interpretation:
    ---------------
    - **FD ≈ 1.0**: 완전한 추세 (직선에 가까움)
      → 매우 강한 방향성
    
    - **FD < 1.3**: 강한 추세
      → 추세 추종 전략 유리
    
    - **1.3 ≤ FD ≤ 1.5**: 약한 추세
      → 신중한 접근 필요
    
    - **FD > 1.5**: 횡보/혼돈
      → 평균회귀 전략 유리
    
    - **FD > 1.7**: 거의 무작위
      → 관망 권장
    
    - **FD ≈ 2.0**: 완전한 무작위 (평면을 채우는 수준)
      → 예측 불가능
    
    Trading Signals:
    ----------------
    1. **전략 선택 필터 (핵심)**:
       - FD < 1.3: 추세 추종 전략
       - 1.3 ≤ FD ≤ 1.5: 신중 (약한 추세)
       - FD > 1.5: 평균회귀/레인지 전략
       - FD > 1.7: 관망 (노이즈)
    
    2. **국면 전환 탐지**:
       - FD 하락: 질서 증가 → 추세 형성
       - FD 상승: 추세 붕괴 → 횡보
    
    3. **포지션 사이징**:
       - FD 낮음: 공격적 (큰 포지션)
       - FD 높음: 보수적 (작은 포지션)
    
    Use Cases:
    ----------
    1. 전략 선택: 시장 복잡도에 맞는 전략
    2. 리스크 관리: 높은 FD에서 포지션 축소
    3. 추세 품질: 낮은 FD = 깨끗한 추세
    4. 노이즈 필터: 높은 FD 구간 회피
    
    Advantages:
    -----------
    - 시장 복잡도 정량화
    - 추세/횡보 객관적 구분
    - Hurst와 상호 보완 (FD ≈ 2 - H)
    - 포지션 크기 조절 기준
    
    Limitations:
    ------------
    - 계산 복잡 (간소화 버전 사용 시)
    - 방향성 없음 (상승/하락 구분 못함)
    - 단독 사용 불가 (필터로만)
    - 후행 지표
    
    Best Practices:
    ---------------
    - Hurst Exponent와 조합 (상호 검증)
    - ADX, Choppiness와 병행
    - FD < 1.3에서만 추세 전략
    - FD > 1.5에서 관망 또는 레인지 전략
    - 다중 기간 분석 (10일, 20일, 50일)
    
    Standard Parameters:
    --------------------
    - nday=10 (단기, 민감)
    - nday=20 (중기, 일반적)
    - nday=50 (장기, 안정적)
    
    Relationship with Hurst:
    ------------------------
    - FD ≈ 2 - H (이론적 관계)
    - H = 0.5 (Random) → FD = 1.5
    - H > 0.5 (Trending) → FD < 1.5
    - H < 0.5 (Mean Reverting) → FD > 1.5
    
    Notes:
    ------
    - 완전한 Higuchi 방법은 계산 무거움
    - 실용적으로 간소화 버전 사용
    - Range-based 근사로 빠른 계산
    - FD는 1.0~2.0 범위 (이론적)
    - 금융 데이터에서 1.2~1.8이 일반적
    """
    # 필수 컬럼 확인
    required = ['High', 'Low', 'Value']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns for Fractal Dimension: {missing}")
        return pd.Series(dtype=float)
    
    def calculate_fd_window(window_data):
        """단일 window에 대한 Fractal Dimension 계산 (간소화 버전)"""
        if len(window_data) < 3:
            return np.nan
        
        # 가격 변화의 절대값 합 (실제 경로 길이)
        price_changes = np.abs(np.diff(window_data))
        total_length = np.sum(price_changes)
        
        # 직선 거리 (시작점 → 끝점)
        straight_distance = np.abs(window_data.iloc[-1] - window_data.iloc[0])
        
        if straight_distance == 0 or total_length == 0:
            return np.nan
        
        # Fractal Dimension 근사
        # FD = 1 + log(total_length / straight_distance) / log(2)
        # 또는 간단히: FD = log(total_length) / log(straight_distance) 비율 기반
        
        # 더 안정적인 방법: Range-based
        n = len(window_data)
        price_range = window_data.max() - window_data.min()
        
        if price_range == 0:
            return 2.0  # 완전 평탄 = 최대 차원
        
        # FD ≈ log(n) / (log(n) + log(price_range / total_length))
        # 간소화: FD ≈ 1 + log(total_length / price_range) / log(n)
        try:
            ratio = total_length / price_range
            if ratio <= 0:
                return np.nan
            
            fd = 1.0 + np.log(ratio) / np.log(n)
            
            # FD는 1.0~2.0 범위로 제한
            fd = np.clip(fd, 1.0, 2.0)
            
            return fd
        except:
            return np.nan
    
    # Rolling window 적용
    fd_values = df['Value'].rolling(window=nday).apply(calculate_fd_window, raw=False)
    
    # 결과 저장
    col_name = f"Fractal_Dimension_{nday}"
    df[col_name] = fd_values
    
    return df[col_name]

def calculate_polarized_fractal_efficiency_index(df: pd.DataFrame, nday: int = 10):
    """
    Polarized Fractal Efficiency (PFE) - 가격 효율성과 추세 강도 측정
    
    Hans Hannula가 개발한 지표로 가격 움직임의 효율성을 측정합니다.
    직선 거리 대비 실제 경로 길이의 비율로 추세의 질을 평가합니다.
    
    Formula:
    --------
    1. Direction = Sign(Close - Close_nday)
    2. Straight_Distance = sqrt((Close - Close_nday)^2 + nday^2)
    3. Path_Length = Sum of |Close_i - Close_{i-1}| for i in (t-nday, t)
    4. Efficiency = Direction × (Straight_Distance / Path_Length) × 100
    5. PFE = Smoothed(Efficiency) (optional)
    
    간소화 버전 (현재 구현):
    PFE = (Close - Close_nday) / sqrt((Close - Close_nday)^2 + nday^2) × 100
    
    Parameters:
    -----------
    df : pd.DataFrame
        가격 데이터 (Value 필수)
    nday : int, default=10
        계산 기간 (일반 표준)
    
    Returns:
    --------
    pd.Series
        PFE_{nday} 컬럼
    
    Interpretation:
    ---------------
    - **PFE > +50**: 강한 상승 추세 + 효율적
      → 매수 신호 강화
    
    - **+25 < PFE < +50**: 중간 상승 추세
      → 상승 추세 약화
    
    - **-25 < PFE < +25**: 횡보/비효율
      → 방향성 없음, 관망
    
    - **-50 < PFE < -25**: 중간 하락 추세
      → 하락 추세 약화
    
    - **PFE < -50**: 강한 하락 추세 + 효율적
      → 매도 신호 강화
    
    Trading Signals:
    ----------------
    1. **Zero Line Cross**:
       - PFE > 0: 상승 추세 (매수)
       - PFE < 0: 하락 추세 (매도)
    
    2. **Threshold Cross**:
       - PFE > +50: 강한 매수 (추세 시작)
       - PFE < -50: 강한 매도 (하락 시작)
       - PFE 진입 후 퇴출: 추세 약화
    
    3. **Divergence**:
       - 가격 고점 상승 + PFE 고점 하락: 약세 전환
       - 가격 저점 하락 + PFE 저점 상승: 강세 전환
    
    4. **Extreme Reversal**:
       - PFE > +80: 과매수, 조정 가능
       - PFE < -80: 과매도, 반등 가능
    
    Use Cases:
    ----------
    1. 추세 강도: PFE 절대값 = 추세 강도
    2. 추세 방향: PFE 부호 = 추세 방향
    3. 효율성: 높은 PFE = 깨끗한 추세
    4. 진입/청산: ±50 돌파로 타이밍
    
    Advantages:
    -----------
    - 추세 방향과 강도 동시 측정
    - 효율성 개념 (노이즈 구분)
    - -100 ~ +100 정규화 (해석 용이)
    - 다이버전스 활용 가능
    
    Limitations:
    ------------
    - 간소화 버전은 실제 경로 미반영
    - 후행 지표
    - 급변동 시 과민 반응
    - 단독 사용 불가
    
    Best Practices:
    ---------------
    - ADX, Trend 지표와 조합
    - ±50 임계값으로 필터링
    - 다이버전스로 전환 조기 감지
    - EMA 스무딩 적용 (노이즈 감소)
    - 다중 기간 분석 (10/20/50)
    
    Standard Parameters:
    --------------------
    - nday=10 (Hans Hannula 권장, 단기)
    - Alternative: 14, 20 (중기), 50 (장기)
    - 짧을수록 민감, 길수록 완만
    
    Enhanced Version:
    -----------------
    실제 경로 길이를 계산하는 버전:
    - Path_Length = Sum(|Close_i - Close_{i-1}|)
    - Efficiency = Straight / Path
    - 더 정확하나 계산 복잡
    
    Notes:
    ------
    - PFE는 방향성 있는 효율성 지표
    - Fractal Efficiency와 유사하나 극성화됨
    - 직선에 가까울수록 효율적 (|PFE| 높음)
    - 지그재그 많을수록 비효율 (|PFE| 낮음)
    - 0선 교차는 추세 전환 신호
    """
    # 필수 컬럼 확인
    if 'Value' not in df.columns:
        print("Error: 'Value' column required for PFE")
        return pd.Series(dtype=float)
    
    # 방향 (현재 가격 - nday 전 가격)
    direction = df['Value'] - df['Value'].shift(nday)
    
    # 유클리드 거리 (직선 거리)
    # sqrt((price_change)^2 + (time_period)^2)
    price_change_sq = (df['Value'] - df['Value'].shift(nday)) ** 2
    straight_distance = np.sqrt(price_change_sq + (nday ** 2))
    
    # Division by zero 방지
    straight_distance = straight_distance.replace(0, np.nan)
    
    # PFE 계산
    # PFE = (direction / straight_distance) × 100
    # direction이 양수면 상승 추세, 음수면 하락 추세
    pfe = (direction / straight_distance) * 100
    
    # 결과 저장
    col_name = f"PFE_{nday}"
    df[col_name] = pfe
    
    return df[col_name]

def calculate_fibonacci_retracement_levels(df: pd.DataFrame, start_idx: int = None, end_idx: int = None, trend: str = 'auto'):
    """
    Fibonacci Retracement Levels - 되돌림 지지/저항 레벨 계산
    
    Leonardo Fibonacci의 수열을 기반으로 가격의 되돌림 지지선과 저항선을 계산합니다.
    추세 조정 후 재진입 레벨을 파악하는 데 사용됩니다.
    
    Formula:
    --------
    Uptrend (상승 추세):
    - Level = Low + (High - Low) × Fibonacci_Ratio
    - 되돌림: High에서 하락 후 지지 레벨
    
    Downtrend (하락 추세):
    - Level = High - (High - Low) × Fibonacci_Ratio
    - 되돌림: Low에서 반등 후 저항 레벨
    
    Standard Fibonacci Ratios:
    - 23.6% (0.236): 얕은 되돌림
    - 38.2% (0.382): 일반 되돌림
    - 50.0% (0.500): 중간 되돌림 (비공식)
    - 61.8% (0.618): 깊은 되돌림 (황금비율)
    - 78.6% (0.786): 매우 깊은 되돌림
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLC 데이터 (High, Low 필수)
    start_idx : int, optional
        시작 인덱스 (None이면 전체 데이터 시작)
    end_idx : int, optional
        종료 인덱스 (None이면 전체 데이터 끝)
    trend : str, default='auto'
        추세 방향 ('up', 'down', 'auto')
        - 'up': 상승 추세 (Low → High)
        - 'down': 하락 추세 (High → Low)
        - 'auto': 자동 감지 (최근 가격 기준)
    
    Returns:
    --------
    dict
        Fibonacci 레벨 딕셔너리
        {
            'trend': 'up' or 'down',
            'swing_high': float,
            'swing_low': float,
            'range': float,
            'levels': {
                '0.0%': price,
                '23.6%': price,
                '38.2%': price,
                '50.0%': price,
                '61.8%': price,
                '78.6%': price,
                '100.0%': price
            }
        }
    
    Interpretation:
    ---------------
    **상승 추세 (Uptrend)**:
    - High에서 하락 조정 시 각 레벨이 지지선으로 작용
    - 23.6%: 약한 지지 (얕은 조정)
    - 38.2%: 일반 지지 (정상 조정)
    - 50.0%: 중간 지지 (심리적 레벨)
    - 61.8%: 강한 지지 (황금비율, 깊은 조정)
    - 78.6%: 매우 강한 지지 (추세 유지의 마지막 방어선)
    
    **하락 추세 (Downtrend)**:
    - Low에서 상승 반등 시 각 레벨이 저항선으로 작용
    - 23.6%: 약한 저항
    - 38.2%: 일반 저항
    - 50.0%: 중간 저항
    - 61.8%: 강한 저항
    - 78.6%: 매우 강한 저항
    
    Trading Signals:
    ----------------
    1. **상승 추세 매수 전략**:
       - 38.2% 근처 매수 (일반 조정)
       - 50.0% 근처 매수 (중간 조정)
       - 61.8% 근처 매수 (깊은 조정, 고위험)
    
    2. **하락 추세 매도/관망**:
       - 각 레벨에서 저항 확인
       - 61.8% 돌파 시 추세 전환 가능
    
    3. **레벨 돌파**:
       - 상승 추세에서 78.6% 이탈: 추세 전환
       - 하락 추세에서 61.8% 돌파: 강세 전환
    
    4. **다중 터치**:
       - 같은 레벨 여러 번 터치: 해당 레벨 중요도 ↑
       - 레벨 근처에서 캔들 패턴 확인
    
    Use Cases:
    ----------
    1. 진입점 찾기: 조정 후 재진입 레벨
    2. 익절 타겟: 확장 레벨 (100% 이상)
    3. 손절 설정: 78.6% 또는 100% 이탈
    4. 지지/저항: 레벨 근처 매매 결정
    
    Advantages:
    -----------
    - 객관적 레벨 계산
    - 심리적 지지/저항 반영
    - 다양한 시장에 적용
    - 다른 기술적 분석과 조합 용이
    
    Limitations:
    ------------
    - 과거 데이터 기반 (후행)
    - Swing High/Low 판단 주관적
    - 레벨이 항상 작동하지 않음
    - 다른 지표와 확인 필수
    
    Best Practices:
    ---------------
    - 명확한 Swing High/Low 사용
    - 레벨 근처에서 캔들/패턴 확인
    - 거래량 증가 확인
    - 다른 지표(RSI, MACD) 조합
    - 61.8%가 가장 신뢰도 높음
    - 여러 타임프레임 분석
    
    Standard Parameters:
    --------------------
    - Ratios: 23.6%, 38.2%, 50%, 61.8%, 78.6% (고정)
    - 61.8%는 황금비율 (가장 중요)
    - 50%는 비공식이나 심리적으로 중요
    
    Extensions (확장 레벨):
    ----------------------
    - 127.2%, 161.8%, 200%, 261.8%
    - 익절 타겟으로 사용
    - 추세 지속 시 목표가
    
    Notes:
    ------
    - Fibonacci 수열: 1, 1, 2, 3, 5, 8, 13, 21, ...
    - 비율 = n / (n+1) → 0.618 (황금비율)
    - 0.236 = 1 - 0.764 (√0.618)
    - 0.382 = 1 - 0.618
    - 0.786 = √0.618
    - 자연과 금융시장에서 자주 나타나는 비율
    """
    # 필수 컬럼 확인
    required = ['High', 'Low']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns for Fibonacci Retracement: {missing}")
        return {}
    
    # 인덱스 범위 설정
    if start_idx is None:
        start_idx = 0
    if end_idx is None:
        end_idx = len(df) - 1
    
    # 범위 유효성 검사
    start_idx = max(0, start_idx)
    end_idx = min(len(df) - 1, end_idx)
    
    if start_idx >= end_idx:
        print("Error: Invalid index range")
        return {}
    
    # 해당 구간의 High/Low
    segment = df.iloc[start_idx:end_idx+1]
    swing_high = segment['High'].max()
    swing_low = segment['Low'].min()
    price_range = swing_high - swing_low
    
    if price_range == 0:
        print("Error: No price range (High = Low)")
        return {}
    
    # 추세 자동 감지
    if trend == 'auto':
        # 최근 가격이 범위의 어디에 있는지로 판단
        if 'Close' in df.columns:
            current_price = df.iloc[end_idx]['Close']
        elif 'Value' in df.columns:
            current_price = df.iloc[end_idx]['Value']
        else:
            current_price = (swing_high + swing_low) / 2
        
        # 현재가가 상위 50%면 상승 추세, 하위 50%면 하락 추세
        if current_price >= (swing_high + swing_low) / 2:
            trend = 'up'
        else:
            trend = 'down'
    
    # Fibonacci 비율
    fib_ratios = {
        '0.0%': 0.000,
        '23.6%': 0.236,
        '38.2%': 0.382,
        '50.0%': 0.500,
        '61.8%': 0.618,
        '78.6%': 0.786,
        '100.0%': 1.000,
    }
    
    # 레벨 계산
    levels = {}
    
    if trend == 'up':
        # 상승 추세: Low → High, High에서 되돌림
        # Level = High - (High - Low) × Ratio
        for label, ratio in fib_ratios.items():
            levels[label] = swing_high - (price_range * ratio)
    else:
        # 하락 추세: High → Low, Low에서 반등
        # Level = Low + (High - Low) × Ratio
        for label, ratio in fib_ratios.items():
            levels[label] = swing_low + (price_range * ratio)
    
    # 결과 딕셔너리
    result = {
        'trend': trend,
        'swing_high': swing_high,
        'swing_low': swing_low,
        'range': price_range,
        'start_idx': start_idx,
        'end_idx': end_idx,
        'levels': levels
    }
    
    return result

def calculate_pivot_points(df: pd.DataFrame, method: str = 'standard'):
    """
    Pivot Points - 일중 지지/저항 레벨 계산
    
    전일 가격(High, Low, Close)을 기반으로 당일 지지선과 저항선을 계산합니다.
    데이 트레이딩 및 단기 매매에서 진입/청산 레벨로 널리 사용됩니다.
    
    Formula:
    --------
    **Standard Pivot (가장 일반적)**:
    - PP (Pivot Point) = (High + Low + Close) / 3
    - R1 (Resistance 1) = (2 × PP) - Low
    - S1 (Support 1) = (2 × PP) - High
    - R2 (Resistance 2) = PP + (High - Low)
    - S2 (Support 2) = PP - (High - Low)
    - R3 (Resistance 3) = High + 2 × (PP - Low)
    - S3 (Support 3) = Low - 2 × (High - PP)
    
    **Fibonacci Pivot**:
    - PP = (High + Low + Close) / 3
    - R1 = PP + 0.382 × (High - Low)
    - R2 = PP + 0.618 × (High - Low)
    - R3 = PP + 1.000 × (High - Low)
    - S1 = PP - 0.382 × (High - Low)
    - S2 = PP - 0.618 × (High - Low)
    - S3 = PP - 1.000 × (High - Low)
    
    **Woodie's Pivot**:
    - PP = (High + Low + 2 × Close) / 4
    - R1 = (2 × PP) - Low
    - S1 = (2 × PP) - High
    - R2 = PP + (High - Low)
    - S2 = PP - (High - Low)
    
    **Camarilla Pivot**:
    - PP = (High + Low + Close) / 3
    - R1 = Close + 1.1 × (High - Low) / 12
    - R2 = Close + 1.1 × (High - Low) / 6
    - R3 = Close + 1.1 × (High - Low) / 4
    - R4 = Close + 1.1 × (High - Low) / 2
    - S1 = Close - 1.1 × (High - Low) / 12
    - S2 = Close - 1.1 × (High - Low) / 6
    - S3 = Close - 1.1 × (High - Low) / 4
    - S4 = Close - 1.1 × (High - Low) / 2
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLC 데이터 (High, Low, Close 필수)
    method : str, default='standard'
        Pivot 계산 방법
        - 'standard': 표준 Pivot (가장 일반적)
        - 'fibonacci': Fibonacci Pivot
        - 'woodie': Woodie's Pivot
        - 'camarilla': Camarilla Pivot
    
    Returns:
    --------
    pd.DataFrame
        Pivot Points 컬럼들:
        - PP: Pivot Point (중심축)
        - R1, R2, R3: Resistance levels (저항선)
        - S1, S2, S3: Support levels (지지선)
        - (Camarilla의 경우 R4, S4 추가)
    
    Interpretation:
    ---------------
    - **PP (Pivot Point)**: 중심 레벨
      → 위: 강세, 아래: 약세
    
    - **R1, R2, R3**: 저항선 (상승 시 목표가/익절)
      → R1 돌파 → R2 목표, R2 돌파 → R3 목표
    
    - **S1, S2, S3**: 지지선 (하락 시 매수/손절)
      → S1 터치 → 매수, S1 이탈 → S2 관찰
    
    Trading Signals:
    ----------------
    1. **Pivot 기준 추세 판단**:
       - 가격 > PP: 강세 (롱 포지션 선호)
       - 가격 < PP: 약세 (숏 포지션 선호)
    
    2. **레벨 돌파 매매**:
       - R1 돌파 → 매수, 목표 R2
       - S1 이탈 → 매도, 목표 S2
    
    3. **레벨 반등 매매**:
       - S1 터치 → 매수, 손절 S2
       - R1 터치 → 매도, 손절 R2
    
    4. **레인지 트레이딩**:
       - S1~R1 사이 횡보 시
       - S1 매수 → R1 매도
       - PP 중심 양방향 매매
    
    Use Cases:
    ----------
    1. 데이 트레이딩: 일중 진입/청산 레벨
    2. 익절/손절: 목표가 설정
    3. 추세 판단: PP 기준 강약
    4. 레인지 매매: S1~R1 구간
    
    Advantages:
    -----------
    - 객관적 계산 (주관 배제)
    - 전 세계 트레이더 사용 (자기실현)
    - 간단한 공식
    - 일중 레벨 명확
    
    Limitations:
    ------------
    - 전일 데이터 기반 (후행)
    - 급변동 시 부정확
    - 갭 발생 시 효과 감소
    - 추세 강한 시장에서 이탈 빈번
    
    Best Practices:
    ---------------
    - PP 근처에서 방향 결정
    - 레벨 근처에서 캔들 패턴 확인
    - 거래량 증가 시 신뢰도 ↑
    - 다른 지표(RSI, MACD) 조합
    - R3/S3 돌파는 강한 추세 신호
    - 여러 타임프레임 Pivot 활용
    
    Standard Parameters:
    --------------------
    - method='standard' (가장 일반적)
    - 일봉 데이터 사용 (전일 → 당일)
    - Alternative methods:
      * fibonacci: Fibonacci 비율 활용
      * woodie: Close 가중치 2배
      * camarilla: 단기 트레이딩용 (레벨 촘촘)
    
    Time Frames:
    ------------
    - Daily: 전일 → 당일 (가장 일반적)
    - Weekly: 전주 → 당주
    - Monthly: 전월 → 당월
    - Intraday: 특정 세션 → 다음 세션
    
    Notes:
    ------
    - 1940년대 Henry Chase가 개발
    - Floor traders들이 사용하기 시작
    - 자기실현적 예언 효과 (많은 트레이더가 같은 레벨 주시)
    - PP는 심리적 균형점
    - Standard 방법이 가장 보편적
    - Camarilla는 스캘핑/단타에 유용
    """
    # 필수 컬럼 확인
    required = ['High', 'Low', 'Value']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns for Pivot Points: {missing}")
        return df
    
    # 전일 데이터를 사용하여 당일 Pivot 계산
    prev_high = df['High'].shift(1)
    prev_low = df['Low'].shift(1)
    prev_close = df['Value'].shift(1)
    
    if method == 'standard':
        # Standard Pivot Points
        pp = (prev_high + prev_low + prev_close) / 3
        r1 = (2 * pp) - prev_low
        s1 = (2 * pp) - prev_high
        r2 = pp + (prev_high - prev_low)
        s2 = pp - (prev_high - prev_low)
        r3 = prev_high + 2 * (pp - prev_low)
        s3 = prev_low - 2 * (prev_high - pp)
        
        df['PP'] = pp
        df['R1'] = r1
        df['R2'] = r2
        df['R3'] = r3
        df['S1'] = s1
        df['S2'] = s2
        df['S3'] = s3
        
    elif method == 'fibonacci':
        # Fibonacci Pivot Points
        pp = (prev_high + prev_low + prev_close) / 3
        range_hl = prev_high - prev_low
        
        r1 = pp + 0.382 * range_hl
        r2 = pp + 0.618 * range_hl
        r3 = pp + 1.000 * range_hl
        s1 = pp - 0.382 * range_hl
        s2 = pp - 0.618 * range_hl
        s3 = pp - 1.000 * range_hl
        
        df['PP'] = pp
        df['R1'] = r1
        df['R2'] = r2
        df['R3'] = r3
        df['S1'] = s1
        df['S2'] = s2
        df['S3'] = s3
        
    elif method == 'woodie':
        # Woodie's Pivot Points (Close에 가중치)
        pp = (prev_high + prev_low + 2 * prev_close) / 4
        r1 = (2 * pp) - prev_low
        s1 = (2 * pp) - prev_high
        r2 = pp + (prev_high - prev_low)
        s2 = pp - (prev_high - prev_low)
        r3 = prev_high + 2 * (pp - prev_low)
        s3 = prev_low - 2 * (prev_high - pp)
        
        df['PP'] = pp
        df['R1'] = r1
        df['R2'] = r2
        df['R3'] = r3
        df['S1'] = s1
        df['S2'] = s2
        df['S3'] = s3
        
    elif method == 'camarilla':
        # Camarilla Pivot Points (단기 트레이딩용)
        pp = (prev_high + prev_low + prev_close) / 3
        range_hl = prev_high - prev_low
        
        r1 = prev_close + 1.1 * range_hl / 12
        r2 = prev_close + 1.1 * range_hl / 6
        r3 = prev_close + 1.1 * range_hl / 4
        r4 = prev_close + 1.1 * range_hl / 2
        s1 = prev_close - 1.1 * range_hl / 12
        s2 = prev_close - 1.1 * range_hl / 6
        s3 = prev_close - 1.1 * range_hl / 4
        s4 = prev_close - 1.1 * range_hl / 2
        
        df['PP'] = pp
        df['R1'] = r1
        df['R2'] = r2
        df['R3'] = r3
        df['R4'] = r4
        df['S1'] = s1
        df['S2'] = s2
        df['S3'] = s3
        df['S4'] = s4
        
    else:
        print(f"Error: Unknown method '{method}'. Use 'standard', 'fibonacci', 'woodie', or 'camarilla'.")
        return df
    
    return df
    
def calculate_trix(df: pd.DataFrame, nday: int = 12, signal: int = 9):
    """
    TRIX (Triple Exponential Average) - 3중 지수 이동평균의 변화율
    
    Jack Hutson이 개발한 모멘텀 오실레이터로 3중 EMA의 변화율을 측정합니다.
    과도한 스무딩으로 노이즈를 제거하고 장기 추세를 파악합니다.
    
    Formula:
    --------
    1. EMA1 = EMA(Price, nday)
    2. EMA2 = EMA(EMA1, nday)
    3. EMA3 = EMA(EMA2, nday)
    4. TRIX = (EMA3 - EMA3_prev) / EMA3_prev × 100
    5. Signal = EMA(TRIX, signal)
    
    Parameters:
    -----------
    df : pd.DataFrame
        가격 데이터 (Value 필수)
    nday : int, default=12
        EMA 기간 (Jack Hutson 표준)
    signal : int, default=9
        Signal Line EMA 기간
    
    Returns:
    --------
    pd.DataFrame
        TRIX_{nday} : TRIX 지표
        TRIX_Signal_{nday}_{signal} : Signal Line
    
    Interpretation:
    ---------------
    - **TRIX > 0**: 상승 모멘텀 (강세)
    - **TRIX < 0**: 하락 모멘텀 (약세)
    - **TRIX 상승**: 모멘텀 증가
    - **TRIX 하락**: 모멘텀 감소
    
    Trading Signals:
    ----------------
    1. **Zero Line Cross (주 신호)**:
       - TRIX > 0: 매수 신호
       - TRIX < 0: 매도 신호
    
    2. **Signal Line Cross**:
       - TRIX > Signal: 매수 (단기 강세)
       - TRIX < Signal: 매도 (단기 약세)
    
    3. **Divergence (고급)**:
       - 가격 고점 상승 + TRIX 고점 하락: 약세 다이버전스
       - 가격 저점 하락 + TRIX 저점 상승: 강세 다이버전스
    
    4. **Trend Confirmation**:
       - TRIX 지속 상승: 상승 추세 확인
       - TRIX 지속 하락: 하락 추세 확인
    
    Use Cases:
    ----------
    1. 추세 필터: 장기 추세 방향 확인
    2. 진입 타이밍: Signal Line Cross
    3. 다이버전스: 추세 전환 조기 감지
    4. 모멘텀 분석: 추세 강도 측정
    
    Advantages:
    -----------
    - 3중 스무딩으로 노이즈 최소화
    - False signal 감소
    - 장기 추세에 집중
    - MACD와 유사하나 더 부드러움
    
    Limitations:
    ------------
    - 극도로 후행 (3중 EMA)
    - 단기 변화 포착 어려움
    - 횡보 시 whipsaw 가능
    - 반응 느림
    
    Best Practices:
    ---------------
    - 장기 추세 확인용으로 사용
    - Signal Line과 조합
    - 다이버전스 활용
    - 추세 지표(MA, ADX)와 병행
    - 단기 매매보다 중장기 투자에 적합
    - Zero Line Cross를 주 신호로
    
    Standard Parameters:
    --------------------
    - nday=12 (Jack Hutson 표준)
    - signal=9 (일반적)
    - Alternative:
      * Short-term: nday=9, signal=5
      * Long-term: nday=20, signal=13
    
    Comparison with MACD:
    ---------------------
    - TRIX: 3중 EMA, 매우 부드러움, 장기 추세
    - MACD: 2개 EMA 차이, 빠른 반응, 중기 추세
    - TRIX는 MACD보다 후행하지만 신뢰도 높음
    
    Notes:
    ------
    - TRIX = Triple Exponential Average
    - 1980년대 Jack Hutson 개발
    - 변화율을 백분율로 표시 (× 100)
    - 0선 중심으로 오실레이션
    - 극값보다 방향과 교차가 중요
    """
    # 필수 컬럼 확인
    if 'Value' not in df.columns:
        print("Error: 'Value' column required for TRIX")
        return pd.Series(dtype=float)
    
    # 3중 EMA 계산
    ema1 = df['Value'].ewm(span=nday, adjust=False).mean()
    ema2 = ema1.ewm(span=nday, adjust=False).mean()
    ema3 = ema2.ewm(span=nday, adjust=False).mean()
    
    # TRIX = EMA3의 변화율 (%)
    trix = ema3.pct_change() * 100
    
    # Signal Line (TRIX의 EMA)
    trix_signal = trix.ewm(span=signal, adjust=False).mean()
    
    # 결과 저장
    trix_col = f"TRIX_{nday}"
    signal_col = f"TRIX_Signal_{nday}_{signal}"
    
    df[trix_col] = trix
    df[signal_col] = trix_signal
    
    return df[[trix_col, signal_col]]

def calculate_dmi(df: pd.DataFrame, nday: int = 14):
    """
    Calculate the Directional Movement Index (DMI) for stock prices.
    
    DMI (Directional Movement Index)는 J. Welles Wilder가 개발한 추세 강도 지표입니다.
    +DI, -DI, 그리고 ADX로 구성되며 추세의 방향과 강도를 동시에 측정합니다.
    
    Components:
    -----------
    1. +DI (Plus Directional Indicator):
       - 상승 방향성의 강도
       - 높을수록 강한 상승 추세
    
    2. -DI (Minus Directional Indicator):
       - 하락 방향성의 강도
       - 높을수록 강한 하락 추세
    
    3. ADX (Average Directional Index):
       - 추세의 강도 (방향 무관)
       - 25 이상: 강한 추세
       - 20-25: 약한 추세
       - 20 이하: 추세 없음 (횡보)
    
    Formula:
    --------
    1. Directional Movement:
       +DM = High - Previous_High (if positive and > -DM, else 0)
       -DM = Previous_Low - Low (if positive and > +DM, else 0)
       TR = max(High-Low, |High-Prev_Close|, |Low-Prev_Close|)
    
    2. Smoothed DM and TR (Wilder's Smoothing):
       Smoothed_+DM = +DM_prev - (+DM_prev/nday) + +DM_current
       Smoothed_-DM = -DM_prev - (-DM_prev/nday) + -DM_current
       Smoothed_TR = TR_prev - (TR_prev/nday) + TR_current
    
    3. Directional Indicators:
       +DI = 100 × (Smoothed_+DM / Smoothed_TR)
       -DI = 100 × (Smoothed_-DM / Smoothed_TR)
    
    4. ADX:
       DX = 100 × |+DI - -DI| / (+DI + -DI)
       ADX = Smoothed_DX (using Wilder's Smoothing)
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (High, Low, Value 컬럼 필요)
    nday : int, default=14
        Smoothing 기간 (J. Welles Wilder 표준)
    
    Returns:
    --------
    pd.DataFrame
        +DI_{nday}, -DI_{nday}, ADX_{nday} 컬럼
    
    Trading Signals:
    ----------------
    1. Trend Direction:
       - +DI > -DI: 상승 추세
       - -DI > +DI: 하락 추세
    
    2. Trend Strength (ADX):
       - ADX > 25: 강한 추세 → 추세 추종 전략
       - ADX < 20: 약한 추세 → 횡보 전략
    
    3. Entry Signals:
       - BUY: +DI가 -DI를 상향 돌파 AND ADX > 20
       - SELL: -DI가 +DI를 상향 돌파 AND ADX > 20
    
    4. Exit Signals:
       - ADX가 하락하기 시작 (추세 약화)
       - +DI와 -DI의 교차
    
    Notes:
    ------
    - J. Welles Wilder의 "New Concepts in Technical Trading Systems" (1978)
    - Wilder's Smoothing은 EMA의 특수 형태 (alpha = 1/nday)
    - ADX는 2×nday 기간이 필요 (초기 데이터 누락 많음)
    - ADX는 후행 지표이므로 추세 전환 감지 느림
    
    References:
    -----------
    - Wilder, J. W. (1978). New Concepts in Technical Trading Systems
    - Standard parameter: nday=14
    """
    # 1. Calculate Directional Movement (+DM, -DM)
    high_diff = df['High'].diff()
    low_diff = -df['Low'].diff()  # Previous_Low - Current_Low
    
    # +DM과 -DM은 상호 배타적
    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)
    
    # +DM: High가 상승하고, 상승폭이 Low 하락폭보다 클 때
    plus_dm[(high_diff > 0) & (high_diff > low_diff)] = high_diff
    
    # -DM: Low가 하락하고, 하락폭이 High 상승폭보다 클 때
    minus_dm[(low_diff > 0) & (low_diff > high_diff)] = low_diff
    
    # 2. Calculate True Range (TR)
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Value'].shift()).abs()
    tr3 = (df['Low'] - df['Value'].shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 3. Wilder's Smoothing (EMA with alpha = 1/nday)
    # 첫 번째 값은 단순 합
    alpha = 1.0 / nday
    
    # Smoothed +DM
    smoothed_plus_dm = plus_dm.ewm(alpha=alpha, adjust=False).mean()
    
    # Smoothed -DM
    smoothed_minus_dm = minus_dm.ewm(alpha=alpha, adjust=False).mean()
    
    # Smoothed TR (ATR)
    smoothed_tr = true_range.ewm(alpha=alpha, adjust=False).mean()
    
    # 4. Calculate Directional Indicators (+DI, -DI)
    # Division by zero 방지
    plus_di = 100 * (smoothed_plus_dm / smoothed_tr.replace(0, pd.NA))
    minus_di = 100 * (smoothed_minus_dm / smoothed_tr.replace(0, pd.NA))
    
    # 5. Calculate DX (Directional Index)
    di_sum = plus_di + minus_di
    di_diff = (plus_di - minus_di).abs()
    
    # Division by zero 방지
    dx = 100 * (di_diff / di_sum.replace(0, pd.NA))
    
    # 6. Calculate ADX (Average Directional Index)
    # ADX도 Wilder's Smoothing 적용
    # NaN/NA 값을 처리하기 위해 fillna 또는 dropna 사용
    dx_numeric = pd.to_numeric(dx, errors='coerce')
    adx = dx_numeric.ewm(alpha=alpha, adjust=False).mean()
    
    # 결과 저장
    df[f'Plus_DI_{nday}'] = plus_di
    df[f'Minus_DI_{nday}'] = minus_di
    df[f'ADX_{nday}'] = adx
    
    return df[[f'Plus_DI_{nday}', f'Minus_DI_{nday}', f'ADX_{nday}']]


def calculate_sumation_of_obv(df: pd.DataFrame, nday: int = 10):
    """
    Calculate the Summation of On-Balance Volume (SOBV) for stock prices.
    
    SOBV (Summation of OBV)는 OBV에 이동평균을 적용한 지표입니다.
    OBV의 단기 노이즈를 제거하고 장기 추세를 파악하기 위해 사용됩니다.
    
    CRITICAL NOTE:
    --------------
    SOBV는 OBV의 누적합(cumsum)이 아닙니다!
    SOBV = SMA(OBV, nday) 또는 EMA(OBV, nday)입니다.
    
    OBV vs SOBV:
    ------------
    1. OBV (On-Balance Volume):
       - 누적 거래량 지표
       - 가격 상승일: +Volume
       - 가격 하락일: -Volume
       - 매우 민감하고 노이즈 많음
    
    2. SOBV (Summation of OBV):
       - OBV의 이동평균 (스무딩)
       - 장기 자금 흐름 파악
       - OBV보다 안정적이고 추세 파악 용이
    
    Formula:
    --------
    1. Calculate OBV:
       if Close > Previous_Close:
           OBV = OBV_prev + Volume
       elif Close < Previous_Close:
           OBV = OBV_prev - Volume
       else:
           OBV = OBV_prev
    
    2. Calculate SOBV (SMA of OBV):
       SOBV = SMA(OBV, nday)
    
    Alternative (EMA):
       SOBV = EMA(OBV, nday)
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (Value, Volume 컬럼 필요)
    nday : int, default=10
        이동평균 기간 (일반적으로 10~20일 사용)
    
    Returns:
    --------
    pd.DataFrame
        OBV, SOBV_SMA_{nday}, SOBV_EMA_{nday} 컬럼
    
    Interpretation:
    ---------------
    1. SOBV 기울기 (가장 중요):
       - 상승 기울기: 장기 자금 유입 (매집)
       - 하락 기울기: 장기 자금 유출 (분배)
       - 절대값보다 방향과 변화율 중요
    
    2. 가격-SOBV Divergence:
       - 가격 횡보 + SOBV 상승: 숨은 매집 (긍정적)
       - 가격 상승 + SOBV 하락: 분배 조짐 (부정적)
    
    3. 장기 다이버전스:
       - 가격 신고가 + SOBV 저점 하락: 중장기 약세
       - 가격 신저가 + SOBV 상승: 장기 바닥 형성
    
    Trading Signals:
    ----------------
    1. Trend Filter:
       - SOBV 상승 구간: 매수 전략
       - SOBV 하락 구간: 매도/관망
    
    2. Divergence:
       - Bullish Divergence: 가격↓ + SOBV↑ → 매수
       - Bearish Divergence: 가격↑ + SOBV↓ → 매도
    
    3. Confirmation:
       - OBV와 SOBV 동시 상승: 강한 매수 신호
       - OBV와 SOBV 동시 하락: 강한 매도 신호
    
    Notes:
    ------
    - OBV는 Joseph Granville이 1963년 개발
    - SOBV는 OBV의 변형으로 실무자들이 개발
    - 표준 파라메터 없음 (10~20일 일반적)
    - SMA 버전이 더 일반적이나 EMA도 사용 가능
    - 절대값은 의미 없고 방향과 변화만 중요
    
    References:
    -----------
    - Granville, J. (1963). Granville's New Key to Stock Market Profits
    - Standard parameter: nday=10 (일반적 사용값)
    """
    # 1. Calculate OBV (On-Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if df['Value'].iloc[i] > df['Value'].iloc[i - 1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Value'].iloc[i] < df['Value'].iloc[i - 1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    
    df['OBV'] = obv
    
    # 2. Calculate SOBV (Summation of OBV)
    # SOBV는 OBV의 이동평균입니다 (cumsum이 아님!)
    
    # SMA 버전 (더 일반적)
    df[f'SOBV_SMA_{nday}'] = df['OBV'].rolling(window=nday).mean()
    
    # EMA 버전 (일부 트레이더들이 선호)
    df[f'SOBV_EMA_{nday}'] = df['OBV'].ewm(span=nday, adjust=False).mean()
    
    return df[['OBV', f'SOBV_SMA_{nday}', f'SOBV_EMA_{nday}']]

def calculate_supertrend_indicator(df: pd.DataFrame, nday: int = 10, multiplier: float = 3.0):
    """
    Calculate the Supertrend Indicator for stock prices.
    
    Supertrend는 ATR 기반 추세 추종 지표로 동적 지지/저항선을 제공합니다.
    가격이 Supertrend 위에 있으면 상승 추세, 아래에 있으면 하락 추세입니다.
    
    Components:
    -----------
    1. Basic Band:
       - HL2 = (High + Low) / 2
       - Upper Band = HL2 + (multiplier × ATR)
       - Lower Band = HL2 - (multiplier × ATR)
    
    2. Final Band (Trailing):
       - Final Upper Band는 하향 조정만 가능
       - Final Lower Band는 상향 조정만 가능
       - 이전 값과 비교하여 더 유리한 방향으로만 이동
    
    3. Supertrend:
       - 상승 추세: Supertrend = Final Lower Band
       - 하락 추세: Supertrend = Final Upper Band
       - 가격이 밴드를 돌파하면 추세 전환
    
    Formula:
    --------
    1. Basic Bands:
       HL2 = (High + Low) / 2
       Basic_UB = HL2 + (multiplier × ATR)
       Basic_LB = HL2 - (multiplier × ATR)
    
    2. Final Bands (Trailing):
       if Basic_UB < Final_UB_prev OR Close_prev > Final_UB_prev:
           Final_UB = Basic_UB
       else:
           Final_UB = Final_UB_prev
       
       if Basic_LB > Final_LB_prev OR Close_prev < Final_LB_prev:
           Final_LB = Basic_LB
       else:
           Final_LB = Final_LB_prev
    
    3. Supertrend Direction:
       if Close <= Final_UB:
           Supertrend = Final_UB (하락 추세)
       else:
           Supertrend = Final_LB (상승 추세)
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (High, Low, Value 컬럼 필요)
    nday : int, default=10
        ATR 계산 기간 (일반적으로 7~14일)
    multiplier : float, default=3.0
        ATR 승수 (변동성 조절, 일반적으로 2~3)
    
    Returns:
    --------
    pd.DataFrame
        Supertrend_{nday}_{multiplier}, Supertrend_Direction_{nday}_{multiplier} 컬럼
    
    Interpretation:
    ---------------
    1. Trend Direction:
       - Direction = 1 (상승): 가격 > Supertrend
       - Direction = -1 (하락): 가격 < Supertrend
    
    2. Trading Signals:
       - BUY: Direction이 -1에서 1로 전환 (Supertrend 돌파)
       - SELL: Direction이 1에서 -1로 전환 (Supertrend 이탈)
    
    3. Stop Loss:
       - 상승 추세: Supertrend가 동적 손절선
       - 하락 추세: Supertrend가 동적 저항선
    
    Trading Strategy:
    -----------------
    1. Trend Following:
       - BUY: Direction = 1 (상승 추세 진입)
       - SELL: Direction = -1 (하락 추세 전환)
    
    2. Dynamic Stop Loss:
       - 매수 후: Supertrend를 트레일링 스탑으로 사용
       - 가격이 Supertrend 하향 돌파 시 청산
    
    Notes:
    ------
    - Olivier Seban이 개발한 트렌드 추종 지표
    - 표준 파라메터: nday=10, multiplier=3.0
    - 일부 사용자는 (7, 3) 또는 (14, 2) 선호
    - ATR 기반으로 변동성에 자동 적응
    - 횡보장에서 잦은 전환 발생 (단점)
    - 추세장에서 매우 효과적
    
    References:
    -----------
    - Olivier Seban (개발자)
    - Standard: nday=10, multiplier=3.0
    - Alternative: (7, 3), (14, 2)
    """
    # 1. Calculate ATR
    atr_result = calculate_atr(df, nday)
    if isinstance(atr_result, pd.Series):
        atr = atr_result
    else:
        atr = atr_result[f'ATR_{nday}']
    
    # 2. Calculate HL2 (average of High and Low)
    hl2 = (df['High'] + df['Low']) / 2
    
    # 3. Calculate Basic Bands
    basic_ub = hl2 + (multiplier * atr)
    basic_lb = hl2 - (multiplier * atr)
    
    # 4. Initialize Final Bands and Supertrend
    final_ub = pd.Series(index=df.index, dtype='float64')
    final_lb = pd.Series(index=df.index, dtype='float64')
    supertrend = pd.Series(index=df.index, dtype='float64')
    direction = pd.Series(index=df.index, dtype='int64')
    
    for i in range(len(df)):
        if i == 0:
            # 첫 번째 값 초기화
            final_ub.iloc[i] = basic_ub.iloc[i]
            final_lb.iloc[i] = basic_lb.iloc[i]
        else:
            # Final Upper Band (하향 조정만 가능)
            if basic_ub.iloc[i] < final_ub.iloc[i-1] or df['Value'].iloc[i-1] > final_ub.iloc[i-1]:
                final_ub.iloc[i] = basic_ub.iloc[i]
            else:
                final_ub.iloc[i] = final_ub.iloc[i-1]
            
            # Final Lower Band (상향 조정만 가능)
            if basic_lb.iloc[i] > final_lb.iloc[i-1] or df['Value'].iloc[i-1] < final_lb.iloc[i-1]:
                final_lb.iloc[i] = basic_lb.iloc[i]
            else:
                final_lb.iloc[i] = final_lb.iloc[i-1]
        
        # Supertrend 결정
        if i == 0:
            # 초기값: 가격에 따라 결정
            if df['Value'].iloc[i] <= final_ub.iloc[i]:
                supertrend.iloc[i] = final_ub.iloc[i]
                direction.iloc[i] = -1
            else:
                supertrend.iloc[i] = final_lb.iloc[i]
                direction.iloc[i] = 1
        else:
            # 이전 방향 기반 결정
            if supertrend.iloc[i-1] == final_ub.iloc[i-1] and df['Value'].iloc[i] <= final_ub.iloc[i]:
                # 하락 추세 유지
                supertrend.iloc[i] = final_ub.iloc[i]
                direction.iloc[i] = -1
            elif supertrend.iloc[i-1] == final_ub.iloc[i-1] and df['Value'].iloc[i] > final_ub.iloc[i]:
                # 하락에서 상승으로 전환
                supertrend.iloc[i] = final_lb.iloc[i]
                direction.iloc[i] = 1
            elif supertrend.iloc[i-1] == final_lb.iloc[i-1] and df['Value'].iloc[i] >= final_lb.iloc[i]:
                # 상승 추세 유지
                supertrend.iloc[i] = final_lb.iloc[i]
                direction.iloc[i] = 1
            else:
                # 상승에서 하락으로 전환
                supertrend.iloc[i] = final_ub.iloc[i]
                direction.iloc[i] = -1
    
    # 결과 저장
    df[f'Supertrend_{nday}_{multiplier}'] = supertrend
    df[f'Supertrend_Direction_{nday}_{multiplier}'] = direction
    
    return df[[f'Supertrend_{nday}_{multiplier}', f'Supertrend_Direction_{nday}_{multiplier}']]

def calculate_williams_percent_r(df: pd.DataFrame, nday: int = 14):
    """
    Calculate the Williams %R for stock prices.
    
    Williams %R은 Larry Williams가 개발한 모멘텀 오실레이터로
    일정 기간 동안의 고가-저가 범위 내에서 현재 가격의 상대적 위치를 나타냅니다.
    
    Formula:
    --------
    Williams %R = -100 × (Highest_High - Close) / (Highest_High - Lowest_Low)
    
    where:
    - Highest_High = 최근 nday 기간의 최고가
    - Lowest_Low = 최근 nday 기간의 최저가
    - Close = 현재 종가
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (High, Low, Value 컬럼 필요)
    nday : int, default=14
        계산 기간 (Larry Williams 표준)
    
    Returns:
    --------
    pd.Series
        WPR_{nday} 컬럼 (-100 ~ 0 범위)
    
    Interpretation:
    ---------------
    Range: -100 to 0
    
    1. Overbought/Oversold Levels:
       - -20 to 0: 과매수 (Overbought) - 매도 고려
       - -80 to -100: 과매도 (Oversold) - 매수 고려
       - -50: 중립
    
    2. Extreme Levels:
       - %R > -20: 강한 과매수 (반전 가능성)
       - %R < -80: 강한 과매도 (반등 가능성)
    
    3. Trend Confirmation:
       - 상승 추세: %R이 -50 위에서 움직임
       - 하락 추세: %R이 -50 아래에서 움직임
    
    Trading Signals:
    ----------------
    1. Classic Strategy (역추세):
       - BUY: %R < -80 (과매도에서 반등)
       - SELL: %R > -20 (과매수에서 조정)
    
    2. Failure Swings:
       - Bullish: 과매도 구간(-80 이하)에서 2번 저점 형성 후 탈출
       - Bearish: 과매수 구간(-20 이상)에서 2번 고점 형성 후 하락
    
    3. Divergence:
       - Bullish Divergence: 가격은 하락, %R은 상승
       - Bearish Divergence: 가격은 상승, %R은 하락
    
    Notes:
    ------
    - Larry Williams 개발 (1973)
    - Stochastic %K와 역수 관계: Williams %R = Stochastic %K - 100
    - 표준 파라메터: nday=14 (Larry Williams)
    - 대안: nday=7 (단기), nday=21 (중기)
    - 0~-100 범위 (Stochastic과 달리 음수)
    - Fast Stochastic과 유사하지만 스케일 반전
    - 과매수/과매도 신호가 주요 용도
    - 추세장에서 과매수/과매도가 장기간 지속 가능 (단점)
    
    Relationship with Stochastic:
    ------------------------------
    Williams %R = -100 × (H - C) / (H - L)
    Stochastic %K = 100 × (C - L) / (H - L)
    
    Therefore: Williams %R = Stochastic %K - 100
    
    References:
    -----------
    - Larry Williams (1973)
    - Standard parameter: nday=14
    - Alternative: 7, 21
    """
    # 최근 nday 기간의 최고가와 최저가
    highest_high = df['High'].rolling(window=nday).max()
    lowest_low = df['Low'].rolling(window=nday).min()
    
    # Williams %R 계산
    # Division by zero 방지
    range_hl = highest_high - lowest_low
    range_hl = range_hl.replace(0, pd.NA)
    
    df[f"WPR_{nday}"] = -100 * (highest_high - df['Value']) / range_hl
    
    return df[f"WPR_{nday}"]

def calculate_elder_ray_index(df: pd.DataFrame, nday: int = 13):
    """
    Calculate the Elder-Ray Index for stock prices.
    
    Elder-Ray Index는 Alexander Elder가 개발한 지표로 Bull Power와 Bear Power로 구성됩니다.
    매수세력(Bull)과 매도세력(Bear)의 힘을 측정하여 추세의 강도와 방향을 파악합니다.
    
    Components:
    -----------
    1. Bull Power (매수세력):
       - High - EMA
       - 양수: 매수세력이 EMA 위로 가격 끌어올림
       - 음수: 매수세력이 약함
    
    2. Bear Power (매도세력):
       - Low - EMA
       - 음수: 매도세력이 EMA 아래로 가격 끌어내림
       - 양수: 매도세력이 약함
    
    Formula:
    --------
    EMA = Exponential Moving Average(Close, nday)
    Bull Power = High - EMA
    Bear Power = Low - EMA
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (High, Low, Value 컬럼 필요)
    nday : int, default=13
        EMA 기간 (Alexander Elder 표준)
    
    Returns:
    --------
    pd.DataFrame
        ERay_Bull_{nday}, ERay_Bear_{nday} 컬럼
    
    Interpretation:
    ---------------
    1. Bull Power (매수세력):
       - Bull Power > 0: 매수세력 강함 (고가가 EMA 위)
       - Bull Power < 0: 매수세력 약함 (고가도 EMA 못넘음)
       - 상승 중: 매수세력 우위
    
    2. Bear Power (매도세력):
       - Bear Power < 0: 매도세력 강함 (저가가 EMA 아래)
       - Bear Power > 0: 매도세력 약함 (저가도 EMA 위)
       - 하락 중: 매도세력 우위
    
    3. Combined Analysis:
       - Bull Power > 0 & Bear Power > 0: 강한 상승 추세
       - Bull Power < 0 & Bear Power < 0: 강한 하락 추세
       - Bull Power > 0 & Bear Power < 0: 혼합 (일반적)
       - Bull Power < 0 & Bear Power > 0: 매우 좁은 범위 (횡보)
    
    Trading Signals:
    ----------------
    1. Bull Power Strategy (상승 추세 진입):
       - EMA 상승 추세
       - Bear Power < 0 but 상승 중
       - Bull Power > 0
       → BUY
    
    2. Bear Power Strategy (하락 추세 진입):
       - EMA 하락 추세
       - Bull Power > 0 but 하락 중
       - Bear Power < 0
       → SELL
    
    3. Divergence:
       - Bullish Divergence: 가격 하락, Bull Power 상승
       - Bearish Divergence: 가격 상승, Bear Power 하락
    
    4. Classic Elder-Ray Rules:
       a) Long Entry:
          - EMA 상승
          - Bear Power < 0 (매도압력 있지만)
          - Bear Power 상승 중 (압력 약화)
       
       b) Short Entry:
          - EMA 하락
          - Bull Power > 0 (매수압력 있지만)
          - Bull Power 하락 중 (압력 약화)
    
    Notes:
    ------
    - Alexander Elder 개발 ("Trading for a Living", 1993)
    - 표준 파라메터: nday=13 (Elder 표준)
    - EMA는 추세 방향 결정
    - Bull/Bear Power는 추세 강도 측정
    - 반드시 EMA 추세와 함께 사용
    - Elder는 13-EMA를 "합의 가격(consensus price)"이라고 명명
    
    Triple Screen Trading System:
    -----------------------------
    Elder-Ray는 Elder의 Triple Screen 시스템의 일부:
    1. Screen 1: 주간 차트로 추세 파악
    2. Screen 2: 일간 차트로 Elder-Ray 확인
    3. Screen 3: 정확한 진입점 포착
    
    References:
    -----------
    - Elder, Alexander (1993). Trading for a Living
    - Standard parameter: nday=13
    - Bull Power = High - EMA(13)
    - Bear Power = Low - EMA(13)
    """
    # EMA 계산 (합의 가격)
    ema = df['Value'].ewm(span=nday, adjust=False).mean()
    
    # Bull Power: 매수세력의 힘
    bull_power = df['High'] - ema
    
    # Bear Power: 매도세력의 힘
    bear_power = df['Low'] - ema
    
    # 결과 저장
    df[f'ERay_Bull_{nday}'] = bull_power
    df[f'ERay_Bear_{nday}'] = bear_power
    
    return df[[f'ERay_Bull_{nday}', f'ERay_Bear_{nday}']]

def calculate_ichimoku_cloud(df: pd, conversion: int = 9, base: int = 26, 
                            lagging: int = 52, displacement: int = 26):
    """
    Ichimoku Cloud (일목균형표) 계산
    
    일목균형표는 일본의 호소다 고이치(Goichi Hosoda)가 개발한 
    종합적인 기술적 분석 지표입니다. "한 눈에 균형을 본다"는 의미로,
    5개의 선으로 구성되어 시장의 추세, 모멘텀, 지지/저항을 파악합니다.
    
    Components (5개 구성 요소):
    ----------------------------
    
    1. 전환선 (Tenkan-sen / Conversion Line):
       - Formula: (9일 최고가 + 9일 최저가) / 2
       - 의미: 단기 추세선 (9일 중간값)
       - 용도: 단기 가격 움직임, 빠른 신호
    
    2. 기준선 (Kijun-sen / Base Line):
       - Formula: (26일 최고가 + 26일 최저가) / 2
       - 의미: 중기 추세선 (26일 중간값)
       - 용도: 추세 확인, 지지/저항
    
    3. 선행스팬A (Senkou Span A / Leading Span A):
       - Formula: (전환선 + 기준선) / 2, 26일 선행
       - 의미: 구름(Cloud)의 첫 번째 경계
       - 용도: 미래 지지/저항 예측
    
    4. 선행스팬B (Senkou Span B / Leading Span B):
       - Formula: (52일 최고가 + 52일 최저가) / 2, 26일 선행
       - 의미: 구름(Cloud)의 두 번째 경계
       - 용도: 장기 추세, 강한 지지/저항
    
    5. 후행스팬 (Chikou Span / Lagging Span):
       - Formula: 현재 종가, 26일 후행 (차트상 26일 뒤로 표시)
       - 의미: 현재 가격과 과거 가격 비교
       - 용도: 추세 확인, 모멘텀 파악
    
    Cloud (구름 / Kumo):
    ---------------------
    - Senkou Span A와 Senkou Span B 사이의 영역
    - Span A > Span B: 상승 구름 (녹색/양운)
    - Span A < Span B: 하락 구름 (적색/음운)
    - 두꺼운 구름: 강한 지지/저항
    - 얇은 구름: 약한 지지/저항
    
    Trading Signals (매매 신호):
    -----------------------------
    1. 전환선/기준선 Cross (TK Cross):
       - 전환선 > 기준선: 강세 신호 (골든크로스)
       - 전환선 < 기준선: 약세 신호 (데드크로스)
    
    2. 가격과 구름 관계:
       - 가격 > 구름: 강한 상승 추세
       - 가격 < 구름: 강한 하락 추세
       - 가격 = 구름 안: 횡보/전환 구간
    
    3. 후행스팬:
       - 후행스팬 > 과거 가격: 상승 모멘텀
       - 후행스팬 < 과거 가격: 하락 모멘텀
    
    4. 구름 돌파:
       - 가격이 구름 상향 돌파: 강한 매수 신호
       - 가격이 구름 하향 이탈: 강한 매도 신호
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (High, Low, Value 컬럼 필수)
    conversion : int, default=9
        전환선 기간 (Tenkan-sen)
    base : int, default=26
        기준선 기간 (Kijun-sen)
    lagging : int, default=52
        선행스팬B 기간 (Senkou Span B)
    displacement : int, default=26
        선행/후행 이동 기간
    
    Returns:
    --------
    pd.DataFrame
        계산된 일목균형표 지표:
        - Tenkan_Sen: 전환선
        - Kijun_Sen: 기준선
        - Senkou_Span_A: 선행스팬A
        - Senkou_Span_B: 선행스팬B
        - Chikou_Span: 후행스팬
    
    Standard Parameters (표준 파라미터):
    ------------------------------------
    - conversion=9 (전환선: 1.5주)
    - base=26 (기준선: 1개월)
    - lagging=52 (선행스팬B: 2개월)
    - displacement=26 (선행/후행: 1개월)
    
    Notes:
    ------
    - 호소다 고이치(Goichi Hosoda) 개발 (1968년 출판)
    - "일목산인(一目山人, Ichimoku Sanjin)" 필명 사용
    - 일본 시장 기준: 6일=1주, 26일=1개월 (당시 토요일 근무)
    - 현대 글로벌 시장: 5일=1주이지만 파라미터는 동일 사용
    - 종합적 분석 시스템 (추세, 모멘텀, 지지/저항 통합)
    
    Examples:
    ---------
    >>> # 기본 사용
    >>> df = calculate_ichimoku_cloud(df)
    >>> 
    >>> # 커스텀 파라미터
    >>> df = calculate_ichimoku_cloud(df, conversion=7, base=22, lagging=44)
    >>> 
    >>> # 매매 신호 예시
    >>> # 전환선/기준선 크로스
    >>> tk_cross_up = (df['Tenkan_Sen'] > df['Kijun_Sen']) & (df['Tenkan_Sen'].shift(1) <= df['Kijun_Sen'].shift(1))
    >>> 
    >>> # 가격이 구름 위
    >>> above_cloud = (df['Value'] > df['Senkou_Span_A']) & (df['Value'] > df['Senkou_Span_B'])
    """
    # 1. 전환선 (Tenkan-sen / Conversion Line)
    # 9일 최고가와 최저가의 중간값
    high_conversion = df['High'].rolling(window=conversion).max()
    low_conversion = df['Low'].rolling(window=conversion).min()
    df['Tenkan_Sen'] = (high_conversion + low_conversion) / 2

    # 2. 기준선 (Kijun-sen / Base Line)
    # 26일 최고가와 최저가의 중간값
    high_base = df['High'].rolling(window=base).max()
    low_base = df['Low'].rolling(window=base).min()
    df['Kijun_Sen'] = (high_base + low_base) / 2

    # 3. 선행스팬A (Senkou Span A / Leading Span A)
    # (전환선 + 기준선) / 2, 26일 선행
    # shift(26): 현재 값을 26일 앞으로 이동 (미래 표시)
    df['Senkou_Span_A'] = ((df['Tenkan_Sen'] + df['Kijun_Sen']) / 2).shift(displacement)

    # 4. 선행스팬B (Senkou Span B / Leading Span B)
    # 52일 최고가와 최저가의 중간값, 26일 선행
    high_lagging = df['High'].rolling(window=lagging).max()
    low_lagging = df['Low'].rolling(window=lagging).min()
    df['Senkou_Span_B'] = ((high_lagging + low_lagging) / 2).shift(displacement)
    
    # 5. 후행스팬 (Chikou Span / Lagging Span)
    # 현재 종가를 26일 후행 (차트상 26일 뒤에 표시)
    # CRITICAL FIX: shift(-26)이어야 함 (과거가 아닌 미래로 이동)
    # 차트상에서는 현재 가격이 과거와 비교되도록 뒤로 표시
    df['Chikou_Span'] = df['Value'].shift(-displacement)

    return df[['Tenkan_Sen', 'Kijun_Sen', 'Senkou_Span_A', 'Senkou_Span_B', 'Chikou_Span']]


def calculate_price_envelope(df: pd, nday: int = 20, percent: float = 0.02):
    """
    Price Envelope (가격 봉투선) 계산
    
    Price Envelope는 이동평균선을 중심으로 일정 비율(%)만큼
    위아래로 벌어진 밴드를 그려 과매수/과매도를 판단하는 지표입니다.
    볼린저 밴드와 유사하지만, 표준편차 대신 고정 비율을 사용합니다.
    
    Formula:
    --------
    Upper Band = SMA(n) × (1 + percent)
    Lower Band = SMA(n) × (1 - percent)
    
    where:
    - SMA(n): n일 단순이동평균
    - percent: 밴드 폭 비율 (예: 0.02 = 2%)
    
    Interpretation (해석):
    ---------------------
    1. 상단 밴드(Upper Band):
       - 가격이 상단 밴드 도달: 과매수 구간
       - 매도 타이밍 또는 추세 강화 신호
    
    2. 하단 밴드(Lower Band):
       - 가격이 하단 밴드 도달: 과매도 구간
       - 매수 타이밍 또는 추세 약화 신호
    
    3. 중심선(SMA):
       - 평균 회귀 기준선
       - 지지/저항 역할
    
    Trading Strategy:
    -----------------
    1. Mean Reversion (평균 회귀):
       - 가격 < Lower Band → 매수 (반등 기대)
       - 가격 > Upper Band → 매도 (조정 기대)
    
    2. Breakout (돌파):
       - 가격이 Upper Band 상향 돌파 → 강한 상승 추세
       - 가격이 Lower Band 하향 이탈 → 강한 하락 추세
    
    3. Band Walking:
       - 추세장에서 가격이 밴드를 따라 이동
       - 상승장: Upper Band 근처 유지
       - 하락장: Lower Band 근처 유지
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (Value 컬럼 필수)
    nday : int, default=20
        이동평균 기간 (일반적으로 20일 사용)
    percent : float, default=0.02
        밴드 폭 비율 (0.02 = 2%)
    
    Returns:
    --------
    pd.DataFrame
        계산된 가격 봉투선:
        - Envelope_Upper_{nday}: 상단 밴드
        - Envelope_Lower_{nday}: 하단 밴드
    
    Standard Parameters (표준 파라미터):
    ------------------------------------
    시간대별 권장 설정:
    
    1. 일봉 차트 (Daily):
       - nday = 20 (약 1개월)
       - percent = 0.02 (2%)
       - 일반적인 주식 투자
    
    2. 주봉 차트 (Weekly):
       - nday = 10-13 (약 2-3개월)
       - percent = 0.10 (10%)
       - 장기 투자
    
    3. 1시간 차트 (Hourly):
       - nday = 20-24 (약 1일)
       - percent = 0.008 (0.8%)
       - 단타 거래
    
    4. 5분 차트 (5-min):
       - nday = 12-20
       - percent = 0.003 (0.3%)
       - 초단타 거래
    
    일반 권장:
    - nday = 20 (약 1개월, 가장 널리 사용)
    - percent = 0.025 (2.5%, 중간 설정)
    
    Notes:
    ------
    - Bollinger Bands와 유사하지만 더 단순
    - Bollinger: 표준편차 기반 (동적 변동)
    - Envelope: 고정 비율 기반 (정적 변동)
    - 횡보장에서 더 효과적 (평균 회귀 전략)
    - 추세장에서 Band Walking 현상 발생
    - 여러 시간대 비율을 조정하여 사용
    
    Comparison with Bollinger Bands:
    --------------------------------
    Price Envelope:
    - 장점: 단순, 명확, 계산 빠름
    - 단점: 변동성 변화에 둔감
    
    Bollinger Bands:
    - 장점: 변동성 적응형
    - 단점: 복잡, 계산 무거움
    
    Examples:
    ---------
    >>> # 기본 사용 (일봉, 2%)
    >>> df = calculate_price_envelope(df)
    >>> 
    >>> # 주봉 설정
    >>> df = calculate_price_envelope(df, nday=13, percent=0.10)
    >>> 
    >>> # 단타 설정 (1시간봉)
    >>> df = calculate_price_envelope(df, nday=24, percent=0.008)
    >>> 
    >>> # 매수 신호 예시
    >>> buy_signal = df['Value'] < df['Envelope_Lower_20']
    >>> 
    >>> # 매도 신호 예시
    >>> sell_signal = df['Value'] > df['Envelope_Upper_20']
    """
    # 이동평균 계산
    sma = df['Value'].rolling(window=nday).mean()
    
    # 상단/하단 밴드 계산 (SMA ± percent)
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

def calculate_Smoothed_Moving_Average(df: pd, nday: int = 14):
    """
    SMMA (Smoothed Moving Average) 계산
    
    SMMA는 Wilder's Smoothing 또는 RMA(Running Moving Average)로도 알려진
    평활 이동평균입니다. J. Welles Wilder가 RSI, ATR, ADX 등의 지표에서
    사용하기 위해 개발했습니다.
    
    Formula:
    --------
    SMMA[0] = SMA(n)  # 첫 n개의 평균
    SMMA[i] = (SMMA[i-1] × (n-1) + Price[i]) / n
    
    or equivalently (EMA form):
    SMMA[i] = SMMA[i-1] + α × (Price[i] - SMMA[i-1])
    where α = 1/n
    
    Characteristics (특징):
    -----------------------
    1. SMA보다 더 부드러움:
       - SMA: 모든 기간에 동일 가중치
       - SMMA: 과거 값에 더 많은 가중치 (누적)
    
    2. EMA보다 더 평활:
       - EMA α = 2/(n+1) ≈ 0.133 (n=14)
       - SMMA α = 1/n = 0.071 (n=14)
       - SMMA가 EMA보다 약 2배 느림
    
    3. 과거 데이터의 영향:
       - 모든 과거 데이터가 영향을 미침
       - 오래된 데이터는 점진적으로 감소
       - 완전히 사라지지 않음 (이론적으로)
    
    4. Wilder's Smoothing:
       - RSI, ATR, ADX의 기본 평활 방법
       - 변동성 감소에 효과적
       - 추세 추종에 적합
    
    Interpretation (해석):
    ---------------------
    1. 추세 확인:
       - Price > SMMA: 상승 추세
       - Price < SMMA: 하락 추세
    
    2. 지지/저항:
       - SMMA 자체가 동적 지지/저항선
       - SMA보다 더 안정적
    
    3. 신호 지연:
       - EMA보다 느림 (더 평활)
       - 잘못된 신호(Whipsaw) 감소
       - 진입/청산 타이밍 늦음
    
    Comparison (비교):
    ------------------
    SMA(14):
    - 가중치: 모두 동일 (1/14)
    - 반응: 보통
    - 노이즈: 보통
    
    EMA(14):
    - 가중치: 지수적 감소 (α=0.133)
    - 반응: 빠름
    - 노이즈: 많음
    
    SMMA(14):
    - 가중치: 누적 평활 (α=0.071)
    - 반응: 느림
    - 노이즈: 적음
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (Value 컬럼 필수)
    nday : int, default=14
        평활 기간 (Wilder 표준)
    
    Returns:
    --------
    pd.Series
        계산된 SMMA 값
    
    Standard Parameters (표준 파라미터):
    ------------------------------------
    - nday = 14 (J. Welles Wilder 표준)
    - RSI, ATR, ADX에서 사용하는 기본값
    - 다른 일반적 설정: 9, 20, 50
    
    Notes:
    ------
    - J. Welles Wilder 개발 (1978)
    - "New Concepts in Technical Trading Systems"
    - Wilder's Smoothing = SMMA = RMA (동일 개념)
    - EMA와 유사하지만 α = 1/n (더 평활)
    - TradingView에서는 RMA로 표기
    - 첫 번째 값은 SMA(n)로 초기화
    
    Wilder's Original Uses:
    -----------------------
    - RSI (Relative Strength Index): 14일
    - ATR (Average True Range): 14일
    - ADX (Average Directional Index): 14일
    - Parabolic SAR: 내부적으로 사용
    
    Examples:
    ---------
    >>> # 기본 사용 (Wilder 표준)
    >>> df['SMMA_14'] = calculate_Smoothed_Moving_Average(df)
    >>> 
    >>> # 커스텀 기간
    >>> df['SMMA_20'] = calculate_Smoothed_Moving_Average(df, nday=20)
    >>> 
    >>> # 매매 신호 예시
    >>> buy_signal = (df['Value'] > df['SMMA_14']) & (df['Value'].shift(1) <= df['SMMA_14'].shift(1))
    >>> 
    >>> # EMA와 비교
    >>> df['EMA_14'] = df['Value'].ewm(span=14, adjust=False).mean()
    >>> # SMMA가 EMA보다 평활함
    """
    # SMMA 계산
    smma = pd.Series(index=df.index, dtype=float)
    
    # 첫 nday 개는 SMA로 초기화
    if len(df) >= nday:
        smma.iloc[nday-1] = df['Value'].iloc[:nday].mean()
        
        # 이후 값들은 재귀 공식 사용
        # SMMA[i] = (SMMA[i-1] × (n-1) + Price[i]) / n
        for i in range(nday, len(df)):
            smma.iloc[i] = (smma.iloc[i-1] * (nday - 1) + df['Value'].iloc[i]) / nday
    
    df[f"SMMA_{nday}"] = smma
    return df[f"SMMA_{nday}"]

def calculate_Kaufman_Adaptive_Moving_Average(df: pd.DataFrame, nday: int = 10, 
                                               fast_ema: int = 2, slow_ema: int = 30) -> pd.Series:
    """
    Calculate the Kaufman Adaptive Moving Average (KAMA) for stock prices.
    
    KAMA (Kaufman Adaptive Moving Average)
    ======================================
    Perry Kaufman이 1995년 개발한 적응형 이동평균선으로,
    시장의 효율성(추세 강도)에 따라 민감도를 자동 조절합니다.
    
    Core Concept:
    -------------
    - 추세장: 빠른 EMA처럼 작동 (민감하게 반응)
    - 횡보장: 느린 EMA처럼 작동 (잡음 제거)
    - Efficiency Ratio (ER)로 시장 상태 판단
    
    Algorithm (3단계):
    ------------------
    1. Efficiency Ratio (ER) 계산:
       ER = |Change| / Volatility
       
       where:
       - Change = |Price[now] - Price[now - n]|
       - Volatility = Σ|Price[i] - Price[i-1]| (n일간)
       
       ER 의미:
       - ER ≈ 1: 완벽한 추세 (한 방향으로 직선 이동)
       - ER ≈ 0: 횡보 (왔다갔다 반복)
    
    2. Smoothing Constant (SC) 계산:
       SC = [ER × (fastest - slowest) + slowest]²
       
       where:
       - fastest = 2/(fast_ema + 1)  [기본: 2/3 = 0.6667]
       - slowest = 2/(slow_ema + 1)  [기본: 2/31 = 0.0645]
       
       SC 범위: [slowest², fastest²]
       - 추세장 (ER=1): SC ≈ fastest² (빠른 반응)
       - 횡보장 (ER=0): SC ≈ slowest² (느린 반응)
    
    3. KAMA 계산 (재귀):
       KAMA[0] = Price[nday-1] (초기값: nday번째 가격)
       KAMA[i] = KAMA[i-1] + SC[i] × (Price[i] - KAMA[i-1])
       
       = (1 - SC[i]) × KAMA[i-1] + SC[i] × Price[i]
       (지수가중 이동평균 형태)
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'Value' 필수)
    nday : int, default=10
        Efficiency Ratio 계산 기간
        - Perry Kaufman 원본: **10일**
        - 짧을수록: 빠른 반응, 많은 신호
        - 길수록: 느린 반응, 적은 신호
        - 일반적 범위: 5~20
    fast_ema : int, default=2
        빠른 EMA 기간 (추세장에서 사용)
        - 원본: **2일** (fastest = 2/3 = 0.6667)
        - 매우 빠른 반응
    slow_ema : int, default=30
        느린 EMA 기간 (횡보장에서 사용)
        - 원본: **30일** (slowest = 2/31 = 0.0645)
        - 매우 느린 반응, 잡음 필터링
    
    Returns:
    --------
    pd.Series
        KAMA_{nday} 컬럼
    
    Mathematical Formula:
    ---------------------
    1. ER[i] = |Price[i] - Price[i-n]| / Σ(j=i-n+1 to i)|Price[j] - Price[j-1]|
    
    2. fastest = 2/(fast_ema + 1)
       slowest = 2/(slow_ema + 1)
       SC[i] = [ER[i] × (fastest - slowest) + slowest]²
    
    3. KAMA[i] = KAMA[i-1] + SC[i] × (Price[i] - KAMA[i-1])
    
    Properties:
    -----------
    - **Adaptive**: 시장 상태에 따라 자동 조절
    - **Trend Following**: 추세 추종형 지표
    - **Low Lag**: 기존 MA보다 지연 적음
    - **Noise Reduction**: 횡보장에서 잡음 제거
    
    Advantages vs Traditional MA:
    ------------------------------
    - SMA: 고정된 가중치 → 둔함
    - EMA: 고정된 α → 횡보장 잡음 多
    - KAMA: 적응형 α → 추세장 빠름 + 횡보장 안정
    
    Trading Signals:
    ----------------
    1. 추세 확인:
       - Price > KAMA: 상승 추세
       - Price < KAMA: 하락 추세
    
    2. 매매 신호:
       - Buy: Price가 KAMA 상향 돌파
       - Sell: Price가 KAMA 하향 돌파
    
    3. 기울기:
       - KAMA 상승: 상승 추세 강화
       - KAMA 하락: 하락 추세 강화
       - KAMA 평평: 횡보장
    
    Efficiency Ratio Interpretation:
    --------------------------------
    - ER > 0.7: 강한 추세 (KAMA 빠르게 반응)
    - ER 0.3~0.7: 약한 추세
    - ER < 0.3: 횡보장 (KAMA 느리게 반응)
    
    Common Use Cases:
    -----------------
    1. 추세 필터:
       - KAMA 기울기로 추세 방향 확인
       - 다른 지표와 조합 (RSI, MACD 등)
    
    2. 지지/저항:
       - KAMA가 동적 지지/저항선 역할
       - 가격이 KAMA에서 반등/하락
    
    3. 크로스오버:
       - 두 개의 KAMA (다른 기간) 교차
       - KAMA(10)과 KAMA(20) 골든/데드 크로스
    
    Parameter Tuning:
    -----------------
    - **Conservative** (안정적):
      nday=14, fast_ema=2, slow_ema=50
      → 적은 신호, 높은 신뢰도
    
    - **Standard** (기본):
      nday=10, fast_ema=2, slow_ema=30
      → Perry Kaufman 원본
    
    - **Aggressive** (적극적):
      nday=5, fast_ema=2, slow_ema=20
      → 많은 신호, 빠른 반응
    
    Implementation Notes:
    ---------------------
    1. Change 계산: n일 전 대비 **절대** 변화
       (방향성 고려 안함, 크기만)
    
    2. Volatility: n일간 일일 변화의 합
       (True Range 개념과 유사)
    
    3. SC 제곱: 변동성 감소 효과
       (원본 공식에 포함)
    
    4. 초기값: nday번째 가격 사용
       (SMA 대신 간단한 초기화)
    
    References:
    -----------
    - "Smarter Trading" (Perry Kaufman, 1995)
    - "Trading Systems and Methods" (Perry Kaufman, 5th ed., 2013)
    - Original paper: "Efficiency Ratio and Adaptive Moving Averages"
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> df = calculate_Kaufman_Adaptive_Moving_Average(df, nday=10)
    >>> # KAMA_10 컬럼 생성됨
    >>> 
    >>> # 추세 확인
    >>> df['Trend'] = np.where(df['Value'] > df['KAMA_10'], 'Up', 'Down')
    >>> 
    >>> # 여러 기간 비교
    >>> df = calculate_Kaufman_Adaptive_Moving_Average(df, nday=5)
    >>> df = calculate_Kaufman_Adaptive_Moving_Average(df, nday=20)
    
    See Also:
    ---------
    - calculate_ema: 지수 이동평균 (고정 α)
    - calculate_Smoothed_Moving_Average: SMMA (Wilder's)
    - calculate_vidya: VIDYA (CMO 기반 적응형)
    - calculate_Triple_Exponential_Moving_Average: TRIX
    
    Notes:
    ------
    - **ER = 0일 때**: Volatility가 Change보다 훨씬 큼 (횡보)
    - **ER = 1일 때**: Change = Volatility (완벽한 일방향 추세)
    - **SC 제곱**: Kaufman의 원본 공식 (감속 효과)
    - **NaN 처리**: 초기 nday 기간은 NaN (데이터 부족)
    """
    if len(df) < nday:
        df[f"KAMA_{nday}"] = np.nan
        return df[f"KAMA_{nday}"]
    
    # Step 1: Efficiency Ratio (ER) 계산
    # Change = |Price[now] - Price[now - nday]| (절대 변화)
    change = df['Value'].diff(nday).abs()
    
    # Volatility = Σ|Price[i] - Price[i-1]| (nday 기간 동안)
    volatility = df['Value'].diff().abs().rolling(window=nday).sum()
    
    # ER = Change / Volatility
    # ER이 1에 가까우면 강한 추세, 0에 가까우면 횡보
    efficiency_ratio = change / volatility
    efficiency_ratio = efficiency_ratio.fillna(0)  # division by zero 처리
    
    # Step 2: Smoothing Constant (SC) 계산
    # fastest = 2/(fast_ema + 1), slowest = 2/(slow_ema + 1)
    fastest = 2.0 / (fast_ema + 1)
    slowest = 2.0 / (slow_ema + 1)
    
    # SC = [ER × (fastest - slowest) + slowest]²
    # 추세장(ER=1): SC ≈ fastest² (빠른 반응)
    # 횡보장(ER=0): SC ≈ slowest² (느린 반응)
    smoothing_constant = (efficiency_ratio * (fastest - slowest) + slowest) ** 2
    
    # Step 3: KAMA 계산 (재귀적)
    kama = pd.Series(index=df.index, dtype=float)
    
    # 초기값: nday번째 가격 (간단한 초기화)
    # (원본 Kaufman은 SMA 사용 가능하지만, 가격도 일반적)
    kama.iloc[nday - 1] = df['Value'].iloc[nday - 1]
    
    # 재귀 계산: KAMA[i] = KAMA[i-1] + SC[i] × (Price[i] - KAMA[i-1])
    for i in range(nday, len(df)):
        sc = smoothing_constant.iloc[i]
        if pd.isna(sc):
            kama.iloc[i] = kama.iloc[i - 1]
        else:
            kama.iloc[i] = kama.iloc[i - 1] + sc * (df['Value'].iloc[i] - kama.iloc[i - 1])
    
    df[f"KAMA_{nday}"] = kama
    return df[f"KAMA_{nday}"]

def calculate_Tema(df: pd.DataFrame, nday: int = 12) -> pd.Series:
    """
    Calculate the Triple Exponential Moving Average (TEMA) for stock prices.
    
    TEMA (Triple Exponential Moving Average)
    ========================================
    Patrick Mulloy가 1994년 개발한 3중 지수 이동평균선으로,
    전통적인 EMA의 지연(lag)을 크게 줄이면서도 평활성을 유지합니다.
    
    Core Concept:
    -------------
    - EMA의 지연 문제 해결
    - 3개의 EMA를 조합하여 더 빠른 반응
    - 가격 변화에 민감하지만 잡음은 억제
    
    Formula:
    --------
    EMA1 = EMA(Price, n)
    EMA2 = EMA(EMA1, n)
    EMA3 = EMA(EMA2, n)
    
    TEMA = 3 × EMA1 - 3 × EMA2 + EMA3
    
    where:
    - EMA1: 가격의 단순 EMA (1차)
    - EMA2: EMA1의 EMA (2차, 더 평활)
    - EMA3: EMA2의 EMA (3차, 가장 평활)
    
    Mathematical Derivation:
    ------------------------
    지연 제거 원리:
    - EMA2는 EMA1보다 지연이 크다
    - EMA3는 EMA2보다 지연이 더 크다
    - 3 × EMA1: 빠른 신호 강조
    - -3 × EMA2: 중간 지연 제거
    - +EMA3: 과도한 보정 조정
    
    결과: 지연 최소화 + 평활성 유지
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (컬럼: 'Value' 필수)
    nday : int, default=12
        EMA 계산 기간
        - Patrick Mulloy 표준: **12일**
        - 일반적 사용: 9, 12, 20
        - 짧을수록: 빠른 반응, 높은 민감도
        - 길수록: 느린 반응, 높은 안정성
    
    Returns:
    --------
    pd.Series
        TEMA_{nday} 컬럼
    
    Properties:
    -----------
    - **Low Lag**: EMA보다 훨씬 적은 지연
    - **Smooth**: 3중 평활로 잡음 감소
    - **Responsive**: 가격 변화에 빠른 반응
    - **Trend Following**: 추세 추종형 지표
    
    Advantages vs Traditional MA:
    ------------------------------
    SMA (Simple Moving Average):
    - 지연: 매우 큼 (모든 데이터 동일 가중)
    - 평활: 높음
    - 반응: 매우 느림
    
    EMA (Exponential Moving Average):
    - 지연: 보통 (최근 데이터 강조)
    - 평활: 보통
    - 반응: 보통
    
    TEMA (Triple Exponential):
    - 지연: 매우 낮음 (3중 보정)
    - 평활: 높음 (3중 평활)
    - 반응: 빠름 (지연 제거)
    
    Trading Signals:
    ----------------
    1. 추세 확인:
       - Price > TEMA: 강한 상승 추세
       - Price < TEMA: 강한 하락 추세
    
    2. 크로스오버:
       - Price가 TEMA 상향 돌파 → 매수
       - Price가 TEMA 하향 돌파 → 매도
    
    3. 기울기:
       - TEMA 상승: 상승 추세 강화
       - TEMA 하락: 하락 추세 강화
       - TEMA 평평: 추세 없음
    
    4. 이중 TEMA:
       - TEMA(12)와 TEMA(26) 사용
       - 골든크로스/데드크로스
    
    Common Use Cases:
    -----------------
    1. 단기 추세 포착:
       - TEMA(9 또는 12) 사용
       - 빠른 진입/청산
       - 데이트레이딩, 스윙트레이딩
    
    2. 중기 추세 추종:
       - TEMA(20 또는 30) 사용
       - 안정적 신호
       - 포지션 트레이딩
    
    3. 이중 TEMA 시스템:
       - 짧은 TEMA: 신호선
       - 긴 TEMA: 추세선
       - 크로스오버로 매매
    
    4. TEMA + 다른 지표:
       - TEMA + RSI: 추세 + 과매수/과매도
       - TEMA + MACD: 이중 확인
       - TEMA + Volume: 거래량 확인
    
    Parameter Tuning:
    -----------------
    - **Short-term (단기)**:
      nday = 9
      → 매우 빠른 반응, 많은 신호
      → 데이트레이딩, 초단타
    
    - **Standard (표준)**:
      nday = 12 (Patrick Mulloy 원본)
      → 균형잡힌 성능
      → 스윙트레이딩
    
    - **Medium-term (중기)**:
      nday = 20
      → 안정적 신호, 적은 잡음
      → 포지션 트레이딩
    
    Comparison with DEMA:
    ---------------------
    DEMA (Double Exponential MA):
    - Formula: 2 × EMA1 - EMA2
    - 지연: TEMA보다 약간 큼
    - 평활: TEMA보다 약간 적음
    
    TEMA (Triple Exponential MA):
    - Formula: 3 × EMA1 - 3 × EMA2 + EMA3
    - 지연: DEMA보다 작음
    - 평활: DEMA보다 높음
    
    일반적으로 TEMA > DEMA (성능)
    
    Implementation Notes:
    ---------------------
    1. EMA 재귀 계산:
       - pandas ewm() 사용
       - adjust=False (정확한 EMA)
    
    2. 3단계 EMA:
       - EMA1 = EMA(Price)
       - EMA2 = EMA(EMA1)
       - EMA3 = EMA(EMA2)
    
    3. 최종 조합:
       - TEMA = 3 × EMA1 - 3 × EMA2 + EMA3
       - 벡터 연산으로 효율적
    
    4. 초기 NaN:
       - 처음 nday-1 개는 NaN
       - EMA 특성상 점진적 수렴
    
    References:
    -----------
    - Patrick Mulloy (1994). "Smoothing Data with Faster Moving Averages"
    - Technical Analysis of Stocks & Commodities, January 1994
    - Standard parameter: nday=12
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> df = calculate_Tema(df, nday=12)
    >>> # TEMA_12 컬럼 생성됨
    >>> 
    >>> # 추세 확인
    >>> df['Trend'] = np.where(df['Value'] > df['TEMA_12'], 'Up', 'Down')
    >>> 
    >>> # 크로스오버 신호
    >>> df['Signal'] = 0
    >>> df.loc[(df['Value'] > df['TEMA_12']) & 
    ...        (df['Value'].shift(1) <= df['TEMA_12'].shift(1)), 'Signal'] = 1  # Buy
    >>> df.loc[(df['Value'] < df['TEMA_12']) & 
    ...        (df['Value'].shift(1) >= df['TEMA_12'].shift(1)), 'Signal'] = -1  # Sell
    >>> 
    >>> # 이중 TEMA
    >>> df = calculate_Tema(df, nday=12)
    >>> df = calculate_Tema(df, nday=26)
    >>> # TEMA(12) > TEMA(26): 상승 신호
    
    See Also:
    ---------
    - calculate_ema: 지수 이동평균 (1차)
    - calculate_Kaufman_Adaptive_Moving_Average: KAMA (적응형)
    - calculate_Smoothed_Moving_Average: SMMA (Wilder's)
    - calculate_vidya: VIDYA (CMO 기반)
    
    Notes:
    ------
    - **Patrick Mulloy 개발** (1994)
    - **표준 파라미터**: nday=12
    - **DEMA와 차이**: TEMA가 더 빠르고 평활
    - **지연 최소화**: EMA의 주요 단점 해결
    - **3중 평활**: 잡음 제거 효과적
    - **추세 추종**: 강한 추세에서 효과적
    - **횡보장 주의**: 잘못된 신호 가능 (EMA와 동일)
    """
    # Step 1: First EMA (가격의 EMA)
    ema1 = df['Value'].ewm(span=nday, adjust=False).mean()
    
    # Step 2: Second EMA (EMA1의 EMA, 더 평활)
    ema2 = ema1.ewm(span=nday, adjust=False).mean()
    
    # Step 3: Third EMA (EMA2의 EMA, 가장 평활)
    ema3 = ema2.ewm(span=nday, adjust=False).mean()
    
    # Step 4: TEMA 계산
    # TEMA = 3 × EMA1 - 3 × EMA2 + EMA3
    # 이 공식은 지연을 제거하면서 평활성을 유지
    df[f"TEMA_{nday}"] = (3 * ema1) - (3 * ema2) + ema3
    
    return df[f"TEMA_{nday}"]

def calculate_vidya(df: pd.DataFrame, nday: int = 9):
    """
    VIDYA (Variable Index Dynamic Average) 계산
    
    VIDYA는 Tushar Chande가 1995년에 개발한 적응형 이동평균으로,
    CMO (Chande Momentum Oscillator)를 사용하여 시장 변동성에 따라
    평활 계수를 동적으로 조정합니다.
    
    Mathematical Formula:
    ---------------------
    1. CMO (Chande Momentum Oscillator) 계산:
       - up_sum = Σ(positive price changes over n periods)
       - down_sum = Σ(absolute negative price changes over n periods)
       - CMO = 100 × (up_sum - down_sum) / (up_sum + down_sum)
       - 범위: -100 ~ +100
    
    2. VIDYA 계산:
       - Alpha = (2 / (n + 1)) × |CMO| / 100
       - VIDYA[i] = Alpha × Price[i] + (1 - Alpha) × VIDYA[i-1]
       - VIDYA[0] = SMA(n)
    
    Working Principle:
    ------------------
    1. 시장 변동성 감지:
       - CMO가 변동성/모멘텀 측정
       - |CMO| 클수록 = 강한 추세
       - |CMO| 작을수록 = 약한 추세/횡보
    
    2. 동적 평활 조정:
       - 강한 추세: Alpha 증가 → 빠른 반응 (가격 추종)
       - 약한 추세: Alpha 감소 → 느린 반응 (잡음 제거)
       - 자동으로 시장 상황에 적응
    
    3. EMA와의 차이:
       EMA:
       - Alpha 고정: 2/(n+1)
       - 모든 상황에서 동일한 반응
       - 단순하고 일관적
       
       VIDYA:
       - Alpha 가변: 0 ~ 2/(n+1)
       - 시장 상황에 따라 반응 조정
       - 추세장: 빠르게 반응
       - 횡보장: 느리게 반응 (whipsaw 감소)
    
    Advantages:
    -----------
    1. 적응성 (Adaptivity):
       - 시장 변동성에 자동 적응
       - 추세/횡보 자동 구분
       - 하나의 지표로 다양한 시장 대응
    
    2. 노이즈 필터링:
       - 횡보장: 낮은 Alpha → 잡음 제거
       - 잘못된 신호 감소
       - 안정적인 추세 추종
    
    3. 추세 민감도:
       - 추세장: 높은 Alpha → 빠른 포착
       - 지연 최소화
       - 추세 전환 신속 감지
    
    Trading Signals:
    ----------------
    1. Trend Following:
       - Price > VIDYA: 상승 추세
       - Price < VIDYA: 하락 추세
       - VIDYA 방향: 추세 확인
    
    2. Crossover:
       - Price crosses above VIDYA: 매수 신호
       - Price crosses below VIDYA: 매도 신호
       - VIDYA가 적응형이므로 신뢰도 높음
    
    3. Support/Resistance:
       - VIDYA가 동적 지지/저항선
       - 추세장: 강한 지지/저항
       - 횡보장: 약한 영향
    
    4. Dual VIDYA:
       - VIDYA(9) vs VIDYA(21) 크로스오버
       - 단기/장기 추세 비교
       - 더 강력한 신호
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터프레임 ('Value' 컬럼 필수)
    nday : int, default=9
        CMO 및 VIDYA 계산 기간
        - Tushar Chande 표준: 9일
        - 짧을수록: 민감, 많은 신호
        - 길수록: 둔감, 적은 신호
    
    Returns:
    --------
    pd.Series
        VIDYA_{nday} 값
        - VIDYA[0:nday-1] = NaN
        - VIDYA[nday-1] = SMA(nday)
        - VIDYA[nday:] = 동적 계산값
    
    Parameter Guidelines:
    ---------------------
    1. nday=9 (표준):
       - Tushar Chande 권장
       - 단기 트레이딩
       - 빠른 적응
    
    2. nday=14:
       - 중기 트레이딩
       - RSI와 동일 기간
       - 균형잡힌 반응
    
    3. nday=21:
       - 장기 트레이딩
       - 안정적인 추세
       - 노이즈 최소화
    
    4. Dual VIDYA:
       - Short: nday=5 or 9
       - Long: nday=14 or 21
       - 크로스오버 전략
    
    Implementation Details:
    -----------------------
    1. CMO 계산 (n일 기간):
       ```python
       up_sum = 0
       down_sum = 0
       for each day in period:
           change = price[i] - price[i-1]
           if change > 0:
               up_sum += change
           elif change < 0:
               down_sum += abs(change)
       
       CMO = 100 × (up_sum - down_sum) / (up_sum + down_sum)
       ```
    
    2. Alpha 동적 조정:
       ```python
       base_alpha = 2 / (nday + 1)  # EMA의 Alpha
       vi = |CMO| / 100  # Volatility Index (0~1)
       alpha = base_alpha × vi
       ```
    
    3. VIDYA 업데이트:
       ```python
       VIDYA[i] = alpha × Price[i] + (1 - alpha) × VIDYA[i-1]
       ```
    
    Comparison with Other Adaptive MAs:
    -----------------------------------
    1. VIDYA:
       - 기반: CMO (모멘텀)
       - 적응: 변동성
       - 특징: 추세/횡보 구분 우수
    
    2. KAMA:
       - 기반: Efficiency Ratio
       - 적응: 방향성
       - 특징: 노이즈 필터링 우수
    
    3. MAMA:
       - 기반: Hilbert Transform
       - 적응: 주기
       - 특징: 사이클 감지 우수
    
    4. ZLEMA:
       - 기반: 지연 보정
       - 적응: 없음 (고정)
       - 특징: 지연 제거 우수
    
    → VIDYA: 모멘텀 기반, 추세 추종에 최적
    → KAMA: 효율성 기반, 노이즈 제거에 최적
    
    Use Cases:
    ----------
    1. 추세 추종 시스템:
       - VIDYA를 주 추세 지표로 사용
       - Price-VIDYA 크로스오버
       - 적응형 동작으로 다양한 시장 대응
    
    2. 다중 시간대 분석:
       - VIDYA(9): 단기 추세
       - VIDYA(21): 장기 추세
       - 크로스오버로 매매 타이밍
    
    3. 지지/저항 동적 레벨:
       - VIDYA를 동적 S/R로 사용
       - 추세장: 강한 지지/저항
       - 횡보장: 자동으로 영향 감소
    
    4. 필터 조합:
       - VIDYA + RSI
       - VIDYA + MACD
       - 추세 + 모멘텀 확인
    
    Notes:
    ------
    - 개발자: Tushar Chande
    - 발표: 1995년
    - 출처: "The New Technical Trader"
    - 핵심: CMO 기반 적응형 평활
    - 장점: 추세/횡보 자동 구분, 노이즈 필터링
    - 단점: CMO 계산 복잡도, 파라미터 최적화 필요
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> df = calculate_vidya(df, nday=9)
    >>> print(df[['Date', 'Value', 'VIDYA_9']].tail())
    
    >>> # Dual VIDYA 크로스오버
    >>> df = calculate_vidya(df, nday=9)
    >>> df = calculate_vidya(df, nday=21)
    >>> df['Signal'] = df['VIDYA_9'] > df['VIDYA_21']
    
    References:
    -----------
    [1] Tushar Chande (1995), "The New Technical Trader"
    [2] Chande Momentum Oscillator (CMO) 이론
    [3] Adaptive Moving Averages 비교 연구
    """
    values = df['Value'].astype(float).values
    vidya = np.full_like(values, np.nan, dtype=float)
    cmo = np.zeros_like(values, dtype=float)
    n = nday
    base_alpha = 2 / (n + 1)  # EMA의 기본 Alpha
    
    if len(values) < n:
        df[f"VIDYA_{nday}"] = vidya
        return df[f"VIDYA_{nday}"]

    # CMO (Chande Momentum Oscillator) 계산
    # CMO = 100 × (up_sum - down_sum) / (up_sum + down_sum)
    for i in range(n, len(values)):
        up_sum = 0.0
        down_sum = 0.0
        
        # n일 동안의 상승/하락 합계
        for j in range(i - n + 1, i + 1):
            change = values[j] - values[j - 1]
            if change > 0:
                up_sum += change
            elif change < 0:
                down_sum += abs(change)  # 절댓값으로 양수화
        
        total = up_sum + down_sum
        if total != 0:
            cmo[i] = ((up_sum - down_sum) / total) * 100
        else:
            cmo[i] = 0.0

    # VIDYA 계산
    # 초기값: n일 SMA
    vidya[n - 1] = np.mean(values[:n])
    
    # 동적 Alpha를 사용한 지수 평활
    for i in range(n, len(values)):
        # Volatility Index: |CMO| / 100 (0~1 범위)
        vi = abs(cmo[i]) / 100.0
        
        # Alpha 동적 조정: base_alpha × VI
        # VI가 클수록 (강한 추세) → Alpha 증가 → 빠른 반응
        # VI가 작을수록 (약한 추세) → Alpha 감소 → 느린 반응
        alpha = base_alpha * vi
        
        # VIDYA 업데이트
        vidya[i] = alpha * values[i] + (1 - alpha) * vidya[i - 1]

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
    # indicators['Price_Channel_Trend'] = calculate_price_channel_trend(df, nday=20) # Price_Channel_Breakout과 동일 로직
    # indicators['Price_Channel_Strength'] = calculate_price_channel_strength(df, nday=20) # Price_Channel_Index와 유사 로직
    # indicators['Price_Channel_Momentum'] = calculate_price_channel_momentum(df, nday=20) # Price_Channel_Index와 유사 로직
    # indicators['Price_Channel_Volatility'] = calculate_price_channel_volatility(df, nday=20) # ATR과 유사 로직
    # indicators['Price_Channel_Average'] = calculate_price_channel_average(df, nday=20)
    # indicators['Price_Channel_Range'] = calculate_price_channel_range(df, nday=20)
    # indicators['Price_Channel_Width'] = calculate_price_channel_width(df, nday=20)
    # indicators['Price_Channel_Breakdown'] = calculate_price_channel_breakdown(df, nday=20)
    # indicators['Price_Channel_Pullback'] = calculate_price_channel_pullback(df, nday=20)
    # indicators['Price_Channel_Reversal'] = calculate_price_channel_reversal(df, nday=20)
    indicators['Coppock_Curve'] = calculate_coppock_curve(df)
    indicators['Price_Oscillator'] = calculate_price_oscillator(df, short_window=12, long_window=26, percentage=False)
    indicators['Price_Percent_Oscillator'] = calculate_price_oscillator(df, short_window=12, long_window=26, percentage=True)
    indicators['Chaikin_Oscillator'] = calculate_chaikin_oscillator(df)
    indicators['Aroon_Indicator'] = calculate_aroon_indicator(df, nday=14)
    indicators['Money_Flow_Index'] = calculate_money_flow_index(df, nday=14)
    indicators['FI_7'] = calculate_force_index(df, nday=7)
    indicators['FI_13'] = calculate_force_index(df, nday=13)
    indicators['FI_14'] = calculate_force_index(df, nday=14)
    indicators['Ease_of_Movement'] = calculate_ease_of_movement(df, nday=14)
    indicators['VROC_25'] = calculate_volume_rate_of_change(df, nday=25)
    indicators['VROC_7'] = calculate_volume_rate_of_change(df, nday=7)
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
    # indicators['Fibonacci_Retracement_Levels'] = calculate_fibonacci_retracement_levels(df)
    indicators['Pivot_Points'] = calculate_pivot_points(df)
    indicators['TRIX'] = calculate_trix(df, nday=12, signal=9)
    indicators['DMI'] = calculate_dmi(df, nday=14)
    indicators['Sumation_of_OBV'] = calculate_sumation_of_obv(df)
    indicators['Supertrend_Indicator'] = calculate_supertrend_indicator(df, nday=10, multiplier=3.0)
    indicators['Williams_PR'] = calculate_williams_percent_r(df, nday=14)
    indicators['Elder_Ray_Index'] = calculate_elder_ray_index(df, nday=13)
    indicators['Ichimoku_Cloud'] = calculate_ichimoku_cloud(df, conversion=9, base=26, lagging=52, displacement=26)
    indicators['Price_Envelope'] = calculate_price_envelope(df, nday=20, percent=0.02)
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
    indicators['TEMA5'] = calculate_Tema(df, nday=12)
    indicators['TEMA20'] = calculate_Tema(df, nday=26)
    indicators['VIDYA9'] = calculate_vidya(df, nday=9)
    indicators['VIDYA21'] = calculate_vidya(df, nday=21)
 
    return indicators
