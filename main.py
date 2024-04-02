"""
Copyright {2018} {Viraj Mavani}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0
"""

from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.ttk import Treeview
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta

config = {
  'user': 'root',
  'password': '123456',
  'host': '127.0.0.1',
  'database': 'LIBRARYDB',
  'raise_on_warnings': True
}

try:
    cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

cursor = None
todays_date = datetime.today()

class MainGUI:
    def __init__(self, master):
        self.parent = master
        self.parent.title("Library Management System")
        self.frame = Frame(self.parent, width=1000, height=500)
        self.frame.grid(row=0, column=0)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_propagate(False)

        # Parameter Initialization
        self.search_string = None
        self.data = None
        self.borrowerId = None
        self.bookForCheckOutIsbn = None

        # Frame for the welcome message and header
        self.HeaderFrame = Frame(self.frame)
        self.HeaderFrame.grid(row=0, column=0, sticky=N)
        self.HeaderFrame.grid_rowconfigure(0, weight=1)
        self.HeaderFrame.grid_columnconfigure(0, weight=1)
        self.HeaderLabel = Label(self.HeaderFrame, text='Welcome to the Library Management System!')
        self.HeaderLabel.grid(row=0, column=0)
        self.HeaderLabel.grid_rowconfigure(0, weight=1)
        self.HeaderLabel.grid_columnconfigure(0, weight=1)
        self.SearchLabel = Label(self.HeaderFrame, text='Search for books here!')
        self.SearchLabel.grid(row=1, column=0)
        self.SearchLabel.grid_rowconfigure(1, weight=1)
        self.SearchLabel.grid_columnconfigure(0, weight=1)

        # Search Frame
        self.SearchFrame = Frame(self.frame)
        self.SearchFrame.grid(row=1, column=0, sticky=N)
        self.SearchFrame.grid_rowconfigure(1, weight=1)
        # self.SearchFrame.grid_columnconfigure(0, weight=1)
        self.SearchLabel = Label(self.SearchFrame, text='Search')
        self.SearchLabel.grid(row=0, column=0)
        self.SearchLabel.grid_rowconfigure(0, weight=1)
        # self.SearchLabel.grid_columnconfigure(0, weight=1)
        self.SearchTextBox = Entry(self.SearchFrame, text='Enter search string here...', width=70)
        self.SearchTextBox.grid(row=1, column=0)
        self.SearchTextBox.grid_rowconfigure(1, weight=1)
        self.SearchButton = Button(self.SearchFrame, text='Search', command=self.search)
        self.SearchButton.grid(row=2, column=0)
        self.SearchButton.grid_rowconfigure(2, weight=1)

        # Search Result Frame
        self.ActiveArea = Frame(self.frame)
        self.ActiveArea.grid(row=2, column=0, sticky=N)
        self.ActiveArea.grid_rowconfigure(2, weight=1)
        self.ResultTreeview = Treeview(self.ActiveArea, columns=["ISBN", "Book Title", "Author(s)", "Availability"])
        self.ResultTreeview.grid(row=0, column=0)
        self.ResultTreeview.grid_rowconfigure(0, weight=1)
        self.ResultTreeview.heading('#0', text="ISBN")
        self.ResultTreeview.heading('#1', text="Book Title")
        self.ResultTreeview.heading('#2', text="Author(s)")
        self.ResultTreeview.heading('#3', text="Availability")
        self.ResultTreeview.bind('<ButtonRelease-1>', self.selectBookForCheckout)

        # Interaction Frame
        self.MajorFunctions = Frame(self.frame)
        self.MajorFunctions.grid(row=3, column=0, sticky=N)
        self.MajorFunctions.grid_rowconfigure(3, weight=1)
        self.checkOutBtn = Button(self.MajorFunctions, text="Check Out Book", command=self.check_out)
        self.checkOutBtn.grid(row=0, column=0, padx=10, pady=10)
        self.checkOutBtn.grid_rowconfigure(0, weight=1)
        self.checkOutBtn.grid_columnconfigure(0, weight=1)
        self.checkInBtn = Button(self.MajorFunctions, text="Check In Book", command=self.check_in)
        self.checkInBtn.grid(row=0, column=1, padx=10, pady=10)
        self.checkOutBtn.grid_rowconfigure(0, weight=1)
        self.checkOutBtn.grid_columnconfigure(1, weight=1)
        self.updateFinesBtn = Button(self.MajorFunctions, text="Updates Fines", command=self.update_fines)
        self.updateFinesBtn.grid(row=1, column=0, padx=10, pady=10)
        self.payFinesBtn = Button(self.MajorFunctions, text="Pay Fines", command=self.pay_fines)
        self.payFinesBtn.grid(row=1, column=1, padx=10, pady=10)
        self.changeDayBtn = Button(self.MajorFunctions, text="Change Day", command=self.change_day)
        self.changeDayBtn.grid(row=1, column=2, padx=10, pady=10)
        self.addBorrowerBtn = Button(self.MajorFunctions, text="Add New Borrower", command=self.add_borrower)
        self.addBorrowerBtn.grid(row=0, column=2, padx=10, pady=10)

    def change_day(self):
        global todays_date
        todays_date = todays_date + timedelta(days=1)
        print(todays_date)

    def search(self):
        self.search_string = self.SearchTextBox.get()
        cursor = cnx.cursor()
        cursor.execute("select BOOK.isbn, BOOK.title, AUTHORS.fullname from BOOK join BOOK_AUTHORS on "
                            "BOOK.isbn = BOOK_AUTHORS.isbn join AUTHORS on BOOK_AUTHORS.author_id = AUTHORS.author_id "
                            "where BOOK.title like concat('%', '" + self.search_string + "', '%') or "
                            "AUTHORS.fullname like concat('%', '" + self.search_string + "', '%') or "
                            "BOOK.isbn like concat('%', '" + self.search_string + "', '%')")

        self.data = cursor.fetchall()
        self.view_data()

    def view_data(self):
        """
        View data on Treeview method.
        """
        self.ResultTreeview.delete(*self.ResultTreeview.get_children())
        for elem in self.data:
            cursor = cnx.cursor()
            cursor.execute("SELECT EXISTS(SELECT BOOK_LOANS.isbn from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(elem[0]) + "')")
            result = cursor.fetchall()
            if result == [(0,)]:
                availability = "Available"
            else:
                cursor = cnx.cursor()
                cursor.execute("SELECT BOOK_LOANS.Date_in from BOOK_LOANS where BOOK_LOANS.isbn = '" + str(elem[0]) + "'")
                result = cursor.fetchall()
                if result[-1][0] is None:
                    availability = "Not Available"
                else:
                    availability = "Available"
            self.ResultTreeview.insert('', 'end', text=str(elem[0]),
                                       values=(elem[1], elem[2], availability))

    def selectBookForCheckout(self, a):
        curItem = self.ResultTreeview.focus()
        self.bookForCheckOutIsbn = self.ResultTreeview.item(curItem)['text']

    def check_out(self):
        if self.bookForCheckOutIsbn is None:
            messagebox.showinfo("Attention!", "Select Book First!")
            return None
        self.borrowerId = simpledialog.askstring("Check Out Book", "Enter Borrower ID")
        cursor = cnx.cursor()
        cursor.execute("SELECT EXISTS(SELECT Card_no from BORROWERS WHERE BORROWERS.Card_no = '" + str(self.borrowerId) + "')")
        result = cursor.fetchall()

        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower not in Database!")
            return None
        else:
            count = 0
            cursor = cnx.cursor()
            cursor.execute("SELECT BOOK_LOANS.Date_in from BOOK_LOANS WHERE BOOK_LOANS.Card_no = '" + str(self.borrowerId) + "'")
            result = cursor.fetchall()
            for elem in result:
                if elem[0] is None:
                    count += 1
            if count >= 3:
                messagebox.showinfo("Not Allowed!", "Borrower has loaned 3 books already!")
                return None
            else:
                cursor = cnx.cursor()
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                cursor.execute("INSERT INTO BOOK_LOANS (ISBN, Card_no, Date_out, Due_date) VALUES ('" + self.bookForCheckOutIsbn + "', '" + self.borrowerId + "', '" + str(todays_date) + "', '" + str(todays_date + timedelta(days=14)) + "')")
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                cnx.commit()
                cursor = cnx.cursor()
                cursor.execute("SELECT MAX(Loan_Id) FROM BOOK_LOANS")
                result = cursor.fetchall()
                loan_id = result[0][0]
                cursor.execute("INSERT INTO FINES (Loan_Id, fine_amt, paid) VALUES ('" + str(loan_id) + "', '0.00', '0')")
                cnx.commit()
                messagebox.showinfo("Done", "Book Loaned Out!")

    def check_in(self):
        self.checkInWindow = Toplevel(self.parent)
        self.checkInWindow.title("Check In Here")
        self.app = CheckIn(self.checkInWindow)

    def update_fines(self):
        cursor = cnx.cursor()
        cursor.execute("SELECT BOOK_LOANS.Loan_Id, BOOK_LOANS.Date_in, BOOK_LOANS.Due_date FROM BOOK_LOANS")
        result = cursor.fetchall()
        for record in result:
            date_in = record[1]
            date_due = record[2]
            if date_in is None:
                date_in = todays_date
            diff = date_in.date() - date_due.date()

            if diff.days > 0:
                fine = int(diff.days) * 0.25
            else:
                fine = 0

            cursor = cnx.cursor()
            cursor.execute("UPDATE FINES SET FINES.fine_amt = '" + str(fine) + "' WHERE FINES.Loan_Id = '" + str(record[0]) + "'")
            cnx.commit()
        messagebox.showinfo("Info", "Fines have been computed!")

    def pay_fines(self):
        self.newPayFinesWindow = Toplevel(self.parent)
        self.newPayFinesWindow.title("Pay Fines")
        self.app1 = PayFines(self.newPayFinesWindow)

    def add_borrower(self):
        self.newBorrowerWindow = Toplevel(self.parent)
        self.newBorrowerWindow.title("Add New Borrower")
        self.newapp = AddBorrower(self.newBorrowerWindow)


class CheckIn:
    def __init__(self, master):
        self.parent = master

        self.bookForCheckInID = None
        self.search_string = None
        self.data = None

        self.searchLabel = Label(self.parent, text="Search here: Borrower ID, Borrower Name or ISBN")
        self.searchLabel.grid(row=0, column=0, padx=20, pady=20)
        self.searchTextBox = Entry(self.parent)
        self.searchTextBox.grid(row=1, column=0)
        self.searchBtn = Button(self.parent, text="Search", command=self.search_book_loans)
        self.searchBtn.grid(row=2, column=0)
        self.table = Treeview(self.parent, columns=["Loan ID", "ISBN", "Borrower ID", "Title"])
        self.table.grid(row=3, column=0)
        self.table.heading('#0', text="Loan ID")
        self.table.heading('#1', text="ISBN")
        self.table.heading('#2', text="Borrower ID")
        self.table.heading('#3', text="Book Title")
        self.table.bind('<ButtonRelease-1>', self.select_book_for_checkin)
        self.checkInBtn = Button(self.parent, text="Check In", command=self.check_in)
        self.checkInBtn.grid(row=4, column=0)

    def search_book_loans(self):
        self.search_string = self.searchTextBox.get()
        cursor = cnx.cursor()
        cursor.execute("select BOOK_LOANS.Loan_Id, BOOK_LOANS.ISBN, BOOK_LOANS.Card_no, BOOK.title, BOOK_LOANS.Date_in from BOOK_LOANS "
                       "join BORROWERS on BOOK_LOANS.Card_no = BORROWERS.Card_no "
                       "join BOOK on BOOK_LOANS.ISBN = BOOK.ISBN "
                       "where BOOK_LOANS.ISBN like concat('%', '" + self.search_string + "', '%') or "
                        "BORROWERS.Fname like concat('%', '" + self.search_string + "', '%') or "
                        "BORROWERS.Lname like concat('%', '" + self.search_string + "', '%') or "
                        "BOOK_LOANS.Card_no like concat('%', '" + self.search_string + "', '%')")

        self.data = cursor.fetchall()
        self.view_data()

    def view_data(self):
        """
        View data on Treeview method.
        """
        self.table.delete(*self.table.get_children())
        for elem in self.data:
            if elem[4] is None:
                self.table.insert('', 'end', text=str(elem[0]), values=(elem[1], elem[2], elem[3]))

    def select_book_for_checkin(self, a):
        curItem = self.table.focus()
        self.bookForCheckInID = self.table.item(curItem)['text']

    def check_in(self):
        if self.bookForCheckInID is None:
            messagebox.showinfo("Attention!", "Select Book to Check In First!")
            return None

        cursor = cnx.cursor()

        cursor.execute("SELECT BOOK_LOANS.Date_in FROM BOOK_LOANS WHERE BOOK_LOANS.Loan_Id = '" + str(self.bookForCheckInID) + "'")

        result = cursor.fetchall()

        if result[0][0] is None:
            cursor.execute("UPDATE BOOK_LOANS SET BOOK_LOANS.Date_in = '" + str(todays_date) + "' WHERE BOOK_LOANS.Loan_Id = '"
                           + str(self.bookForCheckInID) + "'")
            cnx.commit()
            messagebox.showinfo("Done", "Book Checked In Successfully!")
            self.parent.destroy()
        else:
            return None


class AddBorrower:
    def __init__(self, master):
        self.parent = master

        self.titleLabel = Label(self.parent, text="Enter Details")
        self.titleLabel.grid(row=0, column=0, padx=20, pady=20)
        self.fnameLabel = Label(self.parent, text="First Name").grid(row=1, column=0, padx=10, pady=5)
        self.fnameTB = Entry(self.parent)
        self.fnameTB.grid(row=2, column=0, padx=10, pady=5)
        self.lnameLabel = Label(self.parent, text="Last Name").grid(row=3, column=0, padx=10, pady=5)
        self.lnameTB = Entry(self.parent)
        self.lnameTB.grid(row=4, column=0, padx=10, pady=5)
        self.ssnLabel = Label(self.parent, text="SSN").grid(row=5, column=0, padx=10, pady=5)
        self.ssnTB = Entry(self.parent)
        self.ssnTB.grid(row=6, column=0, padx=10, pady=5)
        self.addressLabel = Label(self.parent, text="Street Address").grid(row=7, column=0, padx=10, pady=5)
        self.addressTB = Entry(self.parent)
        self.addressTB.grid(row=8, column=0, padx=10, pady=5)
        self.cityLabel = Label(self.parent, text="City").grid(row=9, column=0, padx=10, pady=5)
        self.cityTB = Entry(self.parent)
        self.cityTB.grid(row=10, column=0, padx=10, pady=5)
        self.stateLabel = Label(self.parent, text="State").grid(row=11, column=0, padx=10, pady=5)
        self.stateTB = Entry(self.parent)
        self.stateTB.grid(row=12, column=0, padx=10, pady=5)
        self.numberLabel = Label(self.parent, text="Phone Number").grid(row=13, column=0, padx=10, pady=5)
        self.numberTB = Entry(self.parent)
        self.numberTB.grid(row=14, column=0, padx=10, pady=5)
        self.addBtn = Button(self.parent, text="Add", command=self.add_borrower)
        self.addBtn.grid(row=15, column=0, padx=10, pady=5)

    def add_borrower(self):
        ssn = self.ssnTB.get()
        cursor = cnx.cursor()
        cursor.execute("SELECT MAX(Card_no) from BORROWERS")
        new_card_no = int(cursor.fetchall()[0][0]) + 1
        new_card_no = str(new_card_no)
        cursor.execute("SELECT EXISTS(SELECT Ssn FROM BORROWERS WHERE BORROWERS.ssn = '" + str(ssn) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            address = ', '.join([self.addressTB.get(), self.cityTB.get(), self.stateTB.get()])
            cursor.execute("Insert into borrowers (Card_no, ssn, fname, lname, address, phone) Values ('" + new_card_no + "', '" + ssn + "', '" + str(self.fnameTB.get()) + "', '" + str(self.lnameTB.get()) + "', '" + str(address) + "', '" + str(self.numberTB.get()) + "')")
            cnx.commit()
            self.parent.destroy()
        else:
            messagebox.showinfo("Error", "Borrower Already Exists!")


class PayFines:
    def __init__(self, master):
        self.parent = master

        self.v = StringVar()

        self.borrowerLabel = Label(self.parent, text="Enter Borrower ID").grid(row=0, column=0, padx=20, pady=20)
        self.borrowerEntry = Entry(self.parent)
        self.borrowerEntry.grid(row=1, column=0, padx=20, pady=20)
        self.showFineBtn = Button(self.parent, text="Show Fines", command=self.show_fines).grid(row=2, column=0, padx=20, pady=20)
        self.fineLabel = Label(self.parent, textvariable=self.v)
        self.fineLabel.grid(row=3, column=0, padx=20, pady=20)
        self.payFineBtn = Button(self.parent, text="Pay Fine", command=self.pay_fine).grid(row=4, column=0, padx=20, pady=20)

    def show_fines(self):
        borrower_id = self.borrowerEntry.get()
        cursor = cnx.cursor()
        cursor.execute("SELECT EXISTS(SELECT Card_no FROM BORROWERS WHERE BORROWERS.Card_no = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower does not exist in data")
        else:
            cursor.execute("SELECT FINES.fine_amt, FINES.paid FROM FINES JOIN BOOK_LOANS ON FINES.Loan_Id = BOOK_LOANS.Loan_Id WHERE BOOK_LOANS.Card_no = '" + str(borrower_id) + "'")
            result = cursor.fetchall()
            total_fine = 0
            for elem in result:
                if elem[1] == 0:
                    total_fine += float(elem[0])

        self.v.set("Fine: $ " + str(total_fine))

    def pay_fine(self):
        borrower_id = self.borrowerEntry.get()
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT Card_no FROM BORROWERS WHERE BORROWERS.Card_no = '" + str(borrower_id) + "')")
        result = cursor.fetchall()
        if result == [(0,)]:
            messagebox.showinfo("Error", "Borrower does not exist in data")
        else:
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT FINES.Loan_Id FROM FINES JOIN BOOK_LOANS ON FINES.Loan_Id = BOOK_LOANS.Loan_Id WHERE BOOK_LOANS.Card_no = '" + str(
                    borrower_id) + "'")
            result = cursor.fetchall()
            for elem in result:
                cursor = cnx.cursor()
                cursor.execute("UPDATE FINES SET FINES.paid = 1 WHERE FINES.Loan_Id = '" + str(elem[0]) + "'")
                cnx.commit()
            messagebox.showinfo("Info", "Fines Paid!")
            self.parent.destroy()

if __name__ == '__main__':
    root = Tk()
    imgicon = PhotoImage(file='icon.gif')
    root.tk.call('wm', 'iconphoto', root._w, imgicon)
    tool = MainGUI(root)
    root.mainloop()
