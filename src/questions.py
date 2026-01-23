import csv
import os
import random


from database import *

"""
Function for loading a specific amount of questions from the question bank
Allows for questions to be loaded for generated problem sets, from a given topic number, a difficulty in that topic, and the amount to be loaded (allows for multiple difficulties in one problem set)
"""
def load_questions_for_problemset(topic_id, topic_difficulty, questions_count):

    # The questionbank dictionary contains the names of all files in the questionbank/ folder, 
    questionbank = {
        1: "unit1_distributive_property",
        2: "unit1_simplifying_expressions",
        3: "unit1_evaluating_expressions",
        4: "unit2_one_step_equations",
        5: "unit2_two_step_equations",
        6: "unit2_multi_step_equations",
        7: "unit3_basic_exponents",
        8: "unit3_exponent_rules"
    }

    # https://www.w3schools.com/python/python_dictionaries.asp
    # The file_to_load is the CSV we want to draw questions from, which is derived from the topic id passed into the function
    # The id passed into the function is connected to the id of the CSV name in the questionbank dictionary
    file_to_load = "questionbank/" + questionbank[topic_id] + ".csv"

    print(f"File to load: {file_to_load}")
    
    # If the file does not exist, then there was an error somewhere and we cannot draw questions
    if not os.path.exists(file_to_load):
        print("Unable to find question CSV file in questionbank/\n")
        return None # This should return maybe an empty list instead
    
    # This list will be contain all questions of the specified difficulty, and each element will be a list of question[]: 
    # question[0] = difficulty, question[1] = question string, question[2] = question answer, question[3] = answer hint
    questions_list = []

    # https://www.geeksforgeeks.org/pandas/reading-csv-files-in-python/
    # Open the CSV of the topic specified, IMPORTANT TO SPECIFY UTF-8 as the encoding, as this is the encoding of CSV files (usually)
    with open(file_to_load, mode = 'r', encoding='utf-8') as file:
        csv_file = csv.DictReader(file)

        # Go through each row of the CSV file
        for row in csv_file:
            # If the current row has the desired difficulty, then we add it to the list of potential questions
            if row["Difficulty"] == topic_difficulty:
                # Create a list for the current question, then append it's attributes
                current_question = []
                current_question.append(row["Difficulty"])
                current_question.append(row["Question"])
                current_question.append(row["Answer"])
                current_question.append(row["Hint"])
                # just for testing teehee
                #print(current_question)

                questions_list.append(current_question)


    # https://www.w3schools.com/python/ref_random_sample.asp
    # Return a random sequence of the questions of the difficulty specified
    return random.sample(questions_list, questions_count)

    












