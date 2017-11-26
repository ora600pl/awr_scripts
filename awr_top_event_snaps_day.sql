REM This script shows top days of wait events delta
REM Usage: @awr_top_event_snaps_day.sql instance_number date_from date_to

set linesize 250
set pagesize 100
set verify off

with v_system_class_wait as
(
select EVENT_NAME, WAIT_CLASS, TIME_WAITED_MICRO-lag(TIME_WAITED_MICRO,1,TIME_WAITED_MICRO) over (partition by event_name order by sys_ev.SNAP_ID) as waited_micro_diff,
       sys_ev.snap_id, TIME_WAITED_MICRO, snap.end_interval_time
from dba_hist_system_event sys_ev, dba_hist_snapshot snap
where sys_ev.snap_id=snap.snap_id
and   snap.end_interval_time between to_date('&&2','YYYY-MM-DD:HH24:MI') and to_date('&&3','YYYY-MM-DD:HH24:MI')
and   wait_Class not in ('Idle','Other')
and   sys_ev.instance_number=&&1
and   snap.instance_number=&&1
and   snap.instance_number=sys_ev.instance_number
), v_system_rank as
(
select to_char(end_interval_time,'YYYY-MM-DD') as snap_day, sum(waited_micro_diff) as sm_waited_micro_diff,
       dense_rank() over (order by sum(waited_micro_diff) desc) as rnk
from v_system_class_wait
group by to_char(end_interval_time,'YYYY-MM-DD')
)
select sr.*
from v_system_rank sr
where rnk<=10
order by rnk
/
