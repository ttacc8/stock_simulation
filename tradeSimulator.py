# This file is to simulate trade operations
import pandas as pd
import numpy as np
import os

root_log_directory = r"D:\stock_simulation_log\kosdaq"
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
    """
    Coppock Curve Strategy Implementation
    
    매수 신호 (Buy Signal):
    - Zero Cross: Coppock Curve가 음수에서 양수로 전환 (이전 값 < 0 and 현재 값 >= 0)
    - 장기 상승 추세의 시작을 포착
    
    매도 신호 (Sell Signal):
    - Zero Cross Down: Coppock Curve가 양수에서 음수로 전환 (이전 값 > 0 and 현재 값 <= 0)
    - 또는 3% 손절 도달
    
    주의사항:
    - Coppock Curve는 원래 월봉 데이터용 지표 (일봉에서는 신호가 빈번할 수 있음)
    - 장기 투자 관점에서 사용 권장
    - RSI, MACD 등 다른 지표와 조합 권장
    """
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
    
    # Validate data length
    if len(df) < period + 1:  # Need at least period + 1 for comparison
        print("Data length is less than required period. Cannot simulate strategy.")
        return final_yield
    
    # Check if Coppock_Curve column exists
    if 'Coppock_Curve' not in df.columns:
        print("Error: 'Coppock_Curve' column not found in DataFrame.")
        print("Please calculate Coppock Curve indicator first using calculate_coppock_curve().")
        return final_yield
    
    for i in range(1, len(df)):  # Start from 1 to compare with previous value
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        current_coppock = df.loc[i, 'Coppock_Curve']
        prev_coppock = df.loc[i-1, 'Coppock_Curve']
        
        # Skip if values are NaN
        if pd.isna(current_coppock) or pd.isna(prev_coppock):
            continue
        
        # Buy signal: Zero Cross (음수 → 양수 전환)
        # Coppock Curve의 핵심 매수 신호
        if prev_coppock < 0 and current_coppock >= 0 and positions != 'BUY':
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
        
        # Sell signal 1: Zero Cross Down (양수 → 음수 전환)
        # Sell signal 2: Stop Loss (3% 손절)
        elif positions == 'BUY' and stock_qty > 0:
            should_sell = False
            
            # Zero Cross Down
            if prev_coppock > 0 and current_coppock <= 0:
                should_sell = True
            
            # Stop Loss
            elif current_price < loss_limit_price:
                should_sell = True
            
            if should_sell:
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

def simulate_price_oscillator_strategy(df: pd.DataFrame, short_period: int = 12, long_period: int = 26, signal_period: int = 9, file_name: str = ""):
    """
    Price Oscillator Strategy Implementation
    
    매수 신호 (Buy Signal):
    1. Zero Cross: Price Oscillator가 음수에서 양수로 전환 (상승 모멘텀)
    2. Signal Line Cross: Price Oscillator가 Signal Line을 상향 돌파
    
    매도 신호 (Sell Signal):
    1. Zero Cross Down: Price Oscillator가 양수에서 음수로 전환 (하락 모멘텀)
    2. Signal Line Cross Down: Price Oscillator가 Signal Line을 하향 돌파
    3. 3% 손절
    
    주의사항:
    - MACD와 유사한 지표로 트렌드 추종 전략
    - 횡보장에서는 거짓 신호 발생 가능
    - RSI, 볼린저밴드 등과 조합 권장
    """
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
        rename_file = f"{name}_log_PriceOscillator_{short_period}_{long_period}_{signal_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    
    # Validate data length
    if len(df) < long_period + signal_period:
        print("Data length is less than required period. Cannot simulate strategy.")
        return final_yield
    
    # Check if Price_Oscillator column exists
    if 'Price_Oscillator' not in df.columns and f'APO_{short_period}_{long_period}' not in df.columns:
        print("Error: 'Price_Oscillator' or 'APO' column not found in DataFrame.")
        print("Please calculate Price Oscillator indicator first using calculate_price_oscillator().")
        return final_yield
    
    # Use APO column if exists, otherwise use Price_Oscillator
    po_column = f'APO_{short_period}_{long_period}' if f'APO_{short_period}_{long_period}' in df.columns else 'Price_Oscillator'
    
    # Calculate Signal Line (9-period EMA of Price Oscillator)
    df['PO_Signal'] = df[po_column].ewm(span=signal_period, adjust=False).mean()
    
    for i in range(1, len(df)):  # Start from 1 to compare with previous value
        if i < long_period + signal_period:
            continue
        
        current_price = df.loc[i, 'Value']
        current_po = df.loc[i, po_column]
        prev_po = df.loc[i-1, po_column]
        current_signal = df.loc[i, 'PO_Signal']
        prev_signal = df.loc[i-1, 'PO_Signal']
        
        # Skip if values are NaN
        if pd.isna(current_po) or pd.isna(prev_po) or pd.isna(current_signal) or pd.isna(prev_signal):
            continue
        
        # Buy Signal 1: Zero Cross (음수 → 양수)
        # Buy Signal 2: Signal Line Cross (PO가 Signal Line 상향 돌파)
        buy_signal = False
        
        # Zero Cross
        if prev_po < 0 and current_po >= 0:
            buy_signal = True
        
        # Signal Line Cross (추가 조건)
        elif prev_po < prev_signal and current_po >= current_signal and current_po > 0:
            buy_signal = True
        
        if buy_signal and positions != 'BUY':
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
        
        # Sell Signal
        elif positions == 'BUY' and stock_qty > 0:
            should_sell = False
            
            # Sell Signal 1: Zero Cross Down (양수 → 음수)
            if prev_po > 0 and current_po <= 0:
                should_sell = True
            
            # Sell Signal 2: Signal Line Cross Down (PO가 Signal Line 하향 돌파)
            elif prev_po > prev_signal and current_po <= current_signal:
                should_sell = True
            
            # Sell Signal 3: Stop Loss
            elif current_price < loss_limit_price:
                should_sell = True
            
            if should_sell:
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


def simulate_chaikin_oscillator_strategy(df: pd.DataFrame, short_period: int = 3, long_period: int = 10, file_name: str = ""):
    """
    Chaikin Oscillator Strategy Implementation
    
    매수 신호 (Buy Signal):
    1. Zero Cross Up: Chaikin Oscillator가 음수에서 양수로 전환 (매수 압력 증가)
    2. Divergence: 가격 신저점 + Chaikin 신고점 (강세 다이버전스)
    
    매도 신호 (Sell Signal):
    1. Zero Cross Down: Chaikin Oscillator가 양수에서 음수로 전환 (매도 압력 증가)
    2. Divergence: 가격 신고점 + Chaikin 신저점 (약세 다이버전스)
    3. 3% 손절
    
    주의사항:
    - 거래량 정보가 필수적으로 필요함
    - 다이버전스가 가장 신뢰할 수 있는 신호
    - 횡보장에서는 거짓 신호 발생 가능
    - RSI, MACD 등과 조합 권장
    """
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
        rename_file = f"{name}_log_ChaikinOscillator_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
        })
    
    # Validate data length
    if len(df) < long_period + 1:
        print("Data length is less than required period. Cannot simulate strategy.")
        return final_yield
    
    # Check if Chaikin_Oscillator column exists
    if 'Chaikin_Oscillator' not in df.columns:
        print("Error: 'Chaikin_Oscillator' column not found in DataFrame.")
        print("Please calculate Chaikin Oscillator indicator first using calculate_chaikin_oscillator().")
        return final_yield
    
    for i in range(1, len(df)):  # Start from 1 to compare with previous value
        if i < long_period:
            continue
        
        current_price = df.loc[i, 'Value']
        current_chaikin = df.loc[i, 'Chaikin_Oscillator']
        prev_chaikin = df.loc[i-1, 'Chaikin_Oscillator']
        
        # Skip if values are NaN
        if pd.isna(current_chaikin) or pd.isna(prev_chaikin):
            continue
        
        # Buy Signal: Zero Cross Up (음수 → 양수)
        # 매수 압력이 매도 압력을 넘어서는 시점
        if prev_chaikin < 0 and current_chaikin >= 0 and positions != 'BUY':
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
        
        # Sell Signal
        elif positions == 'BUY' and stock_qty > 0:
            should_sell = False
            
            # Sell Signal 1: Zero Cross Down (양수 → 음수)
            if prev_chaikin > 0 and current_chaikin <= 0:
                should_sell = True
            
            # Sell Signal 2: Stop Loss
            elif current_price < loss_limit_price:
                should_sell = True
            
            if should_sell:
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

def simulate_aroon_indicator_strategy(df: pd.DataFrame, period: int = 25, file_name: str = "", 
                                     buy_threshold: float = 70.0, sell_threshold: float = 70.0):
    """
    Aroon Indicator 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    1. Strong Trend Entry:
       - BUY: Aroon Up > buy_threshold (기본 70) AND Aroon Down < 30
       - 강한 상승 추세 진입 신호
    
    2. Trend Reversal Exit:
       - SELL: Aroon Down > sell_threshold (기본 70) AND Aroon Up < 30
       - 하락 추세로 전환 신호
    
    3. Alternative: Crossover Strategy:
       - BUY: Aroon Up가 Aroon Down을 상향 돌파
       - SELL: Aroon Down이 Aroon Up을 상향 돌파
    
    4. Stop Loss:
       - 매수가 대비 3% 하락 시 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_aroon_indicator 적용 필수)
    period : int, default=25
        Aroon 계산 기간 (14/25/50)
    file_name : str
        로그 파일명 (비어있으면 로그 생성 안 함)
    buy_threshold : float, default=70.0
        매수 임계값 (Aroon Up이 이 값을 넘어야 함)
    sell_threshold : float, default=70.0
        매도 임계값 (Aroon Down이 이 값을 넘으면 매도)
    
    Returns:
    --------
    float
        최종 수익률 (%)
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    required_columns = [f'Aroon_Up_{period}', f'Aroon_Down_{period}']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Column '{col}' not found. Run calculate_aroon_indicator first.")
            return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_AroonIndicator_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "Aroon_Up", "Aroon_Down"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Aroon_Up": "float",
            "Aroon_Down": "float",
        })
    
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    # 이전 Aroon 값 추적 (교차 감지용)
    prev_aroon_up = None
    prev_aroon_down = None
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        aroon_up = df.loc[i, f'Aroon_Up_{period}']
        aroon_down = df.loc[i, f'Aroon_Down_{period}']
        
        # NaN 체크
        if pd.isna(aroon_up) or pd.isna(aroon_down):
            prev_aroon_up = aroon_up
            prev_aroon_down = aroon_down
            continue
        
        # 매수 신호 판단
        # 전략 1: 강한 상승 추세 (Aroon Up > 70, Aroon Down < 30)
        strong_uptrend = (aroon_up > buy_threshold) and (aroon_down < 30)
        
        # 전략 2: Aroon Up이 Aroon Down을 상향 돌파 (교차)
        crossover_up = False
        if prev_aroon_up is not None and prev_aroon_down is not None:
            crossover_up = (prev_aroon_up <= prev_aroon_down) and (aroon_up > aroon_down)
        
        # 매도 신호 판단
        # 전략 1: 강한 하락 추세 (Aroon Down > 70, Aroon Up < 30)
        strong_downtrend = (aroon_down > sell_threshold) and (aroon_up < 30)
        
        # 전략 2: Aroon Down이 Aroon Up을 상향 돌파
        crossover_down = False
        if prev_aroon_up is not None and prev_aroon_down is not None:
            crossover_down = (prev_aroon_down <= prev_aroon_up) and (aroon_down > aroon_up)
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 실행
        if (strong_uptrend or crossover_up) and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Aroon_Up": aroon_up,
                        "Aroon_Down": aroon_down
                    }])], ignore_index=True)
        
        # 매도 실행
        elif (strong_downtrend or crossover_down or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Aroon_Up": aroon_up,
                        "Aroon_Down": aroon_down
                    }])], ignore_index=True)
        
        # 이전 값 업데이트
        prev_aroon_up = aroon_up
        prev_aroon_down = aroon_down
    
    # 최종 포트폴리오 가치
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Aroon_Up": df.loc[len(df)-1, f'Aroon_Up_{period}'],
            "Aroon_Down": df.loc[len(df)-1, f'Aroon_Down_{period}']
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_money_flow_index_strategy(df: pd.DataFrame, period: int = 14, file_name: str = "",
                                      oversold_level: float = 20.0, overbought_level: float = 80.0):
    """
    Money Flow Index (MFI) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    1. Oversold Entry:
       - BUY: MFI < oversold_level (기본 20)
       - 과매도 상태에서 반등 기대
    
    2. Overbought Exit:
       - SELL: MFI > overbought_level (기본 80)
       - 과매수 상태에서 조정 예상
    
    3. Middle Cross Strategy (추가):
       - BUY: MFI가 50을 상향 돌파 (매수 압력 증가)
       - SELL: MFI가 50을 하향 돌파 (매도 압력 증가)
    
    4. Stop Loss:
       - 매수가 대비 3% 하락 시 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_money_flow_index 적용 필수)
    period : int, default=14
        MFI 계산 기간 (7/14/21)
    file_name : str
        로그 파일명 (비어있으면 로그 생성 안 함)
    oversold_level : float, default=20.0
        과매도 임계값 (이 값 이하면 매수)
    overbought_level : float, default=80.0
        과매수 임계값 (이 값 이상이면 매도)
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - MFI는 Volume-weighted RSI로 거래량을 고려
    - 보수적 전략: 10/90 레벨 사용
    - 공격적 전략: 30/70 레벨 사용
    - 다이버전스 감지 시 더 강력한 신호
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    mfi_col = f'MFI_{period}'
    if mfi_col not in df.columns:
        print(f"Error: Column '{mfi_col}' not found. Run calculate_money_flow_index first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_MoneyFlowIndex_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "MFI"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "MFI": "float",
        })
    
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    # 이전 MFI 값 추적 (50 레벨 교차 감지용)
    prev_mfi = None
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        mfi_value = df.loc[i, mfi_col]
        
        # NaN 체크
        if pd.isna(mfi_value):
            prev_mfi = mfi_value
            continue
        
        # 매수 신호 판단
        # 전략 1: 과매도 (MFI < 20)
        oversold_signal = mfi_value < oversold_level
        
        # 전략 2: 50 레벨 상향 돌파 (매수 압력 증가)
        cross_above_50 = False
        if prev_mfi is not None and not pd.isna(prev_mfi):
            cross_above_50 = (prev_mfi <= 50) and (mfi_value > 50)
        
        # 매도 신호 판단
        # 전략 1: 과매수 (MFI > 80)
        overbought_signal = mfi_value > overbought_level
        
        # 전략 2: 50 레벨 하향 돌파 (매도 압력 증가)
        cross_below_50 = False
        if prev_mfi is not None and not pd.isna(prev_mfi):
            cross_below_50 = (prev_mfi >= 50) and (mfi_value < 50)
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 실행
        if (oversold_signal or cross_above_50) and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                
                action_label = "BUY (OVERSOLD)" if oversold_signal else "BUY (50 CROSS)"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "MFI": mfi_value
                    }])], ignore_index=True)
        
        # 매도 실행
        elif (overbought_signal or cross_below_50 or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                if stop_loss:
                    action_label = "SELL (STOP LOSS)"
                elif overbought_signal:
                    action_label = "SELL (OVERBOUGHT)"
                else:
                    action_label = "SELL (50 CROSS)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "MFI": mfi_value
                    }])], ignore_index=True)
        
        # 이전 MFI 값 업데이트
        prev_mfi = mfi_value
    
    # 최종 포트폴리오 가치
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "MFI": df.loc[len(df)-1, mfi_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_force_index_strategy(df: pd.DataFrame, period: int = 13, file_name: str = ""):
    """
    Force Index 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Alexander Elder's approach):
    ----------------------------------------------
    1. Zero Cross Entry:
       - BUY: FI가 음수에서 양수로 전환 (하락 압력 → 상승 압력)
       - 거래량을 동반한 상승 전환 신호
    
    2. Zero Cross Exit:
       - SELL: FI가 양수에서 음수로 전환 (상승 압력 → 하락 압력)
       - 거래량을 동반한 하락 전환 신호
    
    3. Stop Loss:
       - 매수가 대비 3% 하락 시 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_force_index 적용 필수)
    period : int, default=13
        Force Index 계산 기간
        - 2: 단기 (노이즈 많음)
        - 13: 표준 (Elder 권장)
        - 100: 장기 추세
    file_name : str
        로그 파일명 (비어있으면 로그 생성 안 함)
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - Elder는 13-day EMA Force Index 권장
    - Zero cross는 추세 전환 신호
    - 거래량이 많을수록 신호 강도 증가
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    fi_col = f'FI_{period}'
    if fi_col not in df.columns:
        print(f"Error: Column '{fi_col}' not found. Run calculate_force_index first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ForceIndex_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "Force_Index"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Force_Index": "float",
        })
    
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    # 이전 FI 값 추적 (Zero cross 감지용)
    prev_fi = None
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        fi_value = df.loc[i, fi_col]
        
        # NaN 체크
        if pd.isna(fi_value):
            prev_fi = fi_value
            continue
        
        # Zero cross 감지
        cross_above_zero = False
        cross_below_zero = False
        
        if prev_fi is not None and not pd.isna(prev_fi):
            # 음수 → 양수 (상승 압력 증가)
            cross_above_zero = (prev_fi <= 0) and (fi_value > 0)
            # 양수 → 음수 (하락 압력 증가)
            cross_below_zero = (prev_fi >= 0) and (fi_value < 0)
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 실행 (Zero cross up)
        if cross_above_zero and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Force_Index": fi_value
                    }])], ignore_index=True)
        
        # 매도 실행 (Zero cross down OR stop loss)
        elif (cross_below_zero or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Force_Index": fi_value
                    }])], ignore_index=True)
        
        # 이전 FI 값 업데이트
        prev_fi = fi_value
    
    # 최종 포트폴리오 가치
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Force_Index": df.loc[len(df)-1, fi_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
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
    """
    Ease of Movement (EOM) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Richard Arms' approach):
    ----------------------------------------
    1. Zero Cross Entry:
       - BUY: EOM이 음수에서 양수로 전환
       - 적은 거래량으로 상승 시작 (상승이 쉬워짐)
    
    2. Zero Cross Exit:
       - SELL: EOM이 양수에서 음수로 전환
       - 적은 거래량으로 하락 시작 (하락이 쉬워짐)
    
    3. Stop Loss:
       - 매수가 대비 3% 하락 시 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_ease_of_movement 적용 필수)
    period : int, default=14
        EOM 평활화 기간 (7/14/20)
    file_name : str
        로그 파일명 (비어있으면 로그 생성 안 함)
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - EOM > 0: 적은 거래량으로 상승 (매수 압력 강함)
    - EOM < 0: 적은 거래량으로 하락 (매도 압력 강함)
    - Zero cross는 추세 전환의 조기 신호
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    eom_col = f'EOM_{period}'
    if eom_col not in df.columns:
        print(f"Error: Column '{eom_col}' not found. Run calculate_ease_of_movement first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_EaseOfMovement_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "EOM"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "EOM": "float",
        })
    
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    # 이전 EOM 값 추적 (Zero cross 감지용)
    prev_eom = None
    
    for i in range(len(df)):
        if i < period:
            continue
        
        current_price = df.loc[i, 'Value']
        eom_value = df.loc[i, eom_col]
        
        # NaN 체크
        if pd.isna(eom_value):
            prev_eom = eom_value
            continue
        
        # Zero cross 감지
        cross_above_zero = False
        cross_below_zero = False
        
        if prev_eom is not None and not pd.isna(prev_eom):
            # 음수 → 양수 (상승이 쉬워짐)
            cross_above_zero = (prev_eom <= 0) and (eom_value > 0)
            # 양수 → 음수 (하락이 쉬워짐)
            cross_below_zero = (prev_eom >= 0) and (eom_value < 0)
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 실행 (Zero cross up)
        if cross_above_zero and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "EOM": eom_value
                    }])], ignore_index=True)
        
        # 매도 실행 (Zero cross down OR stop loss)
        elif (cross_below_zero or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "EOM": eom_value
                    }])], ignore_index=True)
        
        # 이전 EOM 값 업데이트
        prev_eom = eom_value
    
    # 최종 포트폴리오 가치
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "EOM": df.loc[len(df)-1, eom_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_volume_rate_of_change_strategy(df: pd.DataFrame, period: int = 25, file_name: str = "",
                                            vroc_threshold: float = 0.0):
    """
    Volume Rate of Change (VROC) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    1. Price Confirmation with Volume:
       - BUY: 가격 상승 AND VROC > threshold (거래량 증가로 상승 확증)
       - 거래량 증가를 동반한 상승 추세 진입
    
    2. Volume Decline Exit:
       - SELL: VROC < threshold (거래량 감소로 추세 약화)
       - 또는 가격 하락
    
    3. Stop Loss:
       - 매수가 대비 3% 하락 시 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_volume_rate_of_change 적용 필수)
    period : int, default=25
        VROC 계산 기간 (12/25/50)
    file_name : str
        로그 파일명 (비어있으면 로그 생성 안 함)
    vroc_threshold : float, default=0.0
        VROC 임계값 (이 값 이상이면 거래량 증가로 판단)
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - VROC > 0: 거래량 증가 추세
    - 가격 상승 + 거래량 증가 = 강한 상승 신호
    - 가격과 거래량이 함께 움직일 때 신뢰도 높음
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    vroc_col = f'VROC_{period}'
    if vroc_col not in df.columns:
        print(f"Error: Column '{vroc_col}' not found. Run calculate_volume_rate_of_change first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_VolumeROC_{period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "VROC"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "VROC": "float",
        })
    
    if len(df) < period:
        print("Data length is less than period. Cannot simulate strategy.")
        return final_yield
    
    # 이전 가격 추적 (가격 상승/하락 판단용)
    prev_price = None
    
    for i in range(len(df)):
        if i < period:
            if i > 0:
                prev_price = df.loc[i-1, 'Value']
            continue
        
        current_price = df.loc[i, 'Value']
        vroc_value = df.loc[i, vroc_col]
        
        # NaN 체크
        if pd.isna(vroc_value):
            prev_price = current_price
            continue
        
        # 가격 변화 계산
        price_rising = False
        price_falling = False
        if prev_price is not None:
            price_rising = current_price > prev_price
            price_falling = current_price < prev_price
        
        # 매수 신호: 가격 상승 + 거래량 증가
        volume_increasing = vroc_value > vroc_threshold
        buy_signal = price_rising and volume_increasing
        
        # 매도 신호: 거래량 감소
        volume_decreasing = vroc_value < vroc_threshold
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 실행
        if buy_signal and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "VROC": vroc_value
                    }])], ignore_index=True)
        
        # 매도 실행
        elif (volume_decreasing or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "VROC": vroc_value
                    }])], ignore_index=True)
        
        # 이전 가격 업데이트
        prev_price = current_price
    
    # 최종 포트폴리오 가치
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "VROC": df.loc[len(df)-1, vroc_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
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


def simulate_accumulation_distribution_strategy(df: pd.DataFrame, file_name: str = "", 
                                                lookback_period: int = 20):
    """
    Accumulation/Distribution Line 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Marc Chaikin's approach):
    ------------------------------------------
    1. Trend Following:
       - BUY: A/D Line 상승 추세 (자금 축적, 매수 압력 증가)
       - SELL: A/D Line 하락 추세 (자금 분배, 매도 압력 증가)
    
    2. Divergence Detection:
       - 가격과 A/D Line의 방향 불일치 시 반전 신호
    
    3. Stop Loss:
       - 매수가 대비 3% 하락 시 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_accumulation_distribution 적용 필수)
    file_name : str
        로그 파일명 (비어있으면 로그 생성 안 함)
    lookback_period : int, default=20
        A/D Line 추세 판단 기간
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - A/D Line 상승: 자금 유입 (축적)
    - A/D Line 하락: 자금 유출 (분배)
    - 다이버전스: 가장 강력한 반전 신호
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    if 'A/D_Line' not in df.columns:
        print("Error: Column 'A/D_Line' not found. Run calculate_accumulation_distribution first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_AD_Line{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "AD_Line"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "AD_Line": "float",
        })
    
    if len(df) < lookback_period:
        print("Data length is less than lookback_period. Cannot simulate strategy.")
        return final_yield
    
    for i in range(lookback_period, len(df)):
        current_price = df.loc[i, 'Value']
        current_ad = df.loc[i, 'A/D_Line']
        
        # NaN 체크
        if pd.isna(current_ad):
            continue
        
        # A/D Line 추세 판단 (현재값 vs lookback_period 전 값)
        lookback_idx = i - lookback_period
        if lookback_idx < 0:
            continue
            
        past_ad = df.loc[lookback_idx, 'A/D_Line']
        
        if pd.isna(past_ad):
            continue
        
        # A/D Line 추세
        ad_rising = current_ad > past_ad
        ad_falling = current_ad < past_ad
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 실행 (A/D Line 상승 추세)
        if ad_rising and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "AD_Line": current_ad
                    }])], ignore_index=True)
        
        # 매도 실행 (A/D Line 하락 추세 OR 손절)
        elif (ad_falling or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "AD_Line": current_ad
                    }])], ignore_index=True)
    
    # 최종 포트폴리오 가치
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "AD_Line": df.loc[len(df)-1, 'A/D_Line']
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield


def simulate_accumulation_distribution_oscillator_strategy(df: pd.DataFrame, file_name: str = "", 
                                                           short_window: int = 3, long_window: int = 10):
    """
    Accumulation/Distribution Oscillator (Chaikin Oscillator) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Zero Line Cross):
    ----------------------------------
    1. BUY Signal:
       - ADO > 0 (자금 유입 모멘텀 전환)
       - 매수 압력이 매도 압력 초과
    
    2. SELL Signal:
       - ADO < 0 (자금 유출 모멘텀 전환)
       - 매도 압력이 매수 압력 초과
       - OR 3% 손절
    
    3. Stop Loss:
       - 매수가 대비 3% 하락 시 강제 청산
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_accumulation_distribution_oscillator 적용 필요)
    file_name : str
        로그 파일명 (비어있으면 로그 생성 안 함)
    short_window : int, default=3
        ADO 단기 EMA 기간 (Chaikin 표준)
    long_window : int, default=10
        ADO 장기 EMA 기간 (Chaikin 표준)
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - ADO는 A/D Line의 모멘텀 측정 (MACD + Volume)
    - 0선 돌파: 가장 신뢰할 수 있는 신호
    - 거래량 정보 포함으로 가격 지표보다 신뢰도 높음
    - 중소형주에서 더 효과적
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    if 'A/D_Oscillator' not in df.columns:
        print("Error: Column 'A/D_Oscillator' not found. Run calculate_accumulation_distribution_oscillator first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ADO_{short_window}_{long_window}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "ADO"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "ADO": "float",
        })
    
    for i in range(1, len(df)):
        current_price = df.loc[i, 'Value']
        ado_value = df.loc[i, 'A/D_Oscillator']
        
        # NaN 체크
        if pd.isna(ado_value):
            continue
        
        # 손절 조건 체크
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호 (ADO > 0: 자금 유입 모멘텀)
        if ado_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "ADO": ado_value
                    }])], ignore_index=True)
                    
        # 매도 신호 (ADO < 0: 자금 유출 모멘텀 OR 손절)
        elif (ado_value < 0 or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "ADO": ado_value
                    }])], ignore_index=True)
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "ADO": df.loc[len(df)-1, 'A/D_Oscillator']
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield


def simulate_mass_index_strategy(df: pd.DataFrame, nday: int = 25, ema_period: int = 9, 
                                 bulge_threshold: float = 27.0, signal_threshold: float = 26.5,
                                 trend_period: int = 9, file_name: str = ""):
    """
    Mass Index Reversal Bulge 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Donald Dorsey's Reversal Bulge):
    -------------------------------------------------
    1. Bulge Detection (2-Step Process):
       Step 1: MI > 27.0 (Bulge 형성 - 반전 경고 상태)
       Step 2: MI < 26.5 (Bulge 완료 - 반전 신호 발생)
    
    2. Trend Direction (반전 방향 결정):
       - Bulge 직전 9일 가격 추세 확인
       - 상승 추세였다면 → SELL (하락 반전)
       - 하락 추세였다면 → BUY (상승 반전)
    
    3. Exit:
       - 새로운 Bulge 형성 (MI > 27.0)
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_mass_index 적용 필수)
    nday : int, default=25
        Mass Index 합계 기간 (Dorsey 표준)
    ema_period : int, default=9
        EMA 기간 (Dorsey 표준)
    bulge_threshold : float, default=27.0
        Bulge 시작 임계값 (경고)
    signal_threshold : float, default=26.5
        Bulge 완료 임계값 (신호)
    trend_period : int, default=9
        추세 판단 기간
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - Mass Index는 변동성 기반 반전 지표
    - 27.0 돌파 = 경고, 26.5 하락 = 신호
    - 추세 반전만 포착 (방향은 직전 추세 반대)
    - False Signal 매우 적음
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # Bulge 상태 추적
    in_bulge = False  # MI > 27.0 상태
    bulge_start_idx = -1
    
    # 필수 컬럼 확인
    if 'Mass_Index' not in df.columns:
        print("Error: Column 'Mass_Index' not found. Run calculate_mass_index first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_MassIndex_{nday}_{ema_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "Mass_Index", "Trend"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Mass_Index": "float",
            "Trend": "object",
        })
    
    if len(df) < max(nday, trend_period):
        print(f"Data length is less than required period ({max(nday, trend_period)}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(max(nday, trend_period), len(df)):
        current_price = df.loc[i, 'Value']
        mi_value = df.loc[i, 'Mass_Index']
        
        # NaN 체크
        if pd.isna(mi_value):
            continue
        
        # Bulge 상태 업데이트
        if mi_value > bulge_threshold and not in_bulge:
            # Bulge 시작 (경고 상태)
            in_bulge = True
            bulge_start_idx = i
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # Reversal Signal: Bulge 완료 (MI < 26.5)
        if in_bulge and mi_value < signal_threshold:
            # Bulge 완료 - 반전 신호 발생
            in_bulge = False
            
            # 추세 방향 판단 (Bulge 시작 전 trend_period 동안)
            if bulge_start_idx >= trend_period:
                trend_start_idx = bulge_start_idx - trend_period
                price_before_bulge = df.loc[trend_start_idx, 'Value']
                price_at_bulge = df.loc[bulge_start_idx, 'Value']
                
                was_uptrend = price_at_bulge > price_before_bulge
                was_downtrend = price_at_bulge < price_before_bulge
                
                # 상승 추세였다면 하락 반전 예상 → SELL
                # 하락 추세였다면 상승 반전 예상 → BUY
                
                # BUY Signal (하락→상승 반전)
                if was_downtrend and positions != 'BUY':
                    if cash >= current_price:
                        stock_qty = cash // current_price
                        cash -= stock_qty * current_price * (1 + trade_fee_rate)
                        positions = 'BUY'
                        buy_price = current_price
                        loss_limit_price = buy_price * loss_limit_rate
                        trade_yield = 0
                        if file_name != "":
                            log_field = pd.concat([log_field, pd.DataFrame([{
                                "Date": df.loc[i,'Date'],
                                "Action": "BUY (Reversal)",
                                "Price": current_price,
                                "Quantity": stock_qty,
                                "Cash_After_Trade": cash,
                                "Trade_Yield": trade_yield,
                                "Mass_Index": mi_value,
                                "Trend": "DOWN→UP"
                            }])], ignore_index=True)
                
                # SELL Signal (상승→하락 반전)
                elif was_uptrend and positions == 'BUY':
                    if stock_qty > 0:
                        cash += stock_qty * current_price * (1 - trade_fee_rate)
                        trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                        stock_qty = 0
                        positions = 'SELL'
                        loss_limit_price = 0
                        if file_name != "":
                            log_field = pd.concat([log_field, pd.DataFrame([{
                                "Date": df.loc[i,'Date'],
                                "Action": "SELL (Reversal)",
                                "Price": current_price,
                                "Quantity": 0,
                                "Cash_After_Trade": cash,
                                "Trade_Yield": trade_yield,
                                "Mass_Index": mi_value,
                                "Trend": "UP→DOWN"
                            }])], ignore_index=True)
        
        # 손절 실행
        if stop_loss and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "SELL (STOP LOSS)",
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Mass_Index": mi_value,
                        "Trend": "STOP"
                    }])], ignore_index=True)
        
        # 새로운 Bulge 형성 시 기존 포지션 청산 (선택적)
        # elif mi_value > bulge_threshold and positions == 'BUY':
        #     # 새로운 반전 경고 - 청산
        
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Mass_Index": df.loc[len(df)-1, 'Mass_Index'],
            "Trend": ""
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield
                    
def simulate_intraday_momentum_index_strategy(df: pd.DataFrame, nday: int = 14, 
                                               overbought: float = 70.0, 
                                               oversold: float = 30.0,
                                               file_name: str = ""):
    """
    Intraday Momentum Index (IMI) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Overbought/Oversold):
    --------------------------------------
    1. BUY Signal:
       - IMI < 30 (과매도 - Oversold)
       - 일중 모멘텀이 과도하게 약해진 상태
    
    2. SELL Signal:
       - IMI > 70 (과매수 - Overbought)
       - 일중 모멘텀이 과도하게 강해진 상태
       - OR 3% 손절
    
    3. Stop Loss:
       - 매수가 대비 3% 하락 시 강제 청산
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_intraday_momentum_index 적용 필수)
    nday : int, default=14
        IMI 계산 기간 (Chande 표준)
    overbought : float, default=70.0
        과매수 임계값
    oversold : float, default=30.0
        과매도 임계값
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - IMI는 RSI보다 민감한 단기 지표
    - 일중 모멘텀 측정 (Open vs Close)
    - 갭 영향 없음 (일중만 측정)
    - 단기 트레이딩에 적합
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    imi_col = f'IMI_{nday}'
    if imi_col not in df.columns:
        print(f"Error: Column '{imi_col}' not found. Run calculate_intraday_momentum_index first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_IMI_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "IMI"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "IMI": "float",
        })
    
    if len(df) < nday:
        print(f"Data length is less than period ({nday}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(nday, len(df)):
        current_price = df.loc[i, 'Value']
        imi_value = df.loc[i, imi_col]
        
        # NaN 체크
        if pd.isna(imi_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호 (과매도 - IMI < 30)
        if imi_value < oversold and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY (Oversold)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "IMI": imi_value
                    }])], ignore_index=True)
                    
        # 매도 신호 (과매수 - IMI > 70 OR 손절)
        elif (imi_value > overbought or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL (Overbought)"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "IMI": imi_value
                    }])], ignore_index=True)
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "IMI": df.loc[len(df)-1, imi_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_true_strength_index_strategy(df: pd.DataFrame, long_window: int = 25, short_window: int = 13, 
                                          signal_window: int = 7, file_name: str = ""):
    """
    True Strength Index (TSI) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Dual Strategy):
    --------------------------------
    1. Primary: Zero Line Cross (더 강력한 신호)
       - BUY: TSI > 0 (모멘텀 전환)
       - SELL: TSI < 0 (모멘텀 약화)
    
    2. Secondary: Signal Line Cross (진입 타이밍)
       - BUY Confirmation: TSI > Signal
       - SELL Confirmation: TSI < Signal
    
    3. Combined Signal (가장 안전):
       - BUY: TSI > 0 AND TSI > Signal
       - SELL: TSI < 0 OR TSI < Signal OR 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_true_strength_index 적용 필수)
    long_window : int, default=25
        첫 번째 EMA 기간 (Blau 표준)
    short_window : int, default=13
        두 번째 EMA 기간 (Blau 표준)
    signal_window : int, default=7
        신호선 EMA 기간 (Blau 표준)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - TSI는 이중 스무딩으로 노이즈 최소화
    - 0선 돌파가 가장 신뢰할 수 있는 신호
    - 신호선 교차로 타이밍 정밀화
    - 중단기 트레이딩에 적합
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    if 'TSI' not in df.columns or 'TSI_Signal' not in df.columns:
        print("Error: 'TSI' or 'TSI_Signal' column not found. Run calculate_true_strength_index first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_TSI_{long_window}_{short_window}_{signal_window}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "TSI", "Signal"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "TSI": "float",
            "Signal": "float",
        })
    
    if len(df) < long_window:
        print(f"Data length is less than period ({long_window}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(long_window, len(df)):
        current_price = df.loc[i, 'Value']
        tsi_value = df.loc[i, 'TSI']
        signal_value = df.loc[i, 'TSI_Signal']
        
        # NaN 체크
        if pd.isna(tsi_value) or pd.isna(signal_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호 (TSI > 0 AND TSI > Signal - 강력한 상승 모멘텀)
        if tsi_value > 0 and tsi_value > signal_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "TSI": tsi_value,
                        "Signal": signal_value
                    }])], ignore_index=True)
        
        # 매도 신호 (TSI < 0 OR TSI < Signal OR 손절)
        elif (tsi_value < 0 or tsi_value < signal_value or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                if stop_loss:
                    action_label = "SELL (STOP LOSS)"
                elif tsi_value < 0:
                    action_label = "SELL (Zero Cross)"
                else:
                    action_label = "SELL (Signal Cross)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "TSI": tsi_value,
                        "Signal": signal_value
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "TSI": df.loc[len(df)-1, 'TSI'],
            "Signal": df.loc[len(df)-1, 'TSI_Signal']
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield
  

def simulate_detrended_price_oscillator_strategy(df: pd.DataFrame, nday: int = 20, file_name: str = ""):
    """
    Detrended Price Oscillator (DPO) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Cycle-based):
    ------------------------------
    DPO는 추세 제거 지표로 사이클 분석에 사용됩니다.
    Zero Line Cross를 매매 신호로 활용합니다.
    
    1. BUY Signal:
       - DPO > 0 (가격이 과거 평균보다 높음)
       - 사이클 상승 국면
    
    2. SELL Signal:
       - DPO < 0 (가격이 과거 평균보다 낮음)
       - 사이클 하락 국면
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_dpo 적용 필수)
    nday : int, default=20
        DPO 기간 (일반 표준)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - DPO는 사이클 식별용 지표
    - 추세 시장에서 효과 낮음
    - 횡보/사이클 시장에 적합
    - 다른 추세 지표와 조합 권장
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    dpo_col = f'DPO_{nday}'
    if dpo_col not in df.columns:
        print(f"Error: Column '{dpo_col}' not found. Run calculate_dpo first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_DPO_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "DPO"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "DPO": "float",
        })
    
    # DPO는 shift된 SMA를 사용하므로 충분한 데이터 필요
    required_period = nday + int(nday / 2) + 1
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        dpo_value = df.loc[i, dpo_col]
        
        # NaN 체크
        if pd.isna(dpo_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호 (DPO > 0 - 사이클 상승 국면)
        if dpo_value > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY (Cycle Up)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "DPO": dpo_value
                    }])], ignore_index=True)
        
        # 매도 신호 (DPO < 0 - 사이클 하락 국면 OR 손절)
        elif (dpo_value < 0 or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL (Cycle Down)"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "DPO": dpo_value
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "DPO": df.loc[len(df)-1, dpo_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_klinger_oscillator_strategy(df: pd.DataFrame, short_period: int = 34, long_period: int = 55, signal_period: int = 13, file_name: str = ""):
    """
    Klinger Volume Oscillator (KVO) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Signal Line Cross):
    ------------------------------------
    KVO는 거래량과 가격 추세를 결합한 지표입니다.
    Signal Line Cross를 주 매매 신호로 사용합니다.
    
    1. BUY Signal:
       - KVO > Signal Line (거래량 기반 매수 압력 증가)
       - 상승 모멘텀 강화
    
    2. SELL Signal:
       - KVO < Signal Line (거래량 기반 매도 압력 증가)
       - 하락 모멘텀 강화
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_klinger_oscillator 적용 필수)
    short_period : int, default=34
        단기 EMA 기간 (Klinger 표준)
    long : int, default=55
        장기 EMA 기간 (Klinger 표준)
    signal : int, default=13
        신호선 기간 (Klinger 표준)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - Signal Line Cross는 단기 전환점 포착
    - 거래량 뒷받침 있는 움직임에 반응
    - 추세 확인 지표와 병행 권장
    - Divergence는 고급 전략에서 활용
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    kvo_col = f'KVO_{short_period}_{long_period}'
    signal_col = f'KVO_Signal_{short_period}_{long_period}_{signal_period}'
    
    if kvo_col not in df.columns or signal_col not in df.columns:
        print(f"Error: Required columns not found. Run calculate_klinger_oscillator first.")
        print(f"Expected: {kvo_col}, {signal_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_KVO_{short_period}_{long_period}_{signal_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "KVO", "Signal"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "KVO": "float",
            "Signal": "float",
        })
    
    # KVO 계산에는 충분한 데이터 필요
    required_period = max(long_period, signal_period) + 10
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        kvo_value = df.loc[i, kvo_col]
        signal_value = df.loc[i, signal_col]
        
        # NaN 체크
        if pd.isna(kvo_value) or pd.isna(signal_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호 (KVO > Signal - 매수 압력 우세)
        if kvo_value > signal_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY (KVO > Signal)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "KVO": kvo_value,
                        "Signal": signal_value
                    }])], ignore_index=True)
        
        # 매도 신호 (KVO < Signal - 매도 압력 우세 OR 손절)
        elif (kvo_value < signal_value or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL (KVO < Signal)"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "KVO": kvo_value,
                        "Signal": signal_value
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "KVO": df.loc[len(df)-1, kvo_col],
            "Signal": df.loc[len(df)-1, signal_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_polirazed_fractal_efficiency_index_strategy(df: pd.DataFrame, nday: int = 10, file_name: str = ""):
    """
    Polarized Fractal Efficiency (PFE) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Zero Line Cross + Threshold):
    ----------------------------------------------
    PFE는 추세의 방향과 효율성을 동시에 측정합니다.
    ±50 임계값을 활용한 강한 추세 진입 전략을 사용합니다.
    
    1. BUY Signal:
       - PFE > +50 (강한 상승 추세 + 효율적)
       - 추세 시작 초기 진입
    
    2. SELL Signal:
       - PFE < 0 (추세 전환, 하락 전환)
       - OR PFE < -50 (강한 하락 추세)
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_polarized_fractal_efficiency_index 적용 필수)
    nday : int, default=10
        PFE 기간 (Hans Hannula 표준)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - PFE > +50은 강한 상승 추세 신호
    - PFE 0선 교차는 추세 전환
    - 효율성 높은 추세에서만 진입
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    pfe_col = f'PFE_{nday}'
    if pfe_col not in df.columns:
        print(f"Error: Column '{pfe_col}' not found. Run calculate_polarized_fractal_efficiency_index first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_PFE_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "PFE"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "PFE": "float",
        })
    
    # PFE 계산에 필요한 충분한 데이터
    required_period = nday + 5
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        pfe_value = df.loc[i, pfe_col]
        
        # NaN 체크
        if pd.isna(pfe_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호 (PFE > +50 - 강한 상승 추세)
        if pfe_value > 50 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY (PFE > +50)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "PFE": pfe_value
                    }])], ignore_index=True)
        
        # 매도 신호 (PFE < 0 추세 전환 OR 손절)
        elif (pfe_value < 0 or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL (PFE < 0)"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "PFE": pfe_value
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "PFE": df.loc[len(df)-1, pfe_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_trix_strategy(df: pd.DataFrame, nday: int = 12, signal: int = 9, file_name: str = ""):
    """
    TRIX (Triple Exponential Average) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Signal Line Cross):
    ------------------------------------
    TRIX는 3중 EMA의 변화율로 장기 추세를 측정합니다.
    Signal Line Cross를 주 매매 신호로 사용합니다.
    
    1. BUY Signal:
       - TRIX > Signal Line (상승 모멘텀 강화)
       - 장기 상승 추세 확인
    
    2. SELL Signal:
       - TRIX < Signal Line (하락 모멘텀 강화)
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_trix 적용 필수)
    nday : int, default=12
        TRIX EMA 기간 (Jack Hutson 표준)
    signal : int, default=9
        Signal Line 기간
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - TRIX는 3중 스무딩으로 노이즈 최소화
    - Signal Line Cross는 단기 전환점 포착
    - 장기 추세 전략에 적합
    - 후행 지표이므로 빠른 진입/청산 어려움
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    trix_col = f'TRIX_{nday}'
    signal_col = f'TRIX_Signal_{nday}_{signal}'
    
    if trix_col not in df.columns or signal_col not in df.columns:
        print(f"Error: Required columns not found. Run calculate_trix first.")
        print(f"Expected: {trix_col}, {signal_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_TRIX_{nday}_{signal}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "TRIX", "Signal"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "TRIX": "float",
            "Signal": "float",
        })
    
    # TRIX 계산에 필요한 충분한 데이터
    # 3중 EMA이므로 nday * 3 정도 필요
    required_period = nday * 3 + signal
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        trix_value = df.loc[i, trix_col]
        signal_value = df.loc[i, signal_col]
        
        # NaN 체크
        if pd.isna(trix_value) or pd.isna(signal_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호 (TRIX > Signal - 상승 모멘텀)
        if trix_value > signal_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "BUY (TRIX > Signal)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "TRIX": trix_value,
                        "Signal": signal_value
                    }])], ignore_index=True)
        
        # 매도 신호 (TRIX < Signal - 하락 모멘텀 OR 손절)
        elif (trix_value < signal_value or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else "SELL (TRIX < Signal)"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "TRIX": trix_value,
                        "Signal": signal_value
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "TRIX": df.loc[len(df)-1, trix_col],
            "Signal": df.loc[len(df)-1, signal_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_dmi_stategy(df: pd.DataFrame, nday: int = 14, file_name: str = ""):
    """
    DMI (Directional Movement Index) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    DMI는 +DI, -DI, ADX로 구성되며 추세의 방향과 강도를 동시에 고려합니다.
    
    1. BUY Signal:
       - +DI > -DI (상승 추세)
       - AND ADX > 25 (강한 추세 확인)
       → 강한 상승 추세 진입
    
    2. SELL Signal:
       - +DI < -DI (하락 추세로 전환)
       - OR 3% 손절
    
    ADX Filter:
    -----------
    - ADX > 25: 강한 추세 (매매 적극)
    - ADX < 25: 약한 추세 (매매 보류)
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_dmi 적용 필수)
    nday : int, default=14
        DMI 기간 (Wilder 표준)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - J. Welles Wilder의 표준 전략
    - ADX 필터로 횡보 구간 회피
    - +DI/-DI 교차로 추세 전환 포착
    - 추세 추종 전략에 적합
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    plus_di_col = f'Plus_DI_{nday}'
    minus_di_col = f'Minus_DI_{nday}'
    adx_col = f'ADX_{nday}'
    
    if plus_di_col not in df.columns or minus_di_col not in df.columns or adx_col not in df.columns:
        print(f"Error: Required columns not found. Run calculate_dmi first.")
        print(f"Expected: {plus_di_col}, {minus_di_col}, {adx_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_DMI_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "Plus_DI", "Minus_DI", "ADX"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Plus_DI": "float",
            "Minus_DI": "float",
            "ADX": "float"
        })
    
    # DMI 계산에 필요한 충분한 데이터
    # ADX는 2×nday 정도 필요 (DX의 스무딩)
    required_period = nday * 2
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    adx_threshold = 25  # Wilder's 표준 임계값
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        plus_di_value = df.loc[i, plus_di_col]
        minus_di_value = df.loc[i, minus_di_col]
        adx_value = df.loc[i, adx_col]
        
        # NaN 체크
        if pd.isna(plus_di_value) or pd.isna(minus_di_value) or pd.isna(adx_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호: +DI > -DI AND ADX > 25 (강한 상승 추세)
        if plus_di_value > minus_di_value and adx_value > adx_threshold and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": f"BUY (+DI>{minus_di_value:.1f}, ADX={adx_value:.1f})",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Plus_DI": plus_di_value,
                        "Minus_DI": minus_di_value,
                        "ADX": adx_value
                    }])], ignore_index=True)
        
        # 매도 신호: +DI < -DI (추세 전환) OR 손절
        elif (plus_di_value < minus_di_value or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else f"SELL (+DI<-DI, ADX={adx_value:.1f})"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Plus_DI": plus_di_value,
                        "Minus_DI": minus_di_value,
                        "ADX": adx_value
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Plus_DI": df.loc[len(df)-1, plus_di_col],
            "Minus_DI": df.loc[len(df)-1, minus_di_col],
            "ADX": df.loc[len(df)-1, adx_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_sumation_of_obv_strategy(df: pd.DataFrame, nday: int = 10, use_ema: bool = False, file_name: str = ""):
    """
    SOBV (Summation of OBV) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    SOBV는 OBV의 이동평균으로 장기 자금 흐름을 파악합니다.
    SOBV의 기울기와 방향을 이용한 추세 추종 전략입니다.
    
    1. BUY Signal:
       - SOBV 상승 (현재 > 이전)
       - 장기 자금 유입 확인
    
    2. SELL Signal:
       - SOBV 하락 (현재 < 이전)
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_sumation_of_obv 적용 필수)
    nday : int, default=10
        SOBV 이동평균 기간
    use_ema : bool, default=False
        True: EMA 사용, False: SMA 사용
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - SOBV는 OBV의 스무딩 버전
    - 기울기(방향)가 가장 중요
    - 장기 자금 흐름 파악에 적합
    - Divergence 분석도 중요
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    sobv_col = f'SOBV_EMA_{nday}' if use_ema else f'SOBV_SMA_{nday}'
    
    if sobv_col not in df.columns:
        print(f"Error: Required column not found. Run calculate_sumation_of_obv first.")
        print(f"Expected: {sobv_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        sobv_type = "EMA" if use_ema else "SMA"
        rename_file = f"{name}_log_SOBV_{sobv_type}_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "SOBV", "SOBV_Slope"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "SOBV": "float",
            "SOBV_Slope": "float"
        })
    
    # SOBV 계산에 필요한 충분한 데이터
    required_period = nday + 1  # SOBV + slope 계산
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        sobv_value = df.loc[i, sobv_col]
        sobv_prev = df.loc[i-1, sobv_col]
        
        # NaN 체크
        if pd.isna(sobv_value) or pd.isna(sobv_prev):
            continue
        
        # SOBV 기울기 (방향)
        sobv_slope = sobv_value - sobv_prev
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호: SOBV 상승 (장기 자금 유입)
        if sobv_slope > 0 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": f"BUY (SOBV↑)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "SOBV": sobv_value,
                        "SOBV_Slope": sobv_slope
                    }])], ignore_index=True)
        
        # 매도 신호: SOBV 하락 (장기 자금 유출) OR 손절
        elif (sobv_slope < 0 or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else f"SELL (SOBV↓)"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "SOBV": sobv_value,
                        "SOBV_Slope": sobv_slope
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "SOBV": df.loc[len(df)-1, sobv_col],
            "SOBV_Slope": df.loc[len(df)-1, sobv_col] - df.loc[len(df)-2, sobv_col] if len(df) > 1 else 0
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_supertrend_indicator_strategy(df: pd.DataFrame, nday: int = 10, multiplier: float = 3.0, file_name: str = ""):
    """
    Supertrend Indicator 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    Supertrend는 ATR 기반 동적 지지/저항선으로 추세 전환을 포착합니다.
    Direction 변화를 이용한 명확한 추세 추종 전략입니다.
    
    1. BUY Signal:
       - Direction: -1 → 1 (하락에서 상승으로 전환)
       - 가격이 Supertrend를 상향 돌파
    
    2. SELL Signal:
       - Direction: 1 → -1 (상승에서 하락으로 전환)
       - 가격이 Supertrend를 하향 이탈
    
    3. Stop Loss:
       - Supertrend 자체가 동적 손절선 역할
       - 추가 3% 손절은 사용하지 않음 (Supertrend가 대체)
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_supertrend_indicator 적용 필수)
    nday : int, default=10
        ATR 기간 (Olivier Seban 표준)
    multiplier : float, default=3.0
        ATR 승수
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - Direction 전환이 명확한 매매 신호
    - Supertrend가 트레일링 스탑 역할
    - 추세장에서 매우 효과적
    - 횡보장에서 잦은 전환 발생 (단점)
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    
    # 필수 컬럼 확인
    supertrend_col = f'Supertrend_{nday}_{multiplier}'
    direction_col = f'Supertrend_Direction_{nday}_{multiplier}'
    
    if supertrend_col not in df.columns or direction_col not in df.columns:
        print(f"Error: Required columns not found. Run calculate_supertrend_indicator first.")
        print(f"Expected: {supertrend_col}, {direction_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Supertrend_{nday}_{multiplier}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "Supertrend", "Direction"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Supertrend": "float",
            "Direction": "int64"
        })
    
    # Supertrend 계산에 필요한 충분한 데이터
    required_period = nday + 1
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        direction_current = df.loc[i, direction_col]
        direction_prev = df.loc[i-1, direction_col]
        supertrend_value = df.loc[i, supertrend_col]
        
        # NaN 체크
        if pd.isna(direction_current) or pd.isna(direction_prev) or pd.isna(supertrend_value):
            continue
        
        # 매수 신호: Direction이 -1 → 1 (상승 전환)
        if direction_prev == -1 and direction_current == 1 and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": f"BUY (Direction: -1→1)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Supertrend": supertrend_value,
                        "Direction": int(direction_current)
                    }])], ignore_index=True)
        
        # 매도 신호: Direction이 1 → -1 (하락 전환)
        elif direction_prev == 1 and direction_current == -1 and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": f"SELL (Direction: 1→-1)",
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Supertrend": supertrend_value,
                        "Direction": int(direction_current)
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Supertrend": df.loc[len(df)-1, supertrend_col],
            "Direction": int(df.loc[len(df)-1, direction_col])
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_williams_percent_range_strategy(df: pd.DataFrame, nday: int = 14, file_name: str = ""):
    """
    Williams %R 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    Williams %R은 과매수/과매도 구간을 이용한 역추세 전략입니다.
    0~-100 범위에서 움직이며 극단값에서 반전을 포착합니다.
    
    1. BUY Signal:
       - Williams %R < -80 (과매도 구간)
       - 반등 기대
    
    2. SELL Signal:
       - Williams %R > -20 (과매수 구간)
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_williams_percent_r 적용 필수)
    nday : int, default=14
        Williams %R 계산 기간 (Larry Williams 표준)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - Larry Williams 개발 (1973)
    - Stochastic %K와 역수 관계
    - 과매수/과매도 역추세 전략
    - 추세장에서 손실 가능 (역추세 전략의 한계)
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    wpr_col = f'WPR_{nday}'
    
    if wpr_col not in df.columns:
        print(f"Error: Required column not found. Run calculate_williams_percent_r first.")
        print(f"Expected: {wpr_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_WilliamsPercentR_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", "Trade_Yield", "Williams_%R"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Williams_%R": "float"
        })
    
    # Williams %R 계산에 필요한 충분한 데이터
    required_period = nday
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    # Williams %R 임계값 (Larry Williams 표준)
    oversold_level = -80  # 과매도
    overbought_level = -20  # 과매수
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        wpr_value = df.loc[i, wpr_col]
        
        # NaN 체크
        if pd.isna(wpr_value):
            continue
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호: Williams %R < -80 (과매도)
        if wpr_value < oversold_level and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": f"BUY (Oversold: %R={wpr_value:.1f})",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Williams_%R": wpr_value
                    }])], ignore_index=True)
        
        # 매도 신호: Williams %R > -20 (과매수) OR 손절
        elif (wpr_value > overbought_level or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                stock_qty = 0
                positions = 'SELL'
                loss_limit_price = 0
                
                action_label = "SELL (STOP LOSS)" if stop_loss else f"SELL (Overbought: %R={wpr_value:.1f})"
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": action_label,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Williams_%R": wpr_value
                    }])], ignore_index=True)
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Williams_%R": df.loc[len(df)-1, wpr_col]
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_elder_ray_strategy(df: pd.DataFrame, nday: int = 13, file_name: str = ""):
    """
    Elder-Ray Index 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Elder's Classic Rules):
    ----------------------------------------
    Elder-Ray는 13-EMA를 "컨센서스 가격"으로 보고, 
    Bull Power와 Bear Power로 매수/매도 세력을 측정합니다.
    
    1. BUY Signal (Elder's Classic Long):
       - EMA 상승 추세 (EMA[i] > EMA[i-1])
       - Bear Power < 0 (매도 세력 약화)
       - Bear Power 상승 (Bear Power[i] > Bear Power[i-1])
       → 하락 압력 감소, 상승 전환 신호
    
    2. SELL Signal (Elder's Classic Short 또는 청산):
       - Bull Power > 0 AND Bull Power 하락
       - AND EMA 하락 추세
       → 상승 압력 감소, 하락 전환 신호
       - OR 3% 손절
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_elder_ray_index 적용 필수)
    nday : int, default=13
        EMA 기간 (Alexander Elder 표준)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - Alexander Elder의 Triple Screen Trading System 일부
    - 13-EMA는 "consensus price" (시장 합의 가격)
    - Bull/Bear Power는 High/Low와 EMA 간 괴리
    - EMA 추세와 Bull/Bear Power를 동시 고려
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    bull_col = f'ERay_Bull_{nday}'
    bear_col = f'ERay_Bear_{nday}'
    
    if bull_col not in df.columns or bear_col not in df.columns:
        print(f"Error: Required columns not found. Run calculate_elder_ray_index first.")
        print(f"Expected: {bull_col}, {bear_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_ElderRay_{nday}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", 
                                          "Trade_Yield", "Bull_Power", "Bear_Power", "EMA_Trend"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Bull_Power": "float",
            "Bear_Power": "float",
            "EMA_Trend": "object"
        })
    
    if len(df) < nday + 1:
        print(f"Data length is less than required period ({nday + 1}). Cannot simulate strategy.")
        return final_yield
    
    # EMA 계산 (Elder-Ray의 "consensus price")
    ema_signal = df['Value'].ewm(span=nday, adjust=False).mean()
    
    for i in range(nday + 1, len(df)):
        current_price = df.loc[i, 'Value']
        bull_power = df.loc[i, bull_col]
        bull_power_prev = df.loc[i-1, bull_col]
        bear_power = df.loc[i, bear_col]
        bear_power_prev = df.loc[i-1, bear_col]
        ema_current = ema_signal.loc[i]
        ema_prev = ema_signal.loc[i-1]
        
        # NaN 체크
        if pd.isna(bull_power) or pd.isna(bear_power) or pd.isna(ema_current):
            continue
        
        # EMA 추세 판단
        ema_rising = ema_current > ema_prev
        ema_falling = ema_current < ema_prev
        ema_trend = "상승" if ema_rising else "하락" if ema_falling else "보합"
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호: Elder's Classic Long
        # - EMA 상승 추세
        # - Bear Power < 0 (매도 세력 약화)
        # - Bear Power 상승 (하락 압력 감소)
        if (ema_rising and bear_power < 0 and bear_power > bear_power_prev) and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "매수 (Elder Classic: EMA↑, Bear Power<0 상승)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Bull_Power": bull_power,
                        "Bear_Power": bear_power,
                        "EMA_Trend": ema_trend
                    }])], ignore_index=True)
                    
        # 매도 신호: Elder's Classic Short (또는 청산)
        # - Bull Power > 0 AND Bull Power 하락 (매수 세력 약화)
        # - AND EMA 하락 추세
        # - OR 손절
        elif ((ema_falling and bull_power > 0 and bull_power < bull_power_prev) or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                positions = 'SELL'
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                
                sell_reason = "손절 (3% 손실)" if stop_loss else "매도 (Elder Classic: EMA↓, Bull Power>0 하락)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": sell_reason,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Bull_Power": bull_power,
                        "Bear_Power": bear_power,
                        "EMA_Trend": ema_trend
                    }])], ignore_index=True)
                
                stock_qty = 0
                loss_limit_price = 0
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Bull_Power": df.loc[len(df)-1, bull_col] if bull_col in df.columns else 0,
            "Bear_Power": df.loc[len(df)-1, bear_col] if bear_col in df.columns else 0,
            "EMA_Trend": "상승" if ema_signal.loc[len(df)-1] > ema_signal.loc[len(df)-2] else "하락"
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

# 일목균형표
def simulate_ichimoku_cloud_strategy(df: pd.DataFrame, conversion: int = 9, base: int = 26, 
                                     lagging: int = 52, displacement: int = 26, file_name: str = ""):
    """
    Ichimoku Cloud (일목균형표) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (종합 신호 시스템):
    ------------------------------------
    일목균형표는 5개의 선으로 추세, 모멘텀, 지지/저항을 종합 분석합니다.
    전환선/기준선 크로스와 가격-구름 관계를 주 신호로 사용합니다.
    
    1. BUY Signal (강한 상승 신호):
       - 전환선 > 기준선 (TK Cross 골든크로스)
       - AND 가격 > 구름 (Senkou Span A & B 모두 위)
       - AND 후행스팬 > 과거 가격 (모멘텀 확인)
       → 추세, 지지, 모멘텀 모두 긍정
    
    2. SELL Signal (약세 전환):
       - 전환선 < 기준선 (TK Cross 데드크로스)
       - OR 가격 < 구름 (지지선 이탈)
       - OR 3% 손절
    
    3. Cloud (구름) 역할:
       - 가격 > 구름: 강한 상승 추세
       - 가격 < 구름: 강한 하락 추세
       - 가격 = 구름 안: 횡보/전환 구간 (관망)
    
    4. TK Cross (전환선/기준선 교차):
       - 단기/중기 추세 전환 신호
       - 구름 위에서 발생 시 신뢰도 높음
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_ichimoku_cloud 적용 필수)
    conversion : int, default=9
        전환선(Tenkan-sen) 기간
    base : int, default=26
        기준선(Kijun-sen) 기간
    lagging : int, default=52
        선행스팬B(Senkou Span B) 기간
    displacement : int, default=26
        선행/후행 이동 기간
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - 호소다 고이치(Goichi Hosoda) 개발 (1968)
    - 일본식 종합 분석 시스템
    - TK Cross + Cloud 필터로 신뢰도 향상
    - 후행스팬은 모멘텀 확인용 (선택적 사용)
    - 구름 두께는 지지/저항 강도 의미
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    required_cols = ['Tenkan_Sen', 'Kijun_Sen', 'Senkou_Span_A', 'Senkou_Span_B', 'Chikou_Span']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"Error: Required columns not found. Run calculate_ichimoku_cloud first.")
        print(f"Missing: {missing_cols}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Ichimoku_{conversion}_{base}_{lagging}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", 
                                          "Trade_Yield", "Tenkan", "Kijun", "Cloud_Position", "Chikou_Status"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Tenkan": "float",
            "Kijun": "float",
            "Cloud_Position": "object",
            "Chikou_Status": "object"
        })
    
    # 일목균형표 계산에 필요한 충분한 데이터
    # lagging(52) + displacement(26) 고려
    required_period = max(lagging, base) + displacement
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        tenkan = df.loc[i, 'Tenkan_Sen']
        tenkan_prev = df.loc[i-1, 'Tenkan_Sen']
        kijun = df.loc[i, 'Kijun_Sen']
        kijun_prev = df.loc[i-1, 'Kijun_Sen']
        senkou_a = df.loc[i, 'Senkou_Span_A']
        senkou_b = df.loc[i, 'Senkou_Span_B']
        chikou = df.loc[i, 'Chikou_Span']
        
        # NaN 체크
        if pd.isna(tenkan) or pd.isna(kijun) or pd.isna(senkou_a) or pd.isna(senkou_b):
            continue
        
        # 구름(Cloud) 경계 계산
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        
        # 가격과 구름 관계
        if current_price > cloud_top:
            cloud_position = "위"  # 강세
        elif current_price < cloud_bottom:
            cloud_position = "아래"  # 약세
        else:
            cloud_position = "안"  # 횡보
        
        # 후행스팬 상태 (displacement 기간 전 가격과 비교)
        chikou_idx = i - displacement
        if chikou_idx >= 0 and not pd.isna(chikou):
            past_price = df.loc[chikou_idx, 'Value']
            chikou_status = "강세" if chikou > past_price else "약세" if chikou < past_price else "중립"
        else:
            chikou_status = "N/A"
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호: TK 골든크로스 + 가격이 구름 위 + 후행스팬 강세
        # TK Cross: 전환선이 기준선을 상향 돌파
        tk_golden_cross = (tenkan > kijun) and (tenkan_prev <= kijun_prev)
        price_above_cloud = cloud_position == "위"
        chikou_bullish = chikou_status == "강세"
        
        # 강한 매수 신호: 모든 조건 충족
        strong_buy = tk_golden_cross and price_above_cloud and chikou_bullish
        # 중간 매수 신호: TK Cross + 구름 위 (후행스팬은 선택적)
        medium_buy = tk_golden_cross and price_above_cloud
        
        if medium_buy and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                
                signal_type = "강력 매수" if strong_buy else "매수"
                signal_desc = f"{signal_type} (전환선>{base}선 Cross, 가격>구름"
                if strong_buy:
                    signal_desc += ", 후행스팬 강세"
                signal_desc += ")"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": signal_desc,
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Tenkan": tenkan,
                        "Kijun": kijun,
                        "Cloud_Position": cloud_position,
                        "Chikou_Status": chikou_status
                    }])], ignore_index=True)
                    
        # 매도 신호: TK 데드크로스 OR 가격이 구름 아래 OR 손절
        tk_dead_cross = (tenkan < kijun) and (tenkan_prev >= kijun_prev)
        price_below_cloud = cloud_position == "아래"
        
        if ((tk_dead_cross or price_below_cloud) or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                positions = 'SELL'
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                
                if stop_loss:
                    sell_reason = "손절 (3% 손실)"
                elif tk_dead_cross:
                    sell_reason = "매도 (전환선<기준선 Cross)"
                else:
                    sell_reason = "매도 (가격이 구름 아래 이탈)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": sell_reason,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Tenkan": tenkan,
                        "Kijun": kijun,
                        "Cloud_Position": cloud_position,
                        "Chikou_Status": chikou_status
                    }])], ignore_index=True)
                
                stock_qty = 0
                loss_limit_price = 0
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        final_tenkan = df.loc[len(df)-1, 'Tenkan_Sen']
        final_kijun = df.loc[len(df)-1, 'Kijun_Sen']
        final_senkou_a = df.loc[len(df)-1, 'Senkou_Span_A']
        final_senkou_b = df.loc[len(df)-1, 'Senkou_Span_B']
        final_cloud_top = max(final_senkou_a, final_senkou_b) if not pd.isna(final_senkou_a) else 0
        final_cloud_bottom = min(final_senkou_a, final_senkou_b) if not pd.isna(final_senkou_a) else 0
        final_price = df.loc[len(df)-1, 'Value']
        
        if final_price > final_cloud_top:
            final_cloud_pos = "위"
        elif final_price < final_cloud_bottom:
            final_cloud_pos = "아래"
        else:
            final_cloud_pos = "안"
        
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": final_price,
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Tenkan": final_tenkan if not pd.isna(final_tenkan) else 0,
            "Kijun": final_kijun if not pd.isna(final_kijun) else 0,
            "Cloud_Position": final_cloud_pos,
            "Chikou_Status": "N/A"
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_envelope_strategy(df: pd.DataFrame, nday: int = 20, percent: float = 0.02, file_name: str = ""):
    """
    Price Envelope (가격 봉투선) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Mean Reversion 평균 회귀):
    ------------------------------------------
    Price Envelope는 이동평균을 중심으로 고정 비율만큼 벌어진 밴드를 그려
    과매수/과매도 구간에서 평균 회귀를 노리는 전략입니다.
    
    1. BUY Signal (과매도 반등):
       - 가격 < Lower Band (SMA × (1 - percent))
       - 과매도 구간, 평균으로 회귀 기대
    
    2. SELL Signal (과매수 조정):
       - 가격 > Upper Band (SMA × (1 + percent))
       - OR 3% 손절
       - 과매수 구간, 평균으로 조정 기대
    
    3. 중심선 (SMA):
       - 평균 회귀 기준선
       - 가격이 중심선 근처로 복귀 경향
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (calculate_price_envelope 적용 필수)
    nday : int, default=20
        이동평균 기간 (표준 설정)
    percent : float, default=0.02
        밴드 폭 비율 (0.02 = 2%)
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - 평균 회귀(Mean Reversion) 전략
    - 횡보장에서 효과적
    - 추세장에서 Band Walking 발생 (손실 위험)
    - Bollinger Bands보다 단순하지만 변동성 적응 없음
    - 시간대별 percent 조정 필요:
      * 일봉: 2%
      * 주봉: 10%
      * 1시간봉: 0.8%
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    upper_col = f'Envelope_Upper_{nday}'
    lower_col = f'Envelope_Lower_{nday}'
    
    if upper_col not in df.columns or lower_col not in df.columns:
        print(f"Error: Required columns not found. Run calculate_price_envelope first.")
        print(f"Expected: {upper_col}, {lower_col}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Envelope_{nday}_{percent}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", 
                                          "Trade_Yield", "Upper_Band", "Lower_Band", "Band_Position"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Upper_Band": "float",
            "Lower_Band": "float",
            "Band_Position": "object"
        })
    
    # Price Envelope 계산에 필요한 충분한 데이터
    required_period = nday
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        upper_band = df.loc[i, upper_col]
        lower_band = df.loc[i, lower_col]
        
        # NaN 체크
        if pd.isna(upper_band) or pd.isna(lower_band):
            continue
        
        # 밴드 위치 판단
        if current_price > upper_band:
            band_position = "상단 이탈 (과매수)"
        elif current_price < lower_band:
            band_position = "하단 이탈 (과매도)"
        else:
            band_position = "밴드 내"
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호: 가격 < Lower Band (과매도, 평균 회귀 기대)
        if current_price < lower_band and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "매수 (하단 밴드 이탈, 과매도 반등 기대)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Upper_Band": upper_band,
                        "Lower_Band": lower_band,
                        "Band_Position": band_position
                    }])], ignore_index=True)
                    
        # 매도 신호: 가격 > Upper Band (과매수, 평균 조정 기대) OR 손절
        elif ((current_price > upper_band) or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                positions = 'SELL'
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                
                sell_reason = "손절 (3% 손실)" if stop_loss else "매도 (상단 밴드 이탈, 과매수 조정 기대)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": sell_reason,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Upper_Band": upper_band,
                        "Lower_Band": lower_band,
                        "Band_Position": band_position
                    }])], ignore_index=True)
                
                stock_qty = 0
                loss_limit_price = 0
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        final_upper = df.loc[len(df)-1, upper_col] if upper_col in df.columns else 0
        final_lower = df.loc[len(df)-1, lower_col] if lower_col in df.columns else 0
        final_price = df.loc[len(df)-1, 'Value']
        
        if final_price > final_upper:
            final_position = "상단 이탈"
        elif final_price < final_lower:
            final_position = "하단 이탈"
        else:
            final_position = "밴드 내"
        
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": final_price,
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Upper_Band": final_upper,
            "Lower_Band": final_lower,
            "Band_Position": final_position
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_high_low_oscillator_strategy(df: pd.DataFrame, period: int = 14, file_name: str = ""):
    # IDea : high값을 BB Upper, low값을 BB Lower로 보고 매수/매도 신호로 활용
    pass

def simulate_alligator_strategy(df: pd.DataFrame, jaw_period: int = 13, jaw_shift: int = 8,
                               teeth_period: int = 8, teeth_shift: int = 5,
                               lips_period: int = 5, lips_shift: int = 3, file_name: str = ""):
    """
    Alligator Indicator 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic (Bill Williams' Alligator):
    -------------------------------------------
    Alligator는 3개의 SMMA(Smoothed Moving Average)로 구성되며,
    각각 다른 기간과 shift를 사용하여 추세와 신호를 파악합니다.
    악어(Alligator)의 입이 벌어지고 닫히는 모습에 비유됩니다.
    
    Components (3개 선):
    --------------------
    1. Jaw (턱, 파란선):
       - 13-period SMMA, shifted 8 bars forward
       - 가장 느린 선, 장기 추세
    
    2. Teeth (이빨, 빨간선):
       - 8-period SMMA, shifted 5 bars forward
       - 중간 속도 선, 중기 추세
    
    3. Lips (입술, 녹색선):
       - 5-period SMMA, shifted 3 bars forward
       - 가장 빠른 선, 단기 추세
    
    Trading Signals:
    ----------------
    1. BUY Signal (악어가 입을 벌림 - Alligator Opening):
       - Lips > Teeth > Jaw (모두 상승 정렬)
       - 3개 선이 순차적으로 위로 정렬
       - 강한 상승 추세 시작
    
    2. SELL Signal (악어가 입을 닫음 - Alligator Closing):
       - Lips < Teeth < Jaw (모두 하락 정렬)
       - OR 3% 손절
       - 추세 약화 또는 전환
    
    3. Sleep Mode (악어가 잠 - Alligator Sleeping):
       - 3개 선이 엉켜있음 (횡보)
       - 매매 보류 (추세 없음)
    
    4. Eating (악어가 먹음 - Alligator Eating):
       - Lips > Teeth > Jaw 상태 유지
       - 추세 지속 (보유 유지)
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (SMMA_5, SMMA_8, SMMA_13 필수)
    jaw_period : int, default=13
        Jaw (턱) 기간
    jaw_shift : int, default=8
        Jaw shift (미래 이동)
    teeth_period : int, default=8
        Teeth (이빨) 기간
    teeth_shift : int, default=5
        Teeth shift
    lips_period : int, default=5
        Lips (입술) 기간
    lips_shift : int, default=3
        Lips shift
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Notes:
    ------
    - Bill Williams 개발 (1995)
    - "Trading Chaos" 책에서 소개
    - SMMA = Wilder's Smoothing = RMA
    - Shift는 미래로 이동 (차트상 앞으로)
    - Fractal과 함께 사용 권장 (진입점 확인)
    - Awesome Oscillator와 조합 효과적
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    required_cols = [f'SMMA_{jaw_period}', f'SMMA_{teeth_period}', f'SMMA_{lips_period}']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"Error: Required SMMA columns not found.")
        print(f"Missing: {missing_cols}")
        print(f"Run calculate_Smoothed_Moving_Average for periods: {jaw_period}, {teeth_period}, {lips_period}")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_Alligator_{jaw_period}_{teeth_period}_{lips_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", "Cash_After_Trade", 
                                          "Trade_Yield", "Jaw", "Teeth", "Lips", "Alligator_State"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Jaw": "float",
            "Teeth": "float",
            "Lips": "float",
            "Alligator_State": "object"
        })
    
    # Alligator 계산에 필요한 충분한 데이터
    required_period = max(jaw_period, teeth_period, lips_period) + max(jaw_shift, teeth_shift, lips_shift)
    if len(df) < required_period:
        print(f"Data length is less than required period ({required_period}). Cannot simulate strategy.")
        return final_yield
    
    # Shift 적용 (미래로 이동)
    # Note: 실전에서는 shift된 값을 사용하지만, 백테스팅에서는 현재 값 사용
    jaw = df[f'SMMA_{jaw_period}']
    teeth = df[f'SMMA_{teeth_period}']
    lips = df[f'SMMA_{lips_period}']
    
    for i in range(required_period, len(df)):
        current_price = df.loc[i, 'Value']
        
        # 현재 시점의 Alligator 선 값
        jaw_value = jaw.iloc[i]
        teeth_value = teeth.iloc[i]
        lips_value = lips.iloc[i]
        
        # NaN 체크
        if pd.isna(jaw_value) or pd.isna(teeth_value) or pd.isna(lips_value):
            continue
        
        # Alligator 상태 판단
        if lips_value > teeth_value > jaw_value:
            alligator_state = "Opening (입 벌림 - 상승)"
        elif lips_value < teeth_value < jaw_value:
            alligator_state = "Closing (입 닫힘 - 하락)"
        else:
            alligator_state = "Sleeping (잠 - 횡보)"
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # 매수 신호: Lips > Teeth > Jaw (악어가 입을 벌림 - 상승 추세)
        if (lips_value > teeth_value > jaw_value) and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "매수 (Alligator Opening - Lips>Teeth>Jaw)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Jaw": jaw_value,
                        "Teeth": teeth_value,
                        "Lips": lips_value,
                        "Alligator_State": alligator_state
                    }])], ignore_index=True)
                    
        # 매도 신호: Lips < Teeth < Jaw (악어가 입을 닫음) OR 손절
        elif ((lips_value < teeth_value < jaw_value) or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                positions = 'SELL'
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                
                sell_reason = "손절 (3% 손실)" if stop_loss else "매도 (Alligator Closing - Lips<Teeth<Jaw)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": sell_reason,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Jaw": jaw_value,
                        "Teeth": teeth_value,
                        "Lips": lips_value,
                        "Alligator_State": alligator_state
                    }])], ignore_index=True)
                
                stock_qty = 0
                loss_limit_price = 0
                    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        final_jaw = jaw.iloc[-1] if not pd.isna(jaw.iloc[-1]) else 0
        final_teeth = teeth.iloc[-1] if not pd.isna(teeth.iloc[-1]) else 0
        final_lips = lips.iloc[-1] if not pd.isna(lips.iloc[-1]) else 0
        
        if final_lips > final_teeth > final_jaw:
            final_state = "Opening"
        elif final_lips < final_teeth < final_jaw:
            final_state = "Closing"
        else:
            final_state = "Sleeping"
        
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Jaw": final_jaw,
            "Teeth": final_teeth,
            "Lips": final_lips,
            "Alligator_State": final_state
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory,rename_file), index=False)
    
    return final_yield

def simulate_kaufmans_adaptive_strategy(df: pd.DataFrame, nday: int = 10, 
                                       fast_ema: int = 2, slow_ema: int = 30, 
                                       file_name: str = ""):
    """
    KAMA (Kaufman Adaptive Moving Average) 기반 트레이딩 전략 시뮬레이션
    
    Strategy Logic:
    ---------------
    KAMA는 시장 효율성(Efficiency Ratio)에 따라 민감도가 자동 조절되는
    적응형 이동평균선입니다. 추세장에서는 빠르게 반응하고,
    횡보장에서는 느리게 반응하여 잡음을 필터링합니다.
    
    Trading Signals:
    ----------------
    1. BUY Signal (상향 돌파):
       - Price가 KAMA를 상향 돌파
       - 이전: Price ≤ KAMA
       - 현재: Price > KAMA
       → 상승 추세 시작 신호
    
    2. SELL Signal (하향 돌파 OR 손절):
       - Price가 KAMA를 하향 돌파
       - OR 3% 손절
       → 추세 약화 또는 전환
    
    KAMA Characteristics:
    ---------------------
    - Efficiency Ratio (ER)가 높을 때:
      * 강한 추세 → KAMA가 빠르게 반응
      * 가격을 가까이 추종
    
    - Efficiency Ratio (ER)가 낮을 때:
      * 횡보장 → KAMA가 느리게 반응
      * 잡음 필터링, 평평하게 유지
    
    Advantages:
    -----------
    1. 적응형 민감도:
       - 시장 상태에 자동 조절
       - 추세장: 신속한 진입/청산
       - 횡보장: 잘못된 신호 감소
    
    2. 지연 감소:
       - 전통적 MA보다 빠른 반응
       - Whipsaw (잘못된 신호) 적음
    
    3. 다목적 활용:
       - 추세 확인
       - 동적 지지/저항선
       - 크로스오버 전략
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (KAMA_{nday} 컬럼 필수)
    nday : int, default=10
        KAMA 계산 기간 (Efficiency Ratio)
        - Perry Kaufman 표준: 10일
        - 짧을수록: 빠른 반응 (5~7)
        - 길수록: 느린 반응 (14~20)
    fast_ema : int, default=2
        빠른 EMA 기간 (추세장 민감도)
        - 표준: 2일
    slow_ema : int, default=30
        느린 EMA 기간 (횡보장 민감도)
        - 표준: 30일
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Strategy Variants:
    ------------------
    1. Conservative (안정적):
       - nday=14, fast_ema=2, slow_ema=50
       - 적은 거래, 높은 신뢰도
    
    2. Standard (표준):
       - nday=10, fast_ema=2, slow_ema=30
       - Perry Kaufman 원본
    
    3. Aggressive (적극적):
       - nday=5, fast_ema=2, slow_ema=20
       - 많은 거래, 빠른 반응
    
    Notes:
    ------
    - Perry Kaufman 개발 (1995)
    - "Smarter Trading" 출처
    - ER = |Change| / Volatility
    - SC = [ER × (fastest - slowest) + slowest]²
    - 추세 추종 전략 (Trend Following)
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # KAMA 컬럼 확인
    kama_col = f'KAMA_{nday}'
    if kama_col not in df.columns:
        print(f"Error: {kama_col} column not found in dataframe.")
        print(f"Run calculate_Kaufman_Adaptive_Moving_Average(df, nday={nday}) first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_KAMA_{nday}_{fast_ema}_{slow_ema}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", 
                                          "Cash_After_Trade", "Trade_Yield", 
                                          "KAMA", "Price_vs_KAMA"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "KAMA": "float",
            "Price_vs_KAMA": "object"
        })
    
    if len(df) < nday:
        print(f"Data length is less than {nday}. Cannot simulate strategy.")
        return final_yield
    
    for i in range(nday, len(df)):
        current_price = df.loc[i, 'Value']
        kama_value = df.loc[i, kama_col]
        prev_price = df.loc[i-1, 'Value']
        prev_kama = df.loc[i-1, kama_col]
        
        # NaN 체크
        if pd.isna(kama_value) or pd.isna(prev_kama):
            continue
        
        # Price vs KAMA 상태
        price_vs_kama = "Above" if current_price > kama_value else "Below"
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # BUY Signal: Price가 KAMA 상향 돌파
        if prev_price <= prev_kama and current_price > kama_value and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "매수 (KAMA 상향 돌파)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "KAMA": kama_value,
                        "Price_vs_KAMA": price_vs_kama
                    }])], ignore_index=True)
        
        # SELL Signal: Price가 KAMA 하향 돌파 OR 손절
        elif ((prev_price >= prev_kama and current_price < kama_value) or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                positions = 'SELL'
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                
                sell_reason = "손절 (3% 손실)" if stop_loss else "매도 (KAMA 하향 돌파)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": sell_reason,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "KAMA": kama_value,
                        "Price_vs_KAMA": price_vs_kama
                    }])], ignore_index=True)
                
                stock_qty = 0
                loss_limit_price = 0
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        final_kama = df.loc[len(df)-1, kama_col]
        final_price = df.loc[len(df)-1, 'Value']
        final_status = "Above" if final_price > final_kama else "Below"
        
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": final_price,
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "KAMA": final_kama,
            "Price_vs_KAMA": final_status
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory, rename_file), index=False)
    
    return final_yield

def simulate_triple_ema_crossover_strategy(df: pd.DataFrame, short_period: int = 12, 
                                          long_period: int = 26, file_name: str = ""):
    """
    TEMA (Triple Exponential Moving Average) Crossover Strategy
    
    Strategy Logic:
    ---------------
    TEMA 크로스오버 전략은 두 개의 서로 다른 기간의 TEMA를 사용하여
    골든크로스/데드크로스 신호로 매매합니다. TEMA는 전통적인 EMA보다
    지연이 적어 더 빠른 신호를 제공합니다.
    
    Trading Signals:
    ----------------
    1. BUY Signal (골든크로스):
       - 짧은 TEMA > 긴 TEMA (상향 돌파)
       - 이전: Short TEMA ≤ Long TEMA
       - 현재: Short TEMA > Long TEMA
       → 상승 추세 시작
    
    2. SELL Signal (데드크로스 OR 손절):
       - 짧은 TEMA < 긴 TEMA (하향 돌파)
       - OR 3% 손절
       → 하락 추세 시작 또는 손실 제한
    
    TEMA Advantages:
    ----------------
    1. 낮은 지연:
       - EMA보다 훨씬 빠른 반응
       - 3중 평활로 지연 최소화
       - 추세 전환을 신속히 포착
    
    2. 평활성:
       - 3중 EMA 조합으로 잡음 감소
       - 잘못된 신호 (whipsaw) 적음
       - 안정적인 크로스오버
    
    3. 반응성:
       - 가격 변화에 민감
       - 단기 추세 포착에 유리
       - 스윙트레이딩에 적합
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (TEMA_{short_period}, TEMA_{long_period} 필수)
    short_period : int, default=12
        짧은 TEMA 기간 (신호선)
        - Patrick Mulloy 표준: 12일
        - 빠른 추세 변화 감지
    long_period : int, default=26
        긴 TEMA 기간 (추세선)
        - MACD 기준 26일
        - 장기 추세 확인
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Strategy Variants:
    ------------------
    1. Fast (빠른):
       - short=9, long=21
       - 많은 신호, 높은 민감도
       - 데이트레이딩
    
    2. Standard (표준):
       - short=12, long=26
       - Patrick Mulloy + MACD 기준
       - 스윙트레이딩
    
    3. Slow (느린):
       - short=20, long=50
       - 적은 신호, 높은 신뢰도
       - 포지션 트레이딩
    
    Comparison with EMA Crossover:
    ------------------------------
    EMA Crossover:
    - 신호: 보통 속도
    - 지연: 있음
    - 잡음: 보통
    
    TEMA Crossover:
    - 신호: 빠름
    - 지연: 매우 적음
    - 잡음: 적음
    
    → TEMA가 EMA보다 빠르고 정확
    
    Notes:
    ------
    - Patrick Mulloy 개발 (1994)
    - TEMA = 3 × EMA1 - 3 × EMA2 + EMA3
    - 지연 최소화가 핵심 장점
    - 추세 추종 전략 (Trend Following)
    - 횡보장에서 주의 (잦은 크로스)
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    short_col = f'TEMA_{short_period}'
    long_col = f'TEMA_{long_period}'
    
    if short_col not in df.columns or long_col not in df.columns:
        print(f"Error: Required TEMA columns not found.")
        print(f"Missing: {short_col} and/or {long_col}")
        print(f"Run calculate_Tema(df, {short_period}) and calculate_Tema(df, {long_period}) first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_TEMA_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", 
                                          "Cash_After_Trade", "Trade_Yield",
                                          "Short_TEMA", "Long_TEMA", "Cross_Status"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Short_TEMA": "float",
            "Long_TEMA": "float",
            "Cross_Status": "object"
        })
    
    if len(df) < long_period:
        print(f"Data length is less than {long_period}. Cannot simulate strategy.")
        return final_yield
    
    for i in range(long_period, len(df)):
        current_price = df.loc[i, 'Value']
        short_tema = df.loc[i, short_col]
        long_tema = df.loc[i, long_col]
        prev_short = df.loc[i-1, short_col]
        prev_long = df.loc[i-1, long_col]
        
        # NaN 체크
        if pd.isna(short_tema) or pd.isna(long_tema) or pd.isna(prev_short) or pd.isna(prev_long):
            continue
        
        # 크로스 상태
        cross_status = "Golden" if short_tema > long_tema else "Dead"
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # BUY Signal: 골든크로스 (Short TEMA가 Long TEMA 상향 돌파)
        if prev_short <= prev_long and short_tema > long_tema and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "매수 (골든크로스)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Short_TEMA": short_tema,
                        "Long_TEMA": long_tema,
                        "Cross_Status": cross_status
                    }])], ignore_index=True)
        
        # SELL Signal: 데드크로스 (Short TEMA가 Long TEMA 하향 돌파) OR 손절
        elif ((prev_short >= prev_long and short_tema < long_tema) or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                positions = 'SELL'
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                
                sell_reason = "손절 (3% 손실)" if stop_loss else "매도 (데드크로스)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": sell_reason,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Short_TEMA": short_tema,
                        "Long_TEMA": long_tema,
                        "Cross_Status": cross_status
                    }])], ignore_index=True)
                
                stock_qty = 0
                loss_limit_price = 0
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        final_short = df.loc[len(df)-1, short_col]
        final_long = df.loc[len(df)-1, long_col]
        final_status = "Golden" if final_short > final_long else "Dead"
        
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Short_TEMA": final_short,
            "Long_TEMA": final_long,
            "Cross_Status": final_status
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory, rename_file), index=False)
    
    return final_yield

def simulate_vidya_ma_crossover_strategy(df: pd.DataFrame, short_period: int = 9, 
                                        long_period: int = 21, file_name: str = ""):
    """
    VIDYA (Variable Index Dynamic Average) Dual Crossover Strategy
    
    Strategy Logic (Adaptive Trend Following):
    -------------------------------------------
    VIDYA 듀얼 크로스오버 전략은 두 개의 서로 다른 기간의 VIDYA를 사용하여
    골든크로스/데드크로스 신호로 매매합니다. VIDYA는 CMO 기반 적응형 MA로
    시장 변동성에 따라 자동으로 민감도를 조절합니다.
    
    VIDYA Characteristics (적응형 동작):
    -------------------------------------
    1. 추세장 (High CMO):
       - 높은 Alpha → 빠른 반응
       - 가격을 가까이 추종
       - 신속한 진입/청산
       - 지연 최소화
    
    2. 횡보장 (Low CMO):
       - 낮은 Alpha → 느린 반응
       - 잡음 필터링
       - 잘못된 신호 감소
       - 안정적 유지
    
    3. vs Fixed MA:
       EMA/SMA (고정):
       - 모든 상황에서 동일 반응
       - 추세장: 적절
       - 횡보장: 잦은 whipsaw
       
       VIDYA (적응):
       - 시장 상황에 따라 자동 조절
       - 추세장: 빠른 반응
       - 횡보장: 느린 반응 (whipsaw 감소)
    
    Trading Signals:
    ----------------
    1. BUY Signal (골든크로스):
       - 짧은 VIDYA > 긴 VIDYA (상향 돌파)
       - 이전: Short VIDYA ≤ Long VIDYA
       - 현재: Short VIDYA > Long VIDYA
       → 상승 추세 시작, 적응형 확인
    
    2. SELL Signal (데드크로스 OR 손절):
       - 짧은 VIDYA < 긴 VIDYA (하향 돌파)
       - OR 3% 손절
       → 하락 추세 시작 또는 손실 제한
    
    Advantages over Traditional MA Crossover:
    -----------------------------------------
    1. 적응성 (Adaptivity):
       - CMO로 시장 변동성 자동 감지
       - 추세/횡보 구분 자동화
       - 시장 상황별 최적 반응
    
    2. 노이즈 필터링:
       - 횡보장에서 낮은 Alpha
       - 잘못된 신호 감소
       - 안정적인 크로스오버
    
    3. 추세 민감도:
       - 추세장에서 높은 Alpha
       - 빠른 추세 포착
       - 신속한 진입/청산
    
    4. 신뢰도:
       - CMO 기반 검증
       - 강한 모멘텀에서만 빠른 반응
       - 약한 신호는 자동 필터링
    
    Parameters:
    -----------
    df : pd.DataFrame
        주가 데이터 (VIDYA_{short_period}, VIDYA_{long_period} 필수)
    short_period : int, default=9
        짧은 VIDYA 기간 (신호선)
        - Tushar Chande 표준: 9일
        - 빠른 추세 변화 감지
        - 적응형 단기 추세
    long_period : int, default=21
        긴 VIDYA 기간 (추세선)
        - 장기 추세 확인
        - 안정적인 기준선
        - 적응형 장기 추세
    file_name : str
        로그 파일명
    
    Returns:
    --------
    float
        최종 수익률 (%)
    
    Parameter Guidelines:
    ---------------------
    1. Fast (빠른):
       - short=5, long=14
       - 많은 신호
       - 데이트레이딩
       - 높은 민감도
    
    2. Standard (표준):
       - short=9, long=21
       - Tushar Chande 권장
       - 스윙트레이딩
       - 균형잡힌 반응
    
    3. Slow (느린):
       - short=14, long=50
       - 적은 신호
       - 포지션 트레이딩
       - 높은 신뢰도
    
    Comparison with Other Adaptive Strategies:
    ------------------------------------------
    1. VIDYA Crossover:
       - 기반: CMO (모멘텀)
       - 적응: 변동성
       - 강점: 추세/횡보 자동 구분
       - 약점: CMO 계산 복잡
    
    2. KAMA Crossover:
       - 기반: Efficiency Ratio
       - 적응: 방향성
       - 강점: 노이즈 필터링
       - 약점: 추세 전환 지연
    
    3. EMA Crossover:
       - 기반: 고정 Alpha
       - 적응: 없음
       - 강점: 단순, 일관성
       - 약점: 횡보장 whipsaw
    
    → VIDYA: 모멘텀 기반, 추세 추종 최적
    → KAMA: 효율성 기반, 노이즈 제거 최적
    → EMA: 고정형, 단순성 최우선
    
    Strategy Implementation Details:
    ---------------------------------
    1. VIDYA 계산 (각 기간):
       - CMO = 100 × (up - down) / (up + down)
       - VI = |CMO| / 100 (Volatility Index)
       - Alpha = (2/(n+1)) × VI
       - VIDYA = Alpha × Price + (1-Alpha) × VIDYA[t-1]
    
    2. 크로스오버 감지:
       - 골든크로스: prev_short ≤ prev_long AND short > long
       - 데드크로스: prev_short ≥ prev_long AND short < long
       - 이전 값 체크로 정확한 교차 시점 포착
    
    3. 적응 상태 확인 (로그):
       - Short_VIDYA, Long_VIDYA 값 기록
       - Cross_Status (Golden/Dead) 표시
       - 추세 강도 간접 확인 가능
    
    Use Cases:
    ----------
    1. 추세 추종 (Trend Following):
       - VIDYA 듀얼 크로스오버 주 신호
       - 적응형 특성으로 다양한 시장 대응
       - 추세장: 빠른 진입, 횡보장: whipsaw 감소
    
    2. 변동성 적응 시스템:
       - VIDYA가 자동으로 시장 적응
       - 파라미터 조정 불필요
       - 단일 전략으로 다양한 시장 커버
    
    3. 필터 조합:
       - VIDYA Crossover + RSI
       - VIDYA Crossover + MACD
       - 적응형 추세 + 모멘텀 확인
    
    Notes:
    ------
    - 개발자: Tushar Chande
    - 발표: 1995년
    - 출처: "The New Technical Trader"
    - 핵심: CMO 기반 적응형 크로스오버
    - 장점: 추세/횡보 자동 구분, 높은 신뢰도
    - 단점: 듀얼 VIDYA 계산 부하, 파라미터 최적화
    - 추천: 추세 추종 전략, 변동성 큰 종목
    
    Example:
    --------
    >>> df = pd.read_csv('stock_data.csv')
    >>> df = calculate_vidya(df, 9)
    >>> df = calculate_vidya(df, 21)
    >>> yield_result = simulate_vidya_ma_crossover_strategy(df, 9, 21, 'stock.csv')
    >>> print(f"Final Yield: {yield_result:.2f}%")
    
    References:
    -----------
    [1] Tushar Chande (1995), "The New Technical Trader"
    [2] CMO (Chande Momentum Oscillator) 기반 적응형 시스템
    [3] VIDYA vs KAMA 비교 연구
    """
    trade_fee_rate = 0.002
    seed_money = 1000000
    cash = seed_money
    stock_qty = 0
    positions = None
    final_yield = 0.0
    buy_price = 0
    trade_yield = 0
    loss_limit_price = 0
    
    # 필수 컬럼 확인
    short_col = f'VIDYA_{short_period}'
    long_col = f'VIDYA_{long_period}'
    
    if short_col not in df.columns or long_col not in df.columns:
        print(f"Error: Required VIDYA columns not found.")
        print(f"Missing: {short_col} and/or {long_col}")
        print(f"Run calculate_vidya(df, {short_period}) and calculate_vidya(df, {long_period}) first.")
        return final_yield
    
    if file_name != "":
        name, ext = os.path.splitext(file_name)
        log_directory = os.path.join(root_log_directory, name)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        rename_file = f"{name}_log_VIDYA_{short_period}_{long_period}{ext}"
        log_field = pd.DataFrame(columns=["Date", "Action", "Price", "Quantity", 
                                          "Cash_After_Trade", "Trade_Yield",
                                          "Short_VIDYA", "Long_VIDYA", "Cross_Status"])
        log_field = log_field.astype({
            "Date": "object",
            "Action": "object",
            "Price": "float",
            "Quantity": "float",
            "Cash_After_Trade": "float",
            "Trade_Yield": "float",
            "Short_VIDYA": "float",
            "Long_VIDYA": "float",
            "Cross_Status": "object"
        })
    
    if len(df) < long_period:
        print(f"Data length is less than {long_period}. Cannot simulate strategy.")
        return final_yield
    
    for i in range(long_period, len(df)):
        current_price = df.loc[i, 'Value']
        short_vidya = df.loc[i, short_col]
        long_vidya = df.loc[i, long_col]
        prev_short = df.loc[i-1, short_col]
        prev_long = df.loc[i-1, long_col]
        
        # NaN 체크
        if pd.isna(short_vidya) or pd.isna(long_vidya) or pd.isna(prev_short) or pd.isna(prev_long):
            continue
        
        # 크로스 상태
        cross_status = "Golden" if short_vidya > long_vidya else "Dead"
        
        # 손절 조건
        stop_loss = False
        if positions == 'BUY' and current_price < loss_limit_price:
            stop_loss = True
        
        # BUY Signal: 골든크로스 (Short VIDYA가 Long VIDYA 상향 돌파)
        if prev_short <= prev_long and short_vidya > long_vidya and positions != 'BUY':
            if cash >= current_price:
                stock_qty = cash // current_price
                cash -= stock_qty * current_price * (1 + trade_fee_rate)
                positions = 'BUY'
                buy_price = current_price
                loss_limit_price = buy_price * loss_limit_rate
                trade_yield = 0
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": "매수 (골든크로스)",
                        "Price": current_price,
                        "Quantity": stock_qty,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Short_VIDYA": short_vidya,
                        "Long_VIDYA": long_vidya,
                        "Cross_Status": cross_status
                    }])], ignore_index=True)
        
        # SELL Signal: 데드크로스 (Short VIDYA가 Long VIDYA 하향 돌파) OR 손절
        elif ((prev_short >= prev_long and short_vidya < long_vidya) or stop_loss) and positions == 'BUY':
            if stock_qty > 0:
                cash += stock_qty * current_price * (1 - trade_fee_rate)
                positions = 'SELL'
                trade_yield = ((current_price * (1 - trade_fee_rate)) - (buy_price * (1 + trade_fee_rate))) / (buy_price * (1 + trade_fee_rate)) * 100
                
                sell_reason = "손절 (3% 손실)" if stop_loss else "매도 (데드크로스)"
                
                if file_name != "":
                    log_field = pd.concat([log_field, pd.DataFrame([{
                        "Date": df.loc[i,'Date'],
                        "Action": sell_reason,
                        "Price": current_price,
                        "Quantity": 0,
                        "Cash_After_Trade": cash,
                        "Trade_Yield": trade_yield,
                        "Short_VIDYA": short_vidya,
                        "Long_VIDYA": long_vidya,
                        "Cross_Status": cross_status
                    }])], ignore_index=True)
                
                stock_qty = 0
                loss_limit_price = 0
    
    final_portfolio_value = cash + stock_qty * df.loc[len(df)-1, 'Value']
    final_yield = (final_portfolio_value - seed_money) / seed_money * 100
    
    if file_name != "":
        final_short = df.loc[len(df)-1, short_col]
        final_long = df.loc[len(df)-1, long_col]
        final_status = "Golden" if final_short > final_long else "Dead"
        
        log_field = pd.concat([log_field, pd.DataFrame([{
            "Date": df.loc[len(df)-1,'Date'],
            "Action": "FINAL",
            "Price": df.loc[len(df)-1, 'Value'],
            "Quantity": stock_qty,
            "Cash_After_Trade": cash,
            "Trade_Yield": final_yield,
            "Short_VIDYA": final_short,
            "Long_VIDYA": final_long,
            "Cross_Status": final_status
        }])], ignore_index=True)
        log_field.to_csv(os.path.join(log_directory, rename_file), index=False)
    
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
    results['Chaikin_Oscillator'] = simulate_chaikin_oscillator_strategy(df, file_name=file_name)
    results['Aroon_Indicator'] = simulate_aroon_indicator_strategy(df, period=14, file_name=file_name)
    results['Money_Flow_Index'] = simulate_money_flow_index_strategy(df, period=14, file_name=file_name)
    results['Force_Index_13'] = simulate_force_index_strategy(df, period=13, file_name=file_name)
    results['Force_Index_CO_7_14'] = simulate_force_index_crossover_strategy(df, short_period=7, long_period=14, file_name=file_name)
    results['EOM_14'] = simulate_ease_of_movement_strategy(df, period=14, file_name=file_name)
    results['VROC_25'] = simulate_volume_rate_of_change_strategy(df, period=25, file_name=file_name)
    results['VROC_CO_7_14'] = simulate_volume_rate_of_change_crossover_strategy(df, short_period=7, long_period=14, file_name=file_name)
    results['MFV_CO_7_14'] = simulate_money_flow_volume_crossover_strategy(df, short_period=7, long_period=14, file_name=file_name)
    results['Accumulation_Distribution_Oscillator'] = simulate_accumulation_distribution_oscillator_strategy(df, file_name=file_name)
    results['Mass_Index_25'] = simulate_mass_index_strategy(df, nday=25, ema_period=9, file_name=file_name)
    results['Intraday_Momentum_Index_14'] = simulate_intraday_momentum_index_strategy(df, nday=14, file_name=file_name)
    results['TSI'] = simulate_true_strength_index_strategy(df, short_window=13, long_window=25, signal_window=7, file_name=file_name)
    results['DPO_20'] = simulate_detrended_price_oscillator_strategy(df, nday=20, file_name=file_name)
    results['Klinger_OC'] = simulate_klinger_oscillator_strategy(df, short_period=34, long_period=55, signal_period=13, file_name=file_name)
    results['PFE'] = simulate_polirazed_fractal_efficiency_index_strategy(df, nday=10, file_name=file_name)
    results['TRIX'] = simulate_trix_strategy(df, nday=12, signal=9, file_name=file_name)
    results['DMI_14'] = simulate_dmi_stategy(df, nday=14, file_name=file_name)
    results['Sumation_OBV'] = simulate_sumation_of_obv_strategy(df, nday=10, use_ema=False, file_name=file_name)
    results['Supertrend_10_3.0'] = simulate_supertrend_indicator_strategy(df, nday=10, multiplier=3.0, file_name=file_name)
    results['Williams_%R_14'] = simulate_williams_percent_range_strategy(df, nday=14, file_name=file_name)
    results['Elder_Ray_13'] = simulate_elder_ray_strategy(df, nday=13, file_name=file_name)
    results['Ichimoku_Cloud'] = simulate_ichimoku_cloud_strategy(df, conversion=9, base=26, lagging=52, displacement=26, file_name=file_name)
    results['ENVELOPE_20'] = simulate_envelope_strategy(df, nday=20, file_name=file_name)
    # results['High_Low_Oscillator_14'] = simulate_high_low_oscillator_strategy(df, nday=14, file_name=file_name) # need more study
    results['Alligator'] = simulate_alligator_strategy(df, file_name=file_name)
    results['Kaufmans_Adaptive_10'] = simulate_kaufmans_adaptive_strategy(df, nday=10, file_name=file_name)
    results['TEMA_CO_5_20'] = simulate_triple_ema_crossover_strategy(df, short_period=12, long_period=26, file_name=file_name)
    results['VIDYA_MA_9_21'] = simulate_vidya_ma_crossover_strategy(df,short_period=9, long_period=21 , file_name=file_name)
    
    return results
    
