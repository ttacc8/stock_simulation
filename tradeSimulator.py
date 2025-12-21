# This file is to simulate trade operations
import pandas as pd
import numpy as np
import os

root_log_directory = r"D:\stock_simulation_log\kospi"
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        bb_upper = df.loc[i, f'BB_upper_{nday}']
        bb_lower = df.loc[i, f'BB_lower_{nday}']
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
        log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
    # print(text_format)
    
    return final_yield


def simulate_sma_strategy(df: pd.DataFrame, nday: int, file_name: str = ""):
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        sma_nday = df.loc[i, f'SMA_{nday}']
        
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

def simulate_sma_crossover_strategy(df: pd.DataFrame, short_sma: int, long_sma: int, file_name: str = ""):
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        short_sma_v = df.loc[i, f'SMA_{short_sma}']
        long_sma_v = df.loc[i, f'SMA_{long_sma}']
        
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

def simulate_ema_crossover_strategy(df: pd.DataFrame, short_ema: int, long_ema: int, file_name: str = ""):
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_EMA_Crossover_{short_ema}_{long_ema}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
        
    if len(df) < long_ema:
        print("Data length is less than long_window. Cannot simulate strategy.")
        return final_yield
    
    if short_ema >= long_ema:
        print("Error:Short EMA period must be less than Long EMA period.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_ema:
            continue
        
        current_price = df.loc[i, 'Value']
        short_ema_v = df.loc[i, f'EMA_{short_ema}']
        long_ema_v = df.loc[i, f'EMA_{long_ema}']
        
        # Buy signal
        if current_price > short_ema_v and current_price > long_ema_v and positions != 'BUY':
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
        if (current_price < short_ema_v and current_price < long_ema_v or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_wma_crossover_strategy(df: pd.DataFrame, short_wma: int, long_wma: int, file_name: str = ""):
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_WMA_Crossover_{short_wma}_{long_wma}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
        
    if len(df) < long_wma:
        print("Data length is less than long_window. Cannot simulate strategy.")
        return final_yield
    
    if short_wma >= long_wma:
        print("Error:Short WMA period must be less than Long WMA period.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_wma:
            continue
        
        current_price = df.loc[i, 'Value']
        short_wma_v = df.loc[i, f'WMA_{short_wma}']
        long_wma_v = df.loc[i, f'WMA_{long_wma}']
        
        # Buy signal
        if current_price > short_wma_v and current_price > long_wma_v and positions != 'BUY':
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
                    log_field.to_csv(os.path.join(log_directory,rename_file) , index=False)
        # Sell signal
        elif (current_price < short_wma_v and current_price < long_wma_v or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_smma_crossover_strategy(df: pd.DataFrame, short_smma: int, long_smma: int, file_name: str = ""):
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_SMMA_Crossover_{short_smma}_{long_smma}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float"
        })
        
    if len(df) < long_smma:
        print("Data length is less than long_window. Cannot simulate strategy.")
        return final_yield
    
    if short_smma >= long_smma:
        print("Error:Short SMMA period must be less than Long SMMA period.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_smma:
            continue
        
        current_price = df.loc[i, 'Value']
        short_smma_v = df.loc[i, f'SMMA_{short_smma}']
        long_smma_v = df.loc[i, f'SMMA_{long_smma}']
        
        # Buy signal
        if current_price > short_smma_v and current_price > long_smma_v and positions != 'BUY':
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
        elif (current_price < short_smma_v and current_price < long_smma_v or current_price < loss_limit_price) and positions != 'SELL':
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        bb_upper = df.loc[i, f'BB_upper_{nday}']
        bb_lower = df.loc[i, f'BB_lower_{nday}']
        
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        bb_upper = df.loc[i, f'BB_upper_{nday}']
        bb_center = df.loc[i, f'SMA_{nday}']
        bb_lower = df.loc[i, f'BB_lower_{nday}']
        
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        bb_upper = df.loc[i, f'BB_upper_{nday}']
        bb_center = df.loc[i, f'SMA_{nday}']
        bb_lower = df.loc[i, f'BB_lower_{nday}']
        bb_bandwidth = (bb_upper - bb_lower) / bb_center if bb_center != 0 else 0
        keltner_upper = df.loc[i, f'KC_upper_{nday}']
        keltner_lower = df.loc[i, f'KC_lower_{nday}']
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        bb_lower = df.loc[i, f'BB_lower_{nday}']
        bb_upper = df.loc[i, f'BB_upper_{nday}']
        sma_20day = df.loc[i, f'SMA_20']
        sma_5day = df.loc[i, f'SMA_5']
        
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        rsi_value = df.loc[i, f'RSI_{rsi_period}']
        
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
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


def simulate_atr_strategy(df: pd.DataFrame, atr_period: int = 14, multiplier: float = 3.0, file_name: str = ""):
    # Placeholder for ATR strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ATR_{atr_period}_{multiplier}{ext}"
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
    if len(df) < atr_period:
        print("Data length is less than atr_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < atr_period:
            continue
        
        current_price = df.loc[i, 'Value']
        atr_value = df.loc[i, f'ATR_{atr_period}']
        upper_band = current_price + (multiplier * atr_value)
        lower_band = current_price - (multiplier * atr_value)
        
        # Buy signal
        if current_price > upper_band and positions != 'BUY':
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
        elif (current_price < lower_band or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_obv_strategy(df: pd.DataFrame, file_name: str = ""):
    # Placeholder for OBV strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_OBV{ext}"
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
    if len(df) < 2:
        print("Data length is less than 2. Cannot simulate strategy.")
        return final_yield
    
    for i in range(1, len(df)):
        current_price = df.loc[i, 'Value']
        prev_obv = df.loc[i-1, 'OBV']
        current_obv = df.loc[i, 'OBV']
        
        # Buy signal
        if current_obv > prev_obv and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_obv < prev_obv or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_cci_strategy(df: pd.DataFrame, cci_period: int = 20, overbought: int = 100, oversold: int = -100, file_name: str = ""):
    # Placeholder for CCI strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_CCI_{cci_period}{ext}"
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
    if len(df) < cci_period:
        print("Data length is less than cci_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < cci_period:
            continue
        
        current_price = df.loc[i, 'Value']
        cci_value = df.loc[i, f'CCI_{cci_period}']
        
        # Buy signal
        if cci_value < oversold and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (cci_value > overbought or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_vwap_strategy(df: pd.DataFrame, file_name: str = ""):
    # Placeholder for VWAP strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_VWAP{ext}"
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
    if len(df) < 1:
        print("Data length is less than 1. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        current_price = df.loc[i, 'Value']
        vwap_value = df.loc[i, 'VWAP']
        
        # Buy signal
        if current_price > vwap_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price < vwap_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_psar_strategy(df: pd.DataFrame, af_start: float = 0.02, af_increment: float = 0.02, af_max: float = 0.2, file_name: str = ""):
    # Placeholder for PSAR strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PSAR_{af_start}_{af_increment}_{af_max}{ext}"
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
    if len(df) < 1:
        print("Data length is less than 1. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        current_price = df.loc[i, 'Value']
        psar_value = df.loc[i, 'PSAR']
        
        # Buy signal
        if current_price > psar_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price < psar_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_momentum_strategy(df: pd.DataFrame, momentum_period: int = 10, file_name: str = ""):
    # Placeholder for Momentum strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Momentum_{momentum_period}{ext}"
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
    if len(df) < momentum_period:
        print("Data length is less than momentum_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < momentum_period:
            continue
        
        current_price = df.loc[i, 'Value']
        momentum_value = df.loc[i, f'Momentum_{momentum_period}']
        
        # Buy signal
        if momentum_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (momentum_value < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_roc_strategy(df: pd.DataFrame, roc_period: int = 12, file_name: str = ""):
    # Placeholder for ROC strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ROC_{roc_period}{ext}"
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
    if len(df) < roc_period:
        print("Data length is less than roc_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < roc_period:
            continue
        
        current_price = df.loc[i, 'Value']
        roc_value = df.loc[i, f'ROC_{roc_period}']
        
        # Buy signal
        if roc_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (roc_value < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_ema_strategy(df: pd.DataFrame, short_period: int = 12, long_period: int = 26, file_name: str = ""):
    # Placeholder for EMA strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_EMA_{short_period}_{long_period}{ext}"
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
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_ema = df.loc[i, f'EMA_{short_period}']
        long_ema = df.loc[i, f'EMA_{long_period}']
        
        # Buy signal
        if short_ema > long_ema and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_ema < long_ema or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_wma_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for WMA strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_WMA_{period}{ext}"
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
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        wma_value = df.loc[i, f'WMA_{period}']
        
        # Buy signal
        if current_price > wma_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price < wma_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_hma_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for HMA strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_HMA_{period}{ext}"
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
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        hma_value = df.loc[i, f'HMA_{period}']
        
        # Buy signal
        if current_price > hma_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price < hma_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_kc_strategy(df: pd.DataFrame, kc_period: int = 20, kc_std_dev: float = 2.0, file_name: str = ""):
    # Placeholder for KC strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_KC_{kc_period}_{kc_std_dev}{ext}"
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
    if len(df) < kc_period:
        print("Data length is less than kc_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < kc_period:
            continue
        
        current_price = df.loc[i, 'Value']
        kc_upper = df.loc[i, f'KC_upper_{kc_period}']
        kc_lower = df.loc[i, f'KC_lower_{kc_period}']
        
        # Buy signal
        if current_price < kc_lower and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price > kc_upper or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_typical_price_crossover_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Typical Price strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_TypicalPrice_{short_period}_{long_period}{ext}"
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
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    short_tp_ma = df["Typical_Price"].rolling(window=short_period).mean()
    long_tp_ma = df["Typical_Price"].rolling(window=long_period).mean()    
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_tp_value = short_tp_ma.loc[i]
        long_tp_value = long_tp_ma.loc[i]
        
        # Buy signal
        if short_tp_value > long_tp_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_tp_value < long_tp_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_weighted_close_price_crossover_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Weighted Close Price strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_WeightedClosePrice_{short_period}_{long_period}{ext}"
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
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    short_wcp_ma = df["Weighted_Close_Price"].rolling(window=short_period).mean()
    long_wcp_ma = df["Weighted_Close_Price"].rolling(window=long_period).mean()
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_wcp_value = short_wcp_ma.loc[i]
        long_wcp_value = long_wcp_ma.loc[i]
        
        # Buy signal
        if short_wcp_value > long_wcp_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_wcp_value < long_wcp_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_volume_trend_strategy(df: pd.DataFrame,  file_name: str = ""):
    pass

def simulate_price_volume_trend_crossover_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Volume Trend strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PVT_{short_period}_{long_period}{ext}"
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
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    short_pvt_ma = df["PVT"].rolling(window=short_period).mean()
    long_pvt_ma = df["PVT"].rolling(window=long_period).mean()
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_pvt_value = short_pvt_ma.loc[i]
        long_pvt_value = long_pvt_ma.loc[i]
        
        # Buy signal
        if short_pvt_value > long_pvt_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_pvt_value < long_pvt_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_vortex_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Vortex strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Vortex_{period}{ext}"
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
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        vortex_plus = df.loc[i, f'Vortex_Pos_{period}']
        vortex_minus = df.loc[i, f'Vortex_Neg_{period}']
        
        # Buy signal
        if vortex_plus > vortex_minus and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (vortex_plus < vortex_minus or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_ultimate_oscillator_strategy(df: pd.DataFrame, short_period: int = 7, mid_period: int = 14, long_period: int = 28, file_name: str = ""):
    # Placeholder for Ultimate Oscillator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_UltimateOscillator_{short_period}_{mid_period}_{long_period}{ext}"
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
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        uo_value = df.loc[i, f'Ultimate_Oscillator_{short_period}_{mid_period}_{long_period}']
        
        # Buy signal
        if uo_value < 30 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (uo_value > 70 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_chande_momentum_oscillator_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Chande Momentum Oscillator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ChandeMomentumOscillator_{period}{ext}"
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
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        cmo_value = df.loc[i, f'CMO_{period}']
        
        # Buy signal
        if cmo_value > 50 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (cmo_value < -50 or current_price < loss_limit_price) and positions != 'SELL':
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
                                                 
def simulate_donchan_channel_strategy(df: pd.DataFrame, period: int = 20, file_name: str = ""):
    # Placeholder for Donchian Channel strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_DonchianChannel_{period}{ext}"
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
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        donchian_upper = df.loc[i, f'DC_upper_{period}']
        donchian_lower = df.loc[i, f'DC_lower_{period}']
        
        # Buy signal
        if current_price > donchian_upper and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price < donchian_lower or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_index_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelIndex_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_tp_ma = df.loc[i, f'TP_MA_{short_period}']
        long_tp_ma = df.loc[i, f'TP_MA_{long_period}']
        
        # Buy signal
        if short_tp_ma > long_tp_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_tp_ma < long_tp_ma or current_price < loss_limit_price) and positions != 'SELL':
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


def simulate_price_channel_breakout_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Breakout strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelBreakout_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_wcp_ma = df.loc[i, f'WCP_MA_{short_period}']
        long_wcp_ma = df.loc[i, f'WCP_MA_{long_period}']
        
        # Buy signal
        if short_wcp_ma > long_wcp_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        #sell signal
        elif (short_wcp_ma < long_wcp_ma or current_price < loss_limit_price) and positions != 'SELL':
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
                    
def simulate_price_channel_trend_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Trend strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelTrend_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_ap_ma = df.loc[i, f'AP_MA_{short_period}']
        long_ap_ma = df.loc[i, f'AP_MA_{long_period}']
        
        # Buy signal
        if short_ap_ma > long_ap_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_ap_ma < long_ap_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_strength_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Strength strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelStrength_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_pvt_ma = df.loc[i, f'PVT_MA_{short_period}']
        long_pvt_ma = df.loc[i, f'PVT_MA_{long_period}']
        
        # Buy signal
        if short_pvt_ma > long_pvt_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_pvt_ma < long_pvt_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_momentum_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Momentum strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelMomentum_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        vortex_plus = df.loc[i, f'Vortex_Plus_{period}']
        vortex_minus = df.loc[i, f'Vortex_Minus_{period}']
        
        # Buy signal
        if vortex_plus > vortex_minus and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (vortex_plus < vortex_minus or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_volatility_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Volatility strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelVolatility_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_atr_ma = df.loc[i, f'ATR_MA_{short_period}']
        long_atr_ma = df.loc[i, f'ATR_MA_{long_period}']
        
        # Buy signal
        if short_atr_ma > long_atr_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_atr_ma < long_atr_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_average_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Average strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelAverage_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_cmo_ma = df.loc[i, f'CMO_MA_{short_period}']
        long_cmo_ma = df.loc[i, f'CMO_MA_{long_period}']
        
        # Buy signal
        if short_cmo_ma > long_cmo_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_cmo_ma < long_cmo_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_range_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Range strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelRange_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        donchian_upper = df.loc[i, f'Donchian_Upper_{period}']
        donchian_lower = df.loc[i, f'Donchian_Lower_{period}']
        
        # Buy signal
        if current_price > donchian_upper and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price < donchian_lower or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_width_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Width strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelWidth_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_tp_ma = df.loc[i, f'TP_MA_{short_period}']
        long_tp_ma = df.loc[i, f'TP_MA_{long_period}']
        
        # Buy signal
        if short_tp_ma > long_tp_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_tp_ma < long_tp_ma or current_price < loss_limit_price) and positions != 'SELL':
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


def simulate_price_channel_breakdown_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Breakdown strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelBreakdown_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_wcp_ma = df.loc[i, f'WCP_MA_{short_period}']
        long_wcp_ma = df.loc[i, f'WCP_MA_{long_period}']
        
        # Buy signal
        if short_wcp_ma > long_wcp_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_wcp_ma < long_wcp_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_pullback_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Rice Channel Pullback strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_RiceChannelPullback_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_ap_ma = df.loc[i, f'AP_MA_{short_period}']
        long_ap_ma = df.loc[i, f'AP_MA_{long_period}']
        
        # Buy signal
        if short_ap_ma > long_ap_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_ap_ma < long_ap_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_channel_reversal_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Price Channel Reversal strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChannelReversal_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_pvt_ma = df.loc[i, f'PVT_MA_{short_period}']
        long_pvt_ma = df.loc[i, f'PVT_MA_{long_period}']
        
        # Buy signal
        if short_pvt_ma > long_pvt_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_pvt_ma < long_pvt_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_coppock_curve_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Coppock Curve strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_CoppockCurve_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        coppock_value = df.loc[i, f'Coppock_Curve']
        
        # Buy signal
        if coppock_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (coppock_value < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_oscillator_strategy(df: pd.DataFrame, short_period: int = 12, long_period: int = 26, file_name: str = ""):
    # Placeholder for Price Oscillator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceOscillator{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        price_oscillator = df.loc[i, f'Price_Oscillator']
        # Buy signal
        if price_oscillator > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (price_oscillator < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_price_chanbdons_strategy(df: pd.DataFrame, period = 20, file_name: str = ""):
    # Placeholder for Price Chanbdons strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PriceChanbdons_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        pcd_upper = df.loc[i, f'PCD_upper_{period}']
        pcd_lower = df.loc[i, f'PCD_lower_{period}']
        
        # Buy signal
        if current_price > pcd_upper and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price < pcd_lower or current_price < loss_limit_price) and positions != 'SELL':
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
      

def simulate_chaikin_oscillator_strategy(df: pd.DataFrame, period: int = 10, file_name: str = ""):
    # Placeholder for Chaikin Oscillator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ChaikinOscillator{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        current_price = df.loc[i, 'Value']
        chaikin_oscillator = df.loc[i, f'Chaikin_Oscillator']
        # Buy signal
        if chaikin_oscillator > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (chaikin_oscillator < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_aroon_indicator_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Aroon Indicator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_AroonIndicator_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        aroon_up = df.loc[i, f'Aroon_Up_{period}']
        aroon_down = df.loc[i, f'Aroon_Down_{period}']
        
        # Buy signal
        if aroon_up > aroon_down and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (aroon_up < aroon_down or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_money_flow_index_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Money Flow Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_MoneyFlowIndex_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        mfi_value = df.loc[i, f'MFI_{period}']
        
        # Buy signal
        if mfi_value < 20 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (mfi_value > 80 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_force_index_strategy(df: pd.DataFrame, period: int = 13, file_name: str = ""):
    # Placeholder for Force Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ForceIndex_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        fi_value = df.loc[i, f'FI_{period}']
        
        # Buy signal
        if fi_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (fi_value < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_force_index_crossover_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Force Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ForceIndex_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_fi_ma = df.loc[i, f'FI_{short_period}']
        long_fi_ma = df.loc[i, f'FI_{long_period}']
        
        # Buy signal
        if short_fi_ma > long_fi_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_fi_ma < long_fi_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_ease_of_movement_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Ease of Movement strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_EaseOfMovement_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        em_value = df.loc[i, f'EOM_{period}']
        
        # Buy signal
        if em_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (em_value < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_volume_rate_of_change_crossover_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Volume Rate of Change strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_VolumeRateOfChange_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_vroc_ma = df.loc[i, f'VROC_{short_period}']
        long_vroc_ma = df.loc[i, f'VROC_{long_period}']
        
        # Buy signal
        if short_vroc_ma > long_vroc_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_vroc_ma < long_vroc_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_money_flow_volume_crossover_strategy(df: pd.DataFrame, short_period: int = 7, long_period: int = 14, file_name: str = ""):
    # Placeholder for Money Flow Volume strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_MoneyFlowVolume_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_mfv_ma = df.loc[i, f'MFV_{short_period}']
        long_mfv_ma = df.loc[i, f'MFV_{long_period}']
        
        # Buy signal
        if short_mfv_ma > long_mfv_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_mfv_ma < long_mfv_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_accumulation_distribution_oscillator_strategy(df: pd.DataFrame, file_name: str = ""):
    # Placeholder for Accumulation/Distribution Oscillator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ADO_{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    for i in range(1, len(df)):
        current_price = df.loc[i, 'Value']
        ado_value = df.loc[i, 'A/D_Oscillator']
        
        # Buy signal
        if ado_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (ado_value < 0 or current_price < loss_limit_price) and positions != 'SELL':
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


def simulate_mass_index_strategy(df: pd.DataFrame, period: int = 25, file_name: str = ""):
    # Placeholder for Mass Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_MassIndex_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        mi_value = df.loc[i, f'Mass_Index']
        
        # Buy signal
        if mi_value < 27 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (mi_value > 30 or current_price < loss_limit_price) and positions != 'SELL':
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
                    
def simulate_intraday_momentum_index_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Intraday Momentum Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_IntradayMomentumIndex_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        imi_value = df.loc[i, f'IMI_{period}']
        
        # Buy signal
        if imi_value < 30 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (imi_value > 70 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_true_strength_index_strategy(df: pd.DataFrame, short_period: int = 13, long_period: int = 25, signal_period: int = 7, file_name: str = ""):
    # Placeholder for True Strength Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_TrueStrengthIndex_{short_period}_{long_period}_{signal_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        current_price = df.loc[i, 'Value']
        tsi_value = df.loc[i, 'TSI']
        signal_value = df.loc[i, 'TSI_signal']
        # Buy signal
        if tsi_value > signal_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (tsi_value < signal_value or current_price < loss_limit_price) and positions != 'SELL':
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
  

def simulate_detrended_price_oscillator_strategy(df: pd.DataFrame, period: int = 20, file_name: str = ""):
    # Placeholder for Detrended Price Oscillator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_DetrendedPriceOscillator_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        dpo_value = df.loc[i, f'DPO_{period}']
        ema5_signal = df.loc[i, 'EMA_5']
        
        # Buy signal
        if dpo_value > ema5_signal and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (dpo_value < 0 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_klinger_oscillator_strategy(df: pd.DataFrame, short_period: int = 34, long_period: int = 55, signal_period: int = 13, file_name: str = ""):
    # Placeholder for Klinger Oscillator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_KlingerOscillator_{short_period}_{long_period}_{signal_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than long_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        klinger_oc_value = df.loc[i, 'Klinger_OC']
        klinger_oc_signal = df.loc[i, 'Klinger_OC_signal']
        
        # Buy signal
        if klinger_oc_value > klinger_oc_signal and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (klinger_oc_value < klinger_oc_signal or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_polirazed_fractal_efficiency_index_strategy(df: pd.DataFrame, windows: int = 10, file_name: str = ""):
    # Placeholder for Polirazed Fractal Efficiency Index strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PolirazedFractalEfficiencyIndex_{windows}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    # Implement the strategy logic here
    if len(df) < windows:
        print("Data length is less than windows. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < windows:
            continue
        
        current_price = df.loc[i, 'Value']
        pfei_value = df.loc[i, f'PFE_{windows}']
        
        # Buy signal
        if pfei_value < -40 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (pfei_value > 40 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_trix_strategy(df: pd.DataFrame, period: int = 12, file_name: str = ""):
    # Placeholder for TRIX strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_TRIX_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    signal_sma9 = df['Value'].rolling(window=9).mean()
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        trix_value = df.loc[i, f'TRIX_{period}']
        signal_value = signal_sma9.loc[i]
        
        # Buy signal
        if trix_value > signal_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (trix_value < signal_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_dmi_stategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for DMI strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_DMI_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    adx_threshold = 25    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        dmi_plus_value = df.loc[i, f'DMI_Plus_{period}']
        dmi_minus_value = df.loc[i, f'DMI_Minus_{period}']
        adx_value = df.loc[i, f'ADX_{period}']
        
        # Buy signal
        if (dmi_plus_value > dmi_minus_value and adx_value > adx_threshold) and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * (1 - loss_limit_rate)  # 3% loss limit
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
        elif (dmi_plus_value < dmi_minus_value or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_williams_percent_range_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # Placeholder for Williams %R strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_WilliamsPercentRange_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        wpr_value = df.loc[i, f'WPR_{period}']
        
        # Buy signal
        if wpr_value < -80 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (wpr_value > -20 or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_elder_ray_strategy(df: pd.DataFrame, period: int = 13, file_name: str = ""):
    # Placeholder for Elder Ray strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ElderRay_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    ema_signal = df['Value'].ewm(span=period, adjust=False).mean()
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        bull_power = df.loc[i, f'ERay_Bull_{period}']
        bull_power_prev = df.loc[i-1, f'ERay_Bull_{period}']
        bear_power = df.loc[i, f'ERay_Bear_{period}']
        bear_power_prev = df.loc[i-1, f'ERay_Bear_{period}']
        ema_signal_value = ema_signal.loc[i]
        ema_signal_prev = ema_signal.loc[i-1]
        
        # Buy signal
        if (bear_power < 0 and (bear_power_prev < bear_power) and (ema_signal_prev < ema_signal_value)) and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif ((bull_power > 0 and (bull_power_prev > bull_power) and (ema_signal_prev > ema_signal_value)) or current_price < loss_limit_price) and positions != 'SELL':
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

# 일목균형표
def simulate_ichimoku_cloud_strategy(df: pd.DataFrame, file_name: str = ""):
    pass

def simulate_envelope_strategy(df: pd.DataFrame, period: int = 20, percent: float = 0.02, file_name: str = ""):
    # Placeholder for Envelope strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Envelope_{period}_{percent}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        ma_value = df.loc[i, f'SMA_{period}']
        upper_band = ma_value * (1 + percent)
        lower_band = ma_value * (1 - percent)
        
        # Buy signal
        if current_price < lower_band and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (current_price > upper_band or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_high_low_oscillator_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # IDea : high값을 BB Upper, low값을 BB Lower로 보고 매수/매도 신호로 활용
    pass

def simulate_alligator_strategy(df: pd.DataFrame, file_name: str = ""):
    # Placeholder for Alligator strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Alligator{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < 21:
        print("Data length is less than 21. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < 21:
            continue
        
        current_price = df.loc[i, 'Value']
        short_ci_ma = df.loc[i, 'SMMA_5']
        long_ci_ma = df.loc[i, 'SMMA_13']
        mid_ci_ma = df.loc[i, 'SMMA_8']
        
        # Buy signal
        if short_ci_ma > mid_ci_ma and mid_ci_ma > long_ci_ma and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_ci_ma < mid_ci_ma and mid_ci_ma < long_ci_ma or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_kaufmans_adaptive_strategy(df: pd.DataFrame, period: int = 10, file_name: str = ""):
    # Placeholder for Kaufman's Adaptive strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_KaufmansAdaptive_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        ka_value = df.loc[i, f'KAMA_{period}']
        
        # Buy signal
        if current_price > ka_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
                        "Trade_Yield": trade_yield,
                    }])], ignore_index=True)
                    
        # Sell signal
        elif (current_price < ka_value or current_price < loss_limit_price) and positions != "SELL":
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
                        "Trade_Yield": trade_yield,
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

def simulate_triple_ema_crossover_strategy(df: pd.DataFrame, short_period: int = 5, long_period: int = 20, file_name: str = ""):
    # Placeholder for Triple EMA strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_TripleEMA_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    # Implement the strategy logic here
    if len(df) < long_period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    for i in range(len(df)):
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        short_tema = df.loc[i, f'TEMA_{short_period}']
        long_tema = df.loc[i, f'TEMA_{long_period}']
        
        # Buy signal
        if short_tema > long_tema and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (short_tema < long_tema or current_price < loss_limit_price) and positions != 'SELL':
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

def simulate_vidya_ma_crossover_strategy(df: pd.DataFrame, vidya_period: int = 9, ma_period: int = 5, file_name: str = ""):
    # Placeholder for VIDYA(Variable Index Dynamic Average) strategy simulation
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
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_VIDYA_{vidya_period}_{ma_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
        
    period = max(vidya_period, ma_period)
        
    # Implement the strategy logic here
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    signal_ma = df['Value'].rolling(window=ma_period).mean()
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        vidya_value = df.loc[i, f'VIDYA_{vidya_period}']
        ma_value = signal_ma.loc[i]
        
        # Buy signal
        if vidya_value > ma_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
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
        elif (vidya_value < ma_value or current_price < loss_limit_price) and positions != 'SELL':
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

                

def simulate_execute_all_strategy(df: pd.DataFrame,  file_name: str = ""):
    results = {}
    results['SMA5']=simulate_sma_strategy(df, nday=5, file_name=file_name)
    results['SMA20']=simulate_sma_strategy(df, nday=20, file_name=file_name)
    results['SMA60']=simulate_sma_strategy(df, nday=60, file_name=file_name)
    results['WMA5']=simulate_wma_strategy(df, period=5, file_name=file_name)
    results['WMA14']=simulate_wma_strategy(df, period=14, file_name=file_name)
    results['WMA20']=simulate_wma_strategy(df, period=20, file_name=file_name)
    results['HMA21']=simulate_hma_strategy(df, period=21, file_name=file_name)
    results['SMA_Crossover_5_20']=simulate_sma_crossover_strategy(df, short_sma=5, long_sma=20, file_name=file_name)
    results['EMA_Crossover_5_20']=simulate_ema_crossover_strategy(df, short_ema=5, long_ema=20, file_name=file_name)
    results['EMA_Crossover_12_26']=simulate_ema_crossover_strategy(df, short_ema=12, long_ema=26, file_name=file_name)
    results['WMA_Crossover_5_20']=simulate_wma_crossover_strategy(df, short_wma=5, long_wma=20, file_name=file_name)
    results['SMMA_Crossover_5_13']=simulate_smma_crossover_strategy(df, short_smma=5, long_smma=13, file_name=file_name)
    results['BB1_20']=simulate_bollinger_strategy(df, nday=20, file_name=file_name)
    results['BB2_20']=simulate_bollinger_strategy2(df, nday=20, file_name=file_name)
    results['BB3_20']=simulate_bollinger_strategy3(df, nday=20, file_name=file_name)
    results['BB4_20']=simulate_bollinger_strategy4(df, nday=20, file_name=file_name)
    results['BB1_30']=simulate_bollinger_strategy(df, nday=30, file_name=file_name)
    results['BB2_30']=simulate_bollinger_strategy2(df, nday=30, file_name=file_name)
    results['BB3_30']=simulate_bollinger_strategy3(df, nday=30, file_name=file_name)
    results['BB4_30']=simulate_bollinger_strategy4(df, nday=30, file_name=file_name)
    results['RSI14']=simulate_rsi_strategy(df, rsi_period=14, file_name=file_name)
    results['MACD_12_16_09']=simulate_macd_strategy(df, short_period=12, long_period=16, signal_period=9, file_name=file_name)
    results['STOCKASTIC_14_3_3']=simulate_stochastic_strategy(df, k_period=14, d_period=3, file_name=file_name)
    results['ATR_14']=simulate_atr_strategy(df, atr_period=14, file_name=file_name)
    results['OBV']=simulate_obv_strategy(df, file_name=file_name)
    results['CCI_20']=simulate_cci_strategy(df, cci_period=20, file_name=file_name)
    # results['VWAP']=simulate_vwap_strategy(df, file_name=file_name) # need more study
    results['PSAR']=simulate_psar_strategy(df, file_name=file_name)
    results['MOMENTUM_10']=simulate_momentum_strategy(df, momentum_period=10, file_name=file_name)
    results['ROC_12']=simulate_roc_strategy(df, roc_period=12, file_name=file_name)
    results['KC_20']=simulate_kc_strategy(df, kc_period=20, file_name=file_name)
    results['Typical_Price_CO_7_14']=simulate_typical_price_crossover_strategy(df, short_period=7, long_period=14 , file_name=file_name)  # need more study
    results['Weighted_Close_Price_CO_7_14']=simulate_weighted_close_price_crossover_strategy(df, short_period=7, long_period=14 , file_name=file_name)  # need more study
    # results['PVT']=simulate_price_volume_trend_strategy(df, file_name=file_name)  # need more study
    results['PVT_CO_7_14'] = simulate_price_volume_trend_crossover_strategy(df, short_period=7, long_period=14, file_name=file_name)
    results['VORTEX_14']=simulate_vortex_strategy(df, period=14, file_name=file_name)
    results['UO_7_14_28']=simulate_ultimate_oscillator_strategy(df, short_period=7, mid_period=14, long_period=28, file_name=file_name)
    results['CMO_14']=simulate_chande_momentum_oscillator_strategy(df, period=14, file_name=file_name)
    results['DON_CH_20']=simulate_donchan_channel_strategy(df, period=20, file_name=file_name)
    # results['PC_INDEX'] = simulate_price_channel_index_strategy(df, short_period=7, long_period=14, file_name=file_name) # need more study
    # results['PC_BREAKOUT'] = simulate_price_channel_breakout_strategy(df, period=20, file_name=file_name) # need more study
    # results['PC_TREND'] = simulate_price_channel_trend_strategy(df, period=20, file_name=file_name) # need more study
    # results['PC_STRANGTH'] = simulate_price_channel_strength_strategy(df, period=20, file_name=file_name) # need more study
    # results['PC_MOMENTUM'] = simulate_price_channel_momentum_strategy(df, period=20, file_name=file_name) # need more study
    # results['PC_VOLATILITY'] = simulate_price_channel_volatility_strategy(df, short_period=7, long_period=14, file_name=file_name) # need more study
    # results['PC_AVERAGE'] = simulate_price_channel_average_strategy(df, short_period=7, long_period=14, file_name=file_name) # need more study
    # results['PC_RANGE'] = simulate_price_channel_range_strategy(df, period=20, file_name=file_name) # need more study
    # results['PC_WIDTH'] = simulate_price_channel_width_strategy # need more study
    # results['PC_BREAKDOWN'] = simulate_price_channel_breakdown_strategy(df, short_period=7, long_period=14, file_name=file_name) # need more study
    # results['PC_PULLBACK'] = simulate_price_channel_pullback_strategy(df, short_period=7, long_period=14, file_name=file_name) # need more study
    # results['PC_REVERSAL'] = simulate_price_channel_reversal_strategy(df, short_period=7, long_period=14, file_name=file_name) # need more study
    results['Coppock_Curve'] = simulate_coppock_curve_strategy(df, file_name=file_name)
    results['Price_Oscillator'] = simulate_price_oscillator_strategy(df, file_name=file_name)
    results['Price_Chanbdons'] = simulate_price_chanbdons_strategy(df, period=20, file_name=file_name)
    results['Chaikin_Oscillator'] = simulate_chaikin_oscillator_strategy(df, file_name=file_name)
    results['Aroon_Indicator'] = simulate_aroon_indicator_strategy(df, period=14, file_name=file_name)
    results['Money_Flow_Index'] = simulate_money_flow_index_strategy(df, period=14, file_name=file_name)
    results['Force_Index_13'] = simulate_force_index_strategy(df, period=13, file_name=file_name)
    results['Force_Index_CO_7_14'] = simulate_force_index_crossover_strategy(df, short_period=7, long_period=14, file_name=file_name)
    results['EOM_14'] = simulate_ease_of_movement_strategy(df, period=14, file_name=file_name)
    results['VROC_CO_7_14'] = simulate_volume_rate_of_change_crossover_strategy(df, short_period=7, long_period=14, file_name=file_name)
    results['MFV_CO_7_14'] = simulate_money_flow_volume_crossover_strategy(df, short_period=7, long_period=14, file_name=file_name)
    results['Accumulation_Distribution_Oscillator'] = simulate_accumulation_distribution_oscillator_strategy(df, file_name=file_name)
    results['Mass_Index_25'] = simulate_mass_index_strategy(df, period=25, file_name=file_name)
    results['Intraday_Momentum_Index_14'] = simulate_intraday_momentum_index_strategy(df, period=14, file_name=file_name)
    results['TSI'] = simulate_true_strength_index_strategy(df, short_period=13, long_period=25, signal_period=7, file_name=file_name)
    results['DPO_20'] = simulate_detrended_price_oscillator_strategy(df, period=20, file_name=file_name)
    results['Klinger_OC'] = simulate_klinger_oscillator_strategy(df, short_period=34, long_period=55, signal_period=13, file_name=file_name)
    results['PFE'] = simulate_polirazed_fractal_efficiency_index_strategy(df, windows=10, file_name=file_name)
    results['TRIX'] = simulate_trix_strategy(df, period=12, file_name=file_name)
    results['DMI_14'] = simulate_dmi_stategy(df, period=14, file_name=file_name)
    results['Williams_%R_14'] = simulate_williams_percent_range_strategy(df, period=14, file_name=file_name)
    results['Elder_Ray_13'] = simulate_elder_ray_strategy(df, period=13, file_name=file_name)
    # results['Ichimoku_Cloud'] = simulate_ichimoku_cloud_strategy(df, file_name=file_name) # need more study
    results['ENVELOPE_20'] = simulate_envelope_strategy(df, period=20, file_name=file_name)
    # results['High_Low_Oscillator_14'] = simulate_high_low_oscillator_strategy(df, period=14, file_name=file_name) # need more study
    results['Alligator'] = simulate_alligator_strategy(df, file_name=file_name)
    results['Kaufmans_Adaptive_10'] = simulate_kaufmans_adaptive_strategy(df, period=10, file_name=file_name)
    results['TEMA_CO_5_20'] = simulate_triple_ema_crossover_strategy(df, short_period=5, long_period=20, file_name=file_name)
    results['VIDYA_MA_9_5'] = simulate_vidya_ma_crossover_strategy(df, vidya_period=9, ma_period=5, file_name=file_name)
    
    return results
    
