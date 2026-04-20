import os
import sys
import django
import csv
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyproject.settings')
django.setup()

from healthcheck.models import Department, Manager, Skill, Team
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
            dept, _ = Department.objects.get_or_create(dept_name=dept_name)

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
                    'dependency_type': dep_type           
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

    print(f"\n DONE! {count} teams are now in your database.")

if __name__ == '__main__':
    force_import_final()