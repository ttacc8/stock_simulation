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
        self.kospi_file_path = "files_kosdaq"
        self.processed_file_path = "modified_kosdaq" 
        self.test_dir = "modified_kosdaq_test"
        self.test_file = "SK증권_001510.csv"
    
    # add data
    def process_file_add_data(self, file_path: str):
        print(f"Adding data to file: {file_path}")
        df = pd.read_csv(file_path)

        moveAverage.calculate_all_indicators(df)
        # moveAverage.calculate_donchian_channels(df, nday=20)
        # moveAverage.calculate_volume_rate_of_change(df, nday=25)
        print(df.head())
        
        df.to_csv(file_path, index=False)

    # reverse data
    def process_file_data_reverse(self, file_path: str):

        try:
            df = pd.read_csv(file_path)
            print(f"Data from {file_path}:")
            # ["None","Value","Volume","Amount","Date", "Open","High", "Low", "None", "None"] 컬럼 출력
            df.columns = ["None","Value","Volume","Amount","Date", "Open","High", "Low", "None"]
            df.drop(columns=["None"], inplace=True, errors='ignore')
            # Filter out rows where Date is earlier than 1993
            # df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            # df = df[df['Date'] >= pd.Timestamp('1993-01-01')]
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
    def do_trade_all_stratage_simulation(self, file_path: str):
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
        cnt = 0

        for root, _, files in os.walk(file_path):
            for file in files:
                # print(f"Processing checking: start {datetime.datetime.now()} file: {file}")
                cnt += 1
                if cnt % 100 == 0:
                    print(f"Processed {cnt} / {csv_file_count} files...{cnt/csv_file_count*100:.2f}% completed.")
                    
                if file.endswith('.csv'):
                    read_file_path = os.path.join(root, file)
                    df = pd.read_csv(read_file_path)

                    # Call trade simulation functions
                    simulated_results = tradeSimulator.simulate_execute_all_strategy(df, file)
                    simulated_results = {'File': os.path.basename(read_file_path), **simulated_results}
                    final_df = pd.concat([final_df, pd.DataFrame([simulated_results])], ignore_index=True)
                    
        final_df.to_csv(target_file_path, index=False,encoding='utf-8-sig')
    
    
    def do_trade_add_single_simulation(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"Directory {file_path} does not exist.")
            return

        print(f"Processing directory: {file_path}")
        target_file_path = os.path.join(self.root_files_path, "trade_simulation_results.csv")
        if os.path.exists(target_file_path):
            final_df = pd.read_csv(target_file_path)
        else:
            final_df = pd.DataFrame()
        temp_series = pd.Series([], dtype='float64')

        # Get the count of all CSV files in the current file_path directory
        csv_file_count = sum(1 for _, _, files in os.walk(file_path) for file in files if file.endswith('.csv'))
        print(f"Total number of CSV files in {file_path}: {csv_file_count}")
        cnt = 0
        
        for root, _, files in os.walk(file_path):
            for file in files:
                cnt += 1
                if cnt % 100 == 0:
                    print(f"Processed {cnt} / {csv_file_count} files...{cnt/csv_file_count*100:.2f}% completed.")
                    
                if file.endswith('.csv'):
                    read_file_path = os.path.join(root, file)
                    df = pd.read_csv(read_file_path)

                    final_yield_special = tradeSimulator.simulate_special_item_strategy(df, file_name = file)
                    # print(f"Special strategy simulation yield for {file}: {final_yield_special}")
                    temp_series = temp_series._append(pd.Series([tradeSimulator.simulate_bollinger_strategy4(df,20,file)]), ignore_index=True)
               
        final_df['SpecialStratage'] = temp_series.values
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
            self.process_directory(target_dir,self.process_file_add_data)
        elif command_input == 3: # trade simulation
            target_dir = os.path.join(self.root_files_path, self.processed_file_path)
            # target_dir = os.path.join(self.root_files_path, self.test_dir)
            self.do_trade_all_stratage_simulation(target_dir)
        elif command_input == 4: # Add special strategy simulation
            target_dir = os.path.join(self.root_files_path, self.processed_file_path)
            self.do_trade_add_single_simulation(target_dir)
        elif command_input == 5: # Special item simulation
            sample_file_path = os.path.join(self.test_dir, self.test_file)
            self.do_special_item_simulation(sample_file_path)
        elif command_input == 6: # test
            # self.process_directory(self.test_dir, self.process_file_data_reverse)
            # print("reverse done")
            # self.process_directory(self.test_dir, self.process_file_add_data)
            # print("add data done")
            # self.do_trade_all_stratage_simulation(self.test_dir)
            # print("trade simulation done")
            # self.process_directory(self.test_dir, self.process_file_data_reverse)
            self.process_directory(self.test_dir, self.process_file_add_data)
        else:
            print("Invalid command input. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    handler = StockDataHandler()
    command_input = int(input("Enter 'process' to start processing files: \n1: Reverse Data, 2: Add Data, 3: All Stratage Simulation, 4: Add Special Simulation 5:Special item simulation : "))
    print("Starting file processing...")
    start_time = datetime.datetime.now()
    handler.do_processing(command_input)
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print(f"start_time: {start_time}, end_time: {end_time}, elapsed_time: {elapsed_time}")
