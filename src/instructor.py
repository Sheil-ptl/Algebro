# Handles all instructor interactions within algebro

from database import *

import re

"""
Function for displaying an instructor's main view
Used for Creating classes, viewing all classes an instructor teaches, and getting data from students in a class
"""
def instructor_main_page(id, db_name):
    print("\nInstructor Main Page\n")

    # Print all classes an instructor teaches, if they teach no classes then this won't print any
    instructor_classes = display_classes(id, db_name)

    # If the instructor teaches no classes right now, we want them to create a class before they can access instructor functions
    if(instructor_classes == []):

        # Ask the instructor if they would like to create a class
        user_choice = input("\nYou aren't teaching any classes yet\nWould you like to add a Class? (1 - Create a class, 2 - Log out): ")
        while(True):
            # If they don't want to create a class, they log out
            if(user_choice == "2"):
                return
            # Get the info of the class, name and class code
            class_name = input("Enter the name of the class: ")
            class_code = input("Enter the class code (4-8 characters, letters and numbers): ")
            # Make sure the code entered is valid (4-8 characters, only letters and numbers)
            valid_code = validate_class_code(class_code)
            # Continue having instructor enter codes as long as they are not valid
            while(not valid_code):
                class_code = input("Invalid code, codes must be 4-8 characters and only contain letters and numbers\nEnter the classes code: ")
                valid_code = validate_class_code(class_code)
            
            # Attempt to create a class with the info entered
            create_class_check = create_class(id, class_code, class_name, db_name)

            # If the class was created successfully, the instructor can move on to using the functions
            if(create_class_check):
                print("\nClass creation successful!\n")
                break
            # Otherwise, the creation was unsuccessful and we ask if they want to try again or log out
            else:
                user_choice = input(f"\nCode {class_code} is currently in use.\nTry to add a class again? (1 - Create a class, 2 - Log out): ")


    # Instructor functions
    while(True):

        # Get the user's choice of action
        user_choice = input("1 - Create a new class\n2 - Print class list with info\n3 - Log Out\nEnter your choice: ")

        # Log out the user
        if(user_choice == "3"):
            break
        
        # Creating a new class, same logic as seen a bit above, enter info, validate info, see if the creation is successful or not
        elif(user_choice == "1"):

            class_name = input("\nEnter the name of the class: ")
            class_code = input("Enter the classes code (4-8 characters, letters and numbers): ")
            valid_code = validate_class_code(class_code)
            while(not valid_code):
                class_code = input("Invalid code, codes must be 4-8 characters and only contain letters and numbers\nEnter the classes code: ")
                valid_code = validate_class_code(class_code)
            
            create_class_check = create_class(id, class_code, class_name, db_name)

            if(create_class_check):
                print("\nClass creation successful!\n")
            else:
                print(f"\nCode {class_code} is currently in use.\n")
            
        # Displaying a specific class's student info    
        elif(user_choice == "2"):

            # Display the classes the instructor can get info from, while obtaining the codes
            class_codes = display_classes(id, db_name)
            # Get the 
            class_code = input("Enter the classes code of the class to show: ")

            while(class_code not in class_codes):
                print("Class code must be a code for a class that instructor teaches")
                class_code = input("Enter the classes code of the class to show: ")

            print_class_list_full(id, class_code, db_name)

        else:
            print("\nInvalid Choice\n")

    return


    # While they haven't chosen to log out yet
    #while(user_choice != "4"):
        # Go to the proper function depending on what option they choose
        #if(user_choice == "1"):
            #class_name = input("Enter class name: ")
            #create_class(id, class_name, db_name)
        #elif(user_choice == "2"):
            #class_id = input("Enter class ID: ")
            #print_class_list_full(class_id, db_name)
        #elif(user_choice == "3"):
            #print("staying in progress")

        # Reprompt for user choice
        #user_choice = input("1 - Create a class\n2 - Print class info\n3 - Class List\n4 - Log Out\n")






"""
Simple verification function for class codes
"""
def validate_class_code(class_code):

    # Codes should be in around 4-8 characters in length
    if(len(class_code) < 4 or len(class_code) > 8):
        return False
    
    # https://stackoverflow.com/questions/89909/how-do-i-verify-that-a-string-only-contains-letters-numbers-underscores-and-da
    # Use a regular expression to ensure the class code the instructor enters ONLY has letters and numbers
    if not re.match("^[A-Za-z0-9]+$", class_code):
        return False
    
    # If it meets the criteria it's a valid code
    return True



