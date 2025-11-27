import os
import sys
import pandas as pd
import moveAverage
import tradeSimulator
import datetime
import threading


class StockDataHandler:
    def __init__(self):
        self.root_files_path = os.getcwd()
        self.kospi_file_path = "files_kospi"
        self.processed_file_path = "modified_kospi" 
        self.test_dir = "modified_kospi_test"
        self.test_file = "GS건설_006360.csv"
    
    # add data
    def process_file_add_data(self, file_path: str):
        # try:
        print(f"Adding data to file: {file_path}")
        df = pd.read_csv(file_path)

        moveAverage.calculate_all_indicators(df)
        
        df.to_csv(file_path, index=False)


        # except Exception as e:
        #     print(f"Error processing file {file_path}: {e}")

    # reverse data
    def process_file_data_reverse(self, file_path: str):

        try:
            df = pd.read_csv(file_path)
            print(f"Data from {file_path}:")
            # ["None","Value","Volume","Amount","Date", "Open","High", "Low", "None", "None"] 컬럼 출력
            df.columns = ["None","Value","Volume","Amount","Date", "Open","High", "Low", "None"]
            df.drop(columns=["None"], inplace=True, errors='ignore')
            df = df.iloc[::-1].reset_index(drop=True)

            target_path = os.path.join(self.root_files_path,self.processed_file_path)
            if not os.path.exists(target_path):
                print("The directory does not exist. Creating now...")
                os.makedirs(target_path)
                print(f"Created directory: {target_path}")

            # print(df.head())
            
            df.to_csv(os.path.join(target_path, os.path.basename(file_path)), index=False)
            print(f"Processed file saved to: {os.path.join(target_path, os.path.basename(file_path))}")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            
            
    # trade simulation 
    def do_trade_simulation(self, file_path: str):
        # try:
        if not os.path.exists(file_path):
            print(f"Directory {file_path} does not exist.")
            return

        print(f"Processing directory: {file_path}")
        final_df = pd.DataFrame()
        
        target_file_path = os.path.join(self.root_files_path, "trade_simulation_results.csv")
        if os.path.exists(target_file_path):
            final_df = pd.read_csv(target_file_path)
            temp_series = pd.Series([], dtype='float64')

        # Get the count of all CSV files in the current file_path directory
        csv_file_count = sum(1 for _, _, files in os.walk(file_path) for file in files if file.endswith('.csv'))
        print(f"Total number of CSV files in {file_path}: {csv_file_count}")
        # if csv_file_count == len(final_df['5daySMAYield']):
        #     print("All files have already been processed. Skipping trade simulation.")
        #     return

        for root, _, files in os.walk(file_path):
            for file in files:
                # print(f"Processing checking: start {datetime.datetime.now()} file: {file}")
                if file.endswith('.csv'):
                    read_file_path = os.path.join(root, file)
                    df = pd.read_csv(read_file_path)

                    # Call trade simulation functions
                    final_yield5 = tradeSimulator.simulate_SMA_strategy(df,5,file)
                    final_yield20 = tradeSimulator.simulate_SMA_strategy(df,20,file)
                    final_yield60 = tradeSimulator.simulate_SMA_strategy(df,60,file)
                    
                    final_yieldCrossover_5_20 = tradeSimulator.simulate_SMA_crossover_strategy(df,5,20,file)
                    
                    final_yieldBollinger = tradeSimulator.simulate_bollinger_strategy(df,20,file)
                    final_yieldBollinger2 = tradeSimulator.simulate_bollinger_strategy2(df,20,file)
                    final_yieldBollinger3 = tradeSimulator.simulate_bollinger_strategy3(df,20,file)
                    final_yieldBollinger4 = tradeSimulator.simulate_bollinger_strategy4(df,20,file)
                    final_yieldRsi = tradeSimulator.simulate_rsi_strategy(df,rsi_period = 14, overbought = 80, oversold = 30, file_name = file)
                    final_yieldMacd = tradeSimulator.simulate_macd_strategy(df,short_period = 12, long_period = 26, signal_period = 9, file_name = file)
                    final_yieldStochastic = tradeSimulator.simulate_stochastic_strategy(df, k_period = 14, d_period = 3, file_name = file)
     
                    final_df = pd.concat([final_df, pd.DataFrame({'File':[os.path.basename(read_file_path)],
                                                                '5daySMAYield':[final_yield5],'20daySMAYield':[final_yield20],'60daySMAYield':[final_yield60],
                                                                'yieldCrossover_5_20':[final_yieldCrossover_5_20],'Bollinger':[final_yieldBollinger],
                                                                'Bollinger2':[final_yieldBollinger2],'Bollinger3':[final_yieldBollinger3],'Bollinger4':[final_yieldBollinger4],
                                                                'RSI':[final_yieldRsi],'MACD':[final_yieldMacd],'Stochastic':[final_yieldStochastic]
                                                                })], ignore_index=True)
                    
                    # temp_series = temp_series._append(pd.Series([tradeSimulator.simulate_bollinger_strategy4(df,20,file)]), ignore_index=True)
               
                # print(f"Processing checking: end {datetime.datetime.now()} file: {file}")    
        # print(final_df)
        # final_df['bollinger4'] = temp_series.values
        final_df.to_csv(target_file_path, index=False,encoding='utf-8-sig')

    def do_special_item_simulation(self, file_path: str):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)

            final_yield_special = tradeSimulator.simulate_special_item_strategy(df, file_name = os.path.basename(file_path))
            print(f"Special item simulation yield for {os.path.basename(file_path)}: {final_yield_special}")
        else:
            print(f"File {file_path} does not exist.")
            
            
            
        # except Exception as e:
        #     print(f"Error simulating trade for file {file_path}: {e}")

    def process_directory(self, dir_path: str, process_file_func):
        if not os.path.exists(dir_path):
            print(f"Directory {dir_path} does not exist.")
            return

        print(f"Processing directory: {dir_path}")

        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    print(f"Processing file: {file_path}")
                    process_file_func(file_path)

    def do_processing(self, command_input: int):
        print(self.root_files_path)
        
        if command_input == 1: # data reverse
            target_dir = os.path.join(self.root_files_path, self.kospi_file_path)
            self.process_directory(target_dir,self.process_file_data_reverse)
        elif command_input == 2:# add data
            target_dir = os.path.join(self.root_files_path, self.processed_file_path)
            # target_dir = os.path.join(self.root_files_path, self.test_dir)
            self.process_directory(target_dir,self.process_file_add_data)
        elif command_input == 3: # trade simulation
            target_dir = os.path.join(self.root_files_path, self.processed_file_path)
            # target_dir = os.path.join(self.root_files_path, self.test_dir)
            self.do_trade_simulation(target_dir)
        elif command_input == 4: # Special item simulation
            sample_file_path = os.path.join(self.test_dir, self.test_file)
            self.do_special_item_simulation(sample_file_path)
        else:
            print("Invalid command input. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    handler = StockDataHandler()
    command_input = int(input("Enter 'process' to start processing files: \n1: Reverse Data, 2: Add Data, 3: Trade Simulation, 4:Special item simulation : "))
    print("Starting file processing...")
    start_time = datetime.datetime.now()
    handler.do_processing(command_input)
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print(f"start_time: {start_time}, end_time: {end_time}, elapsed_time: {elapsed_time}")
