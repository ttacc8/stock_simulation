# This file is to simulate trade operations
import pandas as pd

def simulate_SMA_strategy(df: pd.DataFrame, nday: int):
    trade_free_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    
    if len(df) < nday:
        print("Data length is less than nday. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < nday:
            continue
        
        current_price = df.loc[i, 'Value']
        sma_nday = df.loc[i, f'{nday}_SMA']
        
        # Buy signal
        if current_price > sma_nday and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_free_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                
        # Sell signal
        elif current_price < sma_nday and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_free_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                
    # Final portfolio value
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    # print(text_format)
    return final_yield

def simulate_SMA_crossover_strategy(df: pd.DataFrame, short_sma: int, long_sma: int):
    trade_free_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    
    if len(df) < long_sma:
        print("Data length is less than long_window. Cannot simulate strategy.")
        return final_yield
    
    if short_sma >= long_sma:
        print("Error:Short SMA period must be less than Long SMA period.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_sma:
            continue
        
        current_price = df.loc[i, 'Value']
        short_sma_v = df.loc[i, f'{short_sma}_SMA']
        long_sma_v = df.loc[i, f'{long_sma}_SMA']
        
        # Buy signal
        if current_price > short_sma_v and current_price > long_sma_v and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_free_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                
        # Sell signal
        if current_price < short_sma_v and current_price < long_sma_v  and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_free_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"        
    # print(text_format)    
    return final_yield

def simulate_bollinger_strategy(df: pd.DataFrame, nday: int):
    # Placeholder for Bollinger Bands strategy simulation
    trade_free_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    
    # Implement the strategy logic here
    if len(df) < nday:
        print("Data length is less than nday. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < nday:
            continue
        
        current_price = df.loc[i, 'Value']
        bb_upper = df.loc[i, f'{nday}_BB_upper']
        bb_lower = df.loc[i, f'{nday}_BB_lower']
        
        # Buy signal
        if current_price < bb_lower and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_free_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                
        # Sell signal
        elif current_price > bb_upper and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_free_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"        
    # print(text_format)
    return final_yield

def simulate_rsi_strategy(df: pd.DataFrame, rsi_period: int, overbought: int = 70, oversold: int = 30):
    # Placeholder for RSI strategy simulation
    trade_free_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    
    # Implement the strategy logic here
    if len(df) < rsi_period:
        print("Data length is less than rsi_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < rsi_period:
            continue
        
        current_price = df.loc[i, 'Value']
        rsi_value = df.loc[i, f'RSI_{rsi_period}']
        
        # Buy signal
        if rsi_value < oversold and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_free_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                
        # Sell signal
        elif rsi_value > overbought and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_free_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"        
    # print(text_format)
    return final_yield

def simulate_macd_strategy(df: pd.DataFrame, short_period: int = 12, long_period: int = 26, signal_period: int = 9):
    # Placeholder for MACD strategy simulation
    trade_free_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    
    # Implement the strategy logic here
    if len(df) < long_period + signal_period:
        print("Data length is less than required periods. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_period + signal_period:
            continue
        
        current_price = df.loc[i, 'Value']
        macd_value = df.loc[i, 'MACD']
        signal_value = df.loc[i, 'MACD_Signal']
        
        # Buy signal
        if macd_value > signal_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_free_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                
        # Sell signal
        elif macd_value < signal_value and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_free_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"        
    # print(text_format)
    return final_yield

def simulate_stochastic_strategy(df: pd.DataFrame, k_period: int = 14, d_period: int = 3, overbought: int = 80, oversold: int = 20):
    # Placeholder for Stochastic Oscillator strategy simulation
    trade_free_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    
    # Implement the strategy logic here
    if len(df) < k_period + d_period:
        print("Data length is less than required periods. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < k_period + d_period:
            continue
        
        current_price = df.loc[i, 'Value']
        k_value = df.loc[i, f'Stochastic_%K_{k_period}']
        d_value = df.loc[i, f'Stochastic_%D_{d_period}']
        
        # Buy signal
        if k_value < oversold and d_value < oversold and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_free_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                
        # Sell signal
        elif k_value > overbought and d_value > overbought and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_free_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"        
    # print(text_format)
    return final_yield

