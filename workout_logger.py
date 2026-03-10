#!/usr/bin/env python3
"""
Quy's Workout Logger - GitHub Integration
Syncs workout data to GitHub repository
"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

WORKOUT_ROTATION = ["Pull A", "Push A", "Legs", "Pull B", "Push B", "Legs"]

WORKOUT_EXERCISES = {
    "Pull A": ["Deadlifts", "Lat Pulldowns", "Cable Rows", "Face Pulls", "Cable Hammer Curls", "Cable Curls"],
    "Pull B": ["Barbell Rows", "Lat Pulldowns", "Cable Rows", "Face Pulls", "Cable Hammer Curls", "Cable Curls"],
    "Push A": ["Bench Press", "Overhead Press", "Cable Flyes", "Tricep Pushdowns", "Cable Overhead Tricep Ext", "Cable Lateral Raises"],
    "Push B": ["Overhead Press", "Bench Press", "Cable Flyes", "Tricep Pushdowns", "Cable Overhead Tricep Ext", "Cable Lateral Raises"],
    "Legs": ["Back Squats", "Romanian Deadlifts", "Leg Extensions", "Leg Curls", "Calf Raises"],
}

EXERCISE_TARGETS = {
    "Pull A": {
        "Deadlifts": "1x5",
        "Lat Pulldowns": "3x8-12",
        "Cable Rows": "3x8-12",
        "Face Pulls": "5x15-20",
        "Cable Hammer Curls": "4x8-12",
        "Cable Curls": "4x8-12",
    },
    "Pull B": {
        "Barbell Rows": "5x5",
        "Lat Pulldowns": "3x8-12",
        "Cable Rows": "3x8-12",
        "Face Pulls": "5x15-20",
        "Cable Hammer Curls": "4x8-12",
        "Cable Curls": "4x8-12",
    },
    "Push A": {
        "Bench Press": "5x5",
        "Overhead Press": "3x8-12",
        "Cable Flyes": "3x8-12",
        "Tricep Pushdowns": "3x8-12",
        "Cable Overhead Tricep Ext": "3x8-12",
        "Cable Lateral Raises": "3x15-20",
    },
    "Push B": {
        "Overhead Press": "5x5",
        "Bench Press": "3x8-12",
        "Cable Flyes": "3x8-12",
        "Tricep Pushdowns": "3x8-12",
        "Cable Overhead Tricep Ext": "3x8-12",
        "Cable Lateral Raises": "3x15-20",
    },
    "Legs": {
        "Back Squats": "2x5, 1x5+",
        "Romanian Deadlifts": "3x8-12",
        "Leg Extensions": "3x8-12",
        "Leg Curls": "3x8-12",
        "Calf Raises": "5x8-12",
    },
}


# Weight increment per exercise (lbs)
WEIGHT_INCREMENT = {
    "Deadlifts": 5,
    "Back Squats": 5,
    "Bench Press": 5,
    "Overhead Press": 5,
    "Barbell Rows": 5,
    "Romanian Deadlifts": 5,
    # Cable/machine defaults to 5
}
DEFAULT_INCREMENT = 5


def get_progression_suggestion(target, last_sets_reps):
    """Determine if the lifter should increase weight based on last performance vs target.

    Returns a suggestion string: '↑ Increase', 'Repeat', or '' if no data.
    """
    if not target or not last_sets_reps or last_sets_reps == "—":
        return ""

    # Parse last_sets_reps into list of ints
    reps_str = last_sets_reps.replace(" ", "")
    # Handle compact notation like "4x8" -> [8,8,8,8] and "3x5" -> [5,5,5]
    if "x" in reps_str and reps_str.count("x") == 1 and "," not in reps_str:
        parts = reps_str.split("x")
        try:
            reps = [int(parts[1])] * int(parts[0])
        except ValueError:
            return ""
    else:
        try:
            reps = [int(r) for r in reps_str.split(",")]
        except ValueError:
            return ""

    # Parse target — may be compound like "2x5, 1x5+"
    # Each segment: NxR, NxR+, or NxR-R2
    segments = [s.strip() for s in target.split(",")]
    required = []  # list of (min_reps, is_amrap) for each set
    for seg in segments:
        if "x" not in seg:
            continue
        num_sets_str, rep_part = seg.split("x", 1)
        try:
            num_sets = int(num_sets_str)
        except ValueError:
            continue
        is_amrap = "+" in rep_part
        rep_part_clean = rep_part.replace("+", "")
        if "-" in rep_part_clean:
            # Range target like 8-12 — need to hit upper end to move up
            low, high = rep_part_clean.split("-", 1)
            try:
                min_reps = int(high)
            except ValueError:
                continue
        else:
            try:
                min_reps = int(rep_part_clean)
            except ValueError:
                continue
        for _ in range(num_sets):
            required.append((min_reps, is_amrap))

    if not required or not reps:
        return ""

    # Check if they did enough sets
    if len(reps) < len(required):
        return "Repeat"

    # Check each set meets the target
    for i, (min_r, _) in enumerate(required):
        if i >= len(reps):
            return "Repeat"
        if reps[i] < min_r:
            return "Repeat"

    return "↑ Increase"


class WorkoutLogger:
    def __init__(self):
        self.log_file = Path("workouts.json")

    def init_repo(self):
        """Initialize git repo if needed"""
        # Repo is already initialized in main directory
        pass

    def load_workouts(self):
        """Load existing workouts from file"""
        if self.log_file.exists():
            with open(self.log_file) as f:
                return json.load(f)
        return {"workouts": []}

    def save_workouts(self, data):
        """Save workouts to file"""
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_workout(self, date, day, exercise, weight, sets_reps, notes=""):
        """Add a new workout entry"""
        data = self.load_workouts()

        workout = {
            "date": date,
            "day": day,
            "exercise": exercise,
            "weight": weight,
            "sets_reps": sets_reps,
            "notes": notes
        }

        data["workouts"].append(workout)
        self.save_workouts(data)

        # Commit to git
        subprocess.run(["git", "add", "workouts.json"], check=True)
        subprocess.run(["git", "commit", "-m", f"Add workout: {exercise} on {date}"], check=True)

        print(f"✓ Added: {exercise} ({sets_reps}) on {date}")

    def view_workouts(self, limit=10):
        """View recent workouts"""
        data = self.load_workouts()
        workouts = data["workouts"][-limit:]

        print(f"\n{'Date':<12} {'Day':<10} {'Exercise':<25} {'Weight':<10} {'Sets/Reps':<15}")
        print("-" * 72)
        for w in workouts:
            print(f"{w['date']:<12} {w['day']:<10} {w['exercise']:<25} {w['weight']:<10} {w['sets_reps']:<15}")

    def get_current_weights(self):
        """Get latest weight for each exercise"""
        data = self.load_workouts()
        weights = {}

        for w in data["workouts"]:
            weights[w["exercise"]] = w["weight"]

        return weights

    def get_todays_workout(self):
        """Determine today's workout based on rotation from last logged workout"""
        data = self.load_workouts()
        workouts = data["workouts"]

        if not workouts:
            return WORKOUT_ROTATION[0], {}

        # Find the last workout day and determine next in rotation
        last_day = workouts[-1]["day"]

        # Count completed sessions in the current program by finding sessions
        # where all exercises for that day type were logged
        valid_days = set(WORKOUT_EXERCISES.keys())
        # Group workouts by (date, day) to find sessions
        sessions = {}  # (date, day) -> set of exercises logged
        for w in workouts:
            if w["day"] in valid_days:
                key = (w["date"], w["day"])
                if key not in sessions:
                    sessions[key] = set()
                sessions[key].add(w["exercise"])

        # Check if the most recent session is still in progress
        last_date = workouts[-1]["date"]
        if last_day in valid_days:
            last_key = (last_date, last_day)
            expected_exercises = set(WORKOUT_EXERCISES[last_day])
            logged_exercises = sessions.get(last_key, set())
            if logged_exercises < expected_exercises:
                # Session incomplete — stay on this day
                next_day = last_day
                # Skip rotation counting, go straight to gathering stats
                next_exercises = set(WORKOUT_EXERCISES.get(next_day, []))
                next_targets = EXERCISE_TARGETS.get(next_day, {})
                return self._gather_last_stats(workouts, next_day, next_exercises, next_targets)

        # All exercises logged for last session — count completed sessions
        completed_sessions = []
        for (date, day), exercises in sessions.items():
            if day in valid_days and exercises >= set(WORKOUT_EXERCISES[day]):
                if date not in completed_sessions:
                    completed_sessions.append(date)

        if completed_sessions:
            next_idx = len(completed_sessions) % len(WORKOUT_ROTATION)
            next_day = WORKOUT_ROTATION[next_idx]
        else:
            next_day = WORKOUT_ROTATION[0]

        next_exercises = set(WORKOUT_EXERCISES.get(next_day, []))
        next_targets = EXERCISE_TARGETS.get(next_day, {})
        return self._gather_last_stats(workouts, next_day, next_exercises, next_targets)

    def _gather_last_stats(self, workouts, next_day, next_exercises, next_targets):
        """Gather last-used weights and sets/reps for each exercise in the upcoming workout.

        For exercises whose target differs between days (e.g. Bench Press is 5x5 on
        Push A but 3x8-12 on Push B), only use stats from the same day type so
        strength and hypertrophy weights stay separate.
        """
        # Identify exercises that have a different target on another day
        diff_target_exercises = set()
        for day_name, day_exercises in WORKOUT_EXERCISES.items():
            if day_name == next_day:
                continue
            for ex in day_exercises:
                if ex in next_exercises:
                    other_target = EXERCISE_TARGETS.get(day_name, {}).get(ex)
                    this_target = next_targets.get(ex)
                    if other_target != this_target:
                        diff_target_exercises.add(ex)

        # Days in the current rotation — ignore stats from old/retired day types
        current_days = set(WORKOUT_ROTATION)

        last_stats = {}
        # Also track the most recent weight from ANY day as a fallback reference
        fallback_stats = {}
        for w in workouts:
            if w["exercise"] not in next_exercises:
                continue
            # Always record as fallback regardless of day type
            fallback_stats[w["exercise"]] = {
                "weight": w["weight"],
                "sets_reps": w["sets_reps"],
                "notes": w.get("notes", ""),
            }
            # Skip entries from day types not in the current rotation (e.g. old
            # "Upper A" Barbell Rows shouldn't carry over to Pull B 5x5)
            if w["day"] not in current_days:
                continue
            # For exercises with differing targets across days, only match same day
            if w["exercise"] in diff_target_exercises and w["day"] != next_day:
                continue
            last_stats[w["exercise"]] = {
                "weight": w["weight"],
                "sets_reps": w["sets_reps"],
                "notes": w.get("notes", ""),
            }

        # Fill in fallback stats for exercises with no current-rotation history
        for ex in next_exercises:
            if ex not in last_stats and ex in fallback_stats:
                fb = fallback_stats[ex]
                last_stats[ex] = {
                    "weight": fb["weight"],
                    "sets_reps": fb["sets_reps"],
                    "notes": fb.get("notes", ""),
                    "is_reference": True,
                }

        return next_day, last_stats

    def get_todays_logged(self):
        """Return set of exercises already logged for today's session."""
        data = self.load_workouts()
        workouts = data["workouts"]
        today = datetime.now().strftime("%-m/%-d/%y")

        day, _ = self.get_todays_workout()
        logged = set()
        for w in workouts:
            if w["date"] == today and w["day"] == day:
                logged.add(w["exercise"])
        return day, logged

    def get_next_exercise(self):
        """Return the next unlogged exercise for today's session, or None if complete."""
        day, logged = self.get_todays_logged()
        exercises = WORKOUT_EXERCISES[day]
        for ex in exercises:
            if ex not in logged:
                return ex
        return None

    def show_todays_workout(self):
        """Display today's workout with last-used weights"""
        day, last_stats = self.get_todays_workout()
        today = datetime.now().strftime("%-m/%-d/%y")

        # Find exercises already logged today
        _, logged_today = self.get_todays_logged()

        print(f"\n{'='*50}")
        print(f"  Today's Workout: {day}  ({today})")
        print(f"{'='*50}\n")

        exercises = WORKOUT_EXERCISES[day]
        targets = EXERCISE_TARGETS.get(day, {})
        print(f"  {'Exercise':<28} {'Target':<12} {'Use Today':<12} {'Last':<16} {'Note'}")
        print(f"  {'-'*80}")
        next_up = None
        for ex in exercises:
            stats = last_stats.get(ex, {})
            target = targets.get(ex, "—")
            weight = stats.get("weight", "—")
            sets_reps = stats.get("sets_reps", "—")
            notes = stats.get("notes", "")
            is_ref = stats.get("is_reference", False)
            suggestion = get_progression_suggestion(target, sets_reps) if not is_ref else ""

            # Check if already logged today
            done_today = ex in logged_today

            # Compute today's recommended weight
            if weight == "—" or weight == "BW":
                use_today = weight
                note = ""
            elif suggestion == "↑ Increase":
                increment = WEIGHT_INCREMENT.get(ex, DEFAULT_INCREMENT)
                try:
                    use_today = str(int(weight) + increment)
                except ValueError:
                    use_today = weight
                note = f"↑ from {weight}"
            else:
                use_today = f"~{weight}" if is_ref else weight
                if is_ref:
                    note = "ref from old program"
                elif suggestion == "Repeat":
                    note = "repeat weight"
                else:
                    note = ""
            if notes and not is_ref:
                note = notes if not note else f"{note} — {notes}"

            if done_today:
                status = "  ✓ "
            elif next_up is None:
                status = "  → "
                next_up = ex
            else:
                status = "    "

            line = f"{status}{ex:<28} {target:<12} {use_today:<12} {sets_reps:<16} {note}"
            print(line)

        print()
        if next_up:
            print(f"  Next up: {next_up}")
        else:
            print(f"  ✓ All exercises logged for today!")
        print()


# Historical workout data
HISTORICAL_WORKOUTS = [
    {"date": "1/23/26", "day": "Upper A", "exercise": "Bench Press", "weight": "130", "sets_reps": "8,8,5,3", "notes": ""},
    {"date": "1/23/26", "day": "Upper A", "exercise": "Barbell Rows", "weight": "70", "sets_reps": "8,8,8,8", "notes": ""},
    {"date": "1/23/26", "day": "Upper A", "exercise": "Overhead Press", "weight": "65", "sets_reps": "8,8,5", "notes": ""},
    {"date": "1/23/26", "day": "Upper A", "exercise": "Chin-ups", "weight": "BW", "sets_reps": "4,4,4", "notes": "Shoulders fine"},
    {"date": "1/23/26", "day": "Upper A", "exercise": "Dumbbell Curls", "weight": "25", "sets_reps": "12,5,5", "notes": "Pre-fatigued"},
    {"date": "1/27/26", "day": "Upper B", "exercise": "Bench Press", "weight": "135", "sets_reps": "8,8,5,5", "notes": ""},
    {"date": "1/27/26", "day": "Upper B", "exercise": "Overhead Press", "weight": "65", "sets_reps": "9,8,6", "notes": ""},
    {"date": "1/27/26", "day": "Upper B", "exercise": "Underhand Barbell Rows", "weight": "65", "sets_reps": "10,10,12", "notes": ""},
    {"date": "1/27/26", "day": "Upper B", "exercise": "Overhead Tricep Ext", "weight": "35", "sets_reps": "12,12,8", "notes": ""},
    {"date": "1/27/26", "day": "Upper B", "exercise": "Hammer Curls", "weight": "25", "sets_reps": "12,10,8", "notes": ""},
    {"date": "1/29/26", "day": "Lower B", "exercise": "Romanian Deadlifts", "weight": "85", "sets_reps": "12,12,12,12", "notes": "Ready to increase"},
    {"date": "1/29/26", "day": "Lower B", "exercise": "Goblet Squats", "weight": "35", "sets_reps": "10,12,10", "notes": ""},
    {"date": "1/29/26", "day": "Lower B", "exercise": "Leg Curls", "weight": "55", "sets_reps": "12,12,12", "notes": ""},
    {"date": "1/29/26", "day": "Lower B", "exercise": "Leg Extensions", "weight": "60", "sets_reps": "15,15,15", "notes": "Ready to increase"},
    {"date": "1/29/26", "day": "Lower B", "exercise": "Standing Calf Raises", "weight": "125", "sets_reps": "20,20,20", "notes": ""},
    {"date": "1/31/26", "day": "Upper A", "exercise": "Bench Press", "weight": "130", "sets_reps": "8,8,8,8", "notes": ""},
    {"date": "1/31/26", "day": "Upper A", "exercise": "Barbell Rows", "weight": "70", "sets_reps": "12,12,9,9", "notes": ""},
    {"date": "1/31/26", "day": "Upper A", "exercise": "Overhead Press", "weight": "65", "sets_reps": "12,8,5", "notes": ""},
    {"date": "1/31/26", "day": "Upper A", "exercise": "Tricep Extension", "weight": "35", "sets_reps": "7,8,8", "notes": ""},
    {"date": "1/31/26", "day": "Upper A", "exercise": "Chin-ups", "weight": "BW", "sets_reps": "3,2,2,2", "notes": "Fatigued"},
    {"date": "1/31/26", "day": "Upper A", "exercise": "Dumbbell Curls", "weight": "25", "sets_reps": "8,8,8", "notes": ""},
]

if __name__ == "__main__":
    import sys

    logger = WorkoutLogger()

    if len(sys.argv) > 1 and sys.argv[1] == "history":
        logger.view_workouts(15)
    else:
        logger.show_todays_workout()
