DATABASE = 'database/sqlite.db'
TEST_DATABASE = 'database/sqlite.test.db'

QUERY_DROP_TABLE = 'drop table if exists SCHED_TASKS_QUEUE'

QUERY_CREATE_TABLE = '''
create table SCHED_TASKS_QUEUE (
    queue_id        integer primary key asc,
    name            text,
    created         integer,
    state           integer,
    config          text,
    schedule        integer,
    processed       integer,
    result          text,
    processor       text
)
'''

QUERY_CLEAR_TABLE = '''
delete from SCHED_TASKS_QUEUE
'''

QUERY_CREATE_TASK = '''
insert into SCHED_TASKS_QUEUE
(
    name,
    created,
    state,
    config,
    schedule
)
values
(
    ?,
    ?,
    ?,
    ?,
    ?
)
'''

QUERY_NEXT_ELIGIBLE_TASK = '''
select 
    queue_id, 
    name, 
    created, 
    state, 
    config, 
    schedule
from 
    SCHED_TASKS_QUEUE
where
    state = 0 and
    schedule < %d and
    name in (%s)
order by
    schedule asc
limit 1
'''

QUERY_SET_TASK_IN_PROGRESS = '''
update SCHED_TASKS_QUEUE set state = 1 where queue_id = ?
'''

QUERY_SET_TASK_COMPLETE = '''
update 
    SCHED_TASKS_QUEUE 
set
    state = 2,
    processed = ?,
    result = ?,
    processor = ?
where
    queue_id = ?
'''

QUERY_SET_TASK_INCOMPLETE = '''
update
    SCHED_TASKS_QUEUE
set
    state = 0
where
    queue_id = ?
'''

QUERY_VALIDATE_TASK = '''
select 
    queue_id,
    name,
    schedule
from 
    SCHED_TASKS_QUEUE
where
    queue_id = ? and
    name = ? and
    schedule = ?
'''
