import plotly.offline as py
import plotly.graph_objs as go
import sys
import os
import re
from datetime import datetime
from plotly.subplots import make_subplots


class AWRAnalyzer(object):
    def __init__(self, dirname, name_pattern, param='FULL', scale=False):
        self.dirname = dirname
        self.name_pattern = name_pattern
        self.param = param
        self.scale = scale
        self.cpu_count = 0
        self.event_classes = ["System I/O", "Other", "User I/O", "Configuration", "Cluster", "Concurrency",
                              "Administrative", "Application", "Network", "Commit"]

        self.event_class_name = {"null event": "Other",
                                 "pmon timer": "Idle",
                                 "logout restrictor": "Concurrency",
                                 "VKTM Logical Idle Wait": "Idle",
                                 "VKTM Init Wait for GSGA": "Idle",
                                 "IORM Scheduler Slave Idle Wait": "Idle",
                                 "acknowledge over PGA limit": "Scheduler",
                                 "Parameter File I/O": "User I/O",
                                 "rdbms ipc message": "Idle",
                                 "remote db operation": "Network",
                                 "remote db file read": "Network",
                                 "remote db file write": "Network",
                                 "Disk file operations I/O": "User I/O",
                                 "Disk file I/O Calibration": "User I/O",
                                 "Disk file Mirror Read": "User I/O",
                                 "Disk file Mirror/Media Repair Write": "User I/O",
                                 "direct path sync": "User I/O",
                                 "Clonedb bitmap file write": "System I/O",
                                 "Datapump dump file I/O": "User I/O",
                                 "dbms_file_transfer I/O": "User I/O",
                                 "DG Broker configuration file I/O": "User I/O",
                                 "Data file init write": "User I/O",
                                 "Log file init write": "User I/O",
                                 "Log archive I/O": "System I/O",
                                 "RMAN backup & recovery I/O": "System I/O",
                                 "Standby redo I/O": "System I/O",
                                 "Network file transfer": "System I/O",
                                 "Pluggable Database file copy": "User I/O",
                                 "File Copy": "User I/O",
                                 "Backup: MML initialization": "Administrative",
                                 "Backup: MML v1 open backup piece": "Administrative",
                                 "Backup: MML v1 read backup piece": "Administrative",
                                 "Backup: MML v1 write backup piece": "Administrative",
                                 "Backup: MML v1 close backup piece": "Administrative",
                                 "Backup: MML v1 query backup piece": "Administrative",
                                 "Backup: MML v1 delete backup piece": "Administrative",
                                 "Backup: MML create a backup piece": "Administrative",
                                 "Backup: MML commit backup piece": "Administrative",
                                 "Backup: MML command to channel": "Administrative",
                                 "Backup: MML shutdown": "Administrative",
                                 "Backup: MML obtain textual error": "Administrative",
                                 "Backup: MML query backup piece": "Administrative",
                                 "Backup: MML extended initialization": "Administrative",
                                 "Backup: MML read backup piece": "Administrative",
                                 "Backup: MML delete backup piece": "Administrative",
                                 "Backup: MML restore backup piece": "Administrative",
                                 "Backup: MML write backup piece": "Administrative",
                                 "Backup: MML proxy initialize backup": "Administrative",
                                 "Backup: MML proxy cancel": "Administrative",
                                 "Backup: MML proxy commit backup piece": "Administrative",
                                 "Backup: MML proxy session end": "Administrative",
                                 "Backup: MML datafile proxy backup?": "Administrative",
                                 "Backup: MML datafile proxy restore?": "Administrative",
                                 "Backup: MML proxy initialize restore": "Administrative",
                                 "Backup: MML proxy start data movement": "Administrative",
                                 "Backup: MML data movement done?": "Administrative",
                                 "Backup: MML proxy prepare to start": "Administrative",
                                 "Backup: MML obtain a direct buffer": "Administrative",
                                 "Backup: MML release a direct buffer": "Administrative",
                                 "Backup: MML get base address": "Administrative",
                                 "Backup: MML query for direct buffers": "Administrative",
                                 "OFS operation completion": "Administrative",
                                 "OFS idle": "Idle",
                                 "io done": "System I/O",
                                 "i/o slave wait": "Idle",
                                 "RMAN Disk slave I/O": "System I/O",
                                 "RMAN Tape slave I/O": "System I/O",
                                 "DBWR slave I/O": "System I/O",
                                 "LGWR slave I/O": "System I/O",
                                 "Archiver slave I/O": "System I/O",
                                 "VKRM Idle": "Idle",
                                 "wait for unread message on broadcast channel": "Idle",
                                 "wait for unread message on multiple broadcast channels": "Idle",
                                 "class slave wait": "Idle",
                                 "PING": "Idle",
                                 "watchdog main loop": "Idle",
                                 "process in prespawned state": "Idle",
                                 "BA: Performance API": "Administrative",
                                 "File Repopulation Write": "System I/O",
                                 "DIAG idle wait": "Idle",
                                 "ges remote message": "Idle",
                                 "gcs remote message": "Idle",
                                 "heartbeat monitor sleep": "Idle",
                                 "GCR sleep": "Idle",
                                 "SGA: MMAN sleep for component shrink": "Idle",
                                 "retry contact SCN lock master": "Cluster",
                                 "control file sequential read": "System I/O",
                                 "control file single write": "System I/O",
                                 "control file parallel write": "System I/O",
                                 "control file backup creation": "Administrative",
                                 "Shared IO Pool Memory": "Concurrency",
                                 "Shared IO Pool IO Completion": "User I/O",
                                 "remote log force - commit": "Commit",
                                 "remote log force - buffer update": "Cluster",
                                 "remote log force - buffer read": "Cluster",
                                 "remote log force - buffer send": "Cluster",
                                 "remote log force - SCN range": "Cluster",
                                 "remote log force - session cleanout": "Cluster",
                                 "enq: PW - flush prewarm buffers": "Application",
                                 "latch: cache buffers chains": "Concurrency",
                                 "free buffer waits": "Configuration",
                                 "local write wait": "User I/O",
                                 "checkpoint completed": "Configuration",
                                 "write complete waits": "Configuration",
                                 "write complete waits: flash cache": "Configuration",
                                 "buffer read retry": "User I/O",
                                 "buffer busy waits": "Concurrency",
                                 "gc buffer busy acquire": "Cluster",
                                 "gc buffer busy release": "Cluster",
                                 "read by other session": "User I/O",
                                 "multiple dbwriter suspend/resume for file offline": "Administrative",
                                 "recovery read": "System I/O",
                                 "pi renounce write complete": "Cluster",
                                 "db flash cache single block physical read": "User I/O",
                                 "db flash cache multiblock physical read": "User I/O",
                                 "db flash cache write": "User I/O",
                                 "db flash cache invalidate wait": "Concurrency",
                                 "db flash cache dynamic disabling wait": "Administrative",
                                 "enq: RO - contention": "Application",
                                 "enq: RO - fast object reuse": "Application",
                                 "enq: KO - fast object checkpoint": "Application",
                                 "MRP redo arrival": "Idle",
                                 "RFS sequential i/o": "System I/O",
                                 "RFS random i/o": "System I/O",
                                 "RFS write": "System I/O",
                                 "ARCH wait for net re-connect": "Network",
                                 "ARCH wait for netserver start": "Network",
                                 "LNS wait on LGWR": "Network",
                                 "LGWR wait on LNS": "Network",
                                 "ARCH wait for netserver init 2": "Network",
                                 "ARCH wait for flow-control": "Network",
                                 "ARCH wait for netserver detach": "Network",
                                 "LNS ASYNC archive log": "Idle",
                                 "LNS ASYNC dest activation": "Idle",
                                 "LNS ASYNC end of log": "Idle",
                                 "log file sequential read": "System I/O",
                                 "log file single write": "System I/O",
                                 "log file parallel write": "System I/O",
                                 "latch: redo writing": "Configuration",
                                 "latch: redo copy": "Configuration",
                                 "log buffer space": "Configuration",
                                 "log file switch (checkpoint incomplete)": "Configuration",
                                 "log file switch (private strand flush incomplete)": "Configuration",
                                 "log file switch (archiving needed)": "Configuration",
                                 "switch logfile command": "Administrative",
                                 "log file switch completion": "Configuration",
                                 "log file sync": "Commit",
                                 "log file sync: SCN ordering": "Concurrency",
                                 "simulated log write delay": "Idle",
                                 "heartbeat redo informer": "Idle",
                                 "LGWR real time apply sync": "Idle",
                                 "LGWR worker group idle": "Idle",
                                 "remote log force - log switch/recovery": "Cluster",
                                 "db file sequential read": "User I/O",
                                 "db file scattered read": "User I/O",
                                 "db file single write": "User I/O",
                                 "db file parallel write": "System I/O",
                                 "db file async I/O submit": "System I/O",
                                 "db file parallel read": "User I/O",
                                 "enq: MV - datafile move": "Administrative",
                                 "gc current request": "Cluster",
                                 "gc cr request": "Cluster",
                                 "gc cr disk request": "Cluster",
                                 "gc cr multi block request": "Cluster",
                                 "gc current multi block request": "Cluster",
                                 "gc block recovery request": "Cluster",
                                 "gc imc multi block request": "Cluster",
                                 "gc imc multi block quiesce": "Cluster",
                                 "gc cr block 2-way": "Cluster",
                                 "gc cr block 3-way": "Cluster",
                                 "gc cr block busy": "Cluster",
                                 "gc cr block congested": "Cluster",
                                 "gc cr failure": "Cluster",
                                 "gc cr block lost": "Cluster",
                                 "gc cr block unknown": "Cluster",
                                 "gc current block 2-way": "Cluster",
                                 "gc current block 3-way": "Cluster",
                                 "gc current block busy": "Cluster",
                                 "gc current block congested": "Cluster",
                                 "gc current retry": "Cluster",
                                 "gc current block lost": "Cluster",
                                 "gc current split": "Cluster",
                                 "gc current block unknown": "Cluster",
                                 "gc cr grant 2-way": "Cluster",
                                 "gc cr grant busy": "Cluster",
                                 "gc cr grant congested": "Cluster",
                                 "gc cr grant unknown": "Cluster",
                                 "gc cr disk read": "Cluster",
                                 "gc cr grant ka": "Cluster",
                                 "gc cr grant cluster flash cache read": "Cluster",
                                 "gc cr cluster flash cache read": "Cluster",
                                 "gc cr flash cache copy": "Cluster",
                                 "gc current grant 2-way": "Cluster",
                                 "gc current grant busy": "Cluster",
                                 "gc current grant congested": "Cluster",
                                 "gc current grant unknown": "Cluster",
                                 "gc current grant ka": "Cluster",
                                 "gc current grant cluster flash cache read": "Cluster",
                                 "gc freelist": "Cluster",
                                 "gc remaster": "Cluster",
                                 "gc quiesce": "Cluster",
                                 "gc recovery": "Cluster",
                                 "gc flushed buffer": "Cluster",
                                 "gc send complete": "Cluster",
                                 "gc current cancel": "Cluster",
                                 "gc cr cancel": "Cluster",
                                 "gc assume": "Cluster",
                                 "gc domain validation": "Cluster",
                                 "gc recovery free": "Cluster",
                                 "gc recovery quiesce": "Cluster",
                                 "gc claim": "Cluster",
                                 "gc cancel retry": "Cluster",
                                 "direct path read": "User I/O",
                                 "direct path read temp": "User I/O",
                                 "direct path write": "User I/O",
                                 "direct path write temp": "User I/O",
                                 "parallel recovery slave idle wait": "Idle",
                                 "Backup Appliance waiting for work": "Idle",
                                 "Backup Appliance waiting restore start": "Idle",
                                 "Backup Appliance Surrogate wait": "Idle",
                                 "Backup Appliance Servlet wait": "Idle",
                                 "Backup Appliance Comm SGA setup wait": "Idle",
                                 "LogMiner builder: idle": "Idle",
                                 "LogMiner builder: memory": "Queueing",
                                 "LogMiner builder: DDL": "Queueing",
                                 "LogMiner builder: branch": "Idle",
                                 "LogMiner preparer: idle": "Idle",
                                 "LogMiner preparer: memory": "Queueing",
                                 "LogMiner reader: buffer": "Queueing",
                                 "LogMiner reader: log (idle)": "Idle",
                                 "LogMiner reader: redo (idle)": "Idle",
                                 "LogMiner client: transaction": "Idle",
                                 "LogMiner: other": "Idle",
                                 "LogMiner: activate": "Idle",
                                 "LogMiner: reset": "Idle",
                                 "LogMiner: find session": "Idle",
                                 "LogMiner: internal": "Idle",
                                 "Logical Standby Apply Delay": "Idle",
                                 "wait for possible quiesce finish": "Administrative",
                                 "parallel recovery coordinator waits for slave cleanup": "Idle",
                                 "flashback log file write": "System I/O",
                                 "flashback log file read": "System I/O",
                                 "flashback buf free by RVWR": "Configuration",
                                 "flashback log file sync": "User I/O",
                                 "parallel recovery coordinator idle wait": "Idle",
                                 "parallel recovery control message reply": "Idle",
                                 "cell smart table scan": "User I/O",
                                 "cell smart index scan": "User I/O",
                                 "cell external table smart scan": "User I/O",
                                 "cell statistics gather": "User I/O",
                                 "cell smart incremental backup": "System I/O",
                                 "cell smart file creation": "User I/O",
                                 "cell smart restore from backup": "System I/O",
                                 "parallel recovery slave next change": "Idle",
                                 "concurrent I/O completion": "Administrative",
                                 "datafile copy range completion": "Administrative",
                                 "nologging standby txn commit": "Commit",
                                 "nologging range consumption list": "Configuration",
                                 "recovery sender idle wait": "Idle",
                                 "recovery receiver idle wait": "Idle",
                                 "recovery merger idle wait ": "Idle",
                                 "enq: TM - contention": "Application",
                                 "enq: ST - contention": "Configuration",
                                 "undo segment extension": "Configuration",
                                 "undo segment tx slot": "Configuration",
                                 "switch undo - offline": "Administrative",
                                 "alter rbs offline": "Administrative",
                                 "enq: TX - row lock contention": "Application",
                                 "enq: TX - allocate ITL entry": "Configuration",
                                 "enq: TX - index contention": "Concurrency",
                                 "enq: TW - contention": "Administrative",
                                 "PX Deq: Txn Recovery Start": "Idle",
                                 "PX Deq: Txn Recovery Reply": "Idle",
                                 "latch: Undo Hint Latch": "Concurrency",
                                 "statement suspended, wait error to be cleared": "Configuration",
                                 "latch: In memory undo latch": "Concurrency",
                                 "latch: MQL Tracking Latch": "Concurrency",
                                 "fbar timer": "Idle",
                                 "Archive Manager file transfer I/O": "User I/O",
                                 "SecureFile log buffer": "Configuration",
                                 "IM buffer busy": "Concurrency",
                                 "securefile chain update": "Concurrency",
                                 "enq: HW - contention": "Configuration",
                                 "enq: SS - contention": "Configuration",
                                 "sort segment request": "Configuration",
                                 "smon timer": "Idle",
                                 "PX Deq: Metadata Update": "Idle",
                                 "Space Manager: slave idle wait": "Idle",
                                 "enq: SQ - contention": "Configuration",
                                 "PX Deq: Index Merge Reply": "Idle",
                                 "PX Deq: Index Merge Execute": "Idle",
                                 "PX Deq: Index Merge Close": "Idle",
                                 "enq: HV - contention": "Concurrency",
                                 "PX Deq: kdcph_mai": "Idle",
                                 "PX Deq: kdcphc_ack": "Idle",
                                 "index (re)build online start": "Administrative",
                                 "index (re)build online cleanup": "Administrative",
                                 "index (re)build online merge": "Administrative",
                                 "securefile direct-read completion": "User I/O",
                                 "securefile direct-write completion": "User I/O",
                                 "SecureFile mutex": "Concurrency",
                                 "enq: WG - lock fso": "Concurrency",
                                 "imco timer": "Idle",
                                 "Inmemory Populate: get loadscn": "Concurrency",
                                 "latch: row cache objects": "Concurrency",
                                 "row cache lock": "Concurrency",
                                 "row cache read": "Concurrency",
                                 "libcache interrupt action by LCK": "Concurrency",
                                 "cursor: mutex X": "Concurrency",
                                 "cursor: mutex S": "Concurrency",
                                 "cursor: pin X": "Concurrency",
                                 "cursor: pin S": "Concurrency",
                                 "cursor: pin S wait on X": "Concurrency",
                                 "enq: CB - role operation": "Concurrency",
                                 "Global transaction acquire instance locks": "Configuration",
                                 "enq: BB - 2PC across RAC instances": "Commit",
                                 "latch: shared pool": "Concurrency",
                                 "LCK0 row cache object free": "Concurrency",
                                 "library cache pin": "Concurrency",
                                 "library cache lock": "Concurrency",
                                 "library cache load lock": "Concurrency",
                                 "library cache: mutex X": "Concurrency",
                                 "library cache: mutex S": "Concurrency",
                                 "BFILE read": "User I/O",
                                 "resmgr:cpu quantum": "Scheduler",
                                 "resmgr:large I/O queued": "Scheduler",
                                 "resmgr:small I/O queued": "Scheduler",
                                 "resmgr:internal state change": "Concurrency",
                                 "resmgr:sessions to exit": "Concurrency",
                                 "resmgr:become active": "Scheduler",
                                 "resmgr:pq queued": "Scheduler",
                                 "TCP Socket (KGAS)": "Network",
                                 "utl_file I/O": "User I/O",
                                 "alter system set dispatcher": "Administrative",
                                 "virtual circuit wait": "Network",
                                 "virtual circuit next request": "Idle",
                                 "shared server idle wait": "Idle",
                                 "dispatcher timer": "Idle",
                                 "dispatcher listen timer": "Network",
                                 "dedicated server timer": "Network",
                                 "cmon timer": "Idle",
                                 "pool server timer": "Idle",
                                 "connection pool wait": "Administrative",
                                 "connection broker handoff": "Network",
                                 "lreg timer": "Idle",
                                 "JOX Jit Process Sleep": "Idle",
                                 "jobq slave wait": "Idle",
                                 "Wait for Table Lock": "Application",
                                 "pipe get": "Idle",
                                 "pipe put": "Concurrency",
                                 "enq: DB - contention": "Administrative",
                                 "PX Deque wait": "Idle",
                                 "PX Idle Wait": "Idle",
                                 "PX Deq: Join ACK": "Idle",
                                 "PX Deq Credit: need buffer": "Idle",
                                 "PX Deq Credit: send blkd": "Idle",
                                 "PX Deq: Msg Fragment": "Idle",
                                 "PX Deq: Parse Reply": "Idle",
                                 "PX Deq: Execute Reply": "Idle",
                                 "PX Deq: Execution Msg": "Idle",
                                 "PX Deq: Table Q Normal": "Idle",
                                 "PX Deq: Table Q Sample": "Idle",
                                 "external table read": "User I/O",
                                 "external table write": "User I/O",
                                 "external table open": "User I/O",
                                 "external table seek": "User I/O",
                                 "external table misc IO": "User I/O",
                                 "enq: RC - Result Cache: Contention": "Application",
                                 "enq: JX - SQL statement queue": "Scheduler",
                                 "enq: JX - cleanup of  queue": "Scheduler",
                                 "PX Queuing: statement queue": "Scheduler",
                                 "dbverify reads": "User I/O",
                                 "REPL Apply: txns": "Idle",
                                 "REPL Capture: subscribers to catch up": "Queueing",
                                 "REPL Capture/Apply: memory": "Queueing",
                                 "REPL Apply: commit": "Configuration",
                                 "REPL Apply: dependency": "Concurrency",
                                 "REPL Capture/Apply: flow control": "Queueing",
                                 "REPL Capture/Apply: messages": "Idle",
                                 "REPL Capture: archive log": "Idle",
                                 "REPL Capture: filter callback ruleset": "Application",
                                 "REPL Apply: apply DDL": "Application",
                                 "enq: ZG - contention": "Administrative",
                                 "single-task message": "Idle",
                                 "SQL*Net message to client": "Network",
                                 "SQL*Net message to dblink": "Network",
                                 "SQL*Net more data to client": "Network",
                                 "SQL*Net more data to dblink": "Network",
                                 "SQL*Net message from client": "Idle",
                                 "SQL*Net more data from client": "Network",
                                 "SQL*Net message from dblink": "Network",
                                 "SQL*Net more data from dblink": "Network",
                                 "SQL*Net vector message from client": "Idle",
                                 "SQL*Net vector message from dblink": "Idle",
                                 "SQL*Net vector data to client": "Network",
                                 "SQL*Net vector data from client": "Network",
                                 "SQL*Net vector data to dblink": "Network",
                                 "SQL*Net vector data from dblink": "Network",
                                 "SQL*Net break/reset to client": "Application",
                                 "SQL*Net break/reset to dblink": "Application",
                                 "External Procedure initial connection": "Application",
                                 "External Procedure call": "Application",
                                 "PL/SQL lock timer": "Idle",
                                 "enq: UL - contention": "Application",
                                 "wait for EMON to process ntfns": "Configuration",
                                 "Streams AQ: emn coordinator idle wait": "Idle",
                                 "EMON slave idle wait": "Idle",
                                 "Emon coordinator main loop": "Idle",
                                 "Emon slave main loop": "Idle",
                                 "Streams AQ: waiting for messages in the queue": "Idle",
                                 "Streams AQ: waiting for time management or cleanup tasks": "Idle",
                                 "Streams AQ: enqueue blocked on low memory": "Queueing",
                                 "Streams AQ: enqueue blocked due to flow control": "Queueing",
                                 "Streams AQ: delete acknowledged messages": "Idle",
                                 "Streams AQ: deallocate messages from Streams Pool": "Idle",
                                 "Streams AQ: qmn coordinator idle wait": "Idle",
                                 "Streams AQ: qmn slave idle wait": "Idle",
                                 "AQ: 12c message cache init wait": "Idle",
                                 "AQ Cross Master idle": "Idle",
                                 "AQPC idle": "Idle",
                                 "Streams AQ: load balancer idle": "Idle",
                                 "Sharded  Queues : Part Maintenance idle": "Idle",
                                 "REPL Capture/Apply: RAC AQ qmn coordinator": "Idle",
                                 "HS message to agent": "Idle",
                                 "TEXT: URL_DATASTORE network wait": "Network",
                                 "TEXT: File System I/O": "User I/O",
                                 "OLAP DML Sleep": "Application",
                                 "Cube Build Master Wait for Jobs": "Concurrency",
                                 "ASM sync cache disk read": "User I/O",
                                 "ASM sync relocation I/O": "System I/O",
                                 "ASM async relocation I/O": "System I/O",
                                 "ASM COD rollback operation completion": "Administrative",
                                 "kfk: async disk IO": "System I/O",
                                 "ASM remote SQL": "Network",
                                 "ASM background timer": "Idle",
                                 "iowp io": "System I/O",
                                 "iowp msg": "Idle",
                                 "iowp file id": "Idle",
                                 "netp network": "Idle",
                                 "gopp msg": "Idle",
                                 "ASM Fixed Package I/O": "User I/O",
                                 "ASM mount : wait for heartbeat": "Administrative",
                                 "ASM PST query : wait for [PM][grp][0] grant": "Cluster",
                                 "lock remastering": "Cluster",
                                 "ASM Staleness File I/O": "User I/O",
                                 "auto-sqltune: wait graph update": "Idle",
                                 "WCR: replay client notify": "Idle",
                                 "WCR: replay clock": "Idle",
                                 "WCR: replay lock order": "Application",
                                 "WCR: replay paused": "Idle",
                                 "JS kgl get object wait": "Administrative",
                                 "JS external job": "Idle",
                                 "JS kill job wait": "Administrative",
                                 "JS coord start wait": "Administrative",
                                 "cell single block physical read": "User I/O",
                                 "cell multiblock physical read": "User I/O",
                                 "cell list of blocks physical read": "User I/O",
                                 "cell physical read no I/O": "User I/O",
                                 "cell single block read request": "User I/O",
                                 "cell multiblock read request": "User I/O",
                                 "cell list of blocks read request": "User I/O",
                                 "cell manager opening cell": "System I/O",
                                 "cell manager closing cell": "System I/O",
                                 "cell manager discovering disks": "System I/O",
                                 "cell worker idle": "Idle",
                                 "events in waitclass Other": "Other",
                                 "enq: WM - WLM Plan activation": "Other",
                                 "latch free": "Other",
                                 "kslwait unit test event 1": "Other",
                                 "kslwait unit test event 2": "Other",
                                 "kslwait unit test event 3": "Other",
                                 "unspecified wait event": "Other",
                                 "latch activity": "Other",
                                 "wait list latch activity": "Other",
                                 "wait list latch free": "Other",
                                 "global enqueue expand wait": "Other",
                                 "free process state object": "Other",
                                 "inactive session": "Other",
                                 "process terminate": "Other",
                                 "latch: call allocation": "Other",
                                 "latch: session allocation": "Other",
                                 "check CPU wait times": "Other",
                                 "enq: CI - contention": "Other",
                                 "enq: PR - contention": "Other",
                                 "enq: AK -  contention": "Other",
                                 "enq: XK -  contention": "Other",
                                 "enq: DI -  contention": "Other",
                                 "enq: RM -  contention": "Other",
                                 "enq: BO -  contention": "Other",
                                 "ges resource enqueue open retry sleep": "Other",
                                 "ksim generic wait event": "Other",
                                 "debugger command": "Other",
                                 "ksdxexeother": "Other",
                                 "ksdxexeotherwait": "Other",
                                 "latch: ksm sga alloc latch": "Other",
                                 "defer SGA allocation slave": "Other",
                                 "SGA Allocator termination": "Other",
                                 "enq: PE - contention": "Other",
                                 "enq: PG - contention": "Other",
                                 "ksbsrv": "Other",
                                 "ksbcic": "Other",
                                 "process startup": "Other",
                                 "process shutdown": "Other",
                                 "prior spawner clean up": "Other",
                                 "latch: messages": "Other",
                                 "rdbms ipc message block": "Other",
                                 "rdbms ipc reply": "Other",
                                 "latch: enqueue hash chains": "Other",
                                 "enq: FP - global fob contention": "Other",
                                 "enq: RE - block repair contention": "Other",
                                 "enq: BM - clonedb bitmap file write": "Other",
                                 "asynch descriptor resize": "Other",
                                 "enq: FO - file system operation contention": "Other",
                                 "imm op": "Other",
                                 "slave exit": "Other",
                                 "enq: KM - contention": "Other",
                                 "enq: KT - contention": "Other",
                                 "enq: CA - contention": "Other",
                                 "enq: KD - determine DBRM master": "Other",
                                 "reliable message": "Other",
                                 "broadcast mesg queue transition": "Other",
                                 "broadcast mesg recovery queue transition": "Other",
                                 "KSV master wait": "Other",
                                 "master exit": "Other",
                                 "ksv slave avail wait": "Other",
                                 "enq: PV - syncstart": "Other",
                                 "enq: PV - syncshut": "Other",
                                 "enq: SP - contention 1": "Other",
                                 "enq: SP - contention 2": "Other",
                                 "enq: SP - contention 3": "Other",
                                 "enq: SP - contention 4": "Other",
                                 "enq: SX - contention 5": "Other",
                                 "enq: SX - contention 6": "Other",
                                 "first spare wait event": "Other",
                                 "second spare wait event": "Other",
                                 "IPC send completion sync": "Other",
                                 "OSD IPC library": "Other",
                                 "IPC wait for name service busy": "Other",
                                 "IPC busy async request": "Other",
                                 "IPC waiting for OSD resources": "Other",
                                 "ksxr poll remote instances": "Other",
                                 "ksxr wait for mount shared": "Other",
                                 "DBMS_LDAP: LDAP operation ": "Other",
                                 "wait for FMON to come up": "Other",
                                 "enq: FM - contention": "Other",
                                 "enq: XY - contention": "Other",
                                 "set director factor wait": "Other",
                                 "latch: active service list": "Other",
                                 "enq: AS - service activation": "Other",
                                 "enq: PD - contention": "Other",
                                 "oracle thread bootstrap": "Other",
                                 "os thread creation": "Other",
                                 "cleanup of aborted process": "Other",
                                 "enq: XM -  contention": "Other",
                                 "enq: RU - contention": "Other",
                                 "enq: RU - waiting": "Other",
                                 "rolling migration: cluster quiesce": "Other",
                                 "LMON global data update": "Other",
                                 "process diagnostic dump": "Other",
                                 "enq: MX - sync storage server info": "Other",
                                 "master diskmon startup": "Other",
                                 "master diskmon read": "Other",
                                 "DSKM to complete cell health check": "Other",
                                 "pmon dblkr tst event": "Other",
                                 "pmon cleanup on exit": "Other",
                                 "latch: ksolt alloc": "Other",
                                 "lightweight thread operation": "Other",
                                 "enq: ZX - repopulation file write": "Other",
                                 "DIAG lock acquisition": "Other",
                                 "latch: ges resource hash list": "Other",
                                 "DFS lock handle": "Other",
                                 "ges LMD to shutdown": "Other",
                                 "ges client process to exit": "Other",
                                 "ges global resource directory to be frozen": "Other",
                                 "ges resource directory to be unfrozen": "Other",
                                 "gcs resource directory to be unfrozen": "Other",
                                 "ges LMD to inherit communication channels": "Other",
                                 "ges lmd sync during reconfig": "Other",
                                 "ges wait for lmon to be ready": "Other",
                                 "ges cgs registration": "Other",
                                 "wait for master scn": "Other",
                                 "ges yield cpu in reconfig": "Other",
                                 "ges2 proc latch in rm latch get 1": "Other",
                                 "ges2 proc latch in rm latch get 2": "Other",
                                 "ges lmd/lmses to freeze in rcfg": "Other",
                                 "ges lmd/lmses to unfreeze in rcfg": "Other",
                                 "ges lms sync during dynamic remastering and reconfig": "Other",
                                 "ges LMON to join CGS group": "Other",
                                 "ges pmon to exit": "Other",
                                 "ges lmd and pmon to attach": "Other",
                                 "gcs drm freeze begin": "Other",
                                 "gcs retry nowait latch get": "Other",
                                 "gcs remastering wait for read latch": "Other",
                                 "ges cached resource cleanup": "Other",
                                 "ges generic event": "Other",
                                 "ges retry query node": "Other",
                                 "ges process with outstanding i/o": "Other",
                                 "ges user error": "Other",
                                 "ges enter server mode": "Other",
                                 "gcs enter server mode": "Other",
                                 "gcs drm freeze in enter server mode": "Other",
                                 "gcs ddet enter server mode": "Other",
                                 "ges cancel": "Other",
                                 "ges resource cleanout during enqueue open": "Other",
                                 "ges resource cleanout during enqueue open-cvt": "Other",
                                 "ges master to get established for SCN op": "Other",
                                 "ges LMON to get to FTDONE ": "Other",
                                 "ges1 LMON to wake up LMD - mrcvr": "Other",
                                 "ges2 LMON to wake up LMD - mrcvr": "Other",
                                 "ges2 LMON to wake up lms - mrcvr 2": "Other",
                                 "ges2 LMON to wake up lms - mrcvr 3": "Other",
                                 "ges inquiry response": "Other",
                                 "ges reusing os pid": "Other",
                                 "ges LMON for send queues": "Other",
                                 "ges LMD suspend for testing event": "Other",
                                 "ges performance test completion": "Other",
                                 "kjbopen wait for recovery domain attach": "Other",
                                 "kjudomatt wait for recovery domain attach": "Other",
                                 "kjudomdet wait for recovery domain detach": "Other",
                                 "kjbdomalc allocate recovery domain - retry": "Other",
                                 "kjbdrmcvtq lmon drm quiesce: ping completion": "Other",
                                 "ges RMS0 retry add redo log": "Other",
                                 "readable standby redo apply remastering": "Other",
                                 "ges DFS hang analysis phase 2 acks": "Other",
                                 "ges/gcs diag dump": "Other",
                                 "global plug and play automatic resource creation": "Other",
                                 "gcs lmon dirtydetach step completion": "Other",
                                 "recovery instance recovery completion": "Other",
                                 "ack for a broadcasted res from a remote instance": "Other",
                                 "latch: kjci process context latch": "Other",
                                 "latch: kjci request sequence latch": "Other",
                                 "DLM cross inst call completion": "Other",
                                 "DLM: shared instance mode init": "Other",
                                 "enq: KI - contention": "Other",
                                 "latch: kjoeq omni enqueue hash bucket latch": "Other",
                                 "DLM enqueue copy completion": "Other",
                                 "latch: kjoer owner hash bucket": "Other",
                                 "DLM Omni Enq Owner replication": "Other",
                                 "KJC: Wait for msg sends to complete": "Other",
                                 "ges message buffer allocation": "Other",
                                 "kjctssqmg: quick message send wait": "Other",
                                 "kjctcisnd: Queue/Send client message": "Other",
                                 "gcs domain validation": "Other",
                                 "latch: gcs resource hash": "Other",
                                 "affinity expansion in replay": "Other",
                                 "wait for sync ack": "Other",
                                 "wait for verification ack": "Other",
                                 "wait for assert messages to be sent": "Other",
                                 "wait for scn ack": "Other",
                                 "lms flush message acks": "Other",
                                 "name-service call wait": "Other",
                                 "CGS wait for IPC msg": "Other",
                                 "kjxgrtest": "Other",
                                 "IMR mount phase II completion": "Other",
                                 "IMR disk votes": "Other",
                                 "IMR rr lock release": "Other",
                                 "IMR net-check message ack": "Other",
                                 "IMR rr update": "Other",
                                 "IMR membership resolution": "Other",
                                 "IMR CSS join retry": "Other",
                                 "CGS skgxn join retry": "Other",
                                 "gcs to be enabled": "Other",
                                 "gcs log flush sync": "Other",
                                 "enq: PP -  contention": "Other",
                                 "enq: HM -  contention": "Other",
                                 "GCR ctx lock acquisition": "Other",
                                 "GCR CSS group lock": "Other",
                                 "GCR CSS group join": "Other",
                                 "GCR CSS group leave": "Other",
                                 "GCR CSS group update": "Other",
                                 "GCR CSS group query": "Other",
                                 "enq: AC - acquiring partition id": "Other",
                                 "SGA: allocation forcing component growth": "Other",
                                 "SGA: sga_target resize": "Other",
                                 "enq: SC -  contention": "Other",
                                 "control file heartbeat": "Other",
                                 "control file diagnostic dump": "Other",
                                 "enq: CF - contention": "Other",
                                 "enq: SW - contention": "Other",
                                 "enq: DS - contention": "Other",
                                 "enq: TC - contention": "Other",
                                 "enq: TC - contention2": "Other",
                                 "buffer exterminate": "Other",
                                 "buffer resize": "Other",
                                 "latch: cache buffers lru chain": "Other",
                                 "enq: PW - perwarm status in dbw0": "Other",
                                 "latch: checkpoint queue latch": "Other",
                                 "latch: cache buffer handles": "Other",
                                 "kcbzps": "Other",
                                 "DBWR range invalidation sync": "Other",
                                 "buffer deadlock": "Other",
                                 "buffer latch": "Other",
                                 "cr request retry": "Other",
                                 "writes stopped by instance recovery or database suspension": "Other",
                                 "lock escalate retry": "Other",
                                 "lock deadlock retry": "Other",
                                 "prefetch warmup block being transferred": "Other",
                                 "recovery buffer pinned": "Other",
                                 "TSE master key rekey": "Other",
                                 "TSE SSO wallet reopen": "Other",
                                 "force-cr-override flush": "Other",
                                 "enq: CR - block range reuse ckpt": "Other",
                                 "wait for MTTR advisory state object": "Other",
                                 "latch: object queue header operation": "Other",
                                 "retry cftxn during close": "Other",
                                 "get branch/thread/sequence enqueue": "Other",
                                 "enq: WL - Test access/locking": "Other",
                                 "Data Guard server operation completion": "Other",
                                 "FAL archive wait 1 sec for REOPEN minimum": "Other",
                                 "TEST: action sync": "Other",
                                 "TEST: action hang": "Other",
                                 "RSGA: RAC reconfiguration": "Other",
                                 "enq: WL - RAC-wide SGA initialize": "Other",
                                 "enq: WL - RAC-wide SGA write": "Other",
                                 "enq: WL - RAC-wide SGA dump": "Other",
                                 "LGWR ORL/NoExp FAL archival": "Other",
                                 "enq: WS -  contention": "Other",
                                 "MRP wait on process start": "Other",
                                 "MRP wait on process restart": "Other",
                                 "MRP wait on startup clear": "Other",
                                 "MRP inactivation": "Other",
                                 "MRP termination": "Other",
                                 "MRP state inspection": "Other",
                                 "MRP wait on archivelog arrival": "Other",
                                 "MRP wait on archivelog archival": "Other",
                                 "enq: WL - Far Sync Fail Over": "Other",
                                 "Monitor testing": "Other",
                                 "enq: WL - redo_db table update": "Other",
                                 "enq: WL - redo_db table query": "Other",
                                 "enq: WL - redo_log table update": "Other",
                                 "enq: WL - redo_log table query": "Other",
                                 "enq: PY - AVM RTA access instance": "Other",
                                 "enq: PY - AVM RTA access database": "Other",
                                 "enq: PY - AVM RTA access database 2": "Other",
                                 "log switch/archive": "Other",
                                 "enq: WL - Switchover To Primary": "Other",
                                 "ARCH wait on c/f tx acquire 1": "Other",
                                 "RFS attach": "Other",
                                 "RFS create": "Other",
                                 "RFS close": "Other",
                                 "RFS announce": "Other",
                                 "RFS register": "Other",
                                 "RFS detach": "Other",
                                 "RFS ping": "Other",
                                 "RFS dispatch": "Other",
                                 "enq: WL - RFS global state contention": "Other",
                                 "LGWR simulation latency wait": "Other",
                                 "LNS simulation latency wait": "Other",
                                 "ASYNC Remote Write": "Other",
                                 "SYNC Remote Write": "Other",
                                 "ARCH Remote Write": "Other",
                                 "Redo Transport Attach": "Other",
                                 "Redo Transport Detach": "Other",
                                 "Redo Transport Open": "Other",
                                 "Redo Transport Close": "Other",
                                 "Redo Transport Ping": "Other",
                                 "Remote SYNC Ping": "Other",
                                 "Redo Transport Slave Startup": "Other",
                                 "Redo Transport Slave Shutdown": "Other",
                                 "Redo Writer Remote Sync Notify": "Other",
                                 "Redo Writer Remote Sync Complete": "Other",
                                 "Redo Transport MISC": "Other",
                                 "Data Guard: RFS disk I/O": "Other",
                                 "ARCH wait for process start 1": "Other",
                                 "ARCH wait for process death 1": "Other",
                                 "ARCH wait for process start 3": "Other",
                                 "Data Guard: process exit": "Other",
                                 "Data Guard: process clean up": "Other",
                                 "LGWR-LNS wait on channel": "Other",
                                 "enq: WR - contention": "Other",
                                 "Redo transport testing": "Other",
                                 "enq: RZ - add element": "Other",
                                 "enq: RZ - remove element": "Other",
                                 "Image redo gen delay": "Other",
                                 "LGWR wait for redo copy": "Other",
                                 "latch: redo allocation": "Other",
                                 "log file switch (clearing log file)": "Other",
                                 "target log write size": "Other",
                                 "LGWR any worker group": "Other",
                                 "LGWR all worker groups": "Other",
                                 "LGWR worker group ordering": "Other",
                                 "LGWR intra group sync": "Other",
                                 "LGWR intra group IO completion": "Other",
                                 "enq: WL - contention": "Other",
                                 "enq: RN - contention": "Other",
                                 "DFS db file lock": "Other",
                                 "enq: DF - contention": "Other",
                                 "enq: IS - contention": "Other",
                                 "enq: IP - open/close PDB": "Other",
                                 "enq: FS - contention": "Other",
                                 "enq: FS - online log operation": "Other",
                                 "enq: DM - contention": "Other",
                                 "enq: RP - contention": "Other",
                                 "latch: gc element": "Other",
                                 "enq: RT - contention": "Other",
                                 "enq: RT - thread internal enable/disable": "Other",
                                 "enq: IR - contention": "Other",
                                 "enq: IR - contention2": "Other",
                                 "enq: IR - global serialization": "Other",
                                 "enq: IR - local serialization": "Other",
                                 "enq: IR - arbitrate instance recovery": "Other",
                                 "enq: MR - contention": "Other",
                                 "enq: MR - standby role transition": "Other",
                                 "enq: MR - multi instance redo apply": "Other",
                                 "enq: MR - any role transition": "Other",
                                 "enq: MR - PDB open": "Other",
                                 "enq: MR - datafile online": "Other",
                                 "enq: MR - adg instance recovery": "Other",
                                 "shutdown after switchover to standby": "Other",
                                 "cancel media recovery on switchover": "Other",
                                 "parallel recovery coord wait for reply": "Other",
                                 "parallel recovery coord send blocked": "Other",
                                 "parallel recovery slave wait for change": "Other",
                                 "enq: BR - file shrink": "Other",
                                 "enq: BR - proxy-copy": "Other",
                                 "enq: BR - multi-section restore header": "Other",
                                 "enq: BR - multi-section restore section": "Other",
                                 "enq: BR - space info datafile hdr update": "Other",
                                 "enq: BR - request autobackup": "Other",
                                 "enq: BR - perform autobackup": "Other",
                                 "enq: BR - BA lock db": "Other",
                                 "enq: BR - BA lock storage loc": "Other",
                                 "enq: BR - BA lock timer queue": "Other",
                                 "enq: BR - BA lock scheduler": "Other",
                                 "enq: BR - BA lock API": "Other",
                                 "enq: BR - BA quiesce storage ": "Other",
                                 "enq: BR - BA check quiescence": "Other",
                                 "enq: BR - BA run scheduler": "Other",
                                 "enq: BR - BA purge storage loc": "Other",
                                 "enq: BR - BA invalidate plans": "Other",
                                 "enq: BR - BA protect plans": "Other",
                                 "enq: ID - contention": "Other",
                                 "Backup Restore Throttle sleep": "Other",
                                 "Backup Restore Switch Bitmap sleep": "Other",
                                 "Backup Restore Event 19778 sleep": "Other",
                                 "enq: BS - Backup spare1": "Other",
                                 "enq: BS - Backup spare2": "Other",
                                 "enq: BS - Backup spare3": "Other",
                                 "enq: BS - Backup spare4": "Other",
                                 "enq: BS - Backup spare5": "Other",
                                 "enq: BS - Backup spare6": "Other",
                                 "enq: BS - Backup spare7": "Other",
                                 "enq: BS - Backup spare8": "Other",
                                 "enq: BS - Backup spare9": "Other",
                                 "enq: BS - Backup spare0": "Other",
                                 "enq: AB - ABMR process start/stop": "Other",
                                 "enq: AB - ABMR process initialized": "Other",
                                 "Auto BMR completion": "Other",
                                 "Auto BMR RPC standby catchup": "Other",
                                 "enq: BC - drop container group": "Other",
                                 "enq: BC - create container": "Other",
                                 "enq: BC - group - create container": "Other",
                                 "enq: BC - drop container": "Other",
                                 "enq: BC - group - create file": "Other",
                                 "enq: BI - create file": "Other",
                                 "enq: BI - identify file": "Other",
                                 "enq: BI - delete file": "Other",
                                 "enq: BZ - resize file": "Other",
                                 "enq: BV - rebuild/validate group": "Other",
                                 "Backup Appliance container synchronous read": "Other",
                                 "Backup Appliance container synchronous write": "Other",
                                 "Backup Appliance container I/O": "Other",
                                 "enq: MN - contention": "Other",
                                 "enq: PL - contention": "Other",
                                 "enq: CP - Pluggable database resetlogs": "Other",
                                 "enq: SB - logical standby metadata": "Other",
                                 "enq: SB - table instantiation": "Other",
                                 "Logical Standby Apply shutdown": "Other",
                                 "Logical Standby pin transaction": "Other",
                                 "Logical Standby dictionary build": "Other",
                                 "Logical Standby Terminal Apply": "Other",
                                 "Logical Standby Debug": "Other",
                                 "Resolution of in-doubt txns": "Other",
                                 "enq: XR - quiesce database": "Other",
                                 "enq: XR - database force logging": "Other",
                                 "standby query scn advance": "Other",
                                 "change tracking file synchronous read": "Other",
                                 "change tracking file synchronous write": "Other",
                                 "change tracking file parallel write": "Other",
                                 "block change tracking buffer space": "Other",
                                 "CTWR media recovery checkpoint request": "Other",
                                 "enq: CT - global space management": "Other",
                                 "enq: CT - local space management": "Other",
                                 "enq: CT - change stream ownership": "Other",
                                 "enq: CT - state": "Other",
                                 "enq: CT - state change gate 1": "Other",
                                 "enq: CT - state change gate 2": "Other",
                                 "enq: CT - CTWR process start/stop": "Other",
                                 "enq: CT - reading": "Other",
                                 "recovery area: computing dropped files": "Other",
                                 "recovery area: computing obsolete files": "Other",
                                 "recovery area: computing backed up files": "Other",
                                 "recovery area: computing applied logs": "Other",
                                 "enq: RS - file delete": "Other",
                                 "enq: RS - record reuse": "Other",
                                 "enq: RS - prevent file delete": "Other",
                                 "enq: RS - prevent aging list update": "Other",
                                 "enq: RS - persist alert level": "Other",
                                 "enq: RS - read alert level": "Other",
                                 "enq: RS - write alert level": "Other",
                                 "enq: FL - Flashback database log": "Other",
                                 "enq: FL - Flashback db command": "Other",
                                 "enq: FD - Marker generation": "Other",
                                 "enq: FD - Tablespace flashback on/off": "Other",
                                 "enq: FD - Flashback coordinator": "Other",
                                 "enq: FD - Flashback on/off": "Other",
                                 "enq: FD - Restore point create/drop": "Other",
                                 "enq: FD - Flashback logical operations": "Other",
                                 "flashback free VI log": "Other",
                                 "flashback log switch": "Other",
                                 "enq: FW -  contention": "Other",
                                 "RVWR wait for flashback copy": "Other",
                                 "parallel recovery read buffer free": "Other",
                                 "parallel recovery redo cache buffer free": "Other",
                                 "parallel recovery change buffer free": "Other",
                                 "cell smart flash unkeep": "Other",
                                 "parallel recovery coord: all replies": "Other",
                                 "datafile move cleanup during resize": "Other",
                                 "recovery receive buffer free": "Other",
                                 "recovery send buffer free": "Other",
                                 "DBMS_ROLLING instruction completion": "Other",
                                 "blocking txn id for DDL": "Other",
                                 "transaction": "Other",
                                 "inactive transaction branch": "Other",
                                 "txn to complete": "Other",
                                 "PMON to cleanup pseudo-branches at svc stop time": "Other",
                                 "PMON to cleanup detached branches at shutdown": "Other",
                                 "test long ops": "Other",
                                 "latch: undo global data": "Other",
                                 "undo segment recovery": "Other",
                                 "unbound tx": "Other",
                                 "wait for change": "Other",
                                 "wait for another txn - undo rcv abort": "Other",
                                 "wait for another txn - txn abort": "Other",
                                 "wait for another txn - rollback to savepoint": "Other",
                                 "undo_retention publish retry": "Other",
                                 "enq: TA - contention": "Other",
                                 "enq: TX - contention": "Other",
                                 "enq: US - contention": "Other",
                                 "wait for stopper event to be increased": "Other",
                                 "wait for a undo record": "Other",
                                 "wait for a paralle reco to abort": "Other",
                                 "enq: IM - contention for blr": "Other",
                                 "enq: TD - KTF dump entries": "Other",
                                 "enq: TE - KTF broadcast": "Other",
                                 "enq: CN - race with txn": "Other",
                                 "enq: CN - race with reg": "Other",
                                 "enq: CN - race with init": "Other",
                                 "latch: Change Notification Hash table latch": "Other",
                                 "enq: CO - master slave det": "Other",
                                 "enq: FE - contention": "Other",
                                 "latch: change notification client cache latch": "Other",
                                 "latch: SGA Logging Log Latch": "Other",
                                 "latch: SGA Logging Bkt Latch": "Other",
                                 "enq: MC - Securefile log": "Other",
                                 "enq: MF - flush bkgnd periodic": "Other",
                                 "enq: MF - creating swap in instance": "Other",
                                 "enq: MF - flush space": "Other",
                                 "enq: MF - flush client": "Other",
                                 "enq: MF - flush prior error": "Other",
                                 "enq: MF - flush destroy": "Other",
                                 "latch: ILM activity tracking latch": "Other",
                                 "latch: ILM access tracking extent": "Other",
                                 "IM CU busy": "Other",
                                 "enq: TF - contention": "Other",
                                 "latch: lob segment hash table latch": "Other",
                                 "latch: lob segment query latch": "Other",
                                 "latch: lob segment dispenser latch": "Other",
                                 "Wait for shrink lock2": "Other",
                                 "Wait for shrink lock": "Other",
                                 "L1 validation": "Other",
                                 "Wait for TT enqueue": "Other",
                                 "kttm2d": "Other",
                                 "ktsambl": "Other",
                                 "ktfbtgex": "Other",
                                 "enq: DT - contention": "Other",
                                 "enq: TS - contention": "Other",
                                 "enq: FB - contention": "Other",
                                 "enq: SK - contention": "Other",
                                 "enq: DW - contention": "Other",
                                 "enq: SU - contention": "Other",
                                 "enq: TT - contention": "Other",
                                 "ktm: instance recovery": "Other",
                                 "instance state change": "Other",
                                 "enq: SM -  contention": "Other",
                                 "enq: SJ - Slave Task Cancel": "Other",
                                 "Space Manager: slave messages": "Other",
                                 "enq: FH - contention": "Other",
                                 "latch: IM area scb latch": "Other",
                                 "latch: IM area sb latch": "Other",
                                 "enq: TZ - contention": "Other",
                                 "enq: IN - contention": "Other",
                                 "enq: ZB - contention": "Other",
                                 "latch: IM seg hdr latch": "Other",
                                 "latch: IM emb latch": "Other",
                                 "enq: SV -  contention": "Other",
                                 "index block split": "Other",
                                 "kdblil wait before retrying ORA-54": "Other",
                                 "dupl. cluster key": "Other",
                                 "kdic_do_merge": "Other",
                                 "enq: DL - contention": "Other",
                                 "enq: HQ - contention": "Other",
                                 "enq: HP - contention": "Other",
                                 "enq: KL -  contention": "Other",
                                 "enq: WG - delete fso": "Other",
                                 "enq: SL - get lock": "Other",
                                 "enq: SL - escalate lock": "Other",
                                 "enq: SL - get lock for undo": "Other",
                                 "enq: ZH - compression analysis": "Other",
                                 "Compression analysis": "Other",
                                 "enq: SZ - contention": "Other",
                                 "enq: ZC - FS Seg contention": "Other",
                                 "enq: ZD - FS CU mod": "Other",
                                 "enq: SY - IM populate by other session": "Other",
                                 "IM populate completion": "Other",
                                 "In-Memory populate: over pga limit": "Other",
                                 "row cache cleanup": "Other",
                                 "row cache process": "Other",
                                 "enq: QA -  contention": "Other",
                                 "enq: QB -  contention": "Other",
                                 "enq: QC -  contention": "Other",
                                 "enq: QD -  contention": "Other",
                                 "enq: QE -  contention": "Other",
                                 "enq: QF -  contention": "Other",
                                 "enq: QG -  contention": "Other",
                                 "enq: QH -  contention": "Other",
                                 "enq: QI -  contention": "Other",
                                 "enq: QJ -  contention": "Other",
                                 "enq: QK -  contention": "Other",
                                 "enq: QL -  contention": "Other",
                                 "enq: QM -  contention": "Other",
                                 "enq: QN -  contention": "Other",
                                 "enq: QO -  contention": "Other",
                                 "enq: QP -  contention": "Other",
                                 "enq: QQ -  contention": "Other",
                                 "enq: QR -  contention": "Other",
                                 "enq: QS -  contention": "Other",
                                 "enq: QT -  contention": "Other",
                                 "enq: QU -  contention": "Other",
                                 "enq: QV -  contention": "Other",
                                 "enq: QX -  contention": "Other",
                                 "enq: QY -  contention": "Other",
                                 "enq: QZ -  contention": "Other",
                                 "enq: DV - contention": "Other",
                                 "enq: SO - contention": "Other",
                                 "enq: VA -  contention": "Other",
                                 "enq: VB -  contention": "Other",
                                 "enq: VC -  contention": "Other",
                                 "enq: VD -  contention": "Other",
                                 "enq: VE -  contention": "Other",
                                 "enq: VF -  contention": "Other",
                                 "enq: VG -  contention": "Other",
                                 "enq: VH -  contention": "Other",
                                 "enq: VI -  contention": "Other",
                                 "enq: VJ -  contention": "Other",
                                 "enq: VK -  contention": "Other",
                                 "enq: VL -  contention": "Other",
                                 "enq: VM -  contention": "Other",
                                 "enq: VN -  contention": "Other",
                                 "enq: VO -  contention": "Other",
                                 "enq: VP -  contention": "Other",
                                 "enq: VQ -  contention": "Other",
                                 "enq: VR -  contention": "Other",
                                 "enq: VS -  contention": "Other",
                                 "enq: VT -  contention": "Other",
                                 "enq: VU -  contention": "Other",
                                 "enq: VV -  contention": "Other",
                                 "enq: VX -  contention": "Other",
                                 "enq: VY -  contention": "Other",
                                 "enq: VZ -  contention": "Other",
                                 "enq: EA -  contention": "Other",
                                 "enq: EB -  contention": "Other",
                                 "enq: EC -  contention": "Other",
                                 "enq: ED -  contention": "Other",
                                 "enq: EE -  contention": "Other",
                                 "enq: EF -  contention": "Other",
                                 "enq: EG -  contention": "Other",
                                 "enq: EH -  contention": "Other",
                                 "enq: EI -  contention": "Other",
                                 "enq: EJ -  contention": "Other",
                                 "enq: EK -  contention": "Other",
                                 "enq: EL -  contention": "Other",
                                 "enq: EM -  contention": "Other",
                                 "enq: EN -  contention": "Other",
                                 "enq: EO -  contention": "Other",
                                 "enq: EP -  contention": "Other",
                                 "enq: EQ -  contention": "Other",
                                 "enq: ER -  contention": "Other",
                                 "enq: ES -  contention": "Other",
                                 "enq: ET -  contention": "Other",
                                 "enq: EU -  contention": "Other",
                                 "enq: EV -  contention": "Other",
                                 "enq: EX -  contention": "Other",
                                 "enq: EY -  contention": "Other",
                                 "enq: EZ -  contention": "Other",
                                 "enq: LA -  contention": "Other",
                                 "enq: LB -  contention": "Other",
                                 "enq: LC -  contention": "Other",
                                 "enq: LD -  contention": "Other",
                                 "enq: LE -  contention": "Other",
                                 "enq: LF -  contention": "Other",
                                 "enq: LG -  contention": "Other",
                                 "enq: LH -  contention": "Other",
                                 "enq: LI -  contention": "Other",
                                 "enq: LJ -  contention": "Other",
                                 "enq: LK -  contention": "Other",
                                 "enq: LL -  contention": "Other",
                                 "enq: LM -  contention": "Other",
                                 "enq: LN -  contention": "Other",
                                 "enq: LO -  contention": "Other",
                                 "enq: LP -  contention": "Other",
                                 "enq: LQ -  contention": "Other",
                                 "enq: LR -  contention": "Other",
                                 "enq: LS -  contention": "Other",
                                 "enq: LT -  contention": "Other",
                                 "enq: LU -  contention": "Other",
                                 "enq: LV -  contention": "Other",
                                 "enq: LX -  contention": "Other",
                                 "enq: LY -  contention": "Other",
                                 "enq: LZ -  contention": "Other",
                                 "enq: YA -  contention": "Other",
                                 "enq: YB -  contention": "Other",
                                 "enq: YC -  contention": "Other",
                                 "enq: YD -  contention": "Other",
                                 "enq: YE -  contention": "Other",
                                 "enq: YF -  contention": "Other",
                                 "enq: YG -  contention": "Other",
                                 "enq: YH -  contention": "Other",
                                 "enq: YI -  contention": "Other",
                                 "enq: YJ -  contention": "Other",
                                 "enq: YK -  contention": "Other",
                                 "enq: YL -  contention": "Other",
                                 "enq: YM -  contention": "Other",
                                 "enq: YN -  contention": "Other",
                                 "enq: YO -  contention": "Other",
                                 "enq: YP -  contention": "Other",
                                 "enq: YQ -  contention": "Other",
                                 "enq: YR -  contention": "Other",
                                 "enq: YS -  contention": "Other",
                                 "enq: YT -  contention": "Other",
                                 "enq: YU -  contention": "Other",
                                 "enq: YV -  contention": "Other",
                                 "enq: YX -  contention": "Other",
                                 "enq: YY -  contention": "Other",
                                 "enq: YZ -  contention": "Other",
                                 "enq: GA -  contention": "Other",
                                 "enq: GB -  contention": "Other",
                                 "enq: GC -  contention": "Other",
                                 "enq: GD -  contention": "Other",
                                 "enq: GE -  contention": "Other",
                                 "enq: GF -  contention": "Other",
                                 "enq: GG -  contention": "Other",
                                 "enq: GH -  contention": "Other",
                                 "enq: GI -  contention": "Other",
                                 "enq: GJ -  contention": "Other",
                                 "enq: GK -  contention": "Other",
                                 "enq: GL -  contention": "Other",
                                 "enq: GM -  contention": "Other",
                                 "enq: GN -  contention": "Other",
                                 "enq: GO -  contention": "Other",
                                 "enq: GP -  contention": "Other",
                                 "enq: GQ -  contention": "Other",
                                 "enq: GR -  contention": "Other",
                                 "enq: GS -  contention": "Other",
                                 "enq: GT -  contention": "Other",
                                 "enq: GU -  contention": "Other",
                                 "enq: GV -  contention": "Other",
                                 "enq: GX -  contention": "Other",
                                 "enq: GY -  contention": "Other",
                                 "enq: GZ -  contention": "Other",
                                 "enq: NA -  contention": "Other",
                                 "enq: NB -  contention": "Other",
                                 "enq: NC -  contention": "Other",
                                 "enq: ND -  contention": "Other",
                                 "enq: NE -  contention": "Other",
                                 "enq: NF -  contention": "Other",
                                 "enq: NG -  contention": "Other",
                                 "enq: NH -  contention": "Other",
                                 "enq: NI -  contention": "Other",
                                 "enq: NJ -  contention": "Other",
                                 "enq: NK -  contention": "Other",
                                 "enq: NL -  contention": "Other",
                                 "enq: NM -  contention": "Other",
                                 "enq: NN -  contention": "Other",
                                 "enq: NO -  contention": "Other",
                                 "enq: NP -  contention": "Other",
                                 "enq: NQ -  contention": "Other",
                                 "enq: NR -  contention": "Other",
                                 "enq: NS -  contention": "Other",
                                 "enq: NT -  contention": "Other",
                                 "enq: NU -  contention": "Other",
                                 "enq: NV -  contention": "Other",
                                 "enq: NX -  contention": "Other",
                                 "enq: NY -  contention": "Other",
                                 "enq: NZ -  contention": "Other",
                                 "enq: IV -  contention": "Other",
                                 "enq: TP - contention": "Other",
                                 "enq: RW - MV metadata contention": "Other",
                                 "enq: OC - contention": "Other",
                                 "enq: OL - contention": "Other",
                                 "kkdlgon": "Other",
                                 "kkdlsipon": "Other",
                                 "kkdlhpon": "Other",
                                 "kgltwait": "Other",
                                 "kksfbc research": "Other",
                                 "kksscl hash split": "Other",
                                 "kksfbc child completion": "Other",
                                 "enq: CU - contention": "Other",
                                 "enq: AE - lock": "Other",
                                 "enq: PF - contention": "Other",
                                 "enq: IL - contention": "Other",
                                 "enq: CL - drop label": "Other",
                                 "enq: CL - compare labels": "Other",
                                 "enq: SG - OLS Add Group": "Other",
                                 "enq: SG - OLS Create Group": "Other",
                                 "enq: SG - OLS Drop Group": "Other",
                                 "enq: SG - OLS Alter Group Parent": "Other",
                                 "enq: OP - OLS Store user entries": "Other",
                                 "enq: OP - OLS Cleanup unused profiles": "Other",
                                 "enq: CC - decryption": "Other",
                                 "enq: MK - contention": "Other",
                                 "enq: OW - initialization": "Other",
                                 "enq: OW - termination": "Other",
                                 "enq: RK - set key": "Other",
                                 "enq: HC - HSM cache write": "Other",
                                 "enq: HC - HSM cache read": "Other",
                                 "enq: RL - RAC wallet lock": "Other",
                                 "enq: ZZ - update hash tables": "Other",
                                 "Failed Logon Delay": "Other",
                                 "enq: ZA - add std audit table partition": "Other",
                                 "enq: ZF - add fga audit table partition": "Other",
                                 "enq: ZS - excl access to spill audit file": "Other",
                                 "enq: PA - modify a privilege capture": "Other",
                                 "enq: PA - read a privilege capture": "Other",
                                 "enq: PC - update privilege capture info": "Other",
                                 "enq: PC - read privilege capture info": "Other",
                                 "enq: KZ -  contention": "Other",
                                 "enq: DX - contention": "Other",
                                 "enq: DR - contention": "Other",
                                 "pending global transaction(s)": "Other",
                                 "free global transaction table entry": "Other",
                                 "library cache revalidation": "Other",
                                 "library cache shutdown": "Other",
                                 "BFILE closure": "Other",
                                 "BFILE check if exists": "Other",
                                 "BFILE check if open": "Other",
                                 "BFILE get length": "Other",
                                 "BFILE get name object": "Other",
                                 "BFILE get path object": "Other",
                                 "BFILE open": "Other",
                                 "BFILE internal seek": "Other",
                                 "waiting to get CAS latch": "Other",
                                 "waiting to get RM CAS latch": "Other",
                                 "resmgr:internal state cleanup": "Other",
                                 "xdb schema cache initialization": "Other",
                                 "ASM cluster file access": "Other",
                                 "CSS initialization": "Other",
                                 "CSS group registration": "Other",
                                 "CSS group membership query": "Other",
                                 "CSS operation: data query": "Other",
                                 "CSS operation: data update": "Other",
                                 "CSS Xgrp shared operation": "Other",
                                 "CSS operation: query": "Other",
                                 "CSS operation: action": "Other",
                                 "CSS operation: diagnostic": "Other",
                                 "GIPC operation: dump": "Other",
                                 "GPnP Initialization": "Other",
                                 "GPnP Termination": "Other",
                                 "GPnP Get Item": "Other",
                                 "GPnP Set Item": "Other",
                                 "GPnP Get Error": "Other",
                                 "ADR file lock": "Other",
                                 "ADR block file read": "Other",
                                 "ADR block file write": "Other",
                                 "CRS call completion": "Other",
                                 "dispatcher shutdown": "Other",
                                 "listener registration dump": "Other",
                                 "latch: virtual circuit queues": "Other",
                                 "listen endpoint status": "Other",
                                 "OJVM: Generic": "Other",
                                 "select wait": "Other",
                                 "jobq slave shutdown wait": "Other",
                                 "jobq slave TJ process wait": "Other",
                                 "job scheduler coordinator slave wait": "Other",
                                 "enq: JD - contention": "Other",
                                 "enq: JQ - contention": "Other",
                                 "enq: OD - Serializing DDLs": "Other",
                                 "RAC referential constraint parent lock": "Other",
                                 "RAC: constraint DDL lock": "Other",
                                 "kkshgnc reloop": "Other",
                                 "optimizer stats update retry": "Other",
                                 "wait active processes": "Other",
                                 "SUPLOG PL wait for inflight pragma-d PL/SQL": "Other",
                                 "enq: MD - contention": "Other",
                                 "enq: MS - contention": "Other",
                                 "wait for kkpo ref-partitioning *TEST EVENT*": "Other",
                                 "enq: AP - contention": "Other",
                                 "PX slave connection": "Other",
                                 "PX slave release": "Other",
                                 "PX Send Wait": "Other",
                                 "PX qref latch": "Other",
                                 "PX server shutdown": "Other",
                                 "PX create server": "Other",
                                 "PX signal server": "Other",
                                 "PX Deq Credit: free buffer": "Other",
                                 "PX Deq: Test for msg": "Other",
                                 "PX Deq: Test for credit": "Other",
                                 "PX Deq: Signal ACK RSG": "Other",
                                 "PX Deq: Signal ACK EXT": "Other",
                                 "PX Deq: reap credit": "Other",
                                 "PX Nsq: PQ descriptor query": "Other",
                                 "PX Nsq: PQ load info query": "Other",
                                 "PX Deq Credit: Session Stats": "Other",
                                 "PX Deq: Slave Session Stats": "Other",
                                 "PX Deq: Slave Join Frag": "Other",
                                 "enq: PI - contention": "Other",
                                 "enq: PS - contention": "Other",
                                 "latch: parallel query alloc buffer": "Other",
                                 "kxfxse": "Other",
                                 "kxfxsp": "Other",
                                 "PX Deq: Table Q qref": "Other",
                                 "PX Deq: Table Q Get Keys": "Other",
                                 "PX Deq: Table Q Close": "Other",
                                 "GV$: slave acquisition retry wait time": "Other",
                                 "PX hash elem being inserted": "Other",
                                 "latch: PX hash array latch": "Other",
                                 "enq: AY - contention": "Other",
                                 "enq: TO - contention": "Other",
                                 "enq: IT - contention": "Other",
                                 "enq: BF - allocation contention": "Other",
                                 "enq: BF - PMON Join Filter cleanup": "Other",
                                 "enq: RD - RAC load": "Other",
                                 "enq: KV - key vector creation coordination": "Other",
                                 "timer in sksawat": "Other",
                                 "scginq AST call": "Other",
                                 "kupp process wait": "Other",
                                 "Kupp process shutdown": "Other",
                                 "Data Pump slave startup": "Other",
                                 "Data Pump slave init": "Other",
                                 "enq: KP - contention": "Other",
                                 "Replication Dequeue ": "Other",
                                 "knpc_acwm_AwaitChangedWaterMark": "Other",
                                 "knpc_anq_AwaitNonemptyQueue": "Other",
                                 "knpsmai": "Other",
                                 "enq: SR - contention": "Other",
                                 "REPL Capture/Apply: database startup": "Other",
                                 "REPL Capture/Apply: miscellaneous": "Other",
                                 "enq: SI - contention": "Other",
                                 "REPL Capture/Apply: RAC inter-instance ack": "Other",
                                 "enq: IA - contention": "Other",
                                 "enq: JI - contention": "Other",
                                 "qerex_gdml": "Other",
                                 "enq: AT - contention": "Other",
                                 "opishd": "Other",
                                 "kpodplck wait before retrying ORA-54": "Other",
                                 "enq: CQ - contention": "Other",
                                 "wait for EMON to spawn": "Other",
                                 "EMON termination": "Other",
                                 "Emon coordinator startup": "Other",
                                 "enq: SE - contention": "Other",
                                 "tsm with timeout": "Other",
                                 "Streams AQ: waiting for busy instance for instance_name": "Other",
                                 "enq: TQ - TM contention": "Other",
                                 "enq: TQ - DDL contention": "Other",
                                 "enq: TQ - INI contention": "Other",
                                 "enq: TQ - DDL-INI contention": "Other",
                                 "enq: TQ - INI sq contention": "Other",
                                 "enq: TQ - MC free sync at cross job start": "Other",
                                 "enq: TQ - MC free sync at cross job stop": "Other",
                                 "enq: TQ - MC free sync at cross job end": "Other",
                                 "enq: TQ - MC free sync at export subshard": "Other",
                                 "enq: TQ -  sq TM contention": "Other",
                                 "AQ reload SO release": "Other",
                                 "enq: RQ - Enqueue commit uncached": "Other",
                                 "enq: RQ - Enqueue commit cached": "Other",
                                 "enq: RQ - Dequeue update scn": "Other",
                                 "enq: RQ - Parallel cross update scn": "Other",
                                 "enq: RQ - Cross update scn": "Other",
                                 "enq: RQ - Trucate subshard": "Other",
                                 "enq: RQ - Cross export subshard": "Other",
                                 "enq: RQ - Cross import subshard": "Other",
                                 "enq: RQ - Free shadow shard": "Other",
                                 "enq: RQ - AQ indexed cached commit": "Other",
                                 "enq: RQ - AQ uncached commit WM update": "Other",
                                 "enq: RQ - AQ uncached dequeue": "Other",
                                 "enq: RQ - AQ Eq Ptn Mapping": "Other",
                                 "enq: RQ - AQ Dq Ptn Mapping": "Other",
                                 "enq: RQ - AQ Trnc mem free": "Other",
                                 "enq: RQ - AQ Trnc mem free remote": "Other",
                                 "enq: RQ - AQ Trnc mem free by LB": "Other",
                                 "enq: RQ - AQ Trnc mem free by CP": "Other",
                                 "enq: RQ - AQ Enq commit incarnation wrap": "Other",
                                 "enq: RQ - AQ Rule evaluation segment load": "Other",
                                 "AQ propagation connection": "Other",
                                 "enq: DP - contention": "Other",
                                 "enq: MH - contention": "Other",
                                 "enq: ML - contention": "Other",
                                 "enq: PH - contention": "Other",
                                 "enq: SF - contention": "Other",
                                 "enq: XH - contention": "Other",
                                 "enq: WA - contention": "Other",
                                 "Streams AQ: QueueTable kgl locks": "Other",
                                 "AQ spill debug idle": "Other",
                                 "AQ master shutdown": "Other",
                                 "AQPC: new master": "Other",
                                 "AQ Background Master: slave start": "Other",
                                 "enq: AQ - QPT fg map dqpt": "Other",
                                 "enq: AQ - QPT fg map qpt": "Other",
                                 "enq: PQ - QPT add qpt": "Other",
                                 "enq: PQ - QPT drop qpt": "Other",
                                 "enq: PQ - QPT add dqpt": "Other",
                                 "enq: PQ - QPT drop dqpt": "Other",
                                 "enq: PQ - QPT add qpt fg": "Other",
                                 "enq: PQ - QPT add dqpt fg": "Other",
                                 "enq: PQ - QPT Trunc": "Other",
                                 "enq: PQ - QPT LB Trunc sync": "Other",
                                 "enq: PQ - QPT XSTART Trunc sync": "Other",
                                 "AQ master: time mgmt/task cleanup": "Other",
                                 "AQ slave: time mgmt/task cleanup": "Other",
                                 "enq: BA - SUBBMAP contention": "Other",
                                 "AQ:non durable subscriber add or drop": "Other",
                                 "enq: CX - TEXT: Index Specific Lock": "Other",
                                 "enq: OT - TEXT: Generic Lock": "Other",
                                 "XDB SGA initialization": "Other",
                                 "enq: XC - XDB Configuration": "Other",
                                 "NFS read delegation outstanding": "Other",
                                 "Data Guard Broker Wait": "Other",
                                 "enq: RF - synch: DG Broker metadata": "Other",
                                 "enq: RF - atomicity": "Other",
                                 "enq: RF - synchronization: aifo master": "Other",
                                 "enq: RF - new AI": "Other",
                                 "enq: RF - synchronization: critical ai": "Other",
                                 "enq: RF - RF - Database Automatic Disable": "Other",
                                 "enq: RF - FSFO Observer Heartbeat": "Other",
                                 "enq: RF - DG Broker Current File ID": "Other",
                                 "enq: RF - FSFO Primary Shutdown suspended": "Other",
                                 "enq: RF - Broker State Lock": "Other",
                                 "enq: RF - FSFO string buffer": "Other",
                                 "PX Deq: OLAP Update Reply": "Other",
                                 "PX Deq: OLAP Update Execute": "Other",
                                 "PX Deq: OLAP Update Close": "Other",
                                 "OLAP Parallel Type Deq": "Other",
                                 "OLAP Parallel Temp Grow Request": "Other",
                                 "OLAP Parallel Temp Grow Wait": "Other",
                                 "OLAP Parallel Temp Grew": "Other",
                                 "OLAP Null PQ Reason": "Other",
                                 "OLAP Aggregate Master Enq": "Other",
                                 "OLAP Aggregate Client Enq": "Other",
                                 "OLAP Aggregate Master Deq": "Other",
                                 "OLAP Aggregate Client Deq": "Other",
                                 "enq: AW - AW$ table lock": "Other",
                                 "enq: AW - AW state lock": "Other",
                                 "enq: AW - user access for AW": "Other",
                                 "enq: AW - AW generation lock": "Other",
                                 "enq: AG - contention": "Other",
                                 "enq: AO - contention": "Other",
                                 "enq: OQ - xsoqhiAlloc": "Other",
                                 "enq: OQ - xsoqhiFlush": "Other",
                                 "enq: OQ - xsoq*histrecb": "Other",
                                 "enq: OQ - xsoqhiClose": "Other",
                                 "enq: OQ - xsoqhistrecb": "Other",
                                 "enq: IZ -  contention": "Other",
                                 "enq: AM - client registration": "Other",
                                 "enq: AM - shutdown": "Other",
                                 "enq: AM - rollback COD reservation": "Other",
                                 "enq: AM - background COD reservation": "Other",
                                 "enq: AM - ASM cache freeze": "Other",
                                 "enq: AM - ASM ACD Relocation": "Other",
                                 "enq: AM - group use": "Other",
                                 "enq: AM - group block": "Other",
                                 "enq: AM - ASM File Destroy": "Other",
                                 "enq: AM - ASM User": "Other",
                                 "enq: AM - ASM Password File Update": "Other",
                                 "enq: AM - ASM Amdu Dump": "Other",
                                 "enq: AM - disk offline": "Other",
                                 "enq: AM - ASM reserved": "Other",
                                 "enq: AM - block repair": "Other",
                                 "enq: AM - ASM disk based alloc/dealloc": "Other",
                                 "enq: AM - ASM file descriptor": "Other",
                                 "enq: AM - ASM file relocation": "Other",
                                 "enq: AM - ASM SR relocation": "Other",
                                 "enq: AM - ASM Grow ACD": "Other",
                                 "enq: AM - ASM DD update SrRloc": "Other",
                                 "enq: AM - ASM file chown": "Other",
                                 "enq: AM - Register with IOServer": "Other",
                                 "enq: AM - ASM metadata replication": "Other",
                                 "enq: AM - SR slice Clear/Mark": "Other",
                                 "enq: AM - Enable Remote ASM": "Other",
                                 "enq: AM - Disable Remote ASM": "Other",
                                 "enq: AM - Credential creation": "Other",
                                 "enq: AM - Credential deletion": "Other",
                                 "enq: AM - ASM file access req": "Other",
                                 "enq: AM - ASM client operation": "Other",
                                 "enq: AM - ASM client check": "Other",
                                 "enq: AM - ASM ATB COD creation": "Other",
                                 "enq: AM - Create default DG key in OCR": "Other",
                                 "enq: AM - ASM Audit file Delete": "Other",
                                 "enq: AM - ASM Audit file Cleanup": "Other",
                                 "enq: AM - ASM VAT migration": "Other",
                                 "enq: AM - Update SR nomark flag": "Other",
                                 "enq: AM - ASM VAL cache": "Other",
                                 "enq: AM - ASM SR Segment Reuse": "Other",
                                 "ASM internal hang test": "Other",
                                 "ASM Instance startup": "Other",
                                 "buffer busy": "Other",
                                 "buffer freelistbusy": "Other",
                                 "buffer rememberlist busy": "Other",
                                 "buffer writeList full": "Other",
                                 "no free buffers": "Other",
                                 "buffer write wait": "Other",
                                 "buffer invalidation wait": "Other",
                                 "buffer dirty disabled": "Other",
                                 "ASM metadata cache frozen": "Other",
                                 "enq: FZ -  contention": "Other",
                                 "enq: CM - gate": "Other",
                                 "enq: CM - instance": "Other",
                                 "enq: CM - diskgroup dismount": "Other",
                                 "enq: XQ - recovery": "Other",
                                 "enq: XQ - relocation": "Other",
                                 "enq: XQ - purification": "Other",
                                 "enq: AD - allocate AU": "Other",
                                 "enq: AD - deallocate AU": "Other",
                                 "enq: AD - relocate AU": "Other",
                                 "enq: DO - disk online": "Other",
                                 "enq: DO - disk online recovery": "Other",
                                 "enq: DO - Staleness Registry create": "Other",
                                 "enq: DO - startup of MARK process": "Other",
                                 "extent map load/unlock": "Other",
                                 "enq: XL - fault extent map": "Other",
                                 "Sync ASM rebalance": "Other",
                                 "Sync ASM discovery": "Other",
                                 "enq: DG - contention": "Other",
                                 "enq: DD - contention": "Other",
                                 "enq: HD - contention": "Other",
                                 "enq: DQ -  contention": "Other",
                                 "enq: DN - contention": "Other",
                                 "Cluster stabilization wait": "Other",
                                 "Cluster Suspension wait": "Other",
                                 "ASM background starting": "Other",
                                 "ASM db client exists": "Other",
                                 "ASM file metadata operation": "Other",
                                 "ASM network foreground exits": "Other",
                                 "enq: XB -  contention": "Other",
                                 "enq: FA - access file": "Other",
                                 "enq: RX - relocate extent": "Other",
                                 "enq: RX - unlock extent": "Other",
                                 "enq: AR -  contention": "Other",
                                 "enq: AH -  contention": "Other",
                                 "log write(odd)": "Other",
                                 "log write(even)": "Other",
                                 "checkpoint advanced": "Other",
                                 "enq: FR - contention": "Other",
                                 "enq: FR - use the thread": "Other",
                                 "enq: FR - recover the thread": "Other",
                                 "enq: FG - serialize ACD relocate": "Other",
                                 "enq: FG - FG redo generation enq race": "Other",
                                 "enq: FG - LGWR redo generation enq race": "Other",
                                 "enq: FT - allow LGWR writes": "Other",
                                 "enq: FT - disable LGWR writes": "Other",
                                 "enq: FC - open an ACD thread": "Other",
                                 "enq: FC - recover an ACD thread": "Other",
                                 "enq: FX - issue ACD Xtnt Relocation CIC": "Other",
                                 "rollback operations block full": "Other",
                                 "rollback operations active": "Other",
                                 "enq: RB - contention": "Other",
                                 "ASM: MARK subscribe to msg channel": "Other",
                                 "ASM: Send msg to MARK": "Other",
                                 "call": "Other",
                                 "enq: IC - IOServer clientID": "Other",
                                 "enq: IF - file open": "Other",
                                 "enq: IF - file close": "Other",
                                 "enq: PT - contention": "Other",
                                 "enq: PT - ASM Storage May Split": "Other",
                                 "enq: PM -  contention": "Other",
                                 "ASM PST operation": "Other",
                                 "global cache busy": "Other",
                                 "lock release pending": "Other",
                                 "dma prepare busy": "Other",
                                 "GCS lock cancel": "Other",
                                 "GCS lock open S": "Other",
                                 "GCS lock open X": "Other",
                                 "GCS lock open": "Other",
                                 "GCS lock cvt S": "Other",
                                 "GCS lock cvt X": "Other",
                                 "GCS lock esc X": "Other",
                                 "GCS lock esc": "Other",
                                 "GCS recovery lock open": "Other",
                                 "GCS recovery lock convert": "Other",
                                 "kfcl: instance recovery": "Other",
                                 "no free locks": "Other",
                                 "lock close": "Other",
                                 "enq: KE -  contention": "Other",
                                 "enq: KQ - access ASM attribute": "Other",
                                 "ASM Volume Background": "Other",
                                 "ASM volume directive send": "Other",
                                 "ASM Volume Resource Action": "Other",
                                 "enq: AV - persistent DG number": "Other",
                                 "enq: AV - volume relocate": "Other",
                                 "enq: AV - AVD client registration": "Other",
                                 "enq: AV - add/enable first volume in DG": "Other",
                                 "ASM: OFS Cluster membership update": "Other",
                                 "ASM Scrubbing I/O": "Other",
                                 "enq: WF - contention": "Other",
                                 "enq: WT - contention": "Other",
                                 "enq: WP - contention": "Other",
                                 "enq: FU - contention": "Other",
                                 "enq: MW - contention": "Other",
                                 "AWR Flush": "Other",
                                 "AWR Metric Capture": "Other",
                                 "enq: TB - SQL Tuning Base Cache Update": "Other",
                                 "enq: TB - SQL Tuning Base Cache Load": "Other",
                                 "enq: SH - contention": "Other",
                                 "enq: AF - task serialization": "Other",
                                 "MMON slave messages": "Other",
                                 "MMON (Lite) shutdown": "Other",
                                 "enq: MO - contention": "Other",
                                 "enq: TL - contention": "Other",
                                 "enq: TH - metric threshold evaluation": "Other",
                                 "enq: TK - Auto Task Serialization": "Other",
                                 "enq: TK - Auto Task Slave Lockout": "Other",
                                 "enq: RR - contention": "Other",
                                 "WCR: RAC message context busy": "Other",
                                 "WCR: capture file IO write": "Other",
                                 "WCR: Sync context busy": "Other",
                                 "latch: WCR: sync": "Other",
                                 "latch: WCR: processes HT": "Other",
                                 "enq: RA - RT ADDM flood control": "Other",
                                 "enq: JS - contention": "Other",
                                 "enq: JS - job run lock - synchronize": "Other",
                                 "enq: JS - job recov lock": "Other",
                                 "enq: JS - queue lock": "Other",
                                 "enq: JS - sch locl enqs": "Other",
                                 "enq: JS - q mem clnup lck": "Other",
                                 "enq: JS - evtsub add": "Other",
                                 "enq: JS - evtsub drop": "Other",
                                 "enq: JS - wdw op": "Other",
                                 "enq: JS - evt notify": "Other",
                                 "enq: JS - aq sync": "Other",
                                 "enq: XD - ASM disk drop/add": "Other",
                                 "enq: XD - ASM disk ONLINE": "Other",
                                 "enq: XD - ASM disk OFFLINE": "Other",
                                 "cell worker online completion": "Other",
                                 "cell worker retry ": "Other",
                                 "cell manager cancel work request": "Other",
                                 "opening cell offload device": "Other",
                                 "ioctl to cell offload device": "Other",
                                 "reap block level offload operations": "Other",
                                 "CDB: Per Instance Query for PDB Info": "Other",
                                 "enq: PB - PDB Lock": "Other",
                                 "secondary event": "Other"}

        self.load_profile_sec = ["DB Time", "DB CPU"]
        self.load_profile_mb = ["Redo size", "Read IO", "Write IO", "SQL Work Area"]
        self.load_profile_blk = ["Logical read", "Physical read", "Physical write", "Block changes"]
        self.load_profile_num = ["Read IO requests", "Write IO requests", "User calls", "Parses",
                                 "Hard parses", "Logons", "Executes", "Rollbacks", "Transactions", "Sessions (Begin)",
                                 "Sessions (End)"]

        self.load_profile_elems = self.load_profile_sec + \
                                  self.load_profile_mb + self.load_profile_blk + self.load_profile_num


    def get_class_name(self, event_name_short):
        for event_name in self.event_class_name:
            if event_name.startswith(event_name_short):
                # if event_name_short == "db flash cache single bloc":
                #     print(event_name, self.event_class_name[event_name])
                return self.event_class_name[event_name]

        return "NONE"

    def is_float(self, val):
        try:
            x = float(val.replace(",", ""))
            return True
        except:
            return False

    def plot(self):

        snap_data = {}
        snap_data_profile = {}
        snap_data_cpu = {}
        snap_data_sql_ela = {}
        snap_data_inst_stats = {}
        snap_data_time_model = {}
        sql_ids = {}
        snap_data_io_avg = {}


        for fname in os.listdir(self.dirname):
            if fname.endswith("txt") and fname.find(self.name_pattern) >= 0:
                try:
                    report_file = open(self.dirname + "/" + fname, "r").readlines()
                except Exception as e:
                    print(fname, str(e))
                    raise
                wait_class_section = False
                load_profile_section = False
                host_cpu_section = False
                top_sql_ela = False
                top_sql_ela_ignore = False
                time_model_section = False
                instance_stats_section = False

                event_class_wait_sum = {}
                db_version = "12"
                line_of_db_version = 6
                line_no = 0
                section_line = 0
                profile_pos = 0
                for report_line in report_file:
                    line_no += 1
                    try:
                        report_line_words = report_line.split()
                        report_line_long_words = re.split("\s{2,}", report_line)
                        section_line += 1

                        if line_no == 2 and report_line.find("WARNING") >= 0:
                            line_of_db_version = 10

                        elif line_no == line_of_db_version:
                            db_version = report_line_words[6]
                            if db_version < "11.2.0.4.0":
                                self.load_profile_blk = ["Logical reads", "Physical reads", "Physical writes",
                                                         "Block changes"]
                                self.load_profile_elems = self.load_profile_sec + self.load_profile_mb + \
                                                          self.load_profile_blk + self.load_profile_num

                        elif report_line.find("Begin Snap:") >= 0:
                            date = report_line.split()[3] + " " + report_line.split()[4]
                            date = datetime.strptime(date, "%d-%b-%y %H:%M:%S").strftime("%Y%m%d:%H:%M")
                            date = date + " (" + report_line.split()[2] + ")"
                            snap_data[date] = {}
                            snap_data_profile[date] = {}
                            snap_data_cpu[date] = {}
                            snap_data_sql_ela[date] = {}
                            snap_data_io_avg[date] = {}

                            snap_data_inst_stats[date] = {}
                            snap_data_inst_stats[date]["temp space allocated (bytes)"] = 0
                            snap_data_inst_stats[date]["index fast full scans (direct re"] = 0
                            snap_data_inst_stats[date]["index fast full scans (full)"] = 0
                            snap_data_inst_stats[date]["index fetch by key"] = 0
                            snap_data_inst_stats[date]["index scans kdiixs"] = 0
                            snap_data_inst_stats[date]["sorts (disk)"] = 0
                            snap_data_inst_stats[date]["table fetch by rowid"] = 0
                            snap_data_inst_stats[date]["table scans (direct read)"] = 0
                            snap_data_inst_stats[date]["table scans (long tables)"] = 0
                            snap_data_inst_stats[date]["table scans (short tables)"] = 0
                            snap_data_inst_stats[date]["queries parallelized"] = 0
                            snap_data_inst_stats[date]["cell scans"] = 0

                            snap_data_time_model[date] = {}
                            snap_data_time_model[date]["parse time elapsed"] = 0
                            snap_data_time_model[date]["sql execute elapsed time"] = 0
                            snap_data_time_model[date]["hard parse elapsed time"] = 0
                            snap_data_time_model[date]["failed parse elapsed time"] = 0
                            snap_data_time_model[date]["connection management call elapsed time"] = 0
                            snap_data_time_model[date]["hard parse (sharing criteria) elapsed time"] = 0
                            snap_data_time_model[date]["PL/SQL execution elapsed time"] = 0
                            snap_data_time_model[date]["PL/SQL compilation elapsed time"] = 0
                            snap_data_time_model[date]["sequence load elapsed time"] = 0
                            snap_data_time_model[date]["hard parse (bind mismatch) elapsed time"] = 0
                            snap_data_time_model[date]["Java execution elapsed time"] = 0
                            snap_data_time_model[date]["DB time"] = 0

                            snap_data_profile[date]["Sessions (Begin)"] = int(report_line_words[5].replace(",", ""))

                        elif not time_model_section and (report_line.startswith("Time Model") or report_line[1:].startswith("Time Model")):
                            time_model_section = True

                        elif not instance_stats_section and (report_line.startswith("Instance Activity Stats") or report_line[1:].startswith("Instance Activity Stats")):
                            instance_stats_section = True

                        elif time_model_section and (report_line.startswith("Foreground Wait Events") or report_line[1:].startswith("Foreground Wait Events")):
                            time_model_section = False
                            wait_class_section = True

                        elif instance_stats_section and (report_line.startswith("IOStat") or report_line.startswith("IO Stat")):
                            instance_stats_section = False

                        elif time_model_section:
                            for tm in snap_data_time_model[date]:
                                if report_line.startswith(tm):
                                    tm_words = len(tm.split())
                                    snap_data_time_model[date][tm] = float(report_line_words[tm_words].replace(",", ""))

                        elif instance_stats_section:
                            for ist in snap_data_inst_stats[date]:
                                if report_line.startswith(ist):
                                    ist_words = len(ist.split())
                                    snap_data_inst_stats[date][ist] = float(report_line_words[ist_words+1].replace(",", ""))

                        elif report_line.find("End Snap:") >= 0:
                            snap_data_profile[date]["Sessions (End)"] = int(report_line_words[5].replace(",", ""))

                        elif report_line.startswith("Load Profile"):
                            load_profile_section = True

                        elif db_version >= "11.2.0.4.0" and report_line.startswith("Wait Classes by Total Wait Time"):
                            wait_class_section = True

                        elif db_version < "11.2.0.4.0" and report_line.find("Foreground Wait Events") >= 0:
                            wait_class_section = True

                        elif report_line.find("Host CPU") >= 0:
                            host_cpu_section = True
                            if db_version >= "11.2.0.4.0":
                                wait_class_section = False
                            else:
                                self.cpu_count = report_line_words[3]

                            for class_name in self.event_classes:
                                if snap_data[date].get(class_name, -1) == -1:
                                    snap_data[date][class_name] = 0

                        elif db_version >= "11.2.0.4.0" and host_cpu_section and len(report_line_long_words) > 8 and \
                                self.is_float(report_line_long_words[1]):
                            if len(report_line_long_words) == 10:
                                snap_data_cpu[date]["User"] = float(report_line_long_words[6])
                                snap_data_cpu[date]["System"] = float(report_line_long_words[7])
                                snap_data_cpu[date]["WIO"] = float(report_line_long_words[8])
                                self.cpu_count = report_line_long_words[1]
                            else:
                                snap_data_cpu[date]["User"] = float(report_line_long_words[5])
                                snap_data_cpu[date]["System"] = float(report_line_long_words[6])
                                snap_data_cpu[date]["WIO"] = float(report_line_long_words[7])

                            host_cpu_section = False

                        elif db_version < "11.2.0.4.0" and host_cpu_section and len(report_line_long_words) > 5 and \
                                self.is_float(report_line_long_words[1]):
                            snap_data_cpu[date]["User"] = float(report_line_long_words[3])
                            snap_data_cpu[date]["System"] = float(report_line_long_words[4])
                            snap_data_cpu[date]["WIO"] = float(report_line_long_words[5])

                            host_cpu_section = False

                        elif load_profile_section and len(report_line_long_words) > 2:
                            profile_pos += 1
                            if profile_pos >= 2:
                                load_elem = report_line.split(':')[0].split('(')[0].strip()
                                load_val = report_line.split(':')[1].split()[0].replace(",", "")
                                if load_elem in self.load_profile_elems:
                                    if load_elem.startswith("Redo size"):
                                        snap_data_profile[date][load_elem] = round(float(load_val) / 1024 / 1024, 2)
                                    else:
                                        snap_data_profile[date][load_elem] = float(load_val)

                        elif report_line.startswith("Instance Efficiency"):
                            load_profile_section = False
                            profile_pos = 0

                        elif db_version >= "11.2.0.4.0" and len(report_line_words) > 2 \
                                and (report_line_words[0] + " " + report_line_words[1] in self.event_classes) \
                                and wait_class_section \
                                and report_line.startswith(report_line_words[0]):

                            snap_data[date][report_line_words[0] + " " + report_line_words[1]] = \
                                float(report_line_words[3].replace(",", ""))

                            if report_line.startswith("User I/O"):
                                avg_value = 0
                                if report_line_words[4].find("ms") > 0:
                                    avg_value = float(report_line_words[4].replace(",", "").strip("ms"))
                                elif report_line_words[4].find("us") > 0:
                                    avg_value = float(report_line_words[4].replace(",", "").strip("us")) / 1000
                                else:
                                    avg_value = float(report_line_words[4].replace(",", ""))

                                snap_data_io_avg[date]["User I/O (avg ms)"] = avg_value

                        elif db_version >= "11.2.0.4.0" and len(report_line_words) > 2 \
                             and (report_line_words[0] in self.event_classes) \
                             and wait_class_section \
                             and report_line.startswith(report_line_words[0]):

                            snap_data[date][report_line_words[0]] = float(report_line_words[2].replace(",", ""))

                        elif db_version < "11.2.0.4.0" and wait_class_section and len(report_line_long_words) >= 5 \
                                and self.is_float(report_line_long_words[3]):
                            class_name = self.get_class_name(report_line_long_words[0])

                            if class_name not in ("NONE", "Other", "Idle"):
                                if event_class_wait_sum.get(class_name, -1) >= 0:
                                    event_class_wait_sum[class_name] += float(report_line_long_words[3].replace("," ,""))
                                else:
                                    event_class_wait_sum[class_name] = float(report_line_long_words[3].replace(",", ""))

                        elif db_version < "11.2.0.4.0" and report_line.find("Wait Event Histogram") >= 0 \
                                and wait_class_section:
                            wait_class_section = False

                            for class_name in self.event_classes:
                                snap_data[date][class_name] = event_class_wait_sum.get(class_name, 0)

                        elif report_line.find("SQL ordered by Elapsed Time") >= 0 and not top_sql_ela_ignore:
                            top_sql_ela = True

                        elif top_sql_ela and len(report_line_words) == 7 and len(report_line_words[6]) == 13 \
                                and report_line_words[6][0] != '-' and self.is_float(report_line_words[0]):

                            snap_data_sql_ela[date][report_line_words[6]] = float(report_line_words[0].replace(",", ""))
                            if sql_ids.get(report_line_words[6]) is None:
                                sql_ids[report_line_words[6]] = float(report_line_words[0].replace(",", ""))
                            else:
                                sql_ids[report_line_words[6]] += float(report_line_words[0].replace(",", ""))

                        elif top_sql_ela:
                            if report_line.find("SQL ordered by") >= 0 and top_sql_ela:
                                top_sql_ela = False
                                top_sql_ela_ignore = True

                    except BaseException as e:
                        print(e)
                        print(report_line)
                        print(fname)
                        print("version = " + db_version)
                        raise

        data_x = sorted(snap_data.keys())
        data_y = {}
        data_y_profile_sec = {}
        data_y_profile_mb = {}
        data_y_profile_blk = {}
        data_y_profile_num = {}
        data_y_cpu = {}
        data_y_sql_ela = {}
        data_y_inst_stats = {}
        data_y_time_model = {}
        data_y_io_avg = {}

        sql_ela_ns = []
        for sqlid in sql_ids:
            sql_ela_ns.append([sql_ids[sqlid], sqlid])

        sql_ela_s = sorted(sql_ela_ns)
        sql_ela_top = sql_ela_s[-20:]
        # sql_ela_top = sql_ela_s
        sql_ela_top_dict = {}
        for se in sql_ela_top:
            sql_ela_top_dict[se[1]] = se[0]

        for i in snap_data_sql_ela:
            for sqlid in sql_ids:
                if snap_data_sql_ela[i].get(sqlid) is None:
                    snap_data_sql_ela[i][sqlid] = 0
                if sqlid not in sql_ela_top_dict:
                    del snap_data_sql_ela[i][sqlid]

        for i in data_x:
            for j in snap_data_profile[i]:
                if j in self.load_profile_sec:
                    data_y_profile_sec.setdefault(j, [])
                    data_y_profile_sec[j].append(snap_data_profile[i][j])
                elif j in self.load_profile_mb:
                    data_y_profile_mb.setdefault(j, [])
                    data_y_profile_mb[j].append(snap_data_profile[i][j])
                elif j in self.load_profile_blk:
                    data_y_profile_blk.setdefault(j, [])
                    data_y_profile_blk[j].append(snap_data_profile[i][j])
                elif j in self.load_profile_num:
                    data_y_profile_num.setdefault(j, [])
                    data_y_profile_num[j].append(snap_data_profile[i][j])

            for j in snap_data[i]:
                data_y.setdefault(j, [])
                data_y[j].append(snap_data[i][j])

            for j in snap_data_cpu[i]:
                data_y_cpu.setdefault(j, [])
                data_y_cpu[j].append(snap_data_cpu[i][j])

            for j in snap_data_sql_ela[i]:
                data_y_sql_ela.setdefault(j, [])
                data_y_sql_ela[j].append(snap_data_sql_ela[i][j])

            for j in snap_data_inst_stats[i]:
                data_y_inst_stats.setdefault(j, [])
                data_y_inst_stats[j].append(snap_data_inst_stats[i][j])

            for j in snap_data_time_model[i]:
                data_y_time_model.setdefault(j, [])
                data_y_time_model[j].append(snap_data_time_model[i][j])

            for j in snap_data_io_avg[i]:
                data_y_io_avg.setdefault(j, [])
                data_y_io_avg[j].append(snap_data_io_avg[i][j])

        if self.scale:
            for series in data_y:
                for x in range(len(data_y[series])):
                    # print(series, x, round(data_y[series][x],2), data_y_profile_sec["DB Time"][x])
                    data_y[series][x] = data_y[series][x] / data_y_profile_sec["DB Time"][x]

        if self.param == 'FULL':

            fig = make_subplots(rows=10, cols=1, shared_xaxes=True, subplot_titles=("Wait Event Class & DB Time (sec)",
                                                                                   "Load Profile (DB/CPU)",
                                                                                   "TOP SQL by Elapsed time",
                                                                                   "Time Model",
                                                "I/O Requests, Calls, Parses, Logons, SQL Executes, Rollbacks, Transactions, Sessions",
                                                "Host CPU Average Load",
                                                "Instance stats / s",
                                                "Load Profile (I/O R/W, Redo, SQL Workarea)",
                                                "Logical/Physical Reads/Writes, Block changes",
                                                "AVG User I/O (ms)"
                                                ))

            fig['layout']['yaxis1'].update(title='sec')
            fig['layout']['yaxis2'].update(title='sec/s')
            fig['layout']['yaxis3'].update(title='sec')
            fig['layout']['yaxis4'].update(title='sec')
            fig['layout']['yaxis5'].update(title='#/s')
            fig['layout']['yaxis6'].update(title='%')
            fig['layout']['yaxis7'].update(title='#/s')
            fig['layout']['yaxis8'].update(title='MB/s')
            fig['layout']['yaxis9'].update(title='#blk/s')
            fig['layout']['yaxis10'].update(title='AVG ms / snap')

            fig['layout'].update(title='AWR ' + data_x[0] + " - " + data_x[-1] + " CPUs: " + str(self.cpu_count))

            for series in data_y:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            #stackgroup='waits',
                                            ), 1, 1)

            for series in data_y_profile_sec:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_sec[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 2, 1)
            for series in data_y_sql_ela:
                fig.add_trace(go.Scatter(x=data_x,
                                            #fill="tozeroy",
                                            y=data_y_sql_ela[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            #visible="legendonly",
                                            ), 3, 1)

            for series in data_y_time_model:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_time_model[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 4, 1)

            for series in data_y_profile_num:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_num[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 5, 1)

            for series in data_y_cpu:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_cpu[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            stackgroup='cpu',
                                            ), 6, 1)

            for series in data_y_inst_stats:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_inst_stats[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 7, 1)

            for series in data_y_profile_mb:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_mb[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 8, 1)

            for series in data_y_profile_blk:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_blk[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 9, 1)

            for series in data_y_io_avg:
                fig.append_trace(go.Scatter(x=data_x,
                                            #fill="tozeroy",
                                            y=data_y_io_avg[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 10, 1)



            #fig.update_xaxes(showticklabels=False)
            fig.update_layout(height=1500)

        elif self.param == 'SQL':
            fig = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=("Wait Event Class & DB Time (sec)",
                                                                                   "Load Profile (DB/CPU)",
                                                                                   "TOP SQL Ela (sec)"
                                                                                   "SQL box plots"
                                                                                   ))

            fig['layout']['yaxis1'].update(title='sec')
            fig['layout']['yaxis2'].update(title='sec/s')
            fig['layout']['yaxis3'].update(title='sec')

            fig['layout'].update(title='AWR ' + data_x[0] + " - " + data_x[-1] + " CPUs: " + str(self.cpu_count))

            for series in data_y:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            #stackgroup='waits',
                                            ), 1, 1)

            for series in data_y_profile_sec:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_sec[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 2, 1)

            for series in data_y_sql_ela:
                fig.add_trace(go.Scatter(x=data_x,
                                            #fill="tozeroy",
                                            y=data_y_sql_ela[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            #visible="legendonly",
                                            ), 3, 1)


        elif self.param == 'IO':

            fig = make_subplots(rows=8, cols=1, shared_xaxes=True, subplot_titles=("Wait Event Class & DB Time (sec)",
                                                                                   "Load Profile (DB/CPU)",
                                                                                   "AVG User I/O (ms)",
                                                "I/O Requests, Calls, Parses, Logons, SQL Executes, Rollbacks, Transactions, Sessions",
                                                "Host CPU Average Load",
                                                "Instance stats / s",
                                                "Load Profile (I/O R/W, Redo, SQL Workarea)",
                                                "Logical/Physical Reads/Writes, Block changes"
                                                ))

            fig['layout']['yaxis1'].update(title='sec')
            fig['layout']['yaxis2'].update(title='sec/s')
            fig['layout']['yaxis3'].update(title='AVG ms / snap')
            fig['layout']['yaxis4'].update(title='#/s')
            fig['layout']['yaxis5'].update(title='%')
            fig['layout']['yaxis6'].update(title='#/s')
            fig['layout']['yaxis7'].update(title='MB/s')
            fig['layout']['yaxis8'].update(title='#blk/s')

            fig['layout'].update(title='AWR ' + data_x[0] + " - " + data_x[-1] + " CPUs: " + str(self.cpu_count))

            for series in data_y:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            #stackgroup='waits',
                                            ), 1, 1)

            for series in data_y_profile_sec:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_sec[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 2, 1)

            for series in data_y_io_avg:
                fig.append_trace(go.Scatter(x=data_x,
                                            #fill="tozeroy",
                                            y=data_y_io_avg[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 3, 1)

            for series in data_y_profile_num:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_num[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 4, 1)

            for series in data_y_cpu:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_cpu[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            stackgroup='cpu',
                                            ), 5, 1)

            for series in data_y_inst_stats:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_inst_stats[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 6, 1)

            for series in data_y_profile_mb:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_mb[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 7, 1)

            for series in data_y_profile_blk:
                fig.append_trace(go.Scatter(x=data_x,
                                            fill="tozeroy",
                                            y=data_y_profile_blk[series],
                                            name=series,
                                            mode='lines+markers',
                                            line=dict(shape='hv'),
                                            ), 8, 1)



            #fig.update_xaxes(showticklabels=False)
            #fig.update_layout(height=1500)



        py.plot(fig, filename=self.name_pattern + ".html")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        aa = AWRAnalyzer(sys.argv[1], sys.argv[2])
        aa.plot()
    elif len(sys.argv) == 4 and (sys.argv[3] == 'SQL' or sys.argv[3] == 'IO'):
        aa = AWRAnalyzer(sys.argv[1], sys.argv[2], sys.argv[3])
        aa.plot()

    elif len(sys.argv) == 5 and (sys.argv[3] == 'SQL' or sys.argv[3] == 'IO') and sys.argv[4] == 'scale':
        aa = AWRAnalyzer(sys.argv[1], sys.argv[2], sys.argv[3], True)
        aa.plot()

    else:
        print("This script by Kamil Stawiarski (@ora600pl) is to help you with visualizing data from multiple "
              "awr text reports. Special thanks to Piotr Wrzosek (@pewu78) for improving the charting layout")

        print("Usage:")
        print("python awr_analyzer.py /path/to/reports/ pattern_to_filter_reports_by_name {[TRUE] for reporting SQLids with wait class}")
        print("You have to install plotly first [pip install plotly]\n")
        print("Details can be found on this blog: blog.ora-600.pl "
              "and GitHub: https://github.com/ora600pl/statspack_scripts")

