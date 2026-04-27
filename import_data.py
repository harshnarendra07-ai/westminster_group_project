import os
import sys
import django
import csv
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyproject.settings')
django.setup()

from healthcheck.models import Department, Manager, Skill, Team, Dependency, Project, Repository, UserProfile
from django.contrib.auth.models import User

def force_import_final():
    csv_files = glob.glob("*.csv")
    if not csv_files:
        print(" Error: No CSV file found in the folder.")
        return
    
    file_path = csv_files[0]
    print(f" Found '{file_path}'. Handling Excel encoding...")

    with open(os.path.join(BASE_DIR, file_path), newline='', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            team_name = row.get('Team Name', '').strip()
            if not team_name:
                continue
                
            dept_name = row.get('Department', 'General').strip()
            dept_head = row.get('Department Head', '').strip()


            dept, created = Department.objects.get_or_create(
                dept_name=dept_name,
                defaults={'dept_head': dept_head}
            )

            if not dept.dept_head and dept_head:
                dept.dept_head = dept_head
                dept.save()


            leader = row.get('Team Leader', 'Unknown').strip()
            username = leader.lower().replace(" ", "")[:8]
            user, _ = User.objects.get_or_create(username=username)
            if not user.password:
                user.set_password('skyengineering123')
                user.save()
            manager, _ = Manager.objects.get_or_create(user=user)

            
            focus_area = row.get('Development Focus Areas', '').strip()
            slack = row.get('Slack Channels', '').strip()
            search_terms = row.get('Wiki Search Terms', '').strip()
            downstream = row.get('Downstream Dependencies', '').strip()
            dep_type = row.get('Dependency Type', '').strip()
            team_type = row.get('Team Type', 'Engineering').strip() or 'Engineering'
            jira_project_name = row.get('Jira Project Name', '').strip()
            jira_board_url = row.get('Jira board Link', '').strip()
            repo_url = row.get('Project (codebase) (Github Repo)', '').strip()


            team, _ = Team.objects.update_or_create(
                team_name=team_name,
                defaults={
                    'department': dept,
                    'manager': manager,
                    'methodology': 'Agile',
                    'development_focus_area': focus_area,  
                    'slack_channel': slack,                
                    'search_keywords': search_terms,
                    'downstream_dependency': downstream,
                    'dependency_type': dep_type,
                    'team_type': team_type 
                }
            )
            
            UserProfile.objects.update_or_create(
                user=user, 
                defaults={
                    'role': 'Manager',
                    'team': team 
                }
            )
            
            if jira_project_name or jira_board_url:
             Project.objects.update_or_create(
            team=team,
            jira_project_name=jira_project_name or team.team_name,
            defaults={
            'jira_board_url': jira_board_url or '#'
            }
    )


        if repo_url:
            Repository.objects.update_or_create(
                repo_url=repo_url,
                defaults={
                    'team': team
                }
            )

        for i in range(1, 6):
            safe_team_name = team_name.lower().replace(" ", "_").replace("-", "_")
            eng_username = f"{safe_team_name}_eng_{i}"

            eng_user, created = User.objects.get_or_create(username=eng_username)
            if created or not eng_user.password:
                eng_user.set_password('skyengineering123')
                eng_user.save()

            UserProfile.objects.update_or_create(
                user=eng_user,
                defaults={
                    'role': 'Engineer',
                    'team': team
                }
            )


        skills_str = row.get('Key Skills & Technologies', '')
        if skills_str:
            for s in skills_str.split(','):
                skill_name = s.strip().title()
                if skill_name:
                    skill_obj, _ = Skill.objects.get_or_create(skill_name=skill_name)
                    team.skills.add(skill_obj)

        print(f" Imported: {team_name}")
        count += 1

    with open(os.path.join(BASE_DIR, file_path), newline='', encoding='latin-1') as f:
        reader = csv.DictReader(f)

        for row in reader:
            team_name = row.get('Team Name', '').strip()
            downstream_names = row.get('Downstream Dependencies', '').strip()

            if not team_name or not downstream_names:
                continue

            try:
                upstream_team = Team.objects.get(team_name=team_name)
            except Team.DoesNotExist:
                continue

            for downstream_name in downstream_names.split(','):
                downstream_name = downstream_name.strip()

                if not downstream_name:
                    continue

                try:
                    downstream_team = Team.objects.get(team_name=downstream_name)

                    Dependency.objects.get_or_create(
                        upstream_team=upstream_team,
                        downstream_team=downstream_team
                    )

                    print(f" Dependency added: {downstream_team.team_name} depends on {upstream_team.team_name}")

                except Team.DoesNotExist:
                    print(f" Warning: dependency team not found: {downstream_name}")
    print(f" Import complete. Total teams imported: {count}")

if __name__ == '__main__':
    force_import_final()