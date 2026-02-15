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

WORKOUT_ROTATION = ["Upper A", "Lower A", "Upper B", "Lower B"]

WORKOUT_EXERCISES = {
    "Upper A": ["Bench Press", "Barbell Rows", "Overhead Press", "Tricep Pushdowns", "Dumbbell Curls", "Face Pulls"],
    "Upper B": ["Bench Press", "Lat Pulldowns", "Cable Lateral Raises", "Overhead Tricep Ext", "Hammer Curls", "Face Pulls"],
    "Lower A": ["Back Squats", "Conventional Deadlifts", "Leg Extensions", "Leg Curls", "Calf Raises"],
    "Lower B": ["Romanian Deadlifts", "Cable Pull-Throughs", "Leg Curls", "Leg Extensions", "Standing Calf Raises"],
}


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

        # Find the last workout day
        last_day = workouts[-1]["day"]

        # Advance to next in rotation
        try:
            idx = WORKOUT_ROTATION.index(last_day)
            next_day = WORKOUT_ROTATION[(idx + 1) % len(WORKOUT_ROTATION)]
        except ValueError:
            next_day = WORKOUT_ROTATION[0]

        # Gather last-used weights and sets/reps for each exercise in the upcoming workout
        last_stats = {}
        for w in workouts:
            if w["exercise"] in WORKOUT_EXERCISES.get(next_day, []):
                last_stats[w["exercise"]] = {
                    "weight": w["weight"],
                    "sets_reps": w["sets_reps"],
                    "notes": w.get("notes", ""),
                }

        return next_day, last_stats

    def show_todays_workout(self):
        """Display today's workout with last-used weights"""
        day, last_stats = self.get_todays_workout()
        today = datetime.now().strftime("%-m/%-d/%y")

        print(f"\n{'='*50}")
        print(f"  Today's Workout: {day}  ({today})")
        print(f"{'='*50}\n")

        exercises = WORKOUT_EXERCISES[day]
        print(f"  {'Exercise':<28} {'Weight':<10} {'Last Sets/Reps'}")
        print(f"  {'-'*58}")
        for ex in exercises:
            stats = last_stats.get(ex, {})
            weight = stats.get("weight", "—")
            sets_reps = stats.get("sets_reps", "—")
            notes = stats.get("notes", "")
            line = f"  {ex:<28} {weight:<10} {sets_reps}"
            if notes:
                line += f"  ({notes})"
            print(line)

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
