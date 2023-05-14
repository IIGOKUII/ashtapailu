from tkinter import *
from methods import get_new_entry, get_short_plan, get_complete_plan, delete_plan, get_mold_info, plan_by_mold, submit_entry, re_plan
from tkinter import ttk
from tkinter import messagebox
import sqlite3
# from tkcalendar import Calendar
from tkcalendar import Calendar
from datetime import datetime, timedelta
import pandas as pd
from shared_var import shared_variable
# import seaborn as sns
# import matplotlib.pyplot as plt
from ttkbootstrap import DateEntry
import json


class Planning(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.Activity_start_date = None
        self.title("Mold Planning")
        self.focus_force()
        self.grab_set()

        # Set Window size and Set at center
        window_height = 780
        window_width = 1280
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cor = int((self.winfo_screenwidth() / 2) - (window_width / 2)) - 10
        y_cor = int((self.winfo_screenheight() / 2.3) - (window_height / 2))

        self.geometry(f'{window_width}x{window_height}+{x_cor}+{y_cor}')
        self.minsize(int((self.winfo_screenwidth() / 2)), window_height)

        # Variables
        self.path = shared_variable.path
        self.MDShdb = f"{self.path}database/MDShdb.db"
        self.initial = shared_variable.initial
        self.leave_path = f"{self.path}database/leaveDb.db"

        self.cal_date = StringVar()

        self.Activity_var = StringVar()
        self.Y_var = IntVar()
        self.N_var = IntVar()
        self.Activity_day = StringVar()
        self.Activity_end = StringVar()
        self.Activity_designer = StringVar()

        # Mold Info Variable
        self.info_date = StringVar()
        self.mold_no = StringVar()
        self.customer = StringVar()
        self.machine_type = StringVar()
        self.cav_no = StringVar()
        self.ord_scp = StringVar()
        self.ord_typ = StringVar()
        self.iss_to = StringVar()
        self.zc_var = StringVar()
        self.qmc_var = StringVar()
        self.air_ejt_var = StringVar()
        self.pos_ver = StringVar()
        self.country = StringVar()
        self.bottle_no = StringVar()
        self.req_id = IntVar()
        self.malt = StringVar()
        self.hrtype = StringVar()
        self.difficulty = StringVar()

        # Combobox Variable
        self.mcModel = StringVar()
        self.DegnModel = StringVar()
        self.month = StringVar()
        self.month.set(datetime.today().strftime('%B'))
        self.end_day = StringVar()

        # Change Plan Var
        self.ch_start_date = StringVar()
        self.ch_days = StringVar()
        self.ch_designer = StringVar()

        uname = shared_variable.user_name

        # Fill no of days as per difficulty
        def fill_days(event):
            # create a dictionary of tuples with no of days as per difficulty
            mc_model_values = ('70DPH', '70DPW', '50MB', '12M', 'PF')

            with open('O:/Scheduling/Mold Design Application/Final software/database/planning_days.json', 'r') as f:
                # Load the contents of the file as a dictionary
                days_data = json.load(f)

            mc_model = "70DPH"

            for mc in mc_model_values:
                if mc in self.machine_type.get():
                    mc_model = mc
                    if self.Activity_var.get() == 'Preform':
                        self.DegnModel.set('Preform')
                    else:
                        for mcs in mc_model_values2:
                            if mc in mcs:
                                try:
                                    self.DegnModel.set(mcs)
                                except KeyError:
                                    pass

            try:
                r_dict = days_data[mc_model]

                # get the data corresponding to the selected value from the dictionary
                p, a, ac, d, c, sc, i = r_dict[self.difficulty.get()]

                # display the data in the entry widgets
                set_difficulty = {
                    "Preform": p,
                    "Assembly": a,
                    "Assembly Check": ac,
                    "Detailing": d,
                    "Checking": c,
                    "Second Check": sc,
                    "Mold Issue": i
                }
                try:
                    activity_day = set_difficulty[self.Activity_var.get()]
                    self.Activity_day.set(activity_day)
                except KeyError:
                    self.Activity_day.set('')

            except KeyError:
                self.Activity_day.set('')

        # Select designer
        def sel_dsgn(event, arg):
            # Update variables from tree view
            try:
                selected_item = self.tree.selection()[0]
                arg.set(self.tree.item(selected_item)['values'][0])
            except IndexError:
                arg.set('Select Designer')

        def submit_one():
            print(self.Y_var.get(), self.N_var.get())
            blank_check = (self.Activity_var, self.Activity_day, self.Activity_start_date.entry, self.Activity_designer)

            if self.Y_var.get() == 1 and self.N_var.get() == 1:
                messagebox.showerror("Scheduler", "Please select Yes or No")
                return

            if self.Y_var.get() == 0 and self.N_var.get() == 0:
                messagebox.showerror("Scheduler", "Please plan first")
                return

            if self.Y_var.get() == 1 and self.N_var.get() == 0:

                blank_item = []
                for v in blank_check:
                    if v.get() == "" or v.get() == "***":
                        v.set("***")
                        blank_item.append(v.get())

                if blank_item:
                    return

                submit_entry(self.MDShdb, self.req_id.get(), self.mold_no.get(), self.Activity_var.get(), self.Activity_start_date.entry.get(), self.Activity_day.get(), self.Activity_designer.get())

            get_mold_plan(self.mold_no.get())

            for v in blank_check:
                if v != self.Activity_start_date.entry:
                    v.set("")

            # # Delete all data from the TreeView
            # self.tree.delete(*self.tree.get_children())

        def get_first_day_of_month(month_name):
            current_year = datetime.today().year
            month_number = datetime.strptime(month_name, '%B').month
            first_day = datetime(current_year, month_number, 1)
            return first_day.strftime('%d-%m-%Y')

        def heatmap():
            m_date = get_first_day_of_month(self.month.get())
            m_date = datetime.today().strptime(m_date, "%d-%m-%Y")

            # get the selected value from the combobox
            selection = self.DegnModel.get()

            with open('O:/Scheduling/Mold Design Application/Final software/database/list.json', 'r') as f:
                # Load the contents of the file as a dictionary
                data = json.load(f)

            # get the required dict
            try:
                names = data['designers'][selection]
            except KeyError:
                names = data['designers']['ASB-70DPH']

            # Define the column headings for the dates
            date_columns = [(m_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

            # Create a dictionary with the required data
            data_dict = {'DESIGNER': names, **{col: [0] * len(names) for col in date_columns}}

            # Create a DataFrame from the dictionary
            data = pd.DataFrame(data_dict)

            # Rename the columns
            data.columns = ['DESIGNER'] + date_columns

            # Connect to database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

            # define query
            query = f"SELECT DATE, DESIGNER, DAYS FROM HEATMAP WHERE DATE BETWEEN ? AND date(?, '+30 day')"

            # Define the query parameters
            params = (m_date.strftime('%Y-%m-%d'), m_date.strftime('%Y-%m-%d'),)

            # Execute a SELECT statement with a WHERE clause
            df1 = pd.read_sql(query, conn, params=params)

            # Close the connection
            conn.close()

            # create the pivot table
            pivot_table = pd.pivot_table(df1, index='DESIGNER', columns='DATE', values='DAYS', aggfunc=sum)

            # Convert to DataFrame
            df = pd.DataFrame(pivot_table.to_records()).fillna(0)

            # set the "DESIGNER" column as the index for both dataframes
            data.set_index('DESIGNER', inplace=True)
            df.set_index('DESIGNER', inplace=True)

            # add the two dataframes together
            result = data.add(df, fill_value=0)

            # replace any missing values with zeros
            result.fillna(0, inplace=True)

            # reset the index to make "DESIGNER" a column again
            result = result.reindex(names)

            # create a new figure and axis object
            # fig, ax = plt.subplots(figsize=(screen_width/100, screen_height/100))
            #
            # sns.heatmap(result, annot=True, fmt=".1f", vmin=0, vmax=3, cmap="YlGnBu", center=1.5, ax=ax)
            # plt.show()

        def reset_var():
            self.Activity_var.set('')
            self.Y_var.set(0)
            self.N_var.set(0)
            self.Activity_day.set('')
            self.Activity_end.set('')
            self.Activity_designer.set('')

        def refresh():
            data_1 = get_new_entry(self.MDShdb)

            # Delete all data from the TreeView
            self.new_entry_tree.delete(*self.new_entry_tree.get_children())

            # Insert the data into the TreeView
            for row_1 in data_1:
                self.new_entry_tree.insert('', END, values=row_1)

            data_2 = get_short_plan(self.MDShdb)

            # Delete all data from the TreeView
            self.short_plan_tree.delete(*self.short_plan_tree.get_children())

            # Insert the data into the TreeView
            for row_2 in data_2:
                self.short_plan_tree.insert('', END, values=row_2)

            data_3 = get_complete_plan(self.MDShdb)

            # Delete all data from the TreeView
            self.complete_plan_tree.delete(*self.complete_plan_tree.get_children())

            # Insert the data into the TreeView
            for row_3 in data_3:
                self.complete_plan_tree.insert('', END, values=row_3)

        def update_info(event, arg):

            # Reset all variable
            reset_var()

            trees = (self.new_entry_tree, self.short_plan_tree, self.complete_plan_tree)

            for tree in trees:
                if tree != arg:
                    if len(tree.selection()) > 0:
                        tree.selection_remove(tree.selection()[0])

            mold_no = arg.item(arg.selection()[0])['values'][1]

            df_project_mold = plan_by_mold(self.MDShdb, mold_no)

            # Delete all data from the TreeView
            self.data_tree.delete(*self.data_tree.get_children())

            # Insert the data into the TreeView
            for i, row_mold in df_project_mold.iterrows():
                values = tuple(row_mold.values)
                self.data_tree.insert("", "end", text=i, values=values)

            df_mold_info = get_mold_info(self.MDShdb, mold_no)

            self.req_id.set(df_mold_info.at[0, 'REQ_ID'])
            self.mold_no.set(df_mold_info.at[0, 'MOLD_NO'])
            self.customer.set(df_mold_info.at[0, 'CUSTOMER'])
            self.machine_type.set(df_mold_info.at[0, 'MACHINE_TYPE'])
            self.cav_no.set(df_mold_info.at[0, 'CAVITY'])
            self.ord_scp.set(df_mold_info.at[0, 'ORDER_SCOPE'])
            self.ord_typ.set(df_mold_info.at[0, 'ORDER_TYPE'])
            self.iss_to.set(df_mold_info.at[0, 'ISSUE_TO'])
            self.zc_var.set(df_mold_info.at[0, 'ZC'])
            self.qmc_var.set(df_mold_info.at[0, 'QMC'])
            self.air_ejt_var.set(df_mold_info.at[0, 'AIR_EJECT'])
            self.pos_ver.set(df_mold_info.at[0, 'POS_VER'])
            self.country.set(df_mold_info.at[0, 'COUNTRY'])
            self.bottle_no.set(df_mold_info.at[0, 'CONTAINER_NO'])
            self.malt.set(df_mold_info.at[0, 'MOLDING_MALT'])
            self.hrtype.set(df_mold_info.at[0, 'HR_TYPE'])
            self.difficulty.set(df_mold_info.at[0, 'DIFFICULTY'])

            # Label of mold information
            self.mold_no_label = ttk.Label(self.mold_details, text=f'Mold No : {self.mold_no.get()}')
            self.mold_no_label.grid(column=0, row=0)
            self.req_id_label = ttk.Label(self.mold_details, text=f'Request ID : {self.req_id.get()}')
            self.req_id_label.grid(column=1, row=0)
            self.cust_label = ttk.Label(self.mold_details, text=f'Customer : {self.customer.get()}')
            self.cust_label.grid(column=0, row=1, columnspan=2)
            self.mc_label = ttk.Label(self.mold_details, text=f'Machine Type : {self.machine_type.get()}')
            self.mc_label.grid(column=0, row=2, columnspan=2)
            self.cav_label = ttk.Label(self.mold_details, text=f'Cavity : {self.cav_no.get()}')
            self.cav_label.grid(column=0, row=3)
            self.scope_label = ttk.Label(self.mold_details, text=f'Order Scope : {self.ord_scp.get()}')
            self.scope_label.grid(column=1, row=3)
            self.type_label = ttk.Label(self.mold_details, text=f'Order Type : {self.ord_typ.get()}')
            self.type_label.grid(column=0, row=4)
            self.issue_to_label = ttk.Label(self.mold_details, text=f'Issue To : {self.iss_to.get()}')
            self.issue_to_label.grid(column=1, row=4)
            self.zc_label = ttk.Label(self.mold_details, text=f'ZC : {self.zc_var.get()}')
            self.zc_label.grid(column=0, row=5)
            self.qmc_label = ttk.Label(self.mold_details, text=f'QMC : {self.qmc_var.get()}')
            self.qmc_label.grid(column=1, row=5)
            self.air_label = ttk.Label(self.mold_details, text=f'Air Eject : {self.air_ejt_var.get()}')
            self.air_label.grid(column=0, row=6)
            self.ver_label = ttk.Label(self.mold_details, text=f'POS Ver : {self.pos_ver.get()}')
            self.ver_label.grid(column=1, row=6)
            self.country_label = ttk.Label(self.mold_details, text=f'POS Ver : {self.country.get()}')
            self.country_label.grid(column=0, row=7)
            self.bottle_label = ttk.Label(self.mold_details, text=f'Bottle No : {self.bottle_no.get()}')
            self.bottle_label.grid(column=1, row=7)
            self.malt_label = ttk.Label(self.mold_details, text=f'Molding Material : {self.malt.get()}')
            self.malt_label.grid(column=0, row=8)
            self.hrtype_label = ttk.Label(self.mold_details, text=f'HR Type : {self.hrtype.get()}')
            self.hrtype_label.grid(column=1, row=8)

            # Configure for all widgets in Project Details frame
            for wid in self.mold_details.winfo_children():
                wid.grid_configure(padx=20, pady=3, sticky=W)

        def get_designers(event, arg):
            # try:
            #     m_date = datetime.strptime(cal_date, "%d-%m-%Y")
            # except ValueError:
            #     m_date = cal_date
            if arg.entry.get() == '':
                return
            try:
                m_date = datetime.strptime(arg.entry.get(), "%d-%m-%Y")
            except ValueError:
                return
            if self.cal_date.get() == arg.entry.get():
                print('hi')
                return

            self.cal_date.set(arg.entry.get())

            # get the selected value from the combobox
            selection = self.DegnModel.get()

            with open('O:/Scheduling/Mold Design Application/Final software/database/list.json', 'r') as f:
                # Load the contents of the file as a dictionary
                data = json.load(f)

            # get the required dict
            try:
                names = data['designers'][selection]
            except KeyError:
                names = data['designers']['ASB-70DPH']

            # Define the column headings for the dates
            date_columns = [(m_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]
            #
            # names = designers_list[r_dict]

            # Create a dictionary with the required data
            data_dict = {'DESIGNER': names, **{col: [0] * len(names) for col in date_columns}}

            # Create a DataFrame from the dictionary
            data = pd.DataFrame(data_dict)

            # Rename the columns
            data.columns = ['DESIGNER'] + date_columns

            # Connect to database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

            # define query
            query = f"SELECT DATE, DESIGNER, DAYS FROM HEATMAP WHERE DATE BETWEEN ? AND date(?, '+5 day')"

            # Define the query parameters
            params = (m_date.strftime('%Y-%m-%d'), m_date.strftime('%Y-%m-%d'),)

            # Execute a SELECT statement with a WHERE clause
            df1 = pd.read_sql(query, conn, params=params)

            # Close the connection
            conn.close()

            # create the pivot table
            pivot_table = pd.pivot_table(df1, index='DESIGNER', columns='DATE', values='DAYS', aggfunc=sum)

            # Convert to DataFrame
            df = pd.DataFrame(pivot_table.to_records()).fillna(0)

            # set the "DESIGNER" column as the index for both dataframes
            data.set_index('DESIGNER', inplace=True)
            df.set_index('DESIGNER', inplace=True)

            # add the two dataframes together
            result = data.add(df, fill_value=0)

            # replace any missing values with zeros
            result.fillna(0, inplace=True)

            # reset the index to make "DESIGNER" a column again
            result = result.reindex(names)
            result.reset_index(inplace=True)

            # iterate over the column names
            for col_name in result.columns:
                if col_name != 'DESIGNER':
                    if datetime.strptime(col_name, '%Y-%m-%d').weekday() == 6:
                        result.loc[:, col_name] = ['Sunday'] * len(names)

            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert the data into the TreeView
            for i, row in result.iterrows():
                values = tuple(row.values)
                for j in range(2, 7):
                    date_str = (m_date + timedelta(days=j-2)).strftime("%d-%m-%Y")
                    self.tree.heading("#" + str(j), text=date_str)
                self.tree.heading("#1", text="Designer")
                self.tree.insert("", "end", text=i, values=values)

        def mold_information():
            activity = ('Preform', 'Assembly', 'Assembly Check', 'Detailing', 'Checking', 'Correction', 'Second Check', 'Mold Issue')

            # Labels Heading
            self.activity_label = ttk.Label(self.planning_details, text='Activity')
            self.activity_label.grid(column=0, row=1)
            self.yes_label = ttk.Label(self.planning_details, text='YES')
            self.yes_label.grid(column=1, row=1)
            self.no_label = ttk.Label(self.planning_details, text='NO')
            self.no_label.grid(column=2, row=1)
            self.start_label = ttk.Label(self.planning_details, text='Start Date')
            self.start_label.grid(column=3, row=1)
            self.day_label = ttk.Label(self.planning_details, text='Days')
            self.day_label.grid(column=4, row=1)
            self.end_label = ttk.Label(self.planning_details, text='End Date')
            self.end_label.grid(column=5, row=1)
            self.design_label = ttk.Label(self.planning_details, text='Designer')
            self.design_label.grid(column=6, row=1)

            # Labels row
            self.Activity_combo = ttk.Combobox(self.planning_details, textvariable=self.Activity_var, values=activity, width=15)
            self.Activity_combo.grid(column=0, row=2)
            self.Activity_combo.bind("<<ComboboxSelected>>", fill_days)

            # Activity check buttons
            self.R1 = ttk.Checkbutton(self.planning_details, variable=self.Y_var)
            self.R1.grid(column=1, row=2)

            # Activity check buttons
            self.R11 = ttk.Checkbutton(self.planning_details, variable=self.N_var)
            self.R11.grid(column=2, row=2)

            # Start date
            self.Activity_start_date = DateEntry(self.planning_details, width=12)
            self.Activity_start_date.grid(column=3, row=2)
            self.Activity_start_date.entry.bind('<FocusIn>', lambda event, arg=self.Activity_start_date: get_designers(event, arg))
            self.Activity_start_date.entry.delete(first=0, last=END)

            # Days
            self.Activity_day_entry = ttk.Entry(self.planning_details, textvariable=self.Activity_day, width=10)
            self.Activity_day_entry.grid(column=4, row=2)

            # End date
            self.Activity_end_entry = ttk.Entry(self.planning_details, textvariable=self.Activity_end, width=10)
            self.Activity_end_entry.grid(column=5, row=2)

            # Designers data
            self.Activity_designer_entry = ttk.Entry(self.planning_details, textvariable=self.Activity_designer, width=10)
            self.Activity_designer_entry.grid(column=6, row=2, sticky=W)
            self.Activity_designer_entry.bind('<1>', lambda event, arg=self.Activity_designer: sel_dsgn(event, arg))

            #dummy label
            self.dummy_label = Label(self.planning_details)
            self.dummy_label.grid(column=0, row=3)

            # frame
            self.saperate_frame= Frame(self.planning_details)
            self.saperate_frame.grid(column=0, row=4, columnspan=7, sticky=NSEW)

            # Add buttons
            self.update1_btn = ttk.Button(self.saperate_frame, text="Update", command=update_pre_plan, width=10)
            self.update1_btn.pack(side='left', padx=5)
            self.change1_btn = ttk.Button(self.saperate_frame, text="Delete", command=delete_pre_plan, width=10)
            self.change1_btn.pack(side='left', padx=5)
            self.Activity_Button = ttk.Button(self.saperate_frame, text="Add", command=submit_one, width=10)
            self.Activity_Button.pack(side='right', padx=5)
            self.re_planning_combo = ttk.Combobox(self.saperate_frame, textvariable=self.Activity_var, width=15)
            self.re_planning_combo.pack(side='right', padx=5)

            for p_widgets in self.planning_details.winfo_children():
                p_widgets.grid_configure(padx=5, pady=4)

        def get_mold_plan(mold_no):
            df_project_mold = plan_by_mold(self.MDShdb, mold_no)

            # Delete all data from the TreeView
            self.data_tree.delete(*self.data_tree.get_children())

            # Insert the data into the TreeView
            for i, row_mold in df_project_mold.iterrows():
                values = tuple(row_mold.values)
                self.data_tree.insert("", "end", text=i, values=values)

        def change_plan(event):
            # Update variables from tree view
            try:
                selected_item = self.data_tree.selection()[0]
            except IndexError:
                # messagebox.showerror("Error", 'Select Proper Row')
                return

            # self.ch_start_date.set(self.data_tree.item(selected_item)['values'][2])
            self.Activity_var.set(self.data_tree.item(selected_item)['values'][4])
            self.Y_var.set(1)
            self.Activity_start_date.entry.insert(END, self.data_tree.item(selected_item)['values'][2])
            self.Activity_day.set(self.data_tree.item(selected_item)['values'][5])
            self.Activity_designer.set(self.data_tree.item(selected_item)['values'][3])

            date = "5"
            # if plan date is today
            if date == "":
                delete_plan(self.MDShdb, self.Activity_designer.get(), self.req_id.get(), self.Activity_var.get())
            else:

                self.Activity_combo = ttk.Combobox(self.planning_details, textvariable=self.Activity_var, width=15)
                self.Activity_combo.grid(column=0, row=3, sticky="W")

                re_plan(self.MDShdb, self.Activity_designer.get(), self.req_id.get(), self.Activity_var.get())

            # self.ch_start_date_label = ttk.Label(self.mold_plan_details, text='Start Date')
            # self.ch_start_date_label.place(x=35, y=250)
            # self.ch_start_date_entry = ttk.Entry(self.mold_plan_details, textvariable=self.ch_start_date)
            # self.ch_start_date_entry.place(x=20, y=270, width=100)
            # self.ch_days_label = ttk.Label(self.mold_plan_details, text='No of Days')
            # self.ch_days_label.place(x=145, y=250)
            # self.ch_days_entry = ttk.Entry(self.mold_plan_details, textvariable=self.ch_days)
            # self.ch_days_entry.place(x=130, y=270, width=100)
            # self.ch_designer_date_label = ttk.Label(self.mold_plan_details, text='Designer')
            # self.ch_designer_date_label.place(x=255, y=250)
            # self.ch_designer_date_entry = ttk.Entry(self.mold_plan_details, textvariable=self.ch_designer)
            # self.ch_designer_date_entry.place(x=240, y=270, width=100)
            #
            # self.update1_btn = ttk.Button(self.mold_plan_details, text="Update", command=update_pre_plan)
            # self.update1_btn.place(x=350, y=270, width=80)
            # self.change1_btn = ttk.Button(self.mold_plan_details, text="Delete", command=delete_pre_plan)
            # self.change1_btn.place(x=450, y=270, width=80)

        def update_pre_plan():
            # Update variables from tree view
            try:
                selected_item = self.data_tree.selection()[0]
            except IndexError:
                messagebox.showerror("Error", 'Select Proper Row')
                return

            temp_req_id = self.data_tree.item(selected_item)['values'][0]
            temp_designer = self.data_tree.item(selected_item)['values'][3]
            temp_mold_no = self.data_tree.item(selected_item)['values'][1]
            temp_activity = self.data_tree.item(selected_item)['values'][4]
            temp_start = self.data_tree.item(selected_item)['values'][2]

            # Connect to the SQLite3 database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            c = conn.cursor()
            c.execute("PRAGMA JOURNAL_MODE='wal' ")

            try:
                row = c.execute(f"SELECT REQ_ID FROM {self.ch_designer.get()}")
            except sqlite3.OperationalError:
                return

            c.execute(f"DELETE FROM {temp_designer} WHERE REQ_ID=? AND ACTIVITY=?", (temp_req_id, temp_activity))

            c.execute("DELETE FROM HEATMAP WHERE REQ_ID=? AND DESIGNER=? AND ACTIVITY=?", (temp_req_id, temp_designer, temp_activity))

            result = c.execute("SELECT YEAR2023 FROM holidaylist")
            holiday_list = tuple(date[0] for date in result.fetchall())

            # Define the input values
            if '.' in self.ch_days.get():
                no_of_days = float(self.ch_days.get())
            else:
                no_of_days = int(self.ch_days.get())

            # user log date
            user_log = uname + " " + datetime.now().strftime('%d-%m-%Y')

            # Convert string to datetime object
            try:
                start_date = datetime.strptime(self.ch_start_date.get(), "%d-%m-%Y")
            except ValueError:
                date_string = self.ch_start_date.get()
                datetime_object = datetime.strptime(date_string, "%Y-%m-%d")
                start_date = datetime_object.strftime("%d-%m-%Y")

            # Loop through the number of days and insert records into the database
            for i in range(int(no_of_days)):
                if start_date.weekday() == 6:
                    start_date = start_date + timedelta(days=1)
                    if start_date.strftime("%Y-%m-%d") in holiday_list:
                        start_date = start_date + timedelta(days=1)
                # Create a date string in the format 'dd-mm-yyyy'
                date_str = start_date.strftime("%Y-%m-%d")
                self.end_day.set(date_str)
                # Insert the record into the database
                c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (temp_req_id, temp_mold_no, date_str, self.ch_designer.get(), temp_activity, 1, 0, 'Planned', user_log))
                # Increment the day by 1
                start_date = start_date + timedelta(days=1)

            # If there are remaining days (e.g. 0.5 in this case), insert a record with the remaining days
            if no_of_days % 1 != 0:
                if start_date.weekday() == 6:
                    start_date = start_date + timedelta(days=1)
                    if start_date.strftime("%Y-%m-%d") in holiday_list:
                        start_date = start_date + timedelta(days=1)
                date_str = start_date.strftime("%Y-%m-%d")
                self.end_day.set(date_str)
                c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (temp_req_id, temp_mold_no, date_str, self.ch_designer.get(), temp_activity, no_of_days % 1, 0, 'Planned', user_log))

            # Convert date string
            temp_start = self.ch_start_date.get()
            datetime_object = datetime.strptime(temp_start, "%d-%m-%Y")
            temp_start = datetime_object.strftime("%Y-%m-%d")

            c.execute(f"INSERT INTO {self.ch_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS_REMARK) VALUES (?,?,?,?,?,?,?)",
                      (temp_req_id, temp_mold_no, temp_activity, temp_start, self.end_day.get(), self.ch_days.get(), 'Planned'))

            conn.commit()
            conn.close()

            get_mold_plan(temp_mold_no)

            self.ch_start_date.set("")
            self.ch_days.set("")
            self.ch_designer.set("")

        def delete_pre_plan():
            # Update variables from tree view
            try:
                selected_item = self.data_tree.selection()[0]
            except IndexError:
                messagebox.showerror("Error", 'Select Proper Row')
                return

            temp_req_id = self.data_tree.item(selected_item)['values'][0]
            temp_designer = self.data_tree.item(selected_item)['values'][3]
            temp_mold_no = self.data_tree.item(selected_item)['values'][1]
            temp_activity = self.data_tree.item(selected_item)['values'][4]

            # Connect to the SQLite3 database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            c = conn.cursor()

            try:
                row = c.execute(f"SELECT REQ_ID FROM {self.ch_designer.get()}")
            except sqlite3.OperationalError:
                return

            c.execute(f"DELETE FROM {temp_designer} WHERE REQ_ID=? AND ACTIVITY=?", (temp_req_id, temp_activity))

            c.execute("DELETE FROM HEATMAP WHERE REQ_ID=? AND DESIGNER=? AND ACTIVITY=?", (temp_req_id, temp_designer, temp_activity))

            up_plan = {
                "Preform": "P_PLAN_STATUS",
                "Assembly": "A_PLAN_STATUS",
                "Assembly Check": "AC_PLAN_STATUS",
                "Detailing": "D_PLAN_STATUS",
                "Checking": "C_PLAN_STATUS",
                "Correction": "CR_PLAN_STATUS",
                "Second Check": "SC_PLAN_STATUS",
                "Issue": "I_PLAN_STATUS"
            }

            arg3 = up_plan[temp_activity]

            # Execute the update query
            c.execute(f"UPDATE MOLD_TABLE SET {arg3}={arg3}-?,PRE_PLAN_STATUS=? WHERE REQ_ID=?", (1, 1, self.req_id.get()))

            conn.commit()
            conn.close()

            get_mold_plan(temp_mold_no)

            self.ch_start_date.set("")
            self.ch_days.set("")
            self.ch_designer.set("")

        def submit():
            pass

        # Frame contain mold information
        self.mold_details = ttk.LabelFrame(self, text="Mold Information")
        self.mold_details.place(x=20, y=20, width=650, height=260)
        self.mold_details.columnconfigure((0, 1), weight=1)

        # Frame contain current mold plan and widgets to update plan
        self.planning_details = ttk.LabelFrame(self, text="Planning Information")
        self.planning_details.place(x=20, y=550, width=650, height=150)
        self.planning_details.columnconfigure(0, weight=2)
        self.planning_details.columnconfigure((1, 2), weight=0)
        self.planning_details.columnconfigure((3, 4, 5), weight=3)
        self.planning_details.columnconfigure(6, weight=1)

        # Available Designers tree view
        self.designer_details = ttk.LabelFrame(self, text="Available Designers")
        self.designer_details.place(x=680, y=20, width=575, height=260)

        columns = ('design', 'date1', 'date2', 'date3', 'date4', 'initial')
        self.tree = ttk.Treeview(self.designer_details, columns=columns, show='headings')
        self.tree.place(x=0, y=5, width=573, height=238)

        self.scrollbar_v = ttk.Scrollbar(self.designer_details, orient='vertical', command=self.tree.yview)
        self.scrollbar_v.place(x=1135, y=10, width=20, height=210)

        self.tree.heading('design', text='Designer')
        self.tree.column('design', anchor=CENTER, stretch=NO, minwidth=90, width=80)
        self.tree.heading('date1', text='Day')
        self.tree.column('date1', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('date2', text='Day')
        self.tree.column('date2', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('date3', text='Day')
        self.tree.column('date3', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('date4', text='Day')
        self.tree.column('date4', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('initial', text='Day')
        self.tree.column('initial', anchor=CENTER, stretch=YES, minwidth=70, width=80)

        # self.tree.bind("<Double-1>", on_double_click)
        self.tree.configure(yscrollcommand=self.scrollbar_v.set)

        # Mold Planning
        self.mold_plan_details = Frame(self, width=650, height=250)
        self.mold_plan_details.place(x=20, y=300)

        self.label_plan = ttk.Label(self.mold_plan_details, text="Mold Plan Information:")
        self.label_plan.place(x=0, y=10)

        columns = ('reqid', 'md_no', 'date', 'designer', 'activity', 'days', 'status')
        self.data_tree = ttk.Treeview(self.mold_plan_details, columns=columns, show='headings')
        self.data_tree.place(x=0, y=35, width=637, height=210)

        self.scrollbar_v = ttk.Scrollbar(self.mold_plan_details, orient='vertical', command=self.data_tree.yview)
        self.scrollbar_v.place(x=637, y=35, width=13, height=210)

        self.data_tree.heading('reqid', text='Request ID')
        self.data_tree.column('reqid', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('md_no', text='Mold No')
        self.data_tree.column('md_no', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('date', text='Start Date')
        self.data_tree.column('date', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('designer', text='Designer')
        self.data_tree.column('designer', anchor=CENTER, stretch=NO, minwidth=60, width=75)
        self.data_tree.heading('activity', text='Activity')
        self.data_tree.column('activity', anchor=CENTER, stretch=NO, minwidth=60, width=150)
        self.data_tree.heading('days', text='Days')
        self.data_tree.column('days', anchor=CENTER, stretch=NO, minwidth=60, width=75)
        self.data_tree.heading('status', text='Status')
        self.data_tree.column('status', anchor=CENTER, stretch=NO, minwidth=60, width=75)

        self.data_tree.bind('<<TreeviewSelect>>', change_plan)

        # Mold plan details
        self.mold_plan_details = Frame(self, bd=0, bg='red')
        self.mold_plan_details.place(x=680, y=300, width=575, height=400)

        # //New mold tree view - nothing is planned// #
        # data = get_new_entry(self.MDShdb)
        data = '1'

        self.new_entry_label = ttk.LabelFrame(self.mold_plan_details, text=f"New Mold : {len(data)}")
        self.new_entry_label.place(x=0, y=0, width=185, height=400)

        columns = ('info', 'mold')
        self.new_entry_tree = ttk.Treeview(self.new_entry_label, columns=columns, show='headings')
        self.new_entry_tree.place(x=0, y=5, width=170, height=378)

        self.scrollbar_v = ttk.Scrollbar(self.new_entry_label, orient='vertical', command=self.new_entry_tree.yview)
        self.scrollbar_v.place(x=170, y=5, width=13, height=378)

        self.new_entry_tree.heading('info', text='Info Date')
        self.new_entry_tree.column('info', anchor=CENTER, stretch=NO, minwidth=75, width=70)
        self.new_entry_tree.heading('mold', text='Mold No')
        self.new_entry_tree.column('mold', anchor=CENTER, stretch=NO, minwidth=100, width=95)

        self.new_entry_tree.bind('<Double-1>', lambda event, arg=self.new_entry_tree: update_info(event, arg))

        for row in data:
            self.new_entry_tree.insert('', END, values=row)

        # //Short Plan tree view - some activity is planned// #
        # short_plan_data = get_short_plan(self.MDShdb)
        short_plan_data = '1'

        self.short_plan_details = ttk.LabelFrame(self.mold_plan_details, text=f"Short Plan : {len(short_plan_data)}")
        self.short_plan_details.place(x=195, y=0, width=185, height=400)

        columns = ('info', 'mold')
        self.short_plan_tree = ttk.Treeview(self.short_plan_details, columns=columns, show='headings')
        self.short_plan_tree.place(x=0, y=5, width=170, height=378)

        self.scrollbar_v = ttk.Scrollbar(self.short_plan_details, orient='vertical', command=self.short_plan_tree.yview)
        self.scrollbar_v.place(x=170, y=5, width=13, height=378)

        self.short_plan_tree.heading('info', text='Info Date')
        self.short_plan_tree.column('info', anchor=CENTER, stretch=NO, minwidth=75, width=70)
        self.short_plan_tree.heading('mold', text='Mold No')
        self.short_plan_tree.column('mold', anchor=CENTER, stretch=NO, minwidth=100, width=95)

        self.short_plan_tree.bind('<Double-1>', lambda event, arg=self.short_plan_tree: update_info(event, arg))

        for row in short_plan_data:
            self.short_plan_tree.insert('', END, values=row)

        # //Complete Plan// #
        # complete_plan = get_complete_plan(self.MDShdb)
        complete_plan = '1'

        self.complete_plan_details = ttk.LabelFrame(self.mold_plan_details, text=f"Complete Plan : {len(complete_plan)}")
        self.complete_plan_details.place(x=390, y=0, width=185, height=400)

        columns = ('info', 'mold')
        self.complete_plan_tree = ttk.Treeview(self.complete_plan_details, columns=columns, show='headings')
        self.complete_plan_tree.place(x=0, y=5, width=170, height=378)

        self.scrollbar_v = ttk.Scrollbar(self.complete_plan_details, orient='vertical', command=self.complete_plan_tree.yview)
        self.scrollbar_v.place(x=170, y=5, width=13, height=378)

        self.complete_plan_tree.heading('info', text='Info Date')
        self.complete_plan_tree.column('info', anchor=CENTER, stretch=NO, minwidth=75, width=70)
        self.complete_plan_tree.heading('mold', text='Mold No')
        self.complete_plan_tree.column('mold', anchor=CENTER, stretch=NO, minwidth=100, width=95)

        self.complete_plan_tree.bind('<Double-1>', lambda event, arg=self.complete_plan_tree: update_info(event, arg))

        for row in complete_plan:
            self.complete_plan_tree.insert('', END, values=row)

        # Month Combobox
        month_values = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        self.month_Comb = ttk.Combobox(self, textvariable=self.month, width=12, values=month_values)
        self.month_Comb.place(x=20, y=730)

        # Heatmap Button
        self.heatmap_btn = ttk.Button(self, text="Heatmap", command=heatmap)
        self.heatmap_btn.place(x=130, y=730)

        # Submit Button
        self.submit_btn = ttk.Button(self, text="Submit", command=submit)
        self.submit_btn.place(x=575, y=730)

        # Switch Mold Information and Mold Info Button
        self.switch_btn = ttk.Button(self, text=">", command=refresh, width=1)
        self.switch_btn.place(x=1225, y=730)

        # Designers group combobox
        mc_model_values2 = ('ASB-70DPH', 'ASB-70DPW', 'ASB-50MB', 'ASB-12M', 'PF', 'Preform', 'Modification', 'Parts Order', 'ECM')
        self.Designer_group_label = ttk.Label(self, text='Designers Group:')
        self.Designer_group_label.place(x=250, y=735)
        self.Designer_group_Comb = ttk.Combobox(self, textvariable=self.DegnModel, width=15, values=mc_model_values2)
        self.Designer_group_Comb.place(x=360, y=730)

        # Refresh button to update designer's tree view
        self.refresh_btn = ttk.Button(self, text="\u27F3", command=get_designers)
        self.refresh_btn.place(x=485, y=730, width=40)

        # call required functions
        mold_information()


class XYZ(object):
    def __init__(self, master):
        self.master = master
        self.master.title("Mold Design")
        # self.master.geometry("650x500")
        self.master.state('zoomed')
        Planning()


from ttkbootstrap import Style
# The main function
if __name__ == "__main__":
    root = Tk()
    style = Style(theme='cyborg')

    obj = XYZ(root)
    root.mainloop()
