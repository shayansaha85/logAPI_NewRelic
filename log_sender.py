import requests
import json
import time
import paramiko
import configparser

config = configparser.ConfigParser()

config.read('config.ini')

interval = 30

INSERT_API_KEY = config['NR']['insights_key']
LOGS_API_URL = config['NR']['log_api_us']

hostname = config['SERVER']['hostname']
port = config["SERVER"]['port']
username = config['SERVER']['username']
password = config['SERVER']['password']

remote_file_path = config['SERVER']['log_file_path']
log_level = config['SERVER']['log_level']
service = config['SERVER']['service']
env = config['SERVER']['env']

local_file_path = './error.log'

def main():
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

      try:
            ssh.connect(hostname, port, username, password)
            stdin, stdout, stderr = ssh.exec_command(f'cat {remote_file_path}')
            log_data = stdout.read().decode()
            with open(local_file_path, 'w') as local_file:
                  local_file.write(log_data)
            print(f"--- LOG FILE FETCHED TO LOCAL [{local_file_path}] ---")

      except Exception as e:
            print(f"--- ERROR : {e} ---")

      finally:
            ssh.close()


      logFile = open('error.log', 'r')
      logFileData = logFile.readlines()

      logFile.close()

      log_data = []
      o = []
      for data in logFileData:
            if len(str(data).strip()) != 0:
                  log_data.append(
                        {
                              "timestamp": f"{int(time.time())}",
                              "message": str(data).strip(),
                              "log" : {
                                    "level" : log_level,
                                    "service": service,
                                    "environment": env,
                                    }
                        }
                  )


      headers = {
      'Api-Key': INSERT_API_KEY,
      'Content-Type': 'application/json',
      }

      response = requests.post(LOGS_API_URL, headers=headers, data=json.dumps(log_data))

      print(f"--- FILE SENT TO NEW RELIC | API STATUS CODE {response.status_code} ---")
      
while True:
      main()
      time.sleep(interval)