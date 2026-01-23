import sqlite3

class AlgebroML:
    """
    Lightweight adaptive engine for Algebro.

    Responsibilities:
    - Track per-topic performance for a student.
    - Maintain a 'current_difficulty_level' per topic for each student.
    - Recommend a difficulty level for new problemsets based on past performance.
    - Treat 'correct with hint' as weaker than 'correct without hint'.
    - Track hint reliance per topic.
    """

    def __init__(self, db_name: str):
        """
        db_name: path to the SQLite database (same as you pass around elsewhere).
        We keep behaviour deterministic (no random exploration) to make it predictable.
        """
        self.db_name = db_name

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    # INTERNAL UTILITIES

    def _ensure_topic_progress_row(self, student_id: int, topic_id: int) -> bool:
        """
        Make sure there is a row in student_topic_progress for (student, topic).
        Returns:
            True  -> if a NEW row was created (no previous data for this topic)
            False -> if an existing row was already there
        """
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id
            FROM student_topic_progress
            WHERE student_id = ? AND topic_id = ?
            """,
            (student_id, topic_id),
        )
        row = cur.fetchone()

        if row is None:
            # Default difficulty: 1 (easiest), no stats yet
            cur.execute(
                """
                INSERT INTO student_topic_progress
                    (student_id, topic_id,
                     current_difficulty_level,
                     total_topic_psets,
                     total_topic_questions,
                     total_correct_answers,
                     highest_score)
                VALUES (?, ?, ?, 0, 0, 0, 0.0)
                """,
                (student_id, topic_id, 1),
            )
            conn.commit()
            conn.close()
            return True  # new row created

        conn.close()
        return False  # row already existed



    # PUBLIC ML API

    def recommend_difficulty(self, student_id: int, topic_id: int) -> int:
        """
        Recommend a difficulty level for a new problemset in a topic for a student.

        Rules:
        - If this is the FIRST time the student touches this topic,
          ALWAYS start at difficulty 1.
        - Otherwise, return the saved current_difficulty_level (no randomness).
        """

        # GREG CHANGE! Moving this to update_after_pset() incase a user quits in the middle of a problemset

        # If no row yet, create one, set difficulty 1, and start them at 1.
        #is_new = self._ensure_topic_progress_row(student_id, topic_id)
        #if is_new:
        #    return 1

        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT current_difficulty_level
            FROM student_topic_progress
            WHERE student_id = ? AND topic_id = ?
            """,
            (student_id, topic_id),
        )
        row = cur.fetchone()
        conn.close()

        # Safety default if something unexpected happened
        if row is None:
            return 1

        current_diff = row[0]

        # Clamp difficulty to [1, 3] just in case
        return max(1, min(3, current_diff))
    


    def update_after_question(self, student_id: int, topic_id: int,
                              was_correct: bool, used_hint: bool):
        """
        Called after EACH question is answered.

        Behaviour:
        - Only updates question counts (total_topic_questions and total_correct_answers).
        - Does NOT change difficulty here.
        - We store total_correct_answers as raw "fully correct + correct with hint"
          just as a basic integer summary; weighted logic is handled per problemset.
        """
        self._ensure_topic_progress_row(student_id, topic_id)

        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, total_topic_questions, total_correct_answers
            FROM student_topic_progress
            WHERE student_id = ? AND topic_id = ?
            """,
            (student_id, topic_id),
        )
        row = cur.fetchone()

        if row is None:
            conn.close()
            return

        prog_id, total_q, total_correct = row

        total_q += 1
        if was_correct:
            total_correct += 1  # raw count; hint/non-hint difference handled elsewhere

        cur.execute(
            """
            UPDATE student_topic_progress
            SET total_topic_questions = ?,
                total_correct_answers = ?
            WHERE id = ?
            """,
            (total_q, total_correct, prog_id),
        )

        conn.commit()
        conn.close()


    def update_after_pset(self, student_id: int, topic_id: int,
                          total_questions: int,
                          correct_no_hint: int,
                          correct_with_hint: int,
                          time_spent: float):
        """
        Called once AFTER a problemset is completed.

        Behaviour:
        - Updates:
            * total_topic_psets
            * highest_score (best *weighted* accuracy seen for that topic)
            * current_difficulty_level (at most +1 or -1 per problemset)

        Weighting:
            - correct without hint      -> 1.0
            - correct with hint         -> 0.5
            - incorrect                 -> 0

        Difficulty Scaling based on *weighted* accuracy (and lightly on time_spent):
            * accuracy >= 85%  -> level UP by 1 (if not already at 3),
                                  but only if they didn't rush too fast.
            * accuracy <= 40%  -> level DOWN by 1 (if not already at 1).
            * if they spent a long time and scored around 50%,
              we also move them DOWN.
            * else             -> stay at same level
        """
        self._ensure_topic_progress_row(student_id, topic_id)

        if total_questions <= 0:
            return

        # Weighted correctness (ignoring time for now)
        effective_correct = correct_no_hint + 0.5 * correct_with_hint
        pset_accuracy_eff = effective_correct / total_questions  # 0.0 - 1.0

        # --- NEW: incorporate time_spent into how we interpret this accuracy ---
        # time_spent is in MINUTES (based on your DB design).
        # Compute average time per question in seconds.
        avg_time_sec = None
        if time_spent is not None and total_questions > 0:
            avg_time_sec = (time_spent * 60.0) / total_questions

        # Interpret time:
        fast_threshold_sec = 5.0   # "rushed"
        slow_threshold_sec = 45.0   # "spent a long time"

        is_fast = avg_time_sec is not None and avg_time_sec < fast_threshold_sec
        is_slow = avg_time_sec is not None and avg_time_sec > slow_threshold_sec

        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id,
                   total_topic_psets,
                   current_difficulty_level,
                   highest_score,
                   total_topic_questions,
                   total_correct_answers,
                   proficient
            FROM student_topic_progress
            WHERE student_id = ? AND topic_id = ?
            """,
            (student_id, topic_id),
        )
        row = cur.fetchone()

        if row is None:
            conn.close()
            return

        prog_id, total_psets, current_diff, highest_score, total_questions_overall, total_correct_overall, current_proficiency = row

        total_psets += 1

        # Update best problemset score if this one is higher (using effective accuracy)
        if pset_accuracy_eff > highest_score:
            highest_score = pset_accuracy_eff

        # Difficulty adjustment per problemset (using weighted accuracy + time)
        new_diff = current_diff

        # Case 1: they rushed through it — don't reward too aggressively
        # If it's very fast AND high accuracy, we keep them at current difficulty
        # (we assume maybe some guessing / not enough evidence to promote).
        if is_fast and pset_accuracy_eff >= 0.85:
            # Only allow demotion for VERY bad scores while fast;
            # but high-accuracy fast runs do NOT get an automatic level-up.
            new_diff = current_diff

        else:
            # Case 2: they spent a long time and scored around 50% → move down
            if is_slow and 0.40 < pset_accuracy_eff < 0.60 and current_diff > 1:
                new_diff = current_diff - 1
            else:
                # Case 3: normal time → original rules
                # Level up only for strong performance (>= 85% correct weighted)
                if pset_accuracy_eff >= 0.85 and current_diff < 3:
                    new_diff = current_diff + 1

                # Level down only for clearly weak performance (<= 40% correct weighted)
                elif pset_accuracy_eff <= 0.40 and current_diff > 1:
                    new_diff = current_diff - 1
                # Otherwise keep the same difficulty for "in-between" performance

        # Clamp difficulty just in case
        new_diff = max(1, min(3, new_diff))

        # GREG UPDATE: Allowing for updating the total time spent practicing a topic after the completion of a problemset
        # Also the "proficient" boolean, for now just keep it False but in the future this can be something ML decides?

        # For a user to be proficient in a topic, they need to be max difficulty, have completed at least 6 problem sets, have an average score of at least 75%, and have a highest score of 90%
        # THIS IS ALL MADE UP RIGHT NOW! THIS CAN BE CHANGE WITH ML ETC ETC
        # If a student is not profieicent yet, recalculate if they are with the completion of the recent problemset
        if(not current_proficiency):
            average_score = total_correct_overall / total_questions_overall if total_questions_overall > 0 else 0
            is_now_proficient = ( (current_diff == 3) and (total_psets >= 6) and (average_score >= 0.70) and (highest_score >= 0.90)) 

            if(is_now_proficient):
                proficient = 1
            else:
                proficient = 0

        else:
            proficient = 1


        cur.execute(
            """
            UPDATE student_topic_progress
            SET total_topic_psets = ?,
                current_difficulty_level = ?,
                highest_score = ?,
                time_spent = time_spent + ?,
                proficient = ?
            WHERE id = ?
            """,
            (total_psets, new_diff, highest_score, time_spent, proficient, prog_id),
        )

        conn.commit()
        conn.close()



    def get_topic_summaries(self, student_id: int):
        """
        Returns per-topic performance summary for a student,
        used for the 'Personal Progress' view.

        We combine:
        - stored difficulty & highest_score (weighted best accuracy)
        - live stats from question_attempts to compute:
            * total_questions
            * total_correct (raw)
            * hint_reliance (fraction of questions where a hint was used)
            * effective_accuracy (weighted by hint usage)
        """
        conn = self._get_connection()
        cur = conn.cursor()

        # Get topics where we have a progress row for this student
        cur.execute(
            """
            SELECT
                stp.topic_id,
                t.topic_name,
                stp.current_difficulty_level,
                stp.highest_score
            FROM student_topic_progress stp
            JOIN topics t ON t.id = stp.topic_id
            WHERE stp.student_id = ?
            ORDER BY t.unit_id, t.topic_order
            """,
            (student_id,),
        )

        rows = cur.fetchall()

        summaries = []

        for topic_id, topic_name, diff, best_score in rows:
            # For each topic, compute stats directly from question_attempts
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_q,
                    SUM(CASE WHEN was_student_correct = 1 THEN 1 ELSE 0 END) AS total_correct,
                    SUM(CASE WHEN was_student_correct = 1 AND used_hint = 1 THEN 1 ELSE 0 END) AS correct_with_hint,
                    SUM(CASE WHEN used_hint = 1 THEN 1 ELSE 0 END) AS total_hints
                FROM question_attempts
                WHERE student_id = ? AND topic_id = ?
                """,
                (student_id, topic_id),
            )
            qa_row = cur.fetchone()

            total_q = qa_row[0] or 0
            total_correct_raw = qa_row[1] or 0
            correct_with_hint = qa_row[2] or 0
            total_hints = qa_row[3] or 0

            correct_no_hint = total_correct_raw - correct_with_hint
            if correct_no_hint < 0:
                correct_no_hint = 0  # safety

            # Weighted accuracy + hint reliance
            if total_q > 0:
                effective_correct = correct_no_hint + 0.5 * correct_with_hint
                eff_acc = effective_correct / total_q
                raw_acc = total_correct_raw / total_q
                hint_reliance = total_hints / total_q
            else:
                eff_acc = 0.0
                raw_acc = 0.0
                hint_reliance = 0.0

            summaries.append(
                {
                    "topic_id": topic_id,
                    "topic_name": topic_name,
                    "current_difficulty": diff,
                    "total_questions": total_q,
                    "total_correct_raw": total_correct_raw,
                    "correct_no_hint": correct_no_hint,
                    "correct_with_hint": correct_with_hint,
                    "accuracy": eff_acc,          # weighted accuracy
                    "raw_accuracy": raw_acc,      # plain correct/total
                    "hint_reliance": hint_reliance,
                    "best_score": best_score,     # best weighted accuracy recorded
                }
            )

        conn.close()
        return summaries
