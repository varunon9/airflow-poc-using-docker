import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests, json

# airflow home directory path, PS: this is bindmount volume when running docker image as container
HOME = '/home/airflow/'

# dag will read github username from this file
username_filename = HOME + 'username.txt'

'''
task t1 will hit guthub api to get repos for username read from username_filename
and write response to this file
'''
repos_filename = HOME + 'repos.txt'

'''
task t2 will read repos details from repos_filename, parse it and write
repo names to this file
'''
repo_names_filename = HOME + 'repo-names.txt'

schedule_interval = timedelta(hours = 6)  # run at interval of 6 hours

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 12, 15),
    'email': ['varunon9@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes = 5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

# first argument is id of dag. DAGs are identified by this id and not by filename
dag = DAG('github-repo-names', 
    default_args = default_args,
    schedule_interval = schedule_interval)

# make get request to https://api.github.com/users/:username/repos and write response to file
def fetch_github_repos():
    try:
        username_file = open(username_filename, 'r')
        username = username_file.readline().rstrip()
        username_file.close()

        url = 'https://api.github.com/users/' + username + '/repos'
        response = requests.get(url)
        status_code = response.status_code

        if status_code == 200:
            repos_file = open(repos_filename, 'w')
            repos_file.write(response.content)
            print 'successfully wrote contents to repos.txt file'
        else:
            print 'Request failed with status code: ', status_code


    except IOError:
        print username_filename + ' file not found'

# read response from github api (stored in file), parse it and write repo names to another file
def write_repo_list():
    try:
        repos_file = open(repos_filename, 'r')
        repos_list = repos_file.read()
        repos_file.close()

        repos_list = json.loads(repos_list)
        repo_names_file = open(repo_names_filename, 'w')
        for repo in repos_list:
            repo_names_file.write(repo.get('name') + '\n')


    except IOError:
        print repos_filename + ' file not found'


t1 = PythonOperator(
    task_id = 'read_username_and_write_repo_response_to_file',
    python_callable = fetch_github_repos,
    dag = dag
)

t2 = PythonOperator(
    task_id = 'read_repo_response_and_write_repo_names_to_file',
    python_callable = write_repo_list,
    dag = dag
)

t1 >> t2  # t2 depends on t1 equivalent to t2.set_upstream(t1)
