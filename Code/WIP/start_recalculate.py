from scorer import Scorer
from datetime import datetime


start_time= datetime.now(tz=None)
print(f'Gestartet um: {start_time}')
scorer = Scorer()
scorer.recalculate('any', True)
print(f'Gestartet um: {start_time}')
print(f'Fertig um: {datetime.now(tz=None)}')
print('recalculate abgeschlossen, bitte Feedback an Arne')



"""
print('Fall 1 2021-01-09 01:10:47')
previous_record = scorer.get_record('IPV4', 'zabbix.w-hs.de', '2021-01-08 23:18:49' )
record = scorer.get_record('IPV4', 'zabbix.w-hs.de', '2021-01-09 01:10:47' )
print('record[0][0]:')
print(record[0][0])
print('previous_record[0][0]: ')
print(previous_record[0][0])
print('record[0]:')
print(record[0])
print('previous_record[0]: ')
print(previous_record[0])
print('previous_record  != record:'+ str(previous_record  != record))

print('Fall 2 2021-01-09 01:10:47')
previous_record = scorer.get_record('IPV4', 'zabbix.w-hs.de', '2021-01-13 09:03:54 ' )
record = scorer.get_record('IPV4', 'zabbix.w-hs.de', '2021-01-14 09:05:38' )
print('record[0][0]:')
print(record[0][0])
print('previous_record[0][0]: ')
print(previous_record[0][0])
print('record[0]:')
print(record[0])
print('previous_record[0]: ')
print(previous_record[0])
print('previous_record  != record:'+ str(previous_record  != record))
"""