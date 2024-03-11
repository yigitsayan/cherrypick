import subprocess

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, universal_newlines=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    return result.stdout.strip()

def update_branch(branch):
    print(f"Updating branch '{branch}' with the latest changes from the remote repository...")
    run_command(f"git checkout {branch}")
    run_command(f"git pull origin {branch}")

def filter_commits_by_jira_tickets(source_branch, jira_tickets):
    commits = []
    for jira_ticket in jira_tickets:
        stdout = run_command(f"git log {source_branch} --grep={jira_ticket} --format=%H --no-merges")
        commits.extend(stdout.splitlines())
    return sorted(set(commits), key=lambda x: commits.index(x))

def cherry_pick_commits(source_branch, target_branch_base, new_branch_name, jira_tickets):
    # Update source branch with latest changes
    update_branch(source_branch)

    # Create and switch to the new branch from the target base branch
    print(f"Creating and switching to new branch '{new_branch_name}' from '{target_branch_base}'...")
    run_command(f"git checkout {target_branch_base}")
    run_command(f"git checkout -b {new_branch_name}")

    # Find commits by Jira tickets
    commits = filter_commits_by_jira_tickets(source_branch, jira_tickets)
    if not commits:
        print("No commits found related to specified Jira tickets.")
        return

    # Cherry-pick commits
    for commit_hash in commits:
        print(f"Cherry-picking commit {commit_hash}...")
        result = run_command(f"git cherry-pick {commit_hash}")
        if "conflict" in result.lower():
            print(f"Conflict detected during cherry-pick of commit {commit_hash}.")
            print("Please resolve the conflict and then continue the cherry-pick process manually.")
            return
        

    # Option to push the new branch
    push = input("Do you want to push the new branch to the remote repository? (y/n): ").lower().strip()
    if push == 'y':
        run_command(f"git push origin {new_branch_name}")
        print(f"Pushed '{new_branch_name}' to remote repository.")
    else:
        print("New branch was not pushed.")

if __name__ == "__main__":
    source_branch = input("From which branch should commits be cherry-picked? ").strip()
    new_branch_name = input("Name of the new branch: ").strip()
    target_branch_base = input("From which branch should the new branch be created? ").strip()
    jira_tickets_input = input("What are the Jira tickets (comma-separated, e.g., SLK-1,SLK-25,SLK-30)? ").strip()
    jira_tickets = [ticket.strip() for ticket in jira_tickets_input.split(',')]

    cherry_pick_commits(source_branch, target_branch_base, new_branch_name, jira_tickets)
