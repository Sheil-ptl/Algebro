from questions import *
from database import *

from ml_engine import AlgebroML   

import time


# General Logic for handling problem sets with the database
# - problemset() gets called, we create a new entry in the "psets" database table
# - We initially populate this entry with "student_id", "topic_id", "unit", "topic"
# - We must create this entry FIRST so we have a "pset_id" we can access
# - With this "pset_id", we can create an entry in the "question_attempts" for each question, while linking that question to the "pset_id"
# - Doing this connects all the questions in a problem set individually to the problem set
# - After all questions have been answered, we can update the entry in the "psets" table with "pset_id" with the discovered information
# - This information being "date_completed", "total_questions", "answer_count", "time_spent"
#


"""
Function for problem set
Integrated with the ML component:
- Student still chooses topic and number of questions.
- Difficulty is chosen automatically by the ML engine per (student, topic).
- After each question and after the whole problemset, ML stats are updated.
- Hint flow is supported: students can type 'hint' or 'h' to see a hint.
"""
def problemset(student_id, db_name, topic_id):

    # Problemset header, highlights we are in a problemset
    print("Progress\t\033[4mProblem Sets\033[0m\tClass List\n\n")

    # Get how many questions the student wants in the problemset (set to 10 for now)
    question_count = 10

    # Initialize ML engine and get recommended difficulty
    ml = AlgebroML(db_name)
    difficulty = ml.recommend_difficulty(student_id, topic_id)

    print(f"\n[Algebro ML] Recommended difficulty for this topic: {difficulty} (1 = easy, 3 = hard)\n")

    # Initialize the problemset in the "psets" database table, with the information we currently have
    # We need the ID of this entry for the questions completed in the problemset
    pset_id = initialize_problemset_in_database(db_name, student_id, topic_id)

    # Variables to keep track of:
    # - current question number
    # - amount of correct answers (raw)
    # - total time it takes to complete the problemset
    current_question_num = 0
    correct_answer_count = 0
    total_time_taken = 0.0

    # NEW: split correct answers into with/without hint for ML weighting
    correct_no_hint = 0
    correct_with_hint = 0

    # Load questions of the chosen topic and ML-selected difficulty
    # load_questions_for_problemset expects difficulty as a string
    questions_list = load_questions_for_problemset(topic_id, str(difficulty), question_count)

    # Safety check: if no questions found (e.g., CSV issue), bail gracefully
    if not questions_list:
        print("No questions available for this topic/difficulty. Please contact your instructor.\n")
        return

    # Loop through each question picked out (random sample from CSV of that topic & difficulty)
    for question in questions_list:
        # question structure from questions.py:
        # question[0] = Difficulty
        # question[1] = Question String
        # question[2] = Answer
        # question[3] = Hint

        current_question_num += 1
        print(f"Question {current_question_num}: {question[1]}")

        used_hint = False

        # Hint-capable input flow 
        # First chance: student can answer OR ask for a hint
        start_time = time.perf_counter()
        user_input = input("Answer (or type 'hint' for a hint): ")

        if user_input.lower() in ("hint", "h"):
            # Show the hint and mark that they used it
            print(f"Hint: {question[3]}")
            used_hint = True

            # Restart timer for the actual answer after seeing the hint
            start_time = time.perf_counter()
            student_answer = input("Now enter your answer: ")
            end_time = time.perf_counter()
        else:
            # They answered directly with no hint
            student_answer = user_input
            end_time = time.perf_counter()

        question_time = end_time - start_time
        total_time_taken += question_time

        # True/False depending on if they got the question right
        was_student_correct = (student_answer == question[2])

        # Feedback + counting for ML
        if was_student_correct:
            print("Correct!\n")
            correct_answer_count += 1
            if used_hint:
                correct_with_hint += 1
            else:
                correct_no_hint += 1
        else:
            print(f"Incorrect. Correct Answer: {question[2]}")

        # Insert this attempt into the "question_attempts" table
        insert_question_into_database(
            db_name,
            student_id,
            pset_id,
            topic_id,
            question[1],         # question_text
            question[0],         # difficulty (from CSV)
            student_answer,
            question[2],         # actual_answer
            was_student_correct,
            used_hint,           # records if a hint was used
            question_time
        )

        # Update ML topic progress after this question (only counts, not difficulty)
        ml.update_after_question(student_id, topic_id, was_student_correct, used_hint)

    # Convert the total time taken from seconds into minutes
    total_time_minutes = total_time_taken / 60.0

    # Update the "psets" entry we created earlier with final stats (raw correct count)
    update_problemset_in_database(db_name, pset_id, question_count, correct_answer_count, total_time_minutes)

    # Update ML per-problemset stats (pset count + weighted accuracy + difficulty + time spent on the problemset)
    ml.update_after_pset(student_id, topic_id, question_count, correct_no_hint, correct_with_hint, total_time_minutes)

    # Update student personal progress stats in the "users" table (practice streak, total minutes spent practicing, last practice date)
    update_student_personal_progress(db_name, student_id, total_time_minutes)

    average_question_time_seconds = total_time_taken / question_count




    print(f"================================================")
    print(f"Problemset Complete")
    print(f"Questions Answered: {question_count}")
    print(f"Questions Answered Correctly: {correct_answer_count}")
    print(f"Total Time Taken (min): {total_time_minutes:.2f}")
    print(f"Average Time Per Question (sec): {average_question_time_seconds:.2f}")
    print(f"================================================\n")

    return
