import sqlite3
from datetime import datetime
from ml_engine import AlgebroML

# NOTES: May need to encrypt passwords somehow? Might be overkill

# database.py is meant to contain all database operations of Algebro in one program file
# This is for logical reasons, can keep modules separate and allows for easy understandability and debugging


# Function to initialize all tables used for the program
# Users Table - Contains all key user info when registering, as well as practice streak, time spent, and last time practicing (N/A for instructors)
def initialize_all_database_tables(db_name):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Table 1: Users
    # Contains registration info on each user, including first, last, and middle name, username, password, and their role.
    # Includes an ID for each user that automatically increments, as well as information that comes with use of the program,
    # like practice streak (int), time spent learning (int, in minutes), and last practice date (sql date datatype) - All this info is NULL for instructors
    # Also contains a foreign key linking the users to the classes they are a part of
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname VARCHAR(256) NOT NULL,
            lname VARCHAR(256) NOT NULL,
            mname VARCHAR(256),
            username VARCHAR(256) NOT NULL UNIQUE,
            password VARCHAR(256) NOT NULL,
            role VARCHAR(10) CHECK(role IN ('student', 'instructor', 'general')),
            classid INTEGER,
            pstreak INTEGER DEFAULT 0,
            tspent INTEGER DEFAULT 0,
            lastprac DATE,   
            FOREIGN KEY (classid) REFERENCES classes(id)
        )     
    ''')


    # Table 2: Classes
    # Contains the info for each class, including the ID of the instructor teaching, the class name, and the class code
    # Includes an ID for each class that automatically increments
    # Also contains a foreign key linking the instructor ID to the ID of the instructor in the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Database internal code
            instructor_id INTEGER,       
            class_code VARCHAR(50) UNIQUE,                  -- Human-friendly code chosen by the instructor
            class_name VARCHAR(256) NOT NULL,
            FOREIGN KEY (instructor_id) REFERENCES users(id)
        )     
    ''')



    # Table 3: Units
    # Contains the info of all units included in the program, which are the umbrella over topics (units -> topics -> topic difficulty)
    # Important for linking topics to units, then problem sets to topics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY,                         -- ID of the unit, not autoincremented because unlike other tables these are manually updated at the start of the program, we choose the ID
            unit_name VARCHAR(256)                         -- Name of the unit that contains a group of topics           
        )     
    ''')



    # Table 4: Topics
    #
    #
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,                         -- ID of the topic, not autoincremented because unlike other tables these are manually updated at the start of the program, we choose the ID
            unit_id INTEGER,                                -- ID of the unit this topic is a part of
            topic_name VARCHAR(256),                        -- Name of a particular topic         
            topic_order INTEGER,                            -- Order of this particular topic in the unit, like 1-step equations would be 1, 2-step equations would be 2, etc...
            FOREIGN KEY (unit_id) REFERENCES units(id)      -- Reference to the problem set key so we can keep track of all questions included in a problem set
        )     
    ''')




    # Table 5: Problem Sets
    # Contains the info for each problem set a student completes, including the topic, the difficulty level, their score, and time spent (in minutes)
    # Includes an ID for each problem set that automatically increments
    # Also contains a foreign key linking the student ID to the ID of the student who completed the problem set in the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS psets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,           -- ID of the problemset
            student_id INTEGER,                             -- ID of the student that attempted the problemset
            topic_id INTEGER,                               -- ID of the topic that the problemset is based on
            unit VARCHAR(256),                              -- Name of the unit that the problemset is based on
            topic VARCHAR(256),                             -- Name of the topic that the problemset is based on
            date_completed DATE,                            -- Date the problemset was completed (for practice streak)
            total_questions INTEGER,                        -- Amount of questions on the problemset
            answer_count INTEGER,                           -- Amount of answers on the problemset
            time_spent FLOAT,                               -- Time spent doing the problemset (in minutes)
            FOREIGN KEY (student_id) REFERENCES users(id),  -- Reference to the student key to get the ID of the student who did the problemset
            FOREIGN KEY (topic_id) REFERENCES topics(id)    -- Reference to the topic key to get the ID of the topic the problemset is based on
        )     
    ''')

    # Table 6: Individual Questions
    # Contains the info for a problem a student completes within a problemset
    # Includes the question, it's difficulty level
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,           -- ID of the attempt
            student_id INTEGER,                             -- ID of the student that attempted the question
            pset_id INTEGER,                                -- ID of the problem set the question is apart of
            topic_id INTEGER,                               -- ID of the topic the question is a part of
            question_text VARCHAR(256),                     -- The question being asked, as a string
            difficulty INTEGER,                             -- The question's level of difficulty
            student_answer VARCHAR(256),                    -- The answer the student gave
            actual_answer VARCHAR(256),                     -- The actual answer to the question
            was_student_correct BOOLEAN,                    -- Boolean to keep track of if the student got the question right
            used_hint BOOLEAN,                              -- Boolean to keep track of if the student used a hint or not
            time_spent FLOAT,                               -- Time spent on this particular question (import for tracking if a student struggled)
            FOREIGN KEY (student_id) REFERENCES users(id),  -- Reference to the user's key so we know which student ID is doing the question
            FOREIGN KEY (pset_id) REFERENCES psets(id),     -- Reference to the problem set key so we can keep track of all questions included in a problem set
            FOREIGN KEY (topic_id) REFERENCES topics(id)    -- Reference to the topics key so we can keep track which topic this question is a part of
        )
    ''')


    # Table 7: Student Progress on Topics
    # Tracks a students progress on EACH topic individually
    # Critial for adapting to a students skill level in a topic, can better understand where they are and the ML can adjust accordingly
    # Once they have shown profi
    # Could potentially add avergae time per questions, mastery boolean
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_topic_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,           -- ID of the 
            student_id INTEGER,                             -- ID of the student who's progress is being tracked
            topic_id INTEGER,                               -- ID of the topic that is being tracked
            current_difficulty_level INTEGER,               -- Current level of difficulty the student is at in the topic, (predicted by the ML)
            total_topic_psets INTEGER,                      -- The amount of problemsets the student has completed in this topic
            total_topic_questions INTEGER,                  -- Total questions answered in this topic's domain
            total_correct_answers INTEGER,                  -- Total correct answers made in this topic's domain
            highest_score FLOAT,                            -- Highest score the student has made in a problemset in this topic's domain
            time_spent FLOAT DEFAULT 0,                     -- Total time the student has spent learning and practicing this topic
            proficient BOOLEAN,                             -- Determining if the student has mastered/become proficient enough in a specific topic
            FOREIGN KEY (student_id) REFERENCES users(id),  -- Reference to the user's key so we know which student ID is doing the question
            FOREIGN KEY (topic_id) REFERENCES topics(id)    -- Reference to the topics key so we can keep track which topic this question is a part of
        )
    ''')

    # Commit the changes made
    conn.commit()
    conn.close()





"""
Function for loading units and topics into the database
Since the units/topics are predesigned, this doesn't have to happen dynamically (can hardcode names and such)
"""
def seed_units_and_topics(db_name):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM units")
    check_units = cursor.fetchone()

    if(check_units[0] > 0):
        print("Units are already loaded")
        cursor = conn.cursor()
        return
    

    # Otherwise we populate the units and topics tables

    units = [
        (1, "Expressions and Properties"),
        (2, "Solving for x"),
        (3, "Understanding Exponents")
    ]

    # https://www.tutorialspoint.com/python/python_sqlite3_cursor_executemany_function.htm
    cursor.executemany("""
        INSERT INTO units (id, unit_name)
        VALUES (?, ?)
        """, units)
    

    topics = [
        # Topics for Unit 1
        (1, 1, "Distributive Property", 1),
        (2, 1, "Simplifying Expressions", 2),
        (3, 1, "Evaluating Expressions", 3),

        # Topics for Unit 2 (filler for now)
        (4, 2, "One-Step Equations", 1),
        (5, 2, "Two-Step Equations", 2),
        (6, 2, "Multi-Step Equations", 3),

        # Topics for Unit 3 (filler for now)
        (7, 3, "Basic Exponents", 1),
        (8, 3, "Exponent Rules", 2),
    ]


    cursor.executemany("""
        INSERT INTO topics (id, unit_id, topic_name, topic_order)
        VALUES (?, ?, ?, ?)
        """, topics)
    

    conn.commit()
    conn.close()

    print(f"\nUnits and Topics added to database\nAdded {len(units)} units & {len(topics)} topics.\n")




# Function to try and register a new user to the database, checks if the username is unique and all info is filled
def register_user(fname, lname, mname, username, password, role, classid, db_name):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Ensure the username chosen doesn't already exist in the database
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    check_existing_username = cursor.fetchone()

    # If a matching username was found, we return False as usernames must be unique
    if check_existing_username is not None:
        conn.close()
        return False
    
    # Otherwise, we add the new user's information to the database
    cursor.execute(
        "INSERT INTO users (fname, lname, mname, username, password, role, classid) " \
        "VALUES(?, ?, ?, ?, ?, ?, ?)", \
        (fname, lname, mname, username, password, role, classid)
        )

    # Commit the changes made
    conn.commit()
    conn.close()

    # Return True to show that the registration was successful
    return True


# Function to try and login an existing user to the program, if the username exists and the database and the password matches, they get logged in
# Returns the logged in user's account ID
def login_user(username, password, db_name):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Attempt to retrieve the password from the database matching the username entered
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    # dbPassword is a tuple!
    db_password = cursor.fetchone()

    

    # If there is no password associated with the entered username, then the username doesn't exist
    # If the password entered does not match the database, the login info is invalid
    if db_password is None or db_password[0] != password:
        conn.close()
        return None

    # If the password was found and matches the user entered password, return the ID and role of the user
    cursor.execute("SELECT id, role FROM users WHERE username = ?", (username,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info[0], user_info[1]
    


""" Getter helper function to retrieve a user's first name from their id"""
def get_user_first_name(db_name, id):
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Get the first name from the id
    cursor.execute("SELECT fname FROM users WHERE id = ?", (id,))
    user_first_name = cursor.fetchone()

    conn.close()
    return user_first_name[0]


""" Getter helper function to retrieve a student's last name from their id"""
def get_student_last_name(id, db_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Get the last name from the id
    cursor.execute("SELECT lname FROM users WHERE id = ?", (id,))
    user_lastname = cursor.fetchone()

    conn.close()
    return user_lastname[0]


""" Getter helper function to retrieve a student's ID from their username"""
def get_student_id(username, db_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Get the id from the username
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()

    conn.close()
    return user_id[0]


""" Function for printing student's view of class list"""
def print_class_list_student_view(id, db_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get the user's class ID
    cursor.execute("SELECT classid FROM users WHERE id = ?", (id,))
    student_class_id = cursor.fetchone()
    # Get the first and last names of all students in the same class of the user, as well as their practice streak
    cursor.execute("SELECT fname, lname, pstreak FROM users WHERE classid = ?", (student_class_id[0],))
    # Fetch all returns a list of tuples, each containing a students first and last names, along with their practice streak
    all_student_info = cursor.fetchall()

    # If there is at least one person in the class
    if(all_student_info):
        # For each student in the class, print out their information
        for student_info in all_student_info:
            print(f"{student_info[0]:<15} {student_info[1]:<15} {student_info[2]:<30}")
        print("\n")

    conn.close()
    return



"""
GUI helper function 
Returns a list of tuples of all students in a class with the info (fname, lname, pstreak)
"""
def get_class_list_data(student_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get the user's class ID
    cursor.execute("SELECT classid FROM users WHERE id = ?", (student_id,))
    result = cursor.fetchone()
    
    # Error handling
    if not result or result[0] is None:
        conn.close()
        return []

    student_class_id = result[0]

    # Get the last and first names of all students in the same class of the user, as well as their practice streak
    cursor.execute("SELECT lname, fname, pstreak FROM users WHERE classid = ? AND role = 'student' ORDER BY lname, fname", (student_class_id ,))
    # Fetch all returns a list of tuples, each containing a students first and last names, along with their practice streak
    all_student_info = cursor.fetchall()
    conn.close()

    # Return the list of student info contained in tuples
    return all_student_info


"""
GUI helper function 
Gets ML-based progress data from the ML engine based on student past performance
Returns a list of dictionaries [{"topic_name": str, "current_difficulty": int, "total_questions": int, ...]
"""
def get_student_progress_data(student_id, db_name):
    
    ml = AlgebroML(db_name)
    summaries = ml.get_topic_summaries(student_id)
    return summaries



def get_student_weakest_topic_id(student_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Min starts at 100%
    min_average = 1.00
    min_topic_id = None

    # Get the user's class ID
    cursor.execute("SELECT topic_id, total_topic_questions, total_correct_answers FROM student_topic_progress WHERE student_id = ? AND proficient = 1 AND total_topic_questions > 0", (student_id,))
    results = cursor.fetchall()

    if(results):

        for result in results:

            current_topic_id, current_topic_questions, current_topic_answers = result

            current_topic_average = current_topic_answers/ current_topic_questions

            if(current_topic_average < min_average):
                min_average = current_topic_average
                min_topic_id = current_topic_id

    # Returns none if the user is the same across all topics
    return min_topic_id








"""
Function to retrive a class ID corresponding to a given class code
"""
def get_class_id_from_code(class_code, db_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM classes WHERE class_code = ?", (class_code,))
    result = cursor.fetchone()

    conn.close()

    if(result):
        return result[0]
    else:
        return None
    





#--------------------instructor functions------------------------------

"""GUI Helper function for returning all info for students in a class"""
def return_class_student_info(instructor_id, class_code, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # First, we get the class_id and class_name from the class_code
    cursor.execute("SELECT id FROM classes WHERE class_code = ? AND instructor_id = ?", (class_code, instructor_id))
    result = cursor.fetchone()

    if not result:
        conn.close()
        print(f"\nClass with code {class_code} not found.\n")
        return None

    class_id = result[0]

    # Get the first and last names of all students in the same class of the user, as well as their practice streak
    cursor.execute("SELECT id, lname, fname, pstreak, tspent FROM users WHERE classid = ? AND role = 'student' ORDER BY lname, fname",
                   (class_id,))
    # Fetch all returns a list of tuples, each containing a students first and last names, along with their practice streak
    all_student_info = cursor.fetchall()
    conn.close()

    if all_student_info:
        return all_student_info

    else:
        return []





""" Function for printing all info for students in a class"""
def print_class_list_full(instructor_id, class_code, db_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # First, we get the class_id and class_name from the class_code
    cursor.execute("SELECT id, class_name FROM classes WHERE class_code = ? AND instructor_id = ?", (class_code, instructor_id))

    result = cursor.fetchone()

    if not result:
        conn.close()
        print(f"\nClass with code {class_code} not found.\n")
        return

    class_id, class_name = result

    #print(f"\n{'Class Name':<25} {'Class Code':<8}")
    #print("--------------------------------------------------")


    # Get the first and last names of all students in the same class of the user, as well as their practice streak
    cursor.execute("SELECT id, lname, fname, tspent, pstreak FROM users WHERE classid = ? AND role = 'student' ORDER BY lname, fname",
                   (class_id,))
    # Fetch all returns a list of tuples, each containing a students first and last names, along with their practice streak
    all_student_info = cursor.fetchall()

    #print columns

    #print(f"\n{'ID':<5} {'Last Name':<15} {'First Name':<15} {'Time Spent (min)':<20} {'Practice Streak':<15}")
    # If there is at least one person in the class
    #print(all_student_info)
        #print("\nNo students enrolled in this class yet.\n")

    #print()
    conn.close()
    return all_student_info


""" GUI Helper function to return all names and codes an instructor teaches"""
def return_all_classes(instructor_id, db_name):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Select all class names and ids database
    cursor.execute("SELECT class_name, class_code FROM classes WHERE instructor_id = ?", (instructor_id,))

    # Print out all classes the user is a part of
    output = cursor.fetchall()
    conn.close()

    class_codes = []

    #print(f"\n{'Class Name':<25} {'Class Code':<8}")
    #print("--------------------------------------------------")
    for class_name, class_code in output:
    #    print(f"{class_name:<30} {class_code:<8}")
        class_codes.append(class_code)

   # print()

    return output



# Function to display an instructor's classes
def display_classes(instructor_id, db_name):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Select all class names and ids database
    cursor.execute("SELECT class_name, class_code FROM classes WHERE instructor_id = ?", (instructor_id,))

    # Print out all classes the user is a part of
    output = cursor.fetchall()
    conn.close()

    class_codes = []

    #print(f"\n{'Class Name':<25} {'Class Code':<8}")
    #print("--------------------------------------------------")
    for class_name, class_code in output:
        #print(f"{class_name:<30} {class_code:<8}")
        class_codes.append(class_code)

    #print()

    return output




"""
Function to create a class and insert it into the "classes" table
Takes an instructor's ID, a class name, and a class code and creates a class from it
Ensures info is filled in properly and the class code is unique
"""
def create_class(instructor_id, class_code, class_name, db_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Ensure the class code chosen doesn't already exist in the database
    cursor.execute("SELECT class_code FROM classes WHERE class_code = ?", (class_code,))
    check_existing_class_code = cursor.fetchone()
    # If the class code is not unique we reject the creation of a class
    if(check_existing_class_code):
        conn.close()
        return False

    cursor.execute("INSERT INTO classes (instructor_id, class_code, class_name) VALUES (?, ?, ?)", (instructor_id, class_code, class_name))

    conn.commit()
    conn.close()

    # Return true to signal the creation of the class was successful
    return True

def display_student_info(id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, lname, fname, mname,tspent  FROM users WHERE id = ?", (id,))

    # print columns
    print(f"\033{'Id':<5} {'Username':<15} {'Last Name':<15} {'First Name':<15}{'Middle Name':<15} \033")
    student_info = cursor.fetchone()
    print(f"{student_info[0]:<5} {student_info[1]:<15} {student_info[2]:<15} {student_info[3]:<15} "
                  f"{student_info[4]:<15}")

    conn.close()

def edit_student_info(uname, id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE id = ?", (uname, id))
    conn.commit()
    conn.close()








"""
Function to return all codes of class an instructor teaches
If they are, it returns the id of all classes they teach. If they aren't a part of any, it returns an empty list
Also used to check if an instructor teaches a class at all
"""
def get_instructor_class_codes(db_name, instructor_id):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get all the class codes of the classes the instructor teaches
    cursor.execute("SELECT class_codes FROM classes WHERE instructor_id = ?", (instructor_id,))
    result = cursor.fetchall()

    # If they teach at least one class
    if(result):
        # Append the class codes of the classes they teach in a list, then return it
        class_codes = []
        for row in result:
            class_codes.append(row[0])
        conn.close()
        return class_codes
    # If they aren't teaching any classes, return an empty list
    else:
        conn.close()
        return []



def insert_problemset_to_database(student_id, db_name, topic_id, unit_string, topic_string, question_count, answer_count, total_time_minutes):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (student_id,))
    check_existing_id = cursor.fetchone()

    # If the ID wasn't found in the users table, then we cannot add the problem set results to the psets table
    if check_existing_id is None:
        conn.close()
        return False

    #https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python
    current_date = datetime.today().strftime('%Y-%m-%d')


    
    cursor.execute(
        "INSERT INTO psets (student_id, topic_id, unit, topic, date_completed, total_questions, answer_count, time_spent) " \
        "VALUES(?, ?, ?, ?, ?, ?, ?, ?)", \
        (student_id, topic_id, unit_string, topic_string, current_date, question_count, answer_count, total_time_minutes)
        )


    # Commit the changes made
    conn.commit()
    conn.close()

    # Return True to show that the registration was successful
    return True




""" 
Function initializing an entry in the "psets" table with basic information
Vital so we can gain access to the ID of this entry, which is used for each question that is a part of the problemset
"""
def initialize_problemset_in_database(db_name, student_id, topic_id):

    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # First, by using "topic_id" we are able to find the name of not only the topic, but also the unit
    cursor.execute("SELECT topic_name, unit_id FROM topics WHERE id = ?", (topic_id,))
    topic_info = cursor.fetchone()
    # Derive the topic name, and the ID of the unit the topic is a part of
    topic_name = topic_info[0]
    unit_id = topic_info[1]

    # Second, by using "unit_id" we are able to find the name of the unit
    cursor.execute("SELECT unit_name FROM units WHERE id = ?", (unit_id,))
    unit_info = cursor.fetchone()
    # Derive the name of the unit
    unit_name = unit_info[0]


    # Add the information to a new entry in the "psets" table, with the rest of the elements in the entry being null for now
    cursor.execute("""
        INSERT INTO psets (student_id, topic_id, unit, topic)
        VALUES(?, ?, ?, ?)
        """, (student_id, topic_id, unit_name, topic_name)
        )

    # Since we just added the problemset to the table, this will return the ID of the problemset that was just added to the table
    pset_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Return the ID of the problemset entry
    return pset_id



""" 
Function updating an entry in the "psets" table with information gathered after the completion of a problemset
"""
def update_problemset_in_database(db_name, pset_id, total_questions, answer_count, time_spent):

    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python
    # Get the current date for the completion date of the problemset
    current_date = datetime.today().strftime('%Y-%m-%d')


    # Add the information to the entry in the "psets" table that matches "pset_id" which was created at the start of the problemset
    cursor.execute("""
        UPDATE psets
        SET date_completed = ?, total_questions = ?, answer_count = ?, time_spent = ?
        WHERE id = ?
        """, (current_date, total_questions, answer_count, time_spent, pset_id)
    )

    conn.commit()
    conn.close()
    return 



""" 
Function to add an entry to the "question_attempts" database table
Vital so we can access data on a particular question and see how the user perfomed, if they got it right, how long it took, etc.
"""
def insert_question_into_database(db_name, student_id, pset_id, topic_id, question_text, difficulty, student_answer, actual_answer, was_student_correct, used_hint, time_spent):

    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Insert all the data from the question answered by the student into the database table
    cursor.execute("""
        INSERT INTO question_attempts (student_id, pset_id, topic_id, question_text, difficulty, student_answer, actual_answer, was_student_correct, used_hint, time_spent)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, pset_id, topic_id, question_text, difficulty, student_answer, actual_answer, was_student_correct, used_hint, time_spent)
        )
    

    conn.commit()
    conn.close()

    return


"""
Updates a student's practice streak, overall time spent learning, and their last known practice date
Called after the completion of a problemset
"""
def update_student_personal_progress(db_name, student_id, time_spent):

    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Now since a student's practice streak is kind of part of their progress, we need to update that
    # Find the last time they practiced
    cursor.execute("SELECT lastprac FROM users WHERE id = ?", (student_id,))
    result = cursor.fetchone()

    # If there was a last practice date found, set it
    if(result):
        last_practice_date = result[0]
    # If there wasn't and this was the first problemset completed
    else:
        last_practice_date = None
    
    # First case, updating an existing last practice date
    if(last_practice_date):
        # Check if the student has already practiced today
        cursor.execute("SELECT date('now') = ?", (last_practice_date,))
        practiced_today = cursor.fetchone()[0]

        # If the student has not practiced today
        if(not practiced_today):
            # Check if the student practiced yesterday, so we know if the student has continued their streak
            cursor.execute("SELECT date('now', '-1 day') = ?", (last_practice_date,))
            practiced_yesterday = cursor.fetchone()[0]

            # If the student did practice yesterday, we can increment their streak in the "users" table
            if(practiced_yesterday):
                cursor.execute("""
                    UPDATE users
                    SET pstreak = pstreak + 1, lastprac = date('now')
                    WHERE id = ?
                """, (student_id,))
            # If the student did not practice yesterday, that makes their streak invalid and it resets to 1
            else:
                cursor.execute("""
                    UPDATE users
                    SET pstreak = 1, lastprac = date('now')
                    WHERE id = ?
                """, (student_id,))
        
    # Second case, this is a student's first time practicing/doing a problemset
    else:
        cursor.execute("""
            UPDATE users
            SET pstreak = 1, lastprac = date('now')
            WHERE id = ?
        """, (student_id,))


    # Last thing to do is increase the total time they have spent practicing
    cursor.execute("""
            UPDATE users
            SET tspent = tspent + ?
            WHERE id = ?
        """, (time_spent, student_id,))
    
    conn.commit()
    conn.close()

    return



"""
Returns the id of the topic the user is currently studying
"""
def find_user_current_topic(db_name, student_id):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Currently we offer 9 different topics, could change in the future
    for i in range(1, 10):

        cursor.execute("SELECT proficient FROM student_topic_progress WHERE student_id = ? AND topic_id = ?", (student_id, i))
        result = cursor.fetchone()


        # If there is no record for this student on this topic, then they haven't started it yet and it is up next
        if(result is None):
            conn.close()
            return i

        # Otherwise, the student has started the topic but they haven't mastered it yet
        proficiency_in_topic = result[0]
        if(proficiency_in_topic == 0):
            conn.close()
            return i

    # If we reach here that means the student has reached mastery in all topics
    conn.close()
    return None


"""
Returns the name of a topic from it's ID
"""
def get_topic_name_from_topic_id(db_name, topic_id):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT topic_name FROM topics WHERE id = ?", (topic_id,))

    result = cursor.fetchone()

    if(result is not None):
        conn.close()
        return result[0]
    else:
        conn.close()
        return None


"""
Returns the a list of all topic IDs that a student is proficient in
"""
def get_user_proficient_topics(db_name, student_id):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT topic_id FROM student_topic_progress WHERE student_id = ? AND proficient = ?", (student_id, 1))
    result = cursor.fetchall()

    if(result):

        topic_ids = []

        for row in result:
            topic_ids.append(row[0])
        conn.close()
        return topic_ids

    else:
        conn.close()
        return []



"""
Returns the name of a unit from a topic ID
"""
def get_unit_name_from_topic_id(db_name, topic_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT unit_id FROM topics WHERE id = ?", (topic_id,))
    result = cursor.fetchone()

    if(result is not None):
        cursor.execute("SELECT unit_name FROM units WHERE id = ?", (result[0],))
        result2 = cursor.fetchone()

        conn.close()
        return result2[0]

    conn.close()
    return None