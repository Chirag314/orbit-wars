!pip install -qU kaggle-environments

import shutil
import subprocess
from kaggle_environments import make

# --- Configuration & Paths ---
SRC_PATH = "/kaggle/input/models/jek1wantaufik/buddy/other/orbit-wars/2/submission.py"
DST_PATH = "/kaggle/working/submission.py"
ENV_NAME = "orbit_wars"
COMPETITION_NAME = "orbit-wars"
SUBMISSION_MESSAGE = "Automated submission via optimized pipeline"

def copy_submission(src: str, dst: str) -> None:
    """Copies the submission file to the working directory."""
    shutil.copy(src, dst)
    print(f"✅ Success: Submission file securely copied to {dst}")

def create_env(name: str):
    """Initializes the environment without the UI renderer."""
    return make(name, debug=True)

def run_match(env, agents):
    """Runs a simulation of the agent vs. a random baseline."""
    print("Running local verification match...")
    return env.run(agents)

def print_results(env):
    """Outputs the final status and rewards."""
    print("\n--- Match Results ---")
    for i, state in enumerate(env.steps[-1]):
        print(
            f"Player {i+1} Status: {state.status}, "
            f"Reward: {state.reward}"
        )

def submit_to_kaggle(file_path: str, competition: str, message: str) -> None:
    """Executes the Kaggle CLI command to submit the file."""
    print(f"\n🚀 Initiating Kaggle CLI submission for {competition}...")
    
    # Constructing the CLI command shown in your screenshot
    command = [
        "kaggle", "competitions", "submit",
        "-c", competition,
        "-f", file_path,
        "-m", message
    ]
    
    try:
        # Run the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("✅ Submission Command Executed Successfully!")
        print(f"Kaggle API Response:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print("❌ Submission Failed. Check your API credentials or file paths.")
        print(f"Error Details:\n{e.stderr}")

def main():
    # 1. Generate the submission file
    copy_submission(SRC_PATH, DST_PATH)
    
    # 2. Setup environment and run the match (No UI rendering)
    env = create_env(ENV_NAME)
    run_match(env, ["submission.py", "random"])
    
    # 3. Print the final outcome
    print_results(env)
    
    # 4. Directly submit to the Kaggle Leaderboard
    submit_to_kaggle(DST_PATH, COMPETITION_NAME, SUBMISSION_MESSAGE)

if __name__ == "__main__":
    main()