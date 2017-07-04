DATABASE = 'database/sqlite.db'

QUERY_DROP_TABLE = 'drop table if exists SCHED_TASKS_QUEUE'
QUERY_CREATE_TABLE = '''
create table SCHED_TASKS_QUEUE (
    queue_id        integer primary key asc,
    task_name       text,
    time_created    integer,
    task_state      integer,
    task_config     text,
    sched_time      integer,
    processed_time  integer,
    task_result     text,
    task_metadata   text
)
'''
QUERY_CLEAR_TABLE = '''
delete from SCHED_TASKS_QUEUE
'''
QUERY_NEXT_ELIGIBLE_TASK = '''
select 
    queue_id, 
    task_name, 
    time_created, 
    task_state, 
    task_config, 
    sched_time
from 
    SCHED_TASKS_QUEUE
where
    task_state = 0 and
    sched_time < %d and
    task_name in (%s)
order by
    sched_time asc
limit 1
'''
QUERY_SET_TASK_IN_PROGRESS = '''
update SCHED_TASKS_QUEUE set task_state = 1 where queue_id = %d
'''
QUERY_SET_TASK_COMPLETE = '''
update 
    SCHED_TASKS_QUEUE 
set
    task_state = 2,
    processed_time = ?,
    task_result = ?,
    task_metadata = ?
where
    queue_id = ?
'''
QUERY_SET_TASK_INCOMPLETE = '''
update
    SCHED_TASKS_QUEUE
set
    task_state = 0
where
    queue_id = %d
'''

