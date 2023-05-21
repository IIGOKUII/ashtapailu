import sqlite3
import pandas as pd
from shared_var import shared_variable
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from datetime import datetime, timedelta
import json

class HeatMap(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("Heat Map")
        self.state('zoomed')
        self.overrideredirect(False)
        self.minsize(int(self.winfo_width() / 2), int(self.winfo_height() / 2))
        self.focus_force()
        # self.grab_set()

        self.path = shared_variable.path
        self.month = StringVar()
        self.month.set(datetime.today().strftime('%B'))
        self.DegnModel = StringVar()

        def get_work_map():
            def clear_frame(frame):
                for widget in frame.winfo_children():
                    widget.destroy()
            current_year = datetime.today().year
            month_number = datetime.strptime(self.month.get(), '%B').month
            first_day = datetime(current_year, month_number, 1).strftime('%d-%m-%Y')

            m_date = datetime.today().strptime(first_day, "%d-%m-%Y")

            # get the selected value from the combobox
            selection = self.DegnModel.get()

            with open(r"D:\PYTHON PROJECT\data\database\list.json", 'r') as f:
                # Load the contents of the file as a dictionary
                designers_data = json.load(f)

            # get the required dict
            try:
                names = designers_data['designers'][selection]
            except KeyError:
                names = designers_data['designers']['ASB-70DPH']

            # Define the column headings for the dates
            date_columns = [(m_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

            # Create a dictionary with the required data
            data_dict = {'DESIGNER': names, **{col: [0] * len(names) for col in date_columns}}

            # Create a DataFrame from the dictionary
            data = pd.DataFrame(data_dict)

            # Rename the columns
            data.columns = ['DESIGNER'] + date_columns

            # Connect to database
            conn = sqlite3.connect(r"D:\PYTHON PROJECT\data\database\MDShdb.db")

            # define query
            query = f"SELECT DATE, MOLD_NO, DESIGNER, ACTIVITY, DAYS FROM HEATMAP WHERE DATE BETWEEN ? AND date(?, '+30 day')"

            # Define the query parameters
            params = (m_date.strftime('%Y-%m-%d'), m_date.strftime('%Y-%m-%d'),)

            # Execute a SELECT statement with a WHERE clause
            df1 = pd.read_sql(query, conn, params=params)

            # Close the connection
            conn.close()

            # Map activity to the desired format
            activity_mapping = {
                'Preform': 'P',
                'Assembly': 'A',
                'Assembly Check': 'AC',
                'Detailing': 'D',
                'Checking': 'C',
                'Correction': 'CR',
                'Second Check': 'SC',
                'Issue': 'I',
            }

            df1['ACTIVITY'] = df1['ACTIVITY'].map(activity_mapping)
            # Extract the 4th to 9th digits using string slicing
            df1['MOLD_NO'] = df1['MOLD_NO'].str[3:9]

            # Create pivot table
            pivot_table = pd.pivot_table(df1, values='MOLD_NO', index='DESIGNER', columns='DATE',
                                         aggfunc=lambda x: '\n'.join(x + '-' + df1.loc[x.index, 'ACTIVITY'] + '-' + df1.loc[x.index, 'DAYS'].astype(str)))

            # Convert to DataFrame
            df = pd.DataFrame(pivot_table.to_records()).fillna(0)

            # set the "DESIGNER" column as the index for both dataframes
            data.set_index('DESIGNER', inplace=True)
            df.set_index('DESIGNER', inplace=True)

            # Update the values in data using df
            data.update(df)

            # replace any missing values with zeros
            data.fillna(0, inplace=True)

            # reset the index to make "DESIGNER" a column again
            data1 = data.reindex(names)
            return data1

        def get_day_map():
            current_year = datetime.today().year
            month_number = datetime.strptime(self.month.get(), '%B').month
            first_day = datetime(current_year, month_number, 1).strftime('%d-%m-%Y')

            m_date = datetime.today().strptime(first_day, "%d-%m-%Y")

            # get the selected value from the combobox
            selection = self.DegnModel.get()

            with open(r"D:\PYTHON PROJECT\data\database\list.json", 'r') as f:
                # Load the contents of the file as a dictionary
                designers_data = json.load(f)

            # get the required dict
            try:
                names = designers_data['designers'][selection]
            except KeyError:
                names = designers_data['designers']['ASB-70DPH']

            # Define the column headings for the dates
            date_columns = [(m_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

            # Create a dictionary with the required data
            data_dict = {'DESIGNER': names, **{col: [0] * len(names) for col in date_columns}}

            # Create a DataFrame from the dictionary
            data = pd.DataFrame(data_dict)

            # Rename the columns
            data.columns = ['DESIGNER'] + date_columns

            # Connect to database
            conn = sqlite3.connect(r"D:\PYTHON PROJECT\data\database\MDShdb.db")

            # define query
            query = f"SELECT DATE, MOLD_NO, DESIGNER, ACTIVITY, DAYS FROM HEATMAP WHERE DATE BETWEEN ? AND date(?, '+30 day')"

            # Define the query parameters
            params = (m_date.strftime('%Y-%m-%d'), m_date.strftime('%Y-%m-%d'),)

            # Execute a SELECT statement with a WHERE clause
            df1 = pd.read_sql(query, conn, params=params)

            # Close the connection
            conn.close()

            # Map activity to the desired format
            activity_mapping = {
                'Preform': 'P',
                'Assembly': 'A',
                'Assembly Check': 'AC',
                'Detailing': 'D',
                'Checking': 'C',
                'Correction': 'CR',
                'Second Check': 'SC',
                'Issue': 'I',
            }

            df1['ACTIVITY'] = df1['ACTIVITY'].map(activity_mapping)
            # Extract the 4th to 9th digits using string slicing
            df1['MOLD_NO'] = df1['MOLD_NO'].str[3:9]

            # Create pivot table
            pivot_table = pd.pivot_table(df1, values='MOLD_NO', index='DESIGNER', columns='DATE',
                                         aggfunc=lambda x: '\n'.join(x + '-' + df1.loc[x.index, 'ACTIVITY'] + '-' + df1.loc[x.index, 'DAYS'].astype(str)))

            # Convert to DataFrame
            df = pd.DataFrame(pivot_table.to_records()).fillna(0)

            # set the "DESIGNER" column as the index for both dataframes
            data.set_index('DESIGNER', inplace=True)
            df.set_index('DESIGNER', inplace=True)

            # Update the values in data using df
            data.update(df)

            # replace any missing values with zeros
            data.fillna(0, inplace=True)

            # reset the index to make "DESIGNER" a column again
            data1 = data.reindex(names)
            return data1

        def create_dataframe_frame(in_frame, in_df):
            # Create a frame for the DataFrame
            frame = Frame(in_frame, borderwidth=1, relief="solid")
            frame.pack(side="top", fill="both", expand=True)

            # Create a canvas and a vertical scrollbar
            canvas = Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
            canvas.configure(xscrollcommand=scrollbar.set)
            canvas.pack(side="top", fill="both", expand=True)
            scrollbar.pack(side="top", fill="x")

            # Create a frame inside the canvas
            inner_frame = Frame(canvas)
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            # Function to update the scroll region of the canvas
            def update_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))

            inner_frame.bind("<Configure>", update_scroll_region)

            # Create labels for column names
            for col_index, column in enumerate(in_df.columns):
                label = Label(inner_frame, text=column, width=12, relief="solid", bd=1)
                label.grid(row=0, column=col_index + 1, sticky="nsew")

            # Create labels for row index values
            for row_index, row in enumerate(in_df.index):
                label = Label(inner_frame, text=row, width=10, relief="solid", bd=1)
                label.grid(row=row_index + 1, column=0, sticky="nsew")

            # Create labels for data values
            for row_index, row in enumerate(in_df.index):
                for col_index, value in enumerate(in_df.loc[row]):
                    label = Label(inner_frame, text=value, width=12, relief="solid", bd=1)
                    label.grid(row=row_index + 1, column=col_index + 1, sticky="nsew")

            # Adjust column weights for proper resizing
            for i in range(in_df.shape[1] + 1):
                inner_frame.columnconfigure(i, weight=1)

            # Update the scroll region of the canvas
            update_scroll_region(None)

        def create_table():
            def refresh():
                self.df_frame.destroy()
                create_table()

            data1 = get_work_map()

            # Configure the window to use the grid layout
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

            # Create a frame for the DataFrame viewer
            self.df_frame = Frame(self, borderwidth=1, relief="solid")
            self.df_frame.grid(row=0, column=0, sticky="nsew")

            # Call the function to create the DataFrame frame
            create_dataframe_frame(self.df_frame, data1)

            # Create a frame for the DataFrame viewer
            op_frame = Frame(self, borderwidth=1, relief="solid")
            op_frame.grid(row=1, column=0, sticky="nsew")

            # Month Combobox
            month_values = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
            self.mont_label = ttk.Label(op_frame, text='Month:')
            self.mont_label.pack(side='left', pady=5, padx=5)
            self.month_Comb = ttk.Combobox(op_frame, textvariable=self.month, width=12, values=month_values)
            self.month_Comb.pack(side='left', pady=5, padx=5)

            # Designers group combobox
            mc_model_values2 = ('ASB-70DPH', 'ASB-70DPW', 'ASB-50MB', 'ASB-12M', 'PF', 'Preform', 'Modification', 'Parts Order', 'ECM')
            self.Designer_group_label = ttk.Label(op_frame, text='Designers Group:')
            self.Designer_group_label.pack(side='left', pady=5, padx=5)
            self.Designer_group_Comb = ttk.Combobox(op_frame, textvariable=self.DegnModel, width=15, values=mc_model_values2)
            self.Designer_group_Comb.pack(side='left', pady=5, padx=5)

            # Heatmap Button
            self.heatmap_btn = ttk.Button(op_frame, text="\u27F3", command=refresh)  # , command=refresh
            self.heatmap_btn.pack(side='left', pady=5, padx=5)

            # Heatmap Button
            # self.heatmap1_btn = ttk.Button(op_frame, text="\u27F3", command=refresh)  # , command=refresh
            # self.heatmap1_btn.pack(side='left', pady=5, padx=5)

        create_table()

class XYZ(object):
    def __init__(self, master):
        self.master = master
        self.master.title("Mold Design")
        # self.master.geometry("650x500")
        self.master.state('zoomed')
        HeatMap()


from ttkbootstrap import Style
# The main function
if __name__ == "__main__":
    root = Tk()
    style = Style(theme='flatly')

    obj = XYZ(root)
    root.mainloop()
