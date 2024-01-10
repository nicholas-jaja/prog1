import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import pmdarima as pm



def forecast(n_days):
    cursor.execute("SELECT * FROM input_puth")
    rows = cursor.fetchall()
    path_input=rows[-1][-1]


    data = pd.read_csv(path_input)
    data['date']=pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    endog=data.sales
    exog=data.price


    model_new_exog=pm.auto_arima(exog,seasonal=True,m=7,information_criterion='aic',trace=True,error_action='ignore',stepwise=True,suppress_warnings=True)
    results_new_exog=model_new_exog.fit(exog)
    new_exog = results_new_exog.predict(n_periods=n_days)
    
    
    model=pm.auto_arima(
                        endog,
                        exogenous=exog,
                        seasonal=True,
                        m=7,
                        d=0,
                        D=1,
                        information_criterion='aic',
                        trace=True,
                        error_action='ignore',
                        stepwise=True,
                        suppress_warnings=True
                        )
    results=model.fit(endog, exogenous=exog)
    forecast_values = results.predict(n_periods=n_days, exogenous=new_exog)
    forecast_values = pd.Series(forecast_values.values, index=forecast_values.index, name='sales')
    

    forecast_values_df = pd.DataFrame({'date': forecast_values.index, 'sales': forecast_values.values})
    forecast_values_df["date"]=forecast_values_df["date"]
    forecast_values_df.to_sql('forecast_sales', database, if_exists='replace', index=True)


    plt.clf()
    plt.figure(figsize=(8, 6), dpi=80)
    endog.plot(label='input data')
    forecast_values.plot(label='forecast', color='green')
    plt.title('sales graph')
    plt.xlabel('date', labelpad=-1)
    plt.ylabel('sales')
    plt.legend()
    plt.savefig('C:/Program Files/sarimax-forecast/graf1.png')
    forecast_image = tk.PhotoImage(file='C:/Program Files/sarimax-forecast/graf1.png')
    forecast_label.configure(image=forecast_image)
    forecast_label.image=forecast_image


def compare():
    forecast_values_db=pd.read_sql_query("SELECT date, sales FROM forecast_sales", database)
    forecast_values_db['date']=pd.to_datetime(forecast_values_db['date'])
    forecast_values_db.set_index('date', inplace=True)
    forecast_values=forecast_values_db.sales


    cursor.execute("SELECT * FROM test_puth")
    rows = cursor.fetchall()
    path_test=rows[-1][-1]
    data_test=pd.read_csv(path_test)
    data_test['date']=pd.to_datetime(data_test['date'])
    data_test.set_index('date', inplace=True)
    test_endog=data_test.sales


    table_height=min(len(test_endog),len(forecast_values))
    error2=0.0
    for i in range(table_height):
        real=test_endog.values[i]
        predict=forecast_values.values[i]
        difference=abs(real-predict)
        error2=error2+difference
    error2=error2/table_height

    len_test=len(test_endog)
    up_error=test_endog.copy()
    for i in range(len_test):
        up_error.values[i]=up_error.values[i]+error2
    down_error=test_endog.copy()
    for i in range(len_test):
        down_error.values[i]=down_error.values[i]-error2


    plt.clf()
    test_endog.plot(label='real data', color='orange')
    forecast_values.plot(label='forecast', color='green')
    down_error.plot(label='mean error', color='#fbb4b4', linestyle='dashed')
    up_error.plot(label='mean error', color='#e18d8d', linestyle='dashed')
    plt.title('comparison of forecast and real data')
    plt.xlabel('date', labelpad=-1)
    plt.ylabel('sales')
    plt.legend()
    plt.savefig('C:/Program Files/sarimax-forecast/graf2.png')
    compare_image = tk.PhotoImage(file='C:/Program Files/sarimax-forecast/graf2.png')
    compare_label.configure(image=compare_image)
    compare_label.image=compare_image


#function for button click

def press_button_input():
    filepath = askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
    label_input["text"]=filepath
    cursor.execute("INSERT INTO input_puth (path) VALUES (?)", (filepath,))
    database.commit()

def press_button_output():
    filepath = asksaveasfilename(
        filetypes=[("CSV Files", "*.csv")]
        )
    save_data = pd.read_sql_query("SELECT date, sales FROM forecast_sales", database)
    save_data['date']=pd.to_datetime(save_data['date'])
    save_data.to_csv(filepath, index=False)

def press_button_open_test():
    filepath = askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
    label_test["text"]=filepath
    cursor.execute("INSERT INTO test_puth (path) VALUES (?)", (filepath,))
    database.commit()

def press_button_do_test():
    compare()

def press_button_forecast7():
    forecast(7)

def press_button_forecast14():
    forecast(14)

def press_button_forecast28():
    forecast(28)

def press_button_show_table():
    cursor.execute("SELECT date, sales FROM forecast_sales")
    rows = cursor.fetchall()
    window_table1 = tk.Toplevel(window)
    window_table1.title("forecast values")
    window_table1.iconbitmap('C:/Program Files/sarimax-forecast/empty.png')
    table1 = ttk.Treeview(window_table1, columns=(1,2), show='headings', height=len(rows))
    table1.heading(1, text='date')
    table1.heading(2, text='sales')
    for row in rows:
        row=[row[0][:10], row[1]]
        table1.insert("", "end", values=row)
    table1.pack()

def press_button_show_more():
    cursor.execute("SELECT * FROM test_puth")
    rows = cursor.fetchall()
    path_test=rows[-1][-1]
    data_test=pd.read_csv(path_test)
    cursor.execute("SELECT date, sales FROM forecast_sales")
    data_forecast = cursor.fetchall()
    table_height=min(len(data_test),len(data_forecast))

    window_table2 = tk.Toplevel(window)
    window_table2.title("comparison")
    window_table2.iconbitmap('C:/Program Files/sarimax-forecast/empty.png')
    window_table2.grid_rowconfigure(1, minsize=70)
    table2 = ttk.Treeview(window_table2, columns=(1,2,3,4), show='headings', height=table_height)
    table2.heading(1, text='date')
    table2.heading(2, text='real sales')
    table2.heading(3, text='forecast sales')
    table2.heading(4, text='difference')
    error=0.0
    error2=0.0
    for i in range(table_height):
        real=data_test["sales"][i]
        predict=data_forecast[i][1]
        difference=abs(real-predict)
        error=error+(difference/real)
        error2=error2+difference
        row = [data_forecast[i][0][:10], real, predict, difference]
        table2.insert("", "end", values=row)
    error=(error/table_height)*100
    error_str=str(error)
    error2=error2/table_height
    error2_str=str(error2)
    table2.grid(row=0, column=0, columnspan=4)
    label_error = tk.Label(master=window_table2, text="MAPE error = "+error_str+"%")
    label_error.grid(row=2, column=0)
    label_error2 = tk.Label(master=window_table2, text="MAE error = "+error2_str)
    label_error2.grid(row=1, column=0)


#create database

database = sqlite3.connect('C:/Program Files/sarimax-forecast/main.db')
cursor = database.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS input_puth (
        id INTEGER PRIMARY KEY,
        path TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_puth (
        id INTEGER PRIMARY KEY,
        path TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS forecast_sales (
        id INTEGER PRIMARY KEY,
        date DATE,
        sales INTEGER
    )
''')

#start action
cursor.execute("DELETE FROM input_puth")
cursor.execute("DELETE FROM test_puth")
cursor.execute("DELETE FROM forecast_sales")



#interface

window = tk.Tk()
window.title("")
window.iconbitmap('C:/Program Files/sarimax-forecast/empty.png')
window.grid_rowconfigure(0, minsize=40)
window.grid_rowconfigure(1, minsize=40)
window.grid_rowconfigure(3, minsize=40)
window.grid_columnconfigure(3, minsize=40)
window.grid_columnconfigure(7, minsize=40)

button_input = tk.Button(
    master=window,
    text="open file",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_input
)
button_input.grid(row=0, column=0)

label_input = tk.Label(master=window, width=60, borderwidth=1, relief="solid")
label_input.grid(row=0, column=1, columnspan=2)

button_forecast7 = tk.Button(
    master=window,
    text="forecast on week",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_forecast7
)
button_forecast7.grid(row=1, column=0)

button_forecast14 = tk.Button(
    master=window,
    text="forecast on 2 week",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_forecast14
)
button_forecast14.grid(row=1, column=1)

button_forecast28 = tk.Button(
    master=window,
    text="forecast on 4 week",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_forecast28
)
button_forecast28.grid(row=1, column=2)

forecast_image = tk.PhotoImage(file='C:/Program Files/sarimax-forecast/empty.png')
forecast_label = tk.Label(window, image=forecast_image)
forecast_label.grid(row=2, column=0, columnspan=3)

button_show_table = tk.Button(
    master=window,
    text="show table",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_show_table
)
button_show_table.grid(row=3, column=0)

button_output = tk.Button(
    master=window,
    text="save results",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_output
)
button_output.grid(row=3, column=1)

button_open_test = tk.Button(
    master=window,
    text="open test file",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_open_test
)
button_open_test.grid(row=0, column=4)

label_test = tk.Label(master=window, width=60, borderwidth=1, relief="solid")
label_test.grid(row=0, column=5, columnspan=2)

button_do_test = tk.Button(
    master=window,
    text="test",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_do_test
)
button_do_test.grid(row=1, column=4)

compare_image = tk.PhotoImage(file='C:/Program Files/sarimax-forecast/empty.png')
compare_label = tk.Label(window, image=compare_image)
compare_label.grid(row=2, column=4, columnspan=3)

button_show_more = tk.Button(
    master=window,
    text="show more",
    width=20,
    height=1,
    background="#09BA5C",
    foreground="black",
    borderwidth=2,
    relief="raised",
    command=press_button_show_more
)
button_show_more.grid(row=3, column=5)

window.mainloop()




