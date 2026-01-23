# This script is meant to handle everything a student can do with Algebro,
# such as creating and completing problem sets, viewing personal progress,
# and viewing a class list of their peers

from database import *
from questions import *
from problemset import *

from ml_engine import AlgebroML 


"""
Function for displaying all students in the same class as the user student
Utilizes database.py to run a query on all students in the same class as the user, and printing all info
"""
def student_class_list(id, db_name):
    # Print the header of the app, with "Class List" underlined to show thats where we are
    print("Progress\tProblem Sets\t\033[4mClass List\033[0m\n")
    # Properly aligning the strings: https://www.geeksforgeeks.org/python/string-alignment-in-python-f-string/
    print(f"\033[1m{'First Name':<15} {'Last Name':<15} {'Personal Practice Streak':<30}\033[0m")
    # Call the function to access the database and print all students in the same class
    print_class_list_student_view(id, db_name)

    return


"""
NEW: Function for showing ML-based personal progress.
Uses AlgebroML.get_topic_summaries to display, per topic:
- current difficulty level
- total questions answered
- correct answers
- accuracy
- best problemset score
"""
def show_ml_progress(student_id, db_name):
    ml = AlgebroML(db_name)
    summaries = ml.get_topic_summaries(student_id)

    print("\n=== Personal Progress (ML-based) ===")
    if not summaries:
        print("No data yet. Complete a problem set to start tracking your progress.\n")
        return

    print(f"{'Topic':<25} {'Diff':<6} {'Qns':<5} {'Correct':<8} {'Accuracy':<10} {'Best Score':<10}")
    print("-" * 70)

    for s in summaries:
        topic = s["topic_name"]
        diff = s["current_difficulty"]
        total_q = s["total_questions"]
        total_correct = s["total_correct_raw"]
        acc = s["accuracy"] * 100
        best = s["best_score"] * 100

        print(f"{topic:<25} {diff:<6} {total_q:<5} {total_correct:<8} {acc:>7.1f}% {best:>9.1f}%")

    print()


"""
Function for displaying a student's personal progress, also acts as the home page for a student
Allows for students to choose what action they want to perform, viewing their progress, going to a problem set, viewing the class list, or logging out
"""
def student_personal_progress(id, db_name):

    user_first_name = get_user_first_name(db_name, id)
    print(f"\nHello, {user_first_name}\n")

    # Print the header of the app, with "Progress" underlined to show thats where we are
    print("\033[4mProgress\033[0m\tProblem Sets\tClass List\n\n")

    # Get the user's choice of action
    user_choice = input("1 - Personal Progress\n2 - Problem Set\n3 - Class List\n4 - Log Out\n")

    # While they haven't chosen to log out yet
    while (user_choice != "4"):
        # Go to the proper function depending on what option they choose
        if (user_choice == "1"):
            # NEW: Show ML-based personal progress instead of placeholder
            show_ml_progress(id, db_name)
        elif (user_choice == "2"):
            student_problemset_menu(id, db_name)
        elif (user_choice == "3"):
            student_class_list(id, db_name)

        # Reprompt for user choice
        print("\033[4mProgress\033[0m\tProblem Sets\tClass List\n\n")
        user_choice = input("1 - Personal Progress\n2 - Problem Set\n3 - Class List\n4 - Log Out\n")

    # Once they choose to log out, we return to the landing page
    return



"""
Function for displaying the problemset menu
Allows for students to choose what action they want to perform, continue learning where they left off last, or review old topics
"""
def student_problemset_menu(id, db_name):

    # Print the header of the app, with "Progress" underlined to show thats where we are
    print("Progress\t\033[4mProblem Sets\033[0m\tClass List\n\n")


    while True:
        
        # Need to figure out the id of the topic the user is currently learning
        current_topic_id = find_user_current_topic(db_name, id)

        current_topic_name = get_topic_name_from_topic_id(db_name, current_topic_id)

        # If the user has progressed through all topics, all they can do now is review
        if(current_topic_name is None):
            print("User has completed all topics")
            user_choice = input("1 - Review Past Topics\n2 - Back to Progress\n")

            if(user_choice == "1"):
                view_mastered_topics(id, db_name)

            elif(user_choice == "2"):
                break
        
            else:
                print("Invalid Option")

        else:

            # Get the user's choice of action
            user_choice = input(f"1 - Continue Learning: {current_topic_name}\n2 - Review Past Topics\n3 - Back to Progress\n")

            if(user_choice == "1"):
                problemset(id, db_name, current_topic_id)

            elif(user_choice == "2"):
                view_mastered_topics(id, db_name)

            elif(user_choice == "3"):
                break

            else:
                print("Invalid Option")

    # Return to Progress
    return


"""
Function for viewing topics the student has mastery in
Allows for students to choose an old topic to generate a problemset for
"""
def view_mastered_topics(id, db_name):

    mastered_topics = get_user_proficient_topics(db_name, id)

    if(mastered_topics == []):
        print("\nNo topics mastered yet\n")
        return

    print("\nList of Mastered Topics\n")

    for topic_id in mastered_topics:
        
        current_unit_name = get_unit_name_from_topic_id(db_name, topic_id)
        current_topic_name = get_topic_name_from_topic_id(db_name, topic_id)
        print(f"{current_unit_name}: {current_topic_name} (topic ID = {topic_id})")

    print()
    while True:
        # Get the user's choice of action
        user_choice = input("Enter the topic ID of the topic you wish to review, or 0 to go back to main problemset page: ")

        if(user_choice == "0"):
            break

        try:
            topic_choice = int(user_choice)

            if(topic_choice in mastered_topics):
                problemset(id, db_name, topic_choice)
                break
            
            else:
                print("Invalid topic ID selected")


        except ValueError:
            print("ERROR: Please enter a number")

    # Return to Main Problemset View
    return

    