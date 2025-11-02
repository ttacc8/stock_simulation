import os
import sys
import pandas as pd
import moveAverage
import tradeSimulator
import datetime


class StockDataHandler:
    def __init__(self):
        self.root_files_path = os.getcwd()
        self.kospi_file_path = "files_kospi"
        self.processed_file_path = "modified_kospi"
        self.target_file = None
    
    # add data
    def process_file_add_data(self, file_path: str):
        try:
            print(f"Adding data to file: {file_path}")
            df = pd.read_csv(file_path)

            # Add moving averages
            # moveAverage.calculate_sma(df, 5)
            # moveAverage.calculate_sma(df, 20)
            # moveAverage.calculate_sma(df, 60)
            # moveAverage.calculate_sma(df, 120)
            # moveAverage.calculate_bollinger_bands(df, 20)  
            # moveAverage.calculate_sma(df, 7)
            # moveAverage.calculate_sma(df, 11)
            # moveAverage.calculate_sma(df, 13)
            # moveAverage.calculate_sma(df, 17)
            
            moveAverage.calculate_all_indicators(df)
            
            # print(df.head())
            df.to_csv(file_path, index=False)
            # print(f"Processed file saved to: {file_path}")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

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
                    final_yield5 = tradeSimulator.simulate_SMA_strategy(df,5)
                    final_yield7 = tradeSimulator.simulate_SMA_strategy(df,7)
                    final_yield11 = tradeSimulator.simulate_SMA_strategy(df,11)
                    final_yield13 = tradeSimulator.simulate_SMA_strategy(df,13)
                    final_yield17 = tradeSimulator.simulate_SMA_strategy(df,17)
                    final_yield20 = tradeSimulator.simulate_SMA_strategy(df,20)
                    final_yield60 = tradeSimulator.simulate_SMA_strategy(df,60)
                    
                    final_yieldCrossover_5_20 = tradeSimulator.simulate_SMA_crossover_strategy(df,5,20)
                    final_yieldCrossover_7_11 = tradeSimulator.simulate_SMA_crossover_strategy(df,7,11)
                    final_yieldCrossover_13_17 = tradeSimulator.simulate_SMA_crossover_strategy(df,13,17)
                    final_yieldCrossover_7_17 = tradeSimulator.simulate_SMA_crossover_strategy(df,7,17)
                    
                    final_yieldBollinger20 = tradeSimulator.simulate_bollinger_strategy(df,20)
     
                    final_df = pd.concat([final_df, pd.DataFrame({'File':[os.path.basename(read_file_path)],
                                                                '5daySMAYield':[final_yield5],
                                                                '7daySMAYield':[final_yield7],
                                                                '11daySMAYield':[final_yield11],
                                                                '13daySMAYield':[final_yield13],
                                                                '17daySMAYield':[final_yield17],
                                                                '20daySMAYield':[final_yield20],
                                                                '60daySMAYield':[final_yield60],
                                                                'yieldCrossover_5_20':[final_yieldCrossover_5_20],
                                                                'yieldCrossover_7_11':[final_yieldCrossover_7_11],
                                                                'yieldCrossover_7_17':[final_yieldCrossover_7_17],
                                                                'yieldCrossover_13_17':[final_yieldCrossover_13_17],
                                                                'Bollinger20':[final_yieldBollinger20]
                                                                })], ignore_index=True)
               
                # print(f"Processing checking: end {datetime.datetime.now()} file: {file}")    
        # print(final_df)
        final_df.to_csv(target_file_path, index=False,encoding='utf-8-sig')



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

    def do_processing(self):
        print(self.root_files_path)
        # data reverse
        # target_dir = os.path.join(self.root_files_path, self.kospi_file_path)
        # self.process_directory(target_dir,self.process_file_data_reverse)
        
        # add data
        # target_dir = os.path.join(self.root_files_path, self.processed_file_path)
        # self.process_directory(target_dir,self.process_file_add_data)

        # trade simulation
        target_dir = os.path.join(self.root_files_path, self.processed_file_path)
        self.do_trade_simulation(target_dir)

if __name__ == "__main__":
    handler = StockDataHandler()
    print("Starting file processing...")
    start_time = datetime.datetime.now()
    handler.do_processing()
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print(f"start_time: {start_time}, end_time: {end_time}, elapsed_time: {elapsed_time}")
