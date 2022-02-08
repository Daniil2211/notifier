import requests
import datetime
from pytz import timezone

bot_token = "2027250127:AAGMsZebr2rO8wHP3XGtkeNU8-1waRwv9IA"
chat_id = 584128739


def send_message(text):
    telegram_url = f'https://api.telegram.org/bot{bot_token}/SendMessage?chat_id={chat_id}&parse_mode=Markdown&text={text}'
    requests.get(telegram_url)


r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth', auth=("mylaw.api@gmail.com", "9XuXXHbP"))
refresh_token = r.json()['refresh_token']

url = 'https://api-v3.neuro.net/api/v2/ext/company-agents?company_uuid=96857848-a88f-4cb0-bad8-6f70f3ec6211'
header = {'Authorization': "Bearer " + refresh_token,
          'Content-Type': 'application/json'}

r = requests.get(url, headers=header)
agents = r.json()

for agent in agents:
    url = 'https://api-v3.neuro.net/api/v2/ext/agent-settings/general?agent_uuid=' + agent['agent_uuid']
    header = {
        'Authorization': "Bearer " + refresh_token,
        'Content-Type': 'application/json'}
    r = requests.get(url, headers=header)
    time_zone = r.json()['timezone']

    url = 'https://cms-v3.neuro.net/api/v2/rbac/agent_settings/time_slot?agent_uuid=' + agent['agent_uuid']
    header = {
        'Authorization': "Bearer " + refresh_token,
        'Content-Type': 'application/json'}

    r = requests.get(url, headers=header)
    working_times = r.json()

    if working_times:
        is_working_time = True
        for working_time in working_times:
            if datetime.datetime.now().weekday() == working_time['day']:
                time_now = datetime.datetime.now(timezone(time_zone)).strftime("%H:%M:%S")
                if working_time['not_before'] <= time_now <= working_time['not_after']:
                    hour_offset = (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(hours=datetime.datetime.now().hour)).hour
                    r = requests.post('https://api-v3.neuro.net/api/v2/ext/statistic/dialog-report',
                                      json={"agent_uuid": agent['agent_uuid'],
                                            "start": (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(minutes = 15, hours=(3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S"),
                                            "end": (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(hours=(3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S")},
                                      headers={
                                            'Authorization': "Bearer " + refresh_token})
                    total = r.json()['total']
                    if total == 0:
                        send_message(f"Обзвон {agent['name']} закончен!")
                    else:
                        #pass
                        send_message(f"Обзвон {agent['name']} идет!")
                    break
    else:
        #send_message(f"Робот {agent['name']} не работает")
        pass
