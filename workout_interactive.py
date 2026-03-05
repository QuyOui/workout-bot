#!/usr/bin/env python3
"""
Interactive Workout Logger
"""

from workout_logger import WorkoutLogger

logger = WorkoutLogger()

# Initialize repo
logger.init_repo()

print("\n=== Workout Logger Ready ===\n")
print("I'm ready to log your workouts!")
print("Just provide the date, day, exercise, weight, and sets/reps.\n")

while True:
    try:
        print("\n--- Add New Workout ---")
        date = input("Date (e.g., 2/1/26): ").strip()
        day = input("Day (Upper A/B or Lower A/B): ").strip()
        exercise = input("Exercise: ").strip()
        weight = input("Weight: ").strip()
        sets_reps = input("Sets/Reps (e.g., 8,8,8,8): ").strip()
        notes = input("Notes (optional): ").strip()

        if date and day and exercise and weight and sets_reps:
            logger.add_workout(date, day, exercise, weight, sets_reps, notes)
            print("✓ Workout logged and committed!")

            # Show next exercise in today's workout
            from workout_logger import WORKOUT_EXERCISES, EXERCISE_TARGETS
            exercises = WORKOUT_EXERCISES.get(day, [])
            if exercise in exercises:
                idx = exercises.index(exercise)
                if idx + 1 < len(exercises):
                    next_ex = exercises[idx + 1]
                    target = EXERCISE_TARGETS.get(day, {}).get(next_ex, "")

                    # Look up last stats for next exercise
                    data = logger.load_workouts()
                    last_weight = "—"
                    last_sets = "—"
                    for w in reversed(data["workouts"]):
                        if w["exercise"] == next_ex:
                            last_weight = w["weight"]
                            last_sets = w["sets_reps"]
                            break

                    print(f"\n→ Next up: {next_ex}")
                    print(f"  Target: {target}  |  Last: {last_weight} lbs, {last_sets}")
                    if target:
                        # Parse target rest time hint based on rep range
                        parts = target.split("x")
                        if len(parts) == 2:
                            rep_part = parts[1].replace("+", "")
                            if "-" in rep_part:
                                max_rep = int(rep_part.split("-")[1])
                            else:
                                max_rep = int(rep_part)
                            if max_rep <= 5:
                                print("  Rest: 3-5 min (strength)")
                            elif max_rep <= 12:
                                print("  Rest: 60-90 sec")
                            else:
                                print("  Rest: 30-60 sec")
                else:
                    print("\n✓ That was the last exercise — workout complete!")
        else:
            print("Please fill in all required fields.")

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")
