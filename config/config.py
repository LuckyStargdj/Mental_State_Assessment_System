import os

cofig_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(cofig_dir)
newdir = os.path.split(project_dir)[0]
set_file_path = os.path.join(project_dir, 'config/set.json')
time_file_path = os.path.join(project_dir, 'config/time.yaml')

paths = {
    # 'exe_path': os.path.join(project_dir, '20240914_Depression_Anxiety_Drug.exe'),
    'DrugProbability_path': os.path.join(project_dir, 'EEG_Data/User_Data/DrugProbability.txt'),
    'AnxietyProbability_path': os.path.join(project_dir, 'EEG_Data/User_Data/AnxietyProbability.txt'),
    'DepressionProbability_path': os.path.join(project_dir, 'EEG_Data/User_Data/DepressionProbability.txt'),
    'database_path': os.path.join(project_dir, 'data/db/medical_database.db'),
    'userconfig_path': os.path.join(project_dir, 'config/userconfig.ini'),
}

