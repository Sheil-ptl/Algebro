import tkinter as tk
from tkinter import *
from tkinter import ttk
# Use messagebox for message popups, like invalid info, or just letting the user know something
from tkinter import messagebox
#source: https://www.youtube.com/watch?v=TuLxsvK4svQ
#full tkinter course
#source: https://docs.python.org/3/library/tkinter.html
#tkinter documentation
#source: https://www.youtube.com/watch?v=X5yyKZpZ4vU
#formatting tkinter into classes for easier implementation
from database import *
from students import *
from instructor import *
from ml_engine import AlgebroML
import random
import os
import time


# Constant for the database name
DB_NAME = "algebro.db"
# __file__ in this case is main.py, want the database to be in the same directory as this file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)


class Algebro(tk.Tk):
    def __init__(self):
        super().__init__()

        

        # GREG UPDATE: just sneaking this in here real quick, when we intialize we attempt to intialize the database tables
        # This way if the database doesn't exist it gets created
        initialize_all_database_tables(DB_PATH)
        seed_units_and_topics(DB_PATH)

        # IMPORTANT
        self.current_user_id = None
        self.current_user_type = None


        self.title("Algebro")
        # https://www.geeksforgeeks.org/python/python-geometry-method-in-tkinter/
        # Allows us to specify where hte window opens with offsets
        self.geometry("1000x700+460+190")
        #forcing no resizing to keep padding correct, source: https://stackoverflow.com/questions/21958534/how-can-i-prevent-a-window-from-being-resized-with-tkinter
        self.resizable(width=False, height=False)

        #assets/resizing
        self.logo = PhotoImage(file="assets/logo.png").subsample(3,3)
        self.robo = PhotoImage(file="assets/background.png").subsample(3,3)
        self.login_photo = PhotoImage(file="assets/login.png").subsample(3,3)
        self.register_photo = PhotoImage(file="assets/register.png").subsample(3,3)
        self.logo_label = self.logo.subsample(3,3)
        self.back = PhotoImage(file="assets/back.png").subsample(3,3)
        self.log_button = PhotoImage(file="assets/log_button.png").subsample(4,4)
        self.reg_button = PhotoImage(file="assets/reg_button.png").subsample(4,4)
        self.logout_button = PhotoImage(file="assets/logout_button.png").subsample(3,3)
        self.toolbar_logo = PhotoImage(file="assets/toolbar_logo.png").subsample(3,3)

        #set icon
        self.iconphoto(True, self.toolbar_logo)

        #create homepage
        self.homepage = Frame()
        top_frame = Frame(self.homepage)
        top_frame.pack(side=TOP, anchor="ne")
        #login/register buttons
        #source: https://www.geeksforgeeks.org/python/hide-python-tkinter-text-widget-border/
        #to get rid of the sink
        log_reg = Frame(top_frame)
        log_reg.pack(side=RIGHT, anchor="ne", padx=55, pady=30)
        log_button = Button(log_reg, image=self.login_photo, relief=FLAT, bd=0, command=self.switch_loginpage)
        log_button.pack(side=TOP)
        reg_button = Button(log_reg, image=self.register_photo, relief=FLAT, bd=0, command=self.switch_registerpage)
        reg_button.pack(side=BOTTOM)

        label_top = Label(top_frame, text="Welcome to Algebro!", font=("Yu Gothic UI Semibold", 23), fg="#16538D", image=self.logo, compound="top")
        label_top.pack(side=LEFT, padx=90)
        label_bottom = Label(self.homepage, image=self.robo)
        label_bottom.pack(side=BOTTOM)


        #-----------------------Big seperator for my eyes----------------------------------

        #create login, fill with x to spread the grid across the screen
        self.login = Frame()
        login_bar = Frame(self.login)
        login_bar.pack(side=TOP, fill="x")

        login_bar.grid_columnconfigure(0, weight=1)
        login_bar.grid_columnconfigure(1, weight=1)
        login_bar.grid_columnconfigure(2, weight=1)

        logo_corner = Label(login_bar, image=self.logo_label)
        logo_corner.grid(row=0, column=0, sticky=W, padx=30, pady=20)

        login_label = Label(login_bar, text="Login", font=("Yu Gothic UI Semibold", 23))
        login_label.grid(row=0, column=1)

        back_corner = Button(login_bar, image=self.back, relief=FLAT, bd=0, command=self.switch_homepage)
        back_corner.grid(row=0, column=2, sticky=E, padx=30, pady=20)

        #center input area
        login_details = Frame(self.login)
        login_details.pack(anchor="center", pady=100)

        #username frame
        user_area = Frame(login_details)
        user_area.pack()

        user_label = Label(user_area, text="Username:", font=("Yu Gothic UI Semibold", 15))
        user_label.pack(side=LEFT)

        #using entry from documentation(has better stuff for singleline/password)
        #source: https://www.geeksforgeeks.org/python/python-tkinter-entry-widget/
        # BIG GREG CHANGE! Changing all input fields to instance variables so they can be accessed easily
        # Important so we can clear them at appropriate times
        self.user_input = Entry(user_area, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.user_input.pack(side=RIGHT, padx=10)
        
        #password frame
        pass_area = Frame(login_details)
        pass_area.pack(pady=20)

        pass_label = Label(pass_area, text="Password:", font=("Yu Gothic UI Semibold", 15))
        pass_label.pack(side=LEFT, padx=4)

        #using entry from documentation(has better stuff for singleline/password)
        #source: https://www.geeksforgeeks.org/python/python-tkinter-entry-widget/
        self.pass_input = Entry(pass_area, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", show="*", relief=FLAT, bd=0)
        self.pass_input.pack(side=RIGHT, padx=10)
        #button frame
        login_confirm = Button(login_details, image=self.log_button, relief=FLAT, bd=0,
                               command=lambda: self.login_validate(self.user_input.get(), self.pass_input.get()))
        login_confirm.pack(anchor="sw", padx=115, pady=10)


        #bottom part
        register_redirect = Frame(self.login)
        register_redirect.pack(side=BOTTOM, pady=30)

        register_prompt = Label(register_redirect, text="Don't have an account?", font=("Yu Gothic UI Semibold", 15))
        register_prompt.pack(side=TOP)
        register_link = Button(register_redirect, text="Register", font=("Yu Gothic UI Semibold", 15, "underline"), fg="#14518B", relief=FLAT, bd=0, command=self.switch_registerpage)
        register_link.pack(side=BOTTOM)



        #-----------------------Big seperator for my eyes----------------------------------

        #create register
        self.register_page = Frame()
        register_bar = Frame(self.register_page)
        register_bar.pack(side=TOP, fill="x")

        #source: https://tkdocs.com/tutorial/grid.html
        #configuring the grids to fill space
        register_bar.grid_columnconfigure(0, weight=1)
        register_bar.grid_columnconfigure(1, weight=1)
        register_bar.grid_columnconfigure(2, weight=1)

        logo_corner = Label(register_bar, image=self.logo_label)
        logo_corner.grid(row=0, column=0, sticky=W, padx=30, pady=20)

        register_label = Label(register_bar, text="Register", font=("Yu Gothic UI Semibold", 23))
        register_label.grid(row=0, column=1)

        back_corner = Button(register_bar, image=self.back, relief=FLAT, bd=0, command=self.switch_homepage)
        back_corner.grid(row=0, column=2, sticky=E, padx=30, pady=20)

        #center input area
        register_details = Frame(self.register_page)
        register_details.pack(pady=80)

        register_details.grid_columnconfigure(0, weight=1)
        register_details.grid_columnconfigure(1, weight=1)
        register_details.grid_columnconfigure(2, weight=1)

        #name row
        first_label = Label(register_details, text="First Name *", font=("Yu Gothic UI Semibold", 12))
        middle_label = Label(register_details, text="Middle Name (Optional)", font=("Yu Gothic UI Semibold", 12))
        last_label = Label(register_details, text="Last Name *", font=("Yu Gothic UI Semibold", 12))

        first_label.grid(row=0, column=0, sticky=SW, padx=20)
        middle_label.grid(row=0, column=1, sticky=SW, padx=20)
        last_label.grid(row=0, column=2, sticky=SW, padx=20)

        self.first_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.middle_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.last_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)

        self.first_entry.grid(row=1, column=0, sticky=W, padx=20)
        self.middle_entry.grid(row=1, column=1, sticky=W, padx=20)
        self.last_entry.grid(row=1, column=2, sticky=W, padx=20)

        #email/user row
        email_label = Label(register_details, text="Email Address *", font=("Yu Gothic UI Semibold", 12))
        username_label = Label(register_details, text="Username *", font=("Yu Gothic UI Semibold", 12))

        email_label.grid(row=2, column=0, sticky=SW, padx=20)
        username_label.grid(row=2, column=2, sticky=SW, padx=20)

        self.email_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.username_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)

        self.email_entry.grid(row=3, column=0, columnspan=2, sticky=EW, padx=20)
        self.username_entry.grid(row=3, column=2, sticky=W, padx=20)

        #password row
        pass_label = Label(register_details, text="Password *", font=("Yu Gothic UI Semibold", 12))
        role_label = Label(register_details, text="Select Role", font=("Yu Gothic UI Semibold", 12))
        

        pass_label.grid(row=4, column=0, sticky=SW, padx=20)
        role_label.grid(row=4, column=1, sticky=SW, padx=20)
                
        self.pass_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", show="*", relief=FLAT, bd=0)
        self.pass_entry.grid(row=5, column=0, sticky=W, padx=20)

        self.id_label = Label(register_details, text="Class ID *", font=("Yu Gothic UI Semibold", 12))
        self.id_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.role_var = IntVar()
        def select_role():
            selected_role = self.role_var.get()
            if selected_role == 1:
                self.id_label.grid(row=4, column=2, sticky=SW, padx=20)
                self.id_entry.grid(row=5, column=2, sticky=W, padx=20)
            elif selected_role == 2:
                #hide previous id fields if they exist
                self.id_label.grid_forget()
                self.id_entry.grid_forget()
            elif selected_role == 3:
                self.id_label.grid_forget()
                self.id_entry.grid_forget()

        #selection box
        student_select = Radiobutton(register_details, text="Student", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", variable=self.role_var, value=1, command=select_role)
        teacher_select = Radiobutton(register_details, text="Teacher", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", variable=self.role_var, value=2, command=select_role)
        general_select = Radiobutton(register_details, text="General User", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", variable=self.role_var, value=3, command=select_role)
        
        student_select.grid(row=5, column=1, sticky=EW, padx=20)
        teacher_select.grid(row=6, column=1, sticky=EW, padx=20)
        general_select.grid(row=7, column=1, sticky=EW, padx=20)
        
        #final rows
        verify_label = Label(register_details, text="Verify Password *", font=("Yu Gothic UI Semibold", 12))
        verify_label.grid(row=6, column=0, sticky=SW, padx=20)
        
        self.verify_entry = Entry(register_details, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", show="*", relief=FLAT, bd=0)
        self.verify_entry.grid(row=7, column=0, sticky=W, padx=20)
        
        # GREG UPDATE: Updated register_confirm button, tried to match how login_confirm button was formatted
        register_confirm = Button(register_details, image=self.reg_button, relief=FLAT, bd=0, 
                                  command=lambda: self.register_validate(
                                        self.first_entry, self.middle_entry, self.last_entry,
                                        self.email_entry, self.username_entry,
                                        self.pass_entry, self.verify_entry,
                                        self.role_var, self.id_entry))
        
        register_confirm.grid(row=6, rowspan=2, column=2, sticky=S)
        
        #bottom part
        login_redirect = Frame(self.register_page)
        login_redirect.pack(side=BOTTOM, pady=30)

        login_prompt = Label(login_redirect, text="Already have an account?", font=("Yu Gothic UI Semibold", 15))
        login_prompt.pack(side=TOP)
        login_link = Button(login_redirect, text="Login", font=("Yu Gothic UI Semibold", 15, "underline"), fg="#14518B", relief=FLAT, bd=0, command=self.switch_loginpage)
        login_link.pack(side=BOTTOM)
        #-----------------------Big seperator for my eyes----------------------------------
        
        #main page(tabs for progress, problemset, classlist)
        self.main_page = Frame()
        main_bar = Frame(self.main_page)
        main_bar.pack(side=TOP, fill="x")

        logo_corner = Label(main_bar, image=self.logo_label)
        logo_corner.pack(side=LEFT, padx=30, pady=20)

        logout_corner = Button(main_bar, image=self.logout_button, relief=FLAT, bd=0, command=self.logout_validate)
        logout_corner.pack(side=RIGHT, padx=30, pady=20)
        
        nav_container = Frame(self.main_page)
        nav_container.pack(fill="both", expand=True)

        #ttk elements have different style methods, we have to use Style
        #source: https://www.youtube.com/watch?v=unSu-n5VIL4
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Yu Gothic UI Semibold", 20), relief="flat", )

        #notebook to switch between progress, problemset and classlist
        self.main_nav = ttk.Notebook(nav_container)
    
        self.progress_tab = Frame(self.main_nav)
        self.problem_tab = Frame(self.main_nav)
        self.class_tab = Frame(self.main_nav)
        self.class_view_tab = Frame(self.main_nav)
        self.create_class_tab = Frame(self.main_nav)
                
        self.main_nav.add(self.progress_tab, text="Progress")
        self.main_nav.add(self.problem_tab, text="Problem Set")
        self.main_nav.add(self.class_tab, text="Class List")
        self.main_nav.add(self.class_view_tab, text="Class View")
        self.main_nav.add(self.create_class_tab, text="Create Class")
        self.main_nav.pack(fill="both", expand=True)


        # Hide all tabs initially, they'll be shown based on user role after login
        self.main_nav.hide(self.progress_tab)
        self.main_nav.hide(self.problem_tab)
        self.main_nav.hide(self.class_tab)
        self.main_nav.hide(self.class_view_tab)
        self.main_nav.hide(self.create_class_tab)


        '''
        #WAY FOR PROGRAM TO INITIALLY SEE SPECIFIC ROLE VIEWS, CHANGE WHEN LOGIN IS IMPLEMENTED
        #depending on the role, tabs need to be hidden/shown
        #student: progress, problemset, classlist
        #teacher: classview
        #general user: progress, problemset
        x = 4
        if x == 1:
            self.main_nav.hide(class_view_tab)
        elif x == 2:
            self.main_nav.hide(progress_tab)
            self.main_nav.hide(problem_tab)
            self.main_nav.hide(class_tab)
        elif x == 3:
            self.main_nav.hide(class_tab)
            self.main_nav.hide(class_view_tab)
        '''

        # ADDED THIS! 
        # https://stackoverflow.com/questions/71901422/tkinter-notebook-notebooktabchanged-problem
        # Allows us to update pages if the tab is pressed
        self.main_nav.bind("<<NotebookTabChanged>>", self.on_tab_change)

        #-----------------------Big seperator for my eyes----------------------------------
        #classlist
        #classlist(needs to display Last, First, Streak)
        #classlist_test = [("Last","First","0"),("Last","First","1"),("Last","First","2"),("Last","First","0"),("Last","First","1"),("Last","First","2"),("Last","First","2")]
        self.classlist_frame = Frame(self.class_tab)
        self.classlist_frame.pack(fill="both", expand=True, padx=80, pady=40)

        #canvas needed
        #source: https://www.youtube.com/watch?v=0WafQCaok6g
        '''class_canvas = Canvas(classlist_frame)
        class_canvas.pack(side=LEFT, fill="both", expand=1)'''


        self.classlist_frame.grid_columnconfigure(0, weight=1)
        self.classlist_frame.grid_columnconfigure(1, weight=1)
        self.classlist_frame.grid_columnconfigure(2, weight=1)

        header_1 = Label(self.classlist_frame, text="Last Name", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        header_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        header_2 = Label(self.classlist_frame, text="First Name", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        header_2.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        header_3 = Label(self.classlist_frame, text="Practice Streak", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        header_3.grid(row=0, column=2, sticky="ew", padx=1, pady=1)

        #for i in range(len(classlist_test)):
        #    for j in range(3):
        #        user_header = Label(grid_frame, text=classlist_test[i][j], font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=10, pady=10)
        #        user_header.grid(row=i + 1, column=j, sticky="ew", padx=1, pady=1)

        #-----------------------Big seperator for my eyes----------------------------------

        # CREATE CLASS TAB

        self.create_class_frame = Frame(self.create_class_tab)
        self.create_class_frame.pack(fill="both", expand=True, padx=150, pady=80)


        self.create_class_frame.grid_columnconfigure(0, weight=1)
        self.create_class_frame.grid_columnconfigure(1, weight=1)


        # This label will hold the "Class Name" text
        self.class_name_label = Label(self.create_class_frame, text="Class Name", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        self.class_name_label.grid(row=0, column=0, sticky="ew", padx=1, pady=10)

        # This Frame holds the entry point for instructors to type the name of the class
        self.class_name_entry_frame = Frame(self.create_class_frame, bg="#679FCE", padx=20, pady=20)
        self.class_name_entry_frame.grid(row=0, column=1, sticky="ew", padx=1, pady=10)
        self.class_name_entry = Entry(self.class_name_entry_frame, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.class_name_entry.pack(side=TOP, fill="x", pady=1)


        # This label will hold the "Class Code" text
        self.class_code_label = Label(self.create_class_frame, text="Class Code", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        self.class_code_label.grid(row=1, column=0, sticky="ew", padx=1)

        # This Frame holds the entry point for users to type the code of the class
        self.class_code_entry_frame = Frame(self.create_class_frame, bg="#679FCE", padx=20, pady=20)
        self.class_code_entry_frame.grid(row=1, column=1, sticky="ew", padx=1)
        self.class_code_entry = Entry(self.class_code_entry_frame, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.class_code_entry.pack(side=TOP, fill="x", pady=1)


        # This frame holds the button for submitting a name and code and seeing if its valid
        self.submit_frame = Frame(self.create_class_frame, bg="#C7DBED")
        self.submit_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=30)
        self.submit_button = Button(self.submit_frame, text="Submit", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=self.create_class_submit)
        self.submit_button.pack(side=LEFT, padx=20, pady=20)

        # This label will hold the feedback for the answer the user sent (correct, incorrect, etc.)
        self.create_class_feedback_label = Label(self.submit_frame, text="", font=("Yu Gothic UI Semibold", 14), bg="#C7DBED", padx=20, pady=20)
        self.create_class_feedback_label.pack(padx=20, pady=10)




         #-----------------------Big seperator for my eyes----------------------------------





        #progress

        #progress_test = [("One-Step Equations","3","10","9","90.0%","90.0%"),("Two-Step Equations","1","5","4","80.0%","80.0%"),("Divination","3","17","16","94.1%","94.1%")]
        self.progress_frame = Frame(self.progress_tab)
        self.progress_frame.pack(fill="both", expand=True, padx=80, pady=40)

        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(1, weight=1)
        self.progress_frame.grid_columnconfigure(2, weight=1)
        self.progress_frame.grid_columnconfigure(3, weight=1)
        self.progress_frame.grid_columnconfigure(4, weight=1)
        self.progress_frame.grid_columnconfigure(5, weight=1)

        progress_header_1 = Label(self.progress_frame, text="Topic", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        progress_header_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        progress_header_2 = Label(self.progress_frame, text="Difficulty", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        progress_header_2.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        progress_header_3 = Label(self.progress_frame, text="Questions", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        progress_header_3.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        progress_header_4 = Label(self.progress_frame, text="Correct", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        progress_header_4.grid(row=0, column=3, sticky="ew", padx=1, pady=1)
        progress_header_5 = Label(self.progress_frame, text="Accuracy", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        progress_header_5.grid(row=0, column=4, sticky="ew", padx=1, pady=1)
        progress_header_6 = Label(self.progress_frame, text="Best Score", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        progress_header_6.grid(row=0, column=5, sticky="ew", padx=1, pady=1)

        #for i in range(len(progress_test)):
        #    for j in range(6):
        #        summary_header = Label(self.progress_frame, text=progress_test[i][j], font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
        #        summary_header.grid(row=i + 1, column=j, sticky="ew", padx=1, pady=1)
        #-----------------------Big seperator for my eyes----------------------------------
        
        
        def first_problem_set():
            self.summary_frame.forget()

            self.problem_frame = Frame(self.problem_tab)
            self.problem_frame.pack(fill="both", expand=True, padx=150, pady=110)

            #1x2 grid for questions
            self.problem_frame.grid_columnconfigure(0, weight=1)
            self.problem_frame.grid_columnconfigure(1, weight=1)
            self.problem_frame.grid_columnconfigure(2, weight=1)

            #make it a list cause id rather not refactor this all in a class
            i = [0]
            num_label = Label(self.problem_frame, text=f"{i[0]+1}/10", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
            num_label.grid(row=0, column=0, sticky="ew", padx=1)
            question_label = Label(self.problem_frame, text=problem_test[i[0]][0], font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
            question_label.grid(row=0, column=1, sticky="ew", padx=1)

            answer_entry_frame = Frame(self.problem_frame, bg="#679FCE", padx=20, pady=20)
            answer_entry_frame.grid(row=0, column=2, sticky="ew", padx=1)
            answer_entry = Entry(answer_entry_frame, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
            answer_entry.pack(side=TOP, fill="x", pady=1)

            def submit_answer():

                def next_problem_set():
                    self.summary_frame.forget()
                    i[0] = 0
                    #reset question and num label
                    self.problem_frame.forget()
                    self.problem_frame.pack(fill="both", expand=True, padx=150, pady=110)
                    num_label.config(text=f"{i[0]+1}/10")
                    question_label.config(text=problem_test[i[0]][0])
                    answer_entry.delete(0, END)
                    feedback_label.config(text="")

                answer = answer_entry.get()
                correct_answer = problem_test[i[0]][1]
                explanation = problem_test[i[0]][2]
                if answer == correct_answer:
                    message_int = random.randint(1,4) #random feedback message
                    if message_int == 1:
                        feedback_label.config(text="Great job!")
                    elif message_int == 2:
                        feedback_label.config(text="Correct!")
                    elif message_int == 3:
                        feedback_label.config(text="Well done!")
                    elif message_int == 4:
                        feedback_label.config(text="Amazing work!")
                else:
                    feedback_label.config(text=explanation)

                i[0] += 1
            
                if i[0] < 10:
                    #update question by changing fields and clearing entry
                    num_label.config(text=f"{i[0]+1}/10")
                    question_label.config(text=problem_test[i[0]][0])
                    answer_entry.delete(0, END)
                elif i[0] >= 10:
                    self.problem_frame.forget()
                    self.summary_frame = Frame(self.problem_tab)
                    self.summary_frame.pack(fill="both", expand=True, padx=80, pady=30)

                    self.summary_frame.grid_columnconfigure(0, weight=1)
                    self.summary_frame.grid_columnconfigure(1, weight=1)
                    self.summary_frame.grid_columnconfigure(2, weight=1)
                    self.summary_frame.grid_columnconfigure(3, weight=1)
                    self.summary_frame.grid_columnconfigure(4, weight=1)

                    summary_header_1 = Label(self.summary_frame, text="Topic", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
                    summary_header_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
                    summary_header_2 = Label(self.summary_frame, text="Difficulty", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
                    summary_header_2.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
                    summary_header_3 = Label(self.summary_frame, text="Questions", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
                    summary_header_3.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
                    summary_header_4 = Label(self.summary_frame, text="Correct", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
                    summary_header_4.grid(row=0, column=3, sticky="ew", padx=1, pady=1)
                    summary_header_5 = Label(self.summary_frame, text="Accuracy", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
                    summary_header_5.grid(row=0, column=4, sticky="ew", padx=1, pady=1)

                    dummy_val = ("One-Step Equations","3","10","9","90.0%","90.0%")

                    for j in range(5):
                        personal_summary_header = Label(self.summary_frame, text=dummy_val[j], font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
                        personal_summary_header.grid(row=1, column=j, sticky="ew", padx=1, pady=1)
                        
                    next_set_button = Button(self.summary_frame, text="Next Problem Set: " + suggested_set, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    next_set_button.grid(row=2, column=0, columnspan=5, pady=30)

                    review_label = Label(self.summary_frame, text="Review:", font=("Yu Gothic UI Semibold", 23))
                    review_label.grid(row=3, column=0, columnspan=5)

                    panel_frame = Frame(self.summary_frame)
                    panel_frame.grid(row=4, column=0, columnspan=5)

                    panel_frame.grid_columnconfigure(0, weight=1)
                    panel_frame.grid_columnconfigure(1, weight=1)
                    panel_frame.grid_columnconfigure(2, weight=1)

                    #make 3x3 grid of buttons for the other topics/units
                    topic_1 = Button(panel_frame, text="Topic 1", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
                    topic_2 = Button(panel_frame, text="Topic 2", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_2.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
                    topic_3 = Button(panel_frame, text="Topic 3", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_3.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
                    topic_4 = Button(panel_frame, text="Topic 4", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_4.grid(row=1, column=0, sticky="ew", padx=1, pady=1)
                    topic_5 = Button(panel_frame, text="Topic 5", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_5.grid(row=1, column=1, sticky="ew", padx=1, pady=1)
                    topic_6 = Button(panel_frame, text="Topic 6", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_6.grid(row=1, column=2, sticky="ew", padx=1, pady=1)
                    topic_7 = Button(panel_frame, text="Topic 7", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_7.grid(row=2, column=0, sticky="ew", padx=1, pady=1)
                    topic_8 = Button(panel_frame, text="Topic 8", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=next_problem_set)
                    topic_8.grid(row=2, column=1, sticky="ew", padx=1, pady=1)


            submit_frame = Frame(self.problem_frame, bg="#C7DBED")
            submit_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=30)
            submit_button = Button(submit_frame, text="Submit", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=submit_answer)
            submit_button.pack(side=LEFT, padx=20, pady=20)
            feedback_label = Label(submit_frame, text="", font=("Yu Gothic UI Semibold", 14), bg="#C7DBED", padx=20, pady=20)
            feedback_label.pack(padx=20, pady=20)

        problem_test = [("6(x - 1) + 2x = 3(x + 8) + 5", "4", "Subtract 2x from both sides, then add 6 to both sides"),("x + 3 = 7", "4", "Subtract 3 from both sides"),("2 = x + 1", "1", "Subtract 1 from both sides"),("x + 8 = 9", "1", "Subtract 8 from both sides"),("x + 4 = 7", "3", "Subtract 4 from both sides"),("x + 8 = 8", "0", "Subtract 8 from both sides"),("6 = x + 3", "3", "Subtract 3 from both sides"),("x + 5 = 8", "3", "Subtract 5 from both sides"),("4 = x + 2", "2", "Subtract 2 from both sides"),("x + 6 = 9", "3", "Subtract 6 from both sides")]
        #problem set
        suggested_set = "One-Step Equations"

        self.summary_frame = Frame(self.problem_tab)
        self.summary_frame.pack(fill="both", expand=True, padx=80, pady=40)

        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(1, weight=1)
        self.summary_frame.grid_columnconfigure(2, weight=1)
        self.summary_frame.grid_columnconfigure(3, weight=1)
        self.summary_frame.grid_columnconfigure(4, weight=1)

        next_set_button = Button(self.summary_frame, text="Next Problem Set: " + suggested_set, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        next_set_button.grid(row=2, column=0, columnspan=5, pady=30)

        review_label = Label(self.summary_frame, text="Review:", font=("Yu Gothic UI Semibold", 23), pady=10)
        review_label.grid(row=3, column=0, columnspan=5)

        self.panel_frame = Frame(self.summary_frame)
        self.panel_frame.grid(row=4, column=0, columnspan=5)

        self.panel_frame.grid_columnconfigure(0, weight=1)
        self.panel_frame.grid_columnconfigure(1, weight=1)
        self.panel_frame.grid_columnconfigure(2, weight=1)

        #make 3x3 grid of buttons for the other topics/units
        topic_1 = Button(self.panel_frame, text="Topic 1", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        topic_2 = Button(self.panel_frame, text="Topic 2", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_2.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        topic_3 = Button(self.panel_frame, text="Topic 3", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_3.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        topic_4 = Button(self.panel_frame, text="Topic 4", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_4.grid(row=1, column=0, sticky="ew", padx=1, pady=1)
        topic_5 = Button(self.panel_frame, text="Topic 5", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_5.grid(row=1, column=1, sticky="ew", padx=1, pady=1)
        topic_6 = Button(self.panel_frame, text="Topic 6", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_6.grid(row=1, column=2, sticky="ew", padx=1, pady=1)
        topic_7 = Button(self.panel_frame, text="Topic 7", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_7.grid(row=2, column=0, sticky="ew", padx=1, pady=1)
        topic_8 = Button(self.panel_frame, text="Topic 8", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=first_problem_set)
        topic_8.grid(row=2, column=1, sticky="ew", padx=1, pady=1)

        #-----------------------Big seperator for my eyes----------------------------------

        self.classview_frame = Frame(self.class_view_tab, bg="#C7DBED")
        self.classview_frame.pack(fill="both", expand=True, padx=40, pady=40)

        self.codes_frame = Frame(self.classview_frame, bg="#679FCE", padx=20, pady=20)
        self.codes_frame.pack(side=LEFT, fill="y", padx=20, pady=20)

        self.list_frame = Frame(self.classview_frame, bg="#679FCE", padx=20, pady=20)
        self.list_frame.pack(side=RIGHT, fill="y", padx=20, pady=20)

        #list of class codes on left with a button for viewing
        for i in return_all_classes(self.current_user_id, DB_NAME):
            class_name, class_code = i
            class_code_button = Button(self.codes_frame, text=class_name + " (" + class_code + ")", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", relief=FLAT, bd=0, command=lambda: self.print_class(class_code))
            class_code_button.pack(fill="x", pady=10)

        self.switch_homepage()

    def print_class(self, class_code):
        #forget and repack the grid
        #source: https://tkdocs.com/tutorial/grid.html
        for x in self.list_frame.grid_slaves():
            x.grid_forget()
        #recreate headers
        header_1 = Label(self.list_frame, text="ID", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=5, pady=15, height=2)
        header_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        header_2 = Label(self.list_frame, text="Last Name", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=15, pady=15, height=2)
        header_2.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        header_3 = Label(self.list_frame, text="First Name", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=15, pady=15, height=2)
        header_3.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        header_4 = Label(self.list_frame, text="Practice\nStreak", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=5, pady=15, height=2)
        header_4.grid(row=0, column=3, sticky="ew", padx=1, pady=1)
        header_5 = Label(self.list_frame, text="Time Spent\n(mins)", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=5, pady=15, height=2)
        header_5.grid(row=0, column=4, sticky="ew", padx=1, pady=1)
        #populate with new entries
        class_info = return_class_student_info(self.current_user_id, class_code, DB_NAME)
        for i, student in enumerate(class_info):
            for j, info in enumerate(student):

                # Format time_spent (column 4) to 2 decimal places
                if j == 4 and info is not None:  # Column 4 is tspent
                    display_text = f"{info:.2f}"
                elif j == 5 and info is not None: # Column 5 is pstreak
                    display_text = f"{info} days"
                else:
                    display_text = str(info) if info is not None else "0"


                user_header = Label(self.list_frame, text=display_text, font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=10, pady=10)
                user_header.grid(row=i + 1, column=j, sticky="ew", padx=1, pady=1)











        #-----------------------Big seperator for my eyes----------------------------------


    


    """
    Function for handling if the creation of a class is successful
    """
    def create_class_submit(self):

        class_name = self.class_name_entry.get().strip()
        class_code = self.class_code_entry.get().strip()
        
        # Check if the name and code entered are empty
        if not class_name:
            self.create_class_feedback_label.config(text="Class name cannot be empty")
            return
        if not class_code:
            self.create_class_feedback_label.config(text="Class code cannot be empty")
            return
        
        # Check if the code entered is valid
        check_code = validate_class_code(class_code)
        if not check_code:
            self.create_class_feedback_label.config(text="Codes must be 4-8 characters and use letters/numbers")
            return
        
        # Try to create the class
        create_class_check = create_class(self.current_user_id, class_code, class_name, DB_PATH)
        # If it returned false, the code is in use
        if not create_class_check:
            self.create_class_feedback_label.config(text=f"Class code '{class_code}' is currently in use")
            return
        
        # If there were no problems
        self.create_class_feedback_label.config(text=f"Success! Class '{class_name}'\ncreated with code: {class_code}")
        # Clear the entry fields
        self.class_name_entry.delete(0, END)
        self.class_code_entry.delete(0, END)







        
    #functions for each page
    def switch_homepage(self):
        self.clear_login_fields()
        self.clear_register_fields()
        self.forget_pages()
        self.homepage.pack(fill=BOTH, expand=True)
    def switch_loginpage(self):
        self.clear_register_fields()
        self.forget_pages()
        self.login.pack(fill=BOTH, expand=True)
    def switch_registerpage(self):
        self.clear_login_fields()
        self.forget_pages()
        self.register_page.pack(fill=BOTH, expand=True)
    def switch_mainpage(self):
        self.clear_login_fields()
        self.clear_register_fields()
        self.forget_pages()
        self.main_page.pack(fill=BOTH, expand=True)


    #function for forgetting everything(potion of blunt trauma)
    def forget_pages(self):
        self.homepage.forget()
        self.login.forget()
        self.register_page.forget()
        self.main_page.forget()

    """
    Function for attempting to login a user using an entered username or password
    """
    def login_validate(self, username, password):
        # GREG UPDATES
        # Tried to match the format for logging in same as the CLI, by checking what gets returned from login_user()
        # We get the ID and User Type returned, which lets us know which page we should display next

        if(not username):
            # Replace this with GUI error, maybe popup
            #print("Username is required\n")
            messagebox.showerror("Login Error", "Username cannot be empty")
            return

        if(not password):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Login Error", "Password cannot be empty")
            return


        login_result = login_user(username, password, DB_PATH)

        # If we get a result, we logged in successfully
        if(login_result):
            # Extract the user's id and user's type from the returned tuple
            user_id, user_type = login_result

            # May be needed later?
            self.current_user_id = user_id
            self.current_user_type = user_type

            if(user_type == "student"):
                self.change_tabs_for_user_role()
                self.refresh_mainpage_view()
                self.switch_mainpage()
            elif(user_type == "instructor"):
                self.change_tabs_for_user_role()
                self.refresh_mainpage_view()
                self.switch_mainpage()
            elif(user_type == "general"):
                self.change_tabs_for_user_role()
                self.switch_mainpage()
            else:
                #TODO: notify on gui
                messagebox.showerror("Login Error", "Invalid username or password\nPlease check your credentials and try again")

        else:
            messagebox.showerror("Login Error", "Invalid username or password\nPlease check your credentials and try again")
        

        #put validation logic here
        #if login_user(username, password, DB_PATH):
        #    #TODO: decide whether to go to instructor or student main page, id and type returned from login
        #    self.switch_mainpage()
        #else:
        #    #TODO: notify on gui
        #    print("Login Failed")



    """
    Function for attempting to register a user using entered information
    """
    def register_validate(self, first_entry, middle_entry, last_entry, email_entry, username_entry, pass_entry, verify_entry, role_var, id_entry):

        # Get all info from the input fields
        first_name = first_entry.get().strip()
        middle_name = middle_entry.get().strip()
        last_name = last_entry.get().strip()
        email = email_entry.get().strip()
        username = username_entry.get().strip()
        password = pass_entry.get().strip()
        verify_password = verify_entry.get().strip()
        role = role_var.get()


        # Looong list of making sure each required field is filled
        if(not first_name):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Registration Error", "First Name cannot be empty")
            return
        if(not last_name):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Registration Error", "Last Name cannot be empty")
            return
        if(not email):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Registration Error", "Email cannot be empty")
            return
        if(not username):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Registration Error", "Username cannot be empty")
            return
        if(not password):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Registration Error", "Password cannot be empty")
            return
        if(password != verify_password):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Registration Error", "Passwords do not match\nRe-enter your password and try again")
            return
        if(role == 0):
            # Replace this with GUI error, maybe popup
            messagebox.showerror("Registration Error", "Please select an account role")
            return
        
        # Logic for handling different roles
        # If the role is set to "1", that means it's a student and we need to get a class code from them
        if(role == 1):
            # For the database entry
            role_string = "student"
            # Since we know it's a student, we can now attempt to retrive what they entered in the class code field
            class_code = id_entry.get().strip()
            # If they did not enter anything, thats no good
            if(not class_code):
                messagebox.showerror("Registration Error", "Please enter a valid class code")
                return

            # Want to validate the class code they entered exists in the system
            class_id = get_class_id_from_code(class_code, DB_PATH)
            # If no class ID was matched to the class code, it doesn't exist in the system
            if(class_id is None):
                messagebox.showerror("Registration Error", f"Class code '{class_code}' was not found\nContact your instructor or enter a new class code")
                return
        # If the role is set to "2" that means its' an instructor (no class id)
        elif(role == 2): 
            role_string = "instructor"
            class_id = None
        # If the role is set to "3" that means it's a general user (no class id)
        elif(role == 3):
            role_string = "general"
            class_id = None

        register_check = register_user(first_name, last_name, middle_name, username, password, role_string, class_id, DB_PATH)

        if(register_check):
            # If a user registers successfully, they can go to login page or to the home page
            result = messagebox.askyesno("Algebro", "Your account has been created successfully\nWould you like to be redirected to the login page?")
            # Go to the login page
            if(result):
                self.switch_loginpage()
            # Go to the home page
            else:
                self.switch_homepage()

        else: 
            # If they couldn't register, that means their chosen username is already in use
            messagebox.showerror("Registration Error", f"Username '{username}' is taken\nPlease enter a unique username")
            return

    #logout func
    def logout_validate(self):

        # Hide all tabs
        self.main_nav.hide(self.progress_tab)
        self.main_nav.hide(self.problem_tab)
        self.main_nav.hide(self.class_tab)
        self.main_nav.hide(self.class_view_tab)
        self.main_nav.hide(self.create_class_tab)
        
        # Clear user info
        self.current_user_id = None
        self.current_user_type = None
        
        # Return to homepage
        self.switch_homepage()


    """
    Function for clearing all input fields in the "Login" page, after the user leaves the page
    """
    def clear_login_fields(self):
        self.user_input.delete(0, 'end')
        self.pass_input.delete(0, 'end')

    """
    Function for clearing all input fields in the "Register" page, after the user leaves the page
    """
    def clear_register_fields(self):
        self.first_entry.delete(0, 'end')
        self.middle_entry.delete(0, 'end')
        self.last_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.username_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')
        self.verify_entry.delete(0, 'end')
        # Set the role selector to 0 so it isnt on any of the roles
        self.role_var.set(0)

        self.id_label.grid_forget()
        self.id_entry.delete(0, 'end')
        self.id_entry.grid_forget()


    """
    Function for refreshing pages when the user clicks on a specific tab
    Tkinter requires event for it's event binding system, even if we don't use it
    """
    def on_tab_change(self, event):


        # Safety check: if no tab is selected (all hidden), do nothing
        try:
            selected_tab_id = self.main_nav.select()
            if not selected_tab_id:  # Empty string means no tab selected
                return
            selected_tab = self.main_nav.tab(selected_tab_id, "text")
        except:
            # If there's any error getting the selected tab, just return
            return

        if(selected_tab == "Progress"):
            self.refresh_mainpage_view()

        elif(selected_tab == "Class List"):
            self.refresh_classlist_view()

        elif(selected_tab == "Problem Set"):
            self.refresh_problemset_view()

        elif selected_tab == "Class View":
            self.create_class_feedback_label.config(text="")
            self.refresh_classview_view()

    
    """
    Function for changing tabs based on the user type
    Students can see Progress, Problem Set, and Class List
    Instructors can see Class View
    General Users can see Progress and Problem Set
    """
    def change_tabs_for_user_role(self):
        
        # Hide all tabs initially
        self.main_nav.hide(self.progress_tab)
        self.main_nav.hide(self.problem_tab)
        self.main_nav.hide(self.class_tab)
        self.main_nav.hide(self.class_view_tab)

        # Then show tabs based on the user type
        if(self.current_user_type == "student"):
            self.main_nav.add(self.progress_tab, text="Progress")
            self.main_nav.add(self.problem_tab, text="Problem Set")
            self.main_nav.add(self.class_tab, text="Class List")

            self.main_nav.select(self.progress_tab)

        elif(self.current_user_type == "instructor"):
            self.main_nav.add(self.class_view_tab, text="Class View")
            self.main_nav.add(self.create_class_tab, text="Create Class")
            self.main_nav.select(self.class_view_tab)
        
        elif(self.current_user_type == "general"):
            self.main_nav.add(self.progress_tab, text="Progress")
            self.main_nav.add(self.problem_tab, text="Problem Set")

            self.main_nav.select(self.progress_tab)



    """
    Function for refreshing the progress table with the current data pulled from the database
    Called on initial login and whenever the user clicks the Progress tab
    """
    def refresh_mainpage_view(self):

        # First thing we need to do is clear all the info currently loaded in EXCEPT for the headers, since those stay no matter the user or data
        # https://tkdocs.com/tutorial/grid.html (go to Querying and Changing Grid Options)
        # Since we use a grid to display student topic progress, we can used the grid_slaves() method to get each widgit in the grid
        for w in self.progress_frame.grid_slaves():

            # In order to preserve the header's for the tables, we can make sure we dont delete anything from "row 0"
            info = w.grid_info()
            current_row = int(info["row"])
            # If the current widget is not on row 0 of the table, it's not a header and it can get removed
            if(current_row > 0):
                w.destroy()


        # Get the student's topic summaries
        #print(f"Currnet user id: {self.current_user_id}")
        summaries = get_student_progress_data(self.current_user_id, DB_PATH)
        
        # If the user has topic summaries
        if(summaries):

            # Counter used for the current row number
            i = 0
            # Go through the summary of each topic the user has studied
            for summary in summaries:
                # Increase the row counter
                i += 1
                # Column 0: The topic name
                topic_label = Label(self.progress_frame, text=summary["topic_name"], font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=20, pady=10)
                topic_label.grid(row=i, column=0, sticky="ew", padx=1, pady=1)

                # Column 1: The current difficulty of the topic
                difficulty_label = Label(self.progress_frame, text=summary["current_difficulty"], font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=20, pady=10)
                difficulty_label.grid(row=i, column=1, sticky="ew", padx=1, pady=1)

                # Column 2: The total questions the user has answer on the topic
                questions_label = Label(self.progress_frame, text=summary["total_questions"], font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=20, pady=10)
                questions_label.grid(row=i, column=2, sticky="ew", padx=1, pady=1)

                # Column 3: The total correct answers the user has gotten on the topic
                correct_label = Label(self.progress_frame, text=summary["total_correct_raw"], font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=20, pady=10)
                correct_label.grid(row=i, column=3, sticky="ew", padx=1, pady=1)

                # Column 4: The overall accuracy of the user in the topic
                accuracy_label = Label(self.progress_frame, text=f"{summary["accuracy"]*100:.1f}%", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=20, pady=10)
                accuracy_label.grid(row=i, column=4, sticky="ew", padx=1, pady=1)

                # Column 5: The best score the user has achieved in that topic
                accuracy_label = Label(self.progress_frame, text=f"{summary["best_score"]*100:.1f}%", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=20, pady=10)
                accuracy_label.grid(row=i, column=5, sticky="ew", padx=1, pady=1)

        # If summaries is an empty list, the user has yet to practice anything yet
        elif (summaries == []):
            message_label = Label(self.progress_frame, text="No progress data yet. Start practicing to see your stats!", font=("Yu Gothic UI Semibold", 12), bg="#C7DBED", padx=20, pady=20)
            message_label.grid(row=1, column=0, columnspan=6, sticky="ew", padx=1, pady=1)




    


    """
    Function for refreshing the student classlist view by current data pulled from the database
    Called whenever the user clicks the Class notebook tab
    """
    def refresh_classlist_view(self):    

        # First thing we need to do is clear all the info currently loaded in EXCEPT for the headers, since those stay no matter the user or data
        # https://tkdocs.com/tutorial/grid.html (go to Querying and Changing Grid Options)
        # Since we use a grid to display student topic progress, we can used the grid_slaves() method to get each widgit in the grid
        for w in self.classlist_frame.grid_slaves():

            # In order to preserve the header's for the tables, we can make sure we dont delete anything from "row 0"
            info = w.grid_info()
            current_row = int(info["row"])
            # If the current widget is not on row 0 of the table, it's not a header and it can get removed
            if(current_row > 0):
                w.destroy()


        # Get the student's topic summaries
        all_student_info = get_class_list_data(self.current_user_id, DB_PATH)
        
        # If the user has topic summaries
        if(all_student_info):
            # Counter used for the current row number
            i = 0
            # Go through the summary of each topic the user has studied
            for student in all_student_info:
                # Increase the row counter
                i += 1

                lname_label = Label(self.classlist_frame, text=student[0], font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=9)
                lname_label.grid(row=i, column=0, sticky="ew", padx=1, pady=1)

                fname_label = Label(self.classlist_frame, text=student[1], font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=9)
                fname_label.grid(row=i, column=1, sticky="ew", padx=1, pady=1)

                pstreak_label = Label(self.classlist_frame, text=f"{student[2]} days", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=9)
                pstreak_label.grid(row=i, column=2, sticky="ew", padx=1, pady=1)



    """
    Function for refreshing the student problemset view, pulling the next topic they should learn 
    Called whenever the user clicks the Problemset tab
    """
    def refresh_problemset_view(self): 

        # First thing we need to do is clear all the info currently loaded in EXCEPT for the headers, since those stay no matter the user or data
        # https://tkdocs.com/tutorial/grid.html (go to Querying and Changing Grid Options)
        # Since we use a grid to display student topic progress, we can used the grid_slaves() method to get each widgit in the grid
        for w in self.summary_frame.grid_slaves():

            # In order to preserve the header's for the tables, we can make sure we dont delete anything from "row 0"
            info = w.grid_info()
            current_row = int(info["row"])
            # If the current widget is not on row 0 of the table, it's not a header and it can get removed
            if(current_row > 0):
                w.destroy()

        # Need to figure out the id of the topic the user is currently learning
        current_topic_id = find_user_current_topic(DB_PATH, self.current_user_id)

        # Get the name of the current topic being learned
        suggested_topic_name = get_topic_name_from_topic_id(DB_PATH, current_topic_id)

        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(1, weight=1)
        self.summary_frame.grid_columnconfigure(2, weight=1)
        self.summary_frame.grid_columnconfigure(3, weight=1)
        self.summary_frame.grid_columnconfigure(4, weight=1)

        # If there is no suggested topic, the user has mastered all
        if(suggested_topic_name is not None):
            next_set_button = Button(self.summary_frame, text="Next Problem Set: " + suggested_topic_name, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(current_topic_id))
            next_set_button.grid(row=2, column=0, columnspan=5, pady=30)
        # If there is no suggested topic, we recommend they study their weakest average topic
        else:
            suggested_topic_id = get_student_weakest_topic_id(self.current_user_id, DB_PATH)
            suggested_weakest_topic_name = get_topic_name_from_topic_id(DB_PATH, suggested_topic_id)
            next_set_button = Button(self.summary_frame, text=f"All Topics Mastered! Recommended Review: {suggested_weakest_topic_name}", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(suggested_topic_id))
            next_set_button.grid(row=2, column=0, columnspan=5, pady=30)

        review_label = Label(self.summary_frame, text="Review:", font=("Yu Gothic UI Semibold", 23), pady=10)
        review_label.grid(row=3, column=0, columnspan=5)

        self.panel_frame = Frame(self.summary_frame)
        self.panel_frame.grid(row=4, column=0, columnspan=5)

        self.panel_frame.grid_columnconfigure(0, weight=1)
        self.panel_frame.grid_columnconfigure(1, weight=1)
        self.panel_frame.grid_columnconfigure(2, weight=1)

        # Initially grey out all topic buttons
        topic_1 = Button(self.panel_frame, text="Distributive\nProperty", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        topic_2 = Button(self.panel_frame, text="Simplifying\nExpressions", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        topic_3 = Button(self.panel_frame, text="Evaluating\nExpressions", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        topic_4 = Button(self.panel_frame, text="One-Step\nEquations", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        topic_5 = Button(self.panel_frame, text="Two-Step\nEquations", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        topic_6 = Button(self.panel_frame, text="Multi-Step\nEquations", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        topic_7 = Button(self.panel_frame, text="Basic\nExponents", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        topic_8 = Button(self.panel_frame, text="Exponent\nRules", font=("Yu Gothic UI Semibold", 12), bg="#6C7984", relief=FLAT, bd=0, padx=20, pady=10)
        

        if(current_topic_id > 1):
            topic_1 = Button(self.panel_frame, text="Distributive\nProperty", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(1))
        if(current_topic_id > 2):
            topic_2 = Button(self.panel_frame, text="Evaluating\nExpressions", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(2))
        if(current_topic_id > 3):
            topic_3 = Button(self.panel_frame, text="Simplifying\nExpressions", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(3))
        if(current_topic_id > 4):
            topic_4 = Button(self.panel_frame, text="One-Step\nEquations", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(4))
        if(current_topic_id > 5):
            topic_5 = Button(self.panel_frame, text="Two-Step\nEquations", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(5))
        if(current_topic_id > 6):
            topic_6 = Button(self.panel_frame, text="Multi-Step\nEquations", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(5))
        if(current_topic_id > 7):
            topic_7 = Button(self.panel_frame, text="Basic\nExponents", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(6))
        if(current_topic_id > 8):
            topic_8 = Button(self.panel_frame, text="Exponent\nRules", font=("Yu Gothic UI Semibold", 12), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=lambda:self.questions_problemset_view(7))

        topic_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        topic_2.grid(row=1, column=0, sticky="ew", padx=1, pady=1)
        topic_3.grid(row=2, column=0, sticky="ew", padx=1, pady=1)
        topic_4.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        topic_5.grid(row=1, column=1, sticky="ew", padx=1, pady=1)
        topic_6.grid(row=2, column=1, sticky="ew", padx=1, pady=1)
        topic_7.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        topic_8.grid(row=1, column=2, sticky="ew", padx=1, pady=1)


    def refresh_classview_view(self):

        for w in self.codes_frame.pack_slaves():
            w.destroy()

        for w in self.list_frame.grid_slaves():
            w.destroy()

        #list of class codes on left with a button for viewing
        for i in return_all_classes(self.current_user_id, DB_NAME):
            class_name, class_code = i
            class_code_button = Button(self.codes_frame, text=class_name + " (" + class_code + ")", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", relief=FLAT, bd=0, command=lambda code=class_code: self.print_class(code))
            class_code_button.pack(fill="x", pady=10)


        

    """
    Function for going through a problemset
    Called whenever the user clicks a Review Topic button, or next recommended topic button
    """
    def questions_problemset_view(self, topic_id):
        
        question_count = 10
        self.current_topic_id = topic_id

        # TODO: Pull questions from questions.py
        # For now, using dummy data
        self.ml = AlgebroML(DB_PATH)
        difficulty = self.ml.recommend_difficulty(self.current_user_id, self.current_topic_id)
        questions_list = load_questions_for_problemset(topic_id, str(difficulty), question_count)

        self.pset_id = initialize_problemset_in_database(DB_PATH, self.current_user_id, topic_id)

        self.current_question_num = 0

        self.correct_answer_count = 0
        self.correct_with_hint_count = 0
        self.correct_no_hint_count = 0

        self.question_list = questions_list
        # Get the difficulty from the difficulty of the first question
        self.problemset_difficulty = questions_list[0][0]
        self.total_time_taken = 0

        # Hide the summary frame and show the problem frame
        self.summary_frame.forget()
        self.problem_frame = Frame(self.problem_tab)
        self.problem_frame.pack(fill="both", expand=True, padx=150, pady=80)

        # Configure the grid for questions
        self.problem_frame.grid_columnconfigure(0, weight=1)
        self.problem_frame.grid_columnconfigure(1, weight=1)
        self.problem_frame.grid_columnconfigure(2, weight=1)

        # This label will hold the current question number of the problemset
        self.num_label = Label(self.problem_frame, text="", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        self.num_label.grid(row=0, column=0, sticky="ew", padx=1)

        # This label will hold the current question of the problemset
        self.question_label = Label(self.problem_frame, text="", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=20)
        self.question_label.grid(row=0, column=1, sticky="ew", padx=1)

        # This Frame holds the entry point for users to type the answer to a problem
        self.answer_entry_frame = Frame(self.problem_frame, bg="#679FCE", padx=20, pady=20)
        self.answer_entry_frame.grid(row=0, column=2, sticky="ew", padx=1)
        self.answer_entry = Entry(self.answer_entry_frame, font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0)
        self.answer_entry.pack(side=TOP, fill="x", pady=1)

        # This frame holds the button for submitting an answer and checking if its correct
        self.submit_frame = Frame(self.problem_frame, bg="#C7DBED")
        self.submit_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=30)
        self.submit_button = Button(self.submit_frame, text="Submit", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=self.submit_answer)
        self.submit_button.pack(side=LEFT, padx=20, pady=20)

        # This label will hold the feedback for the answer the user sent (correct, incorrect, etc.)
        self.feedback_label = Label(self.submit_frame, text="", font=("Yu Gothic UI Semibold", 14), bg="#C7DBED", padx=20, pady=20)
        self.feedback_label.pack(padx=20, pady=10)

        # This frame holds the button for getting a hint to a question
        self.hint_frame = Frame(self.problem_frame, bg="#C7DBED")
        self.hint_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)
        self.hint_button = Button(self.hint_frame, text="Hint", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=self.load_hint)
        self.hint_button.pack(side=LEFT, padx=20, pady=10)
        # This label will hold the hint text
        self.hint_label = Label(self.hint_frame, text="", font=("Yu Gothic UI Semibold", 14), bg="#C7DBED", padx=20, pady=20)
        self.hint_label.pack(padx=20, pady=10)

        # Call the function for loading a question to the problem page
        self.load_question()




    """
    Function for loading a question into the problemset
    Called intially after creating the problemset page
    """
    def load_question(self):

        self.used_hint = False

        # Get the current question to load based on what number question the user is on
        self.current_question = self.question_list[self.current_question_num]

        # Set the current question number
        self.num_label.config(text=f"{self.current_question_num + 1}/10")
        # Set the question text
        self.question_label.config(text=f"{self.current_question[1]}")
        # Clear the answer field, potentially still has text in it from the previous question
        self.answer_entry.delete(0,END)
        # Clear the feedback area, potentially still has text in it from the previous question
        self.feedback_label.config(text="")
        # CLear the hint area
        self.hint_label.config(text="")

        # START TIMER - Record when question is loaded
        self.question_start_time = time.perf_counter()

    
    def load_hint(self):
        self.used_hint = True
        self.hint_label.config(text=self.current_question[3])


    """
    Function for handling when the user presses the "Submit" button on a question to submit their answer
    """
    def submit_answer(self):

        # END TIMER - Calculate the time spent on this question
        question_end_time = time.perf_counter()
        question_time = question_end_time - self.question_start_time
        self.total_time_taken += question_time

        # Keeps track of if the user was correct, used for moving fast/slow to the next problem
        user_correct = False

        # Get the user's answer from the field
        user_answer = self.answer_entry.get().strip()
        # Get the correct answer for the question
        correct_answer = self.current_question[2]
        # Get the hint for the question
        question_hint = self.current_question[3]

        # If the user was correct, we up the correct answers count, and print a random feedback message
        if(user_answer == correct_answer):

            self.correct_answer_count += 1

            if(self.used_hint):
                self.correct_with_hint_count += 1
            else:
                self.correct_no_hint_count += 1

            user_correct = True

            message_int = random.randint(1,4)
            if message_int == 1:
                self.feedback_label.config(text="Great job! Moving on...")
            elif message_int == 2:
                self.feedback_label.config(text="Correct! Moving on...")
            elif message_int == 3:
                self.feedback_label.config(text="Well done! Moving on...")
            elif message_int == 4:
                self.feedback_label.config(text="Amazing work! Moving on...")

        # If the user was incorrect, let them not
        else:
            message_int = random.randint(1,4)
            if message_int == 1:
                self.feedback_label.config(text=f"Not quite, {question_hint}. Moving on...")
            elif message_int == 2:
                self.feedback_label.config(text=f"Good try, {question_hint}. Moving on...")
            elif message_int == 3:
                self.feedback_label.config(text=f"You're on the right track, {question_hint}. Moving on...")
            elif message_int == 4:
                self.feedback_label.config(text=f"Almost there, {question_hint}. Moving on...")

        # Increase the question counter
        self.current_question_num += 1

        # Insert this attempt into the "question_attempts" table
        insert_question_into_database(
            DB_PATH,
            self.current_user_id,
            self.pset_id,
            self.current_topic_id,
            self.current_question[1],         # question_text
            self.current_question[0],         # difficulty (from CSV)
            user_answer,
            self.current_question[2],         # actual_answer
            user_correct,
            self.used_hint,           # records if a hint was used
            question_time
        )

        # Update ML topic progress after this question (only counts, not difficulty)
        self.ml.update_after_question(self.current_user_id, self.current_topic_id, user_correct, self.used_hint)

        # If this wasn't the last question, then we move onto the next question
        if(self.current_question_num < len(self.question_list)):

            if(user_correct):
                # Go to next question after 1.5 seconds
                self.after(1500, self.load_question)
            else:

                # Go to next question after 4.0 seconds
                self.after(4000, self.load_question)


        # If it was the last question, update database and go to the results after 3 seconds
        else:

            # Convert the total time taken from seconds into minutes
            total_time_minutes = self.total_time_taken / 60.0

            # Update the "psets" entry we created earlier with final stats (raw correct count)
            update_problemset_in_database(DB_PATH, self.pset_id, len(self.question_list), self.correct_answer_count, total_time_minutes)

            # Update ML per-problemset stats (pset count + weighted accuracy + difficulty + time spent on the problemset)
            self.ml.update_after_pset(self.current_user_id, self.current_topic_id, len(self.question_list), self.correct_no_hint_count, self.correct_with_hint_count, total_time_minutes)

            # Update student personal progress stats in the "users" table (practice streak, total minutes spent practicing, last practice date)
            update_student_personal_progress(DB_PATH, self.current_user_id, total_time_minutes)

            # Go to results after 3 seconds
            self.after(2000, self.show_results)


    """
    Function for showing the results of a problemset after it's completion
    """
    def show_results(self):

        # Hide the problem frame for now
        self.problem_frame.forget()

        self.results_frame = Frame(self.problem_tab)
        self.results_frame.pack(fill="both", expand=True, padx=80, pady=30)

        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(2, weight=1)
        self.results_frame.grid_columnconfigure(3, weight=1)
        self.results_frame.grid_columnconfigure(4, weight=1)

        results_header_1 = Label(self.results_frame, text="Topic", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
        results_header_1.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        results_header_2 = Label(self.results_frame, text="Difficulty", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
        results_header_2.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        results_header_3 = Label(self.results_frame, text="Questions", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
        results_header_3.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        results_header_4 = Label(self.results_frame, text="Correct", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
        results_header_4.grid(row=0, column=3, sticky="ew", padx=1, pady=1)
        results_header_5 = Label(self.results_frame, text="Accuracy", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
        results_header_5.grid(row=0, column=4, sticky="ew", padx=1, pady=1)
        
        # Get the name of the topic from it's ID
        topic_name = get_topic_name_from_topic_id(DB_PATH, self.current_topic_id)
        total_questions = len(self.question_list)
        accuracy = (self.correct_answer_count / total_questions) * 100

        stats = [topic_name, self.problemset_difficulty, total_questions, self.correct_answer_count]

        for j in range(4):
            personal_summary_header = Label(self.results_frame, text=stats[j], font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
            personal_summary_header.grid(row=1, column=j, sticky="ew", padx=1, pady=1)
        # Do accuracy separetly
        personal_summary_header = Label(self.results_frame, text=f"{accuracy}%", font=("Yu Gothic UI Semibold", 15), bg="#C7DBED", padx=20, pady=10)
        personal_summary_header.grid(row=1, column=4, sticky="ew", padx=1, pady=1)

        return_button = Button(self.results_frame, text="Return to Problem Sets", font=("Yu Gothic UI Semibold", 15), bg="#679FCE", relief=FLAT, bd=0, padx=20, pady=10, command=self.return_to_problemset)
        return_button.grid(row=2, column=0, columnspan=5, pady=30)

    """
    Function to return from results to the main problemset view
    """
    def return_to_problemset(self):

        self.results_frame.forget()

        self.summary_frame.pack(fill="both", expand=True, padx=80, pady=30)
        self.refresh_problemset_view()

        

if __name__ == "__main__":
    app = Algebro()
    app.mainloop()