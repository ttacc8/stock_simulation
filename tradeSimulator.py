# This file is to simulate trade operations
import pandas as pd
import numpy as np
import os

log_directory = r"C:\Project\PycharmProjects\stock_data\simulation_logs"
temp_directory = os.getcwd()
loss_limit_rate = 0.97  # 3% loss limit

def simulate_special_item_strategy(df: pd.DataFrame, nday: int = 20, file_name: str = ""):
    # Placeholder for special item strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    continue_loss_times = 0
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_SpecialItem{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
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
        # dmi_minus = df.loc[i, '14_DMI_Minus']
        dmi_minus_inclination = df.loc[i, '14_DMI_Minus'] - df.loc[i-1, '14_DMI_Minus']

        # Buy signal
        if current_price < bb_lower and positions != 'BUY':
            if continue_loss_times > 0 and dmi_minus_inclination > 0:
                continue
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                # Calculate trade yield
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif (current_price > bb_upper or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                if current_price < buy_price:
                    continue_loss_times += 1
                else:
                    continue_loss_times = 0
                    
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                    
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(temp_directory,rename_file) , index=False)
    # print(text_format)
    
    return final_yield


def simulate_SMA_strategy(df: pd.DataFrame, nday: int, file_name: str = ""):
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_SMA_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
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
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                # Calculate trade yield
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif (current_price < sma_nday or current_price < loss_limit_price)  and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
    # Final portfolio value
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
    # print(text_format)
    return final_yield

def simulate_SMA_crossover_strategy(df: pd.DataFrame, short_sma: int, long_sma: int, file_name: str = ""):
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_SMA_Crossover_{short_sma}_{long_sma}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
        
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
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                buy_price = current_price
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        if (current_price < short_sma_v and current_price < long_sma_v or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)   
    # print(text_format)    
    return final_yield

# bollinger bands strategy
# 1. BBands 하단선 이하에서 매수, 상단선 이상에서 매도
def simulate_bollinger_strategy(df: pd.DataFrame, nday: int, file_name: str = ""):
    # Placeholder for Bollinger Bands strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_Bollinger_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
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
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                # Calculate trade yield
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif (current_price > bb_upper or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                                   
                
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
    # print(text_format)
    return final_yield

# 2. BB 상단 돌파시 매수 BB Center 이하일 때 매도
def simulate_bollinger_strategy2(df: pd.DataFrame, nday: int, file_name: str = ""):
    # Placeholder for Bollinger Bands strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_Bollinger2_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
    # Implement the strategy logic here
    if len(df) < nday:
        print("Data length is less than nday. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < nday:
            continue
        
        current_price = df.loc[i, 'Value']
        bb_upper = df.loc[i, f'{nday}_BB_upper']
        bb_center = df.loc[i, f'{nday}_SMA']
        bb_lower = df.loc[i, f'{nday}_BB_lower']
        
        # Buy signal
        if current_price > bb_upper and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                # Calculate trade yield
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif (current_price < bb_center or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                                   
                
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
    # print(text_format)
    return final_yield

# 3. 스퀴즈(bb폭이 keltner Band안으로 왔을 때) 상태에서 매수, 20일 하단 에서 매도
def simulate_bollinger_strategy3(df: pd.DataFrame, nday: int, file_name: str = ""):
    # Placeholder for Bollinger Bands strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_Bollinger3_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
    # Implement the strategy logic here
    if len(df) < nday:
        print("Data length is less than nday. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < nday:
            continue
        
        current_price = df.loc[i, 'Value']
        bb_upper = df.loc[i, f'{nday}_BB_upper']
        bb_center = df.loc[i, f'{nday}_SMA']
        bb_lower = df.loc[i, f'{nday}_BB_lower']
        bb_bandwidth = (bb_upper - bb_lower) / bb_center if bb_center != 0 else 0
        keltner_upper = df.loc[i, f'{nday}_KC_upper']
        keltner_lower = df.loc[i, f'{nday}_KC_lower']
        keltner_bandwidth = (keltner_upper - keltner_lower) / bb_center if bb_center != 0 else 0
        
        # Buy signal
        if bb_bandwidth < keltner_bandwidth and current_price > bb_upper and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                # Calculate trade yield
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif (current_price < bb_center or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                                   
                
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
    # print(text_format)
    return final_yield

def simulate_bollinger_strategy4(df: pd.DataFrame, nday: int, file_name: str = ""):
    # Placeholder for Bollinger Bands strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    past_contion = False
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_Bollinger4_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
    # Implement the strategy logic here
    if len(df) < nday:
        print("Data length is less than nday. Cannot simulate strategy.")
        return final_yield
    
    # Strategy logic to be implemented here
    for i in range(len(df)):
        if i < nday:
            continue
        
        current_price = df.loc[i, 'Value']
        bb_lower = df.loc[i, f'{nday}_BB_lower']
        bb_upper = df.loc[i, f'{nday}_BB_upper']
        sma_20day = df.loc[i, '20_SMA']
        sma_5day = df.loc[i, '5_SMA']
        
        # Buy signal
        if current_price < bb_lower and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                # Calculate trade yield
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
        elif positions == 'BUY' and current_price > bb_upper:
            past_contion = True
        elif ((current_price < sma_5day and past_contion) or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                past_contion = False
                loss_limit_price = 0
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
    # print(text_format)
    
    return final_yield

def simulate_rsi_strategy(df: pd.DataFrame, rsi_period: int, overbought: int = 70, oversold: int = 30, file_name: str = ""):
    # Placeholder for RSI strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_RSI_{rsi_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })

    # Implement the strategy logic here
    if len(df) < rsi_period:
        print("Data length is less than rsi_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < rsi_period:
            continue
        
        current_price = df.loc[i, 'Value']
        rsi_value = df.loc[i, f'{rsi_period}_RSI']
        
        # Buy signal
        if rsi_value < oversold and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif (rsi_value > overbought or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)            
    # print(text_format)
    return final_yield

def simulate_macd_strategy(df: pd.DataFrame, short_period: int = 12, long_period: int = 26, signal_period: int = 9, file_name: str = ""):
    # Placeholder for MACD strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_MACD_{short_period}_{long_period}_{signal_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
    # Implement the strategy logic here
    if len(df) < long_period + signal_period:
        print("Data length is less than required periods. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_period + signal_period:
            continue
        
        current_price = df.loc[i, 'Value']
        macd_value = df.loc[i, 'MACD']
        signal_value = df.loc[i, 'MACD_signal']
        
        # Buy signal
        if macd_value > signal_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif (macd_value < signal_value or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"  
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)      
    # print(text_format)
    return final_yield

def simulate_stochastic_strategy(df: pd.DataFrame, k_period: int = 14, d_period: int = 3, overbought: int = 80, oversold: int = 20, file_name: str = ""):
    # Placeholder for Stochastic Oscillator strategy simulation
    trade_fee_rate = 0.002
    seed_money = 1000000  # Initial capital
    cash = seed_money
    stock_qty = 0
    positions = None # Current stock positions : 'BUY' or 'SELL'
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        rename_file = f"{name}_log_Stochastic_{k_period}_{d_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
    
    # Implement the strategy logic here
    if len(df) < k_period + d_period:
        print("Data length is less than required periods. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < k_period + d_period:
            continue
        
        current_price = df.loc[i, 'Value']
        k_value = df.loc[i, '%K']
        d_value = df.loc[i, '%D']
        
        # Buy signal
        if k_value < oversold and d_value < oversold and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                # print(f"Day {df.loc[i,'Date']}: BUY {stock_qty} stocks at {current_price}, Cash left: {cash}")
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate  # 3% loss limit
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                
        # Sell signal
        elif ((k_value > overbought and d_value > overbought) or current_price < loss_limit_price) and positions != 'SELL':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                # print(f"Day {df.loc[i,'Date']}: SELL {stock_qty} stocks at {current_price}, Cash now: {cash}")
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                # Calculate trade yield
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield
                    }])], ignore_index=True)
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100    
    # text_format = f"Final Poertfolio yield: {final_yield:.2f}"        
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
    # print(text_format)
    return final_yield


