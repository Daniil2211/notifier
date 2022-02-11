import requests
import datetime
from pytz import timezone

bot_token = "2027250127:AAGMsZebr2rO8wHP3XGtkeNU8-1waRwv9IA"
chat_id = 584128739


def send_message(text):
    telegram_url = f'https://api.telegram.org/bot{bot_token}/SendMessage?chat_id={chat_id}&parse_mode=Markdown&text={text}'
    requests.get(telegram_url)


str_encode = b'\xff\xfe9\x00X\x00u\x00X\x00X\x00H\x00b\x00P\x00'

r = requests.post('https://api-v3.neuro.net/api/v2/ext/auth', auth=("mylaw.api@gmail.com", str_encode.decode('UTF-16')))
refresh_token = r.json()['refresh_token']

company_uuids = ['96857848-a88f-4cb0-bad8-6f70f3ec6211', '0af1c261-2417-47ce-8511-602b4a4a2e7b', '1c07c539-916c-4519-b26a-2c7a67a6f24e',
                 'e3cd14a1-a289-4d2f-86ab-182dc5e889ce', 'd2069c81-b66a-4e8d-88b9-46e60ee01a34', '70196014-fa26-48fe-b586-84a752eee58f']

for company_uuid in company_uuids:
    url = f'https://api-v3.neuro.net/api/v2/ext/company-agents?company_uuid={company_uuid}'
    header = {'Authorization': "Bearer " + refresh_token,
              'Content-Type': 'application/json'}

    r = requests.get(url, headers=header)
    agents = r.json()

    is_begin_work = {}
    is_end_work = {}
    for agent in agents:
        is_begin_work[agent['agent_uuid']] = False
        is_end_work[agent['agent_uuid']] = False

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
            for working_time in working_times:
                if datetime.datetime.now(timezone(time_zone)).weekday() == working_time['day']:
                    time_begin_work_obj = datetime.datetime.strptime(working_time['not_before'], '%H:%M:%S').time()
                    time_end_work_obj = datetime.datetime.strptime(working_time['not_after'], '%H:%M:%S').time()
                    datetime_now_obj = datetime.datetime.now(timezone(time_zone))
                    time_now_obj = datetime_now_obj.time()
                    datetime_now_str = datetime.datetime.now(timezone(time_zone)).strftime("%H:%M:%S")
                    datetime_begin_work_obj = datetime.datetime(year=datetime_now_obj.year, month=datetime_now_obj.month, day=datetime_now_obj.day,
                                                        hour=time_begin_work_obj.hour, minute=time_begin_work_obj.minute,
                                                        second=time_begin_work_obj.second)
                    if time_begin_work_obj <= time_now_obj <= time_end_work_obj:
                        hour_offset = (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(hours=datetime.datetime.now().hour)).hour
                        if not is_begin_work[agent['agent_uuid']]:
                            r = requests.post('https://api-v3.neuro.net/api/v2/ext/statistic/dialog-report',
                                              json={"agent_uuid": agent['agent_uuid'],
                                                    "start": (datetime_begin_work_obj - datetime.timedelta(hours=(
                                                                3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S"),
                                                    "end": (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(
                                                        hours=(3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S")},
                                              headers={
                                                  'Authorization': "Bearer " + refresh_token})
                            total = r.json()['total']
                            if total != 0:
                                is_begin_work[agent['agent_uuid']] = True
                        if is_begin_work[agent['agent_uuid']]:
                            #hour_offset = (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(hours=datetime.datetime.now().hour)).hour
                            r = requests.post('https://api-v3.neuro.net/api/v2/ext/statistic/dialog-report',
                                              json={"agent_uuid": agent['agent_uuid'],
                                                    "start": (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(minutes=15, hours=(3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S"),
                                                    "end": (datetime.datetime.now(timezone(time_zone)) - datetime.timedelta(hours=(3 + hour_offset))).strftime("%Y-%m-%d %H:%M:%S")},
                                              headers={
                                                    'Authorization': "Bearer " + refresh_token})
                            total = r.json()['total']
                            if total == 0:
                                send_message(f"Обзвон {agent['name']} закончен!")
                                is_end_work[agent['agent_uuid']] = True
                            else:
                                #pass
                                send_message(f"Обзвон {agent['name']} идет!")
                        else:
                            send_message(f"{agent['name']} не начинал работу!")
                        break
        else:
            send_message(f"Робот {agent['name']} не работает")
            pass