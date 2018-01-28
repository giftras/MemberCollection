from tkinter import *
from tkinter import ttk
import sqlite3
from twilio.rest import Client
from credentials import account_sid, auth_token, my_cell, my_twilio

class Members:
    db_name = 'member.db'
    #creat GUI
    def __init__(self, wind):
        self.wind = wind
        self.wind.title ('Member Collection')

        #Create frame
        frame = LabelFrame (self.wind, text='Add new record')
        frame.grid (row=0, column=1)

        Label (frame, text='Name:').grid (row=1, column=1)
        self.name = Entry (frame)
        self.name.grid (row=1, column=2)

        Label (frame, text='Phone number:').grid (row=2, column=1)
        self.phonenumber = Entry (frame)
        self.phonenumber.grid (row=2, column=2)

        Label (frame, text='Points:').grid (row=3, column=1)
        self.point = Entry (frame)
        self.point.grid (row=3, column=2)

        ttk.Button (frame, text = 'Add record', command = self.adding).grid (row=4, column=2)
        self.message = Label (text = '', fg = 'red')
        self.message.grid (row = 4, column = 1)

        self.tree = ttk.Treeview (height = 10, columns = 2)
        self.tree.grid (row = 5, column=0, columnspan =3)
        self.tree.heading('#0', text = 'Name', anchor = W)
        self.tree.heading(2 , text = 'Points', anchor = W)

        self.blank = Label (text = '', fg = 'white')
        self.blank.grid (row = 6, column = 0)
        ttk.Button (text = 'Delete record', command = self.deleting).grid (row=7, column = 0)
        ttk.Button (text = 'Add point', command = self.editing).grid (row=7, column = 1)
        ttk.Button (text = 'Notify Point', command = self.sent_message).grid (row=7, column = 2)
        self.blank1 = Label (text = '', fg = 'white')
        self.blank1.grid (row = 8, column = 0)

        self.viewing_records ()
    #connect the database
    def run_query (self, query, parameters =() ):
        with sqlite3.connect (self.db_name) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute (query, parameters)
            conn.commit()
        return query_result
    #view the record from database
    def viewing_records (self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = 'SELECT * FROM memberinfo'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert('', 0, text = row[1], values = row[2])
    #3 fields should not be null
    def validation (self):
        return self.name.get().strip() != '' and len (self.point.get()) != 0 and len (self.phonenumber.get()) == 10

    #If it not null then add to info to database
    def adding (self):
        if self.validation():
            query = 'INSERT INTO memberinfo VALUES (?, ?, ?)'
            parameters = (self.phonenumber.get(), self.name.get(), self.point.get())
            self.run_query(query, parameters)
            self.message ['text'] = 'Record {} added'.format(self.name.get())
            self.name.delete(0, END)
            self.phonenumber.delete(0, END)
            self.point.delete(0, END)
        else:
            self.message ['text'] = 'Please fills name, phone number with 10 digits, or points'
        self.viewing_records()
#delete the selected item
    def deleting (self):
        self.message ['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Please select the record!'
            return
        self.message ['text'] = ''
        name = self.tree.item(self.tree.selection()) ['text']
        query = 'DELETE FROM memberinfo WHERE name = ?'
        self.run_query(query, (name, ))
        self.message['text'] = 'Record {} is deleted.'.format(name)
        self.viewing_records()
#editing selected item
    def editing (self):
        self.message ['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Please select the record!'
            return
        name = self.tree.item (self.tree.selection())['text']
        old_point = self.tree.item(self.tree.selection())['values'][0]


        #create new window
        self.edit_wind = Toplevel()
        self.edit_wind.title ('Add point')

        Label (self.edit_wind, text = 'Name:').grid (row =0, column=1)
        Label (self.edit_wind, text = name).grid(row =0, column=2, sticky = W)
        Label (self.edit_wind, text = 'Point:').grid (row =1, column=1)
        Label (self.edit_wind, text = old_point).grid(row =1, column=2, sticky = W)
        Label (self.edit_wind, text = 'Add Point:').grid (row =2, column =1)
        new_point = Entry(self.edit_wind)
        new_point.grid (row =2, column=2)

        Button (self.edit_wind, text = 'Add', command = lambda : self.edit_records (name, new_point.get(), old_point)).grid (row =3, column=1, sticky = W)
        Button (self.edit_wind, text = 'Redeem', command = lambda : self.redeem_records (name, old_point)).grid (row =3, column=2, sticky = W)
        self.edit_wind.mainloop()

    def edit_records (self, name, new_point, old_point):
        query = 'UPDATE memberinfo SET points = ? WHERE name = ? AND points = ?'
        addpoint = int(new_point) + int(old_point)
        parameters = (addpoint, name, old_point)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = 'Point of {} added.'.format(name) + ' Now has {} points.'.format(addpoint)
        self.viewing_records()

    def redeem_records (self, name, old_point):
        query = 'UPDATE memberinfo SET points = ? WHERE name = ? AND points = ?'
        parameters = ( 0 , name, old_point)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = 'Point of {} redeemed.'.format(name)
        self.viewing_records()

    #sent message

    def sent_message (self):
        self.message ['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Please select the record!'
            return
        name = self.tree.item (self.tree.selection())['text']
        point = self.tree.item(self.tree.selection())['values'][0]
        client = Client(account_sid, auth_token)

        my_msg = name +' has ' + str(point) + ' points.'

        message = client.messages.create(to=my_cell, from_=my_twilio,
                                     body=my_msg)

wind = Tk ()
application = Members(wind)
wind.mainloop ()
