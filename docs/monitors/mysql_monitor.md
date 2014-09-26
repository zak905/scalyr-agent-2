/// DECLARE path=/help/monitors/mysql
/// DECLARE title=MySQL Monitor
/// DECLARE section=help
/// DECLARE subsection=monitors

# MySQL Monitor

This agent monitor plugin records performance and usage data from a MySQL server.

NOTE: the MySQL monitor requires Python 2.6 or higher. (This applies to the server on which the Scalyr Agent
is running, which needn't necessarily be the same machine where the MySQL server is running.) If you need
to monitor MySQL from a machine running an older version of Python, [let us know](mailto:support@scalyr.com).

@class=bg-warning docInfoPanel: An *agent monitor plugin* is a component of the Scalyr Agent. To use a plugin,
simply add it to the ``monitors`` section of the Scalyr Agent configuration file (``/etc/scalyr/agent.json``).
For more information, see [Agent Plugins](/help/scalyr-agent#plugins).


## Sample Configuration

To configure the MySQL monitor plugin, you will need the following information:

- A MySQL username with administrative privileges. The user needs to be able to query the information_schema table,
  as well as assorted global status information.
- The password for that user.

Here is a sample configuration fragment:

    monitors: [
      {
         module:            "scalyr_agent.builtin_monitors.mysql_monitor",
         database_socket:   "default",
         database_username: "USERNAME",
         database_password: "PASSWORD"
      }
    ]

This configuration assumes that MySQL is running on the same server as the Scalyr Agent, and is using the default
MySQL socket. If not, you will need to specify the server's socket file, or hostname (or IP address) and port number;
see Configuration Reference.


## Viewing Data

After adding this plugin to the agent configuration file, wait one minute for data to begin recording. Then 
click the {{menuRef:Dashboards}} menu and select {{menuRef:MySQL}}. (The dashboard may not be listed until
the agent begins sending MySQL data.)

The dashboard shows only some of the data collected by the MySQL monitor plugin. To explore the full range
of data collected, go to the Search page and search for [$monitor = 'mysql_monitor'](/events?filter=$monitor%20%3D%20%27mysql_monitor%27).
This will show all data collected by this plugin, across all servers. You can use the {{menuRef:Refine search by}}
dropdown to narrow your search to specific servers and monitors.

The [View Logs](/help/view) page describes the tools you can use to view and analyze log data.
[Query Language](/help/query-language) lists the operators you can use to select specific metrics and values.
You can also use this data in [Dashboards](/help/dashboards) and [Alerts](/help/alerts).


## Configuration Reference

|||# Option                   ||| Usage
|||# ``module``               ||| Always ``scalyr_agent.builtin_monitors.mysql_monitor ``
|||# ``id``                   ||| Optional. Included in each log message generated by this monitor, as a field named ``instance``. \
                                  Allows you to distinguish between values recorded by different monitors. This is especially \
                                  useful if you are running multiple MySQL instances on a single server; you can monitor each \
                                  instance with a separate mysql_monitor record in the Scalyr Agent configuration.
|||# ``database_username``    ||| Username which the agent uses to connect to MySQL to retrieve monitoring data.
|||# ``database_password``    ||| Password for connecting to MySQL.
|||# ``database_socket``      ||| Location of the socket file for connecting to MySQL, e.g. ``/var/run/mysqld_instance2/mysqld.sock``. \
                                  If MySQL is running on the same server as the Scalyr Agent, you can usually set this to "default".
|||# ``database_hostport``    ||| Hostname (or IP address) and port number of the MySQL server, e.g. ``dbserver:3306``, or simply ``3306`` \
                                  when connecting to the local machine. You should specify one of ``database_socket`` or ``database_hostport``, \
                                  but not both.


## Log Reference

Each event recorded by this plugin will have the following fields:

|||# Field                    ||| Meaning
|||# ``monitor``              ||| Always ``mysql_monitor``
|||# ``instance``             ||| The ``id`` value from the monitor configuration.
|||# ``metric``               ||| The name of a metric being measured, e.g. "mysql.vars"
|||# ``value``                ||| The metric value


### Data Categories
  
This plugin records an extensive array of values, in several categories. The exact list of metrics will vary,
depending on which version of MySQL you are using and how you have configured MySQL.


#### mysql.global

These values are the output of the "SHOW GLOBAL STATUS" query. These are discussed in the MySQL documentation chapter
"Server Status Variables".  To reduce the number of metrics recorded, not all command counts are reported.


|||# Metric name                      ||| Description
|||``mysql.global.aborted_clients``   ||| The number of connections aborted because the client died or didn't close \
                                          the connection properly.  The value is relative to the uptime of the server.
||| ``mysql.global.aborted_connects`` ||| The number of failed connection attempts.  The value is relative to the \
                                          uptime of the server.
||| ``mysql.global.bytes_received``   ||| How much data has been sent to the database from all clients.  The value is \
                                          relative to the uptime of the server.
||| ``mysql.global.bytes_sent``       ||| How much data has been sent from the database to all clients.  The value \
                                          is relative to the uptime of the server.
||| ``mysql.global.com_insert``       ||| The number of ``insert`` commands run against the server
||| ``mysql.global.com_delete``       ||| The number of ``delete`` commands run against the server
||| ``mysql.global.com_replace``      ||| The number of ``replace`` commands run against the server
||| ``mysql.global.com_select``       ||| The number of ``select`` commands run against the server
||| ``mysql.global.connections``      ||| Total number of connection attempts (successful and failed).  The value is \
                                          relative to the uptime of the server.
||| ``mysql.global.key_blocks_unused``||| The total number of keyblocks unused at the time of the monitor check.  A \
                                          high number indicates that the key cache might be large.
||| ``mysql.global.key_blocks_used``  ||| Maximum number of key blocks used at any one point.  Indicates a high water \
                                          mark of the number used.  The value is relative to the uptime of the server.
||| ``mysql.global.max_used_connections``||| High water mark for the total number of connections used at any one time \
                                             since the server was started.
||| ``mysql.global.slow_queries``     ||| The total number of queries over the uptime of the server that exceeded the \
                                          "long_query_time" configuration.


#### mysql.innodb

If MySQL is configured to use the InnoDB storage engine, information about InnoDB usage will be emitted. These are discussed
in the MySQL documentation chapter "SHOW ENGINE INNODB STATUS and the InnoDB Monitors".

|||#Metric name                                    ||| Description
|||``mysql.innodb.oswait_array.reservation_count`` ||| A measure of how actively innodb uses it's internal sync array. \
                                                       Specifically, how frequently slots are allocated.
|||``mysql.innodb.oswait_array.signal_count``      ||| As above, part of the measure of activity of the internal sync \
                                                       array, in this case how frequently threads are signaled using \
                                                       the sync array.
|||``mysql.innodb.locks.spin_waits``               ||| The number of times since server start that a thread tried to a \
                                                       mutex that wasn't available.
|||``mysql.innodb.locks.rounds``                   ||| The number of times since server start that a thread looped \
                                                       through the spin-wait cycle.
|||``mysql.innodb.locks.os_waits``                 ||| The number of times since server start that a thread gave up \
                                                       spin-waiting and went to sleep.
|||``mysql.innodb.history_list_length``            ||| The number of unpurged transactions in the internal undo buffer.\
                                                       It typically increases while transactions with updates are run \
                                                       and will decrease once the internal purge runs.
|||``mysql.innodb.innodb.ibuf.size``               ||| The size of the insert buffer.
|||``mysql.innodb.innodb.ibuf.free_list_len``      ||| The size free list for the insert buffer.
|||``mysql.innodb.innodb.ibuf.seg_size``           ||| The segment size of the insert buffer.
|||``mysql.innodb.innodb.ibuf.inserts``            ||| The total number of inserts since server start into the insert \
                                                       buffer.
|||``mysql.innodb.innodb.ibuf.merged_recs``        ||| The total number of records merged in the insert buffer since \
                                                       server start.
|||``mysql.innodb.innodb.ibuf.merges``             ||| The total number of merges for the insert buffer since \
                                                       server start.   
|||``mysql.innodb.queries_queued``                 ||| The number of queries waiting to be processed.  The value is \
                                                       based on the time the monitor sample is run.
|||``mysql.innodb.opened_read_views``              ||| The number of views into the db, this is "started transactions" \
                                                       which have no current statement actively operating.


#### mysql.process

The result of "SHOW PROCESSLIST". These show the types of commands being run and the number of threads performing each
command. 

|||#Metric name                                    ||| Description
|||``mysql.process.query``                         ||| The number of threads performing a query.
|||``mysql.process.sleep``                         ||| The number of threads sleeping.
||| ...                                            ||| ...
|||``mysql.process.xxx``                           ||| The number of threads in state ``xxx``


#### mysql.vars

These values reflect the current configuration of the MySQL server. They are discussed MySQL documentation chapter titled "Using System Variables".
Currently, the monitor only records two specific variables.

|||#Metric name                  ||| Description
|||``mysql.max_connections``     ||| The maximum number of allowed open connections to server.
|||``mysql.open_files_limit``    ||| The maximum number of allowed open files.
 
#### mysql.slave

If your MySQL instance is configured as a slave, the values from "SHOW SLAVE STATUS" are listed in this category. See the MySQL documentation
chapter "Checking Replication Status".


#### mysql.derived

These are values computed by the MySQL monitor plugin based on raw data collected from MySQL. Most values reflect performance since
the MySQL server was last started.

|||#Metric name                                     ||| Description
|||``mysql.derived.slow_query_percentage``          ||| Measure of what percentage of queries are taking a long time \
                                                        to execute. The value of what defines a "long time" is \
                                                        controlled by the variable "long_query_time" within the MySQL \
                                                        config file (the default as of MySQL 5.0 is 10 seconds). \
                                                        The higher the percentage, the more your server is being kept \
                                                        busy fulfilling requests and the possible higher load on your \
                                                        server. 
|||``mysql.derived.connections_used_percentage``    ||| Measure, as a percentage, of how many of simultaneous \
                                                        connections were used out of the number of connections \
                                                        configured within the MySQL configuration file.  If connections\
                                                        run out, client requests will be blocked.  A high percentage \
                                                        could indicate an application not making efficient use of \
                                                        connections (for instance, not caching an existing connection)\
                                                        or it could indicate more clients connecting than anticipated.
|||``mysql.derived.aborted_connections_percentage`` ||| A percentage of client connection attempts that fail to \
                                                        connect.  Typical reasons include a client doesn't have \
                                                        permission to connect to the database (or invalid password),\
                                                        a corrupt connection packet from the client, or the client \
                                                        is slow in sending it's connect message.  This could \
                                                        indicate something wrong with the clients or possibly even \
                                                        attempts to break into the server.
|||``mysql.derived.aborted_clients_percentage``     ||| A measure of the number of clients that disconnect improperly\ 
                                                        (the don't close the connection).  This could indicate a \
                                                        poorly written client, inactivity on the part of clients, or \
                                                        possibly a problematic connection to the database.
|||``mysql.derived.read_percentage``                ||| Measure of what percentage of database activity is reads. \
                                                        Depending on your configuration, a high read percentage could \
                                                        be expected or might be a problem.  If you have setup read \
                                                        slaves and write masters and the masters show heavy reads, that\
                                                        could indicate a problem.
|||``mysql.derived.write_percentage``               ||| Measure of what percentage of database activity is writes. \ 
                                                        Writes are generally quite costly and could impact read \
                                                        performance.
|||``mysql.derived.query_cache_efficiency``         ||| Measure of what percentage of queries are cached.  A higher \
                                                        percentage means that the query will be more responsive.  \
                                                        A low percentage could indicate that queries aren't used \
                                                        that often or the query cache size is not sufficient to keep \
                                                        the queries that do get made in memory.
|||``mysql.derived.joins_without_indexes``          ||| A count of the number of joins performing table scans that do \
                                                        not use indices as well as the joins that check for key usage \
                                                        after each row.  If this value is greater than 0, it could \
                                                        indicate missing or improper indexes on your tables.
|||``mysql.derived.table_cache_hit_rate``           ||| How efficient is the table cache being used?  If the hit rate \
                                                        is low, then increasing the size of the table cache could be \
                                                        beneficial.  Note, that the larger the table cache, however, \
                                                        the more file descriptors are used by the system.
|||``mysql.derived.open_file_percentage``           ||| Of the allowed number of open files, what percentage of them \
                                                        are open.  The higher the percentage, the more file descriptors\
                                                        MySQL is using and the likelihood of operations being delayed \
                                                        (or failing) if too many files are open.  A solution may be as \
                                                        simple as uping the "open_file_limit" in the MySQL config.
|||``mysql.derived.immediate_table_lock_percentage``||| What percentage of requests to lock a table are granted \
                                                        immediately versus having to wait?  For instance, is another \
                                                        operation locking the table.  If this value is low and there \
                                                        are performance issues, it might be worth considering looking \
                                                        at the table structure or possibly replication.
|||``mysql.derived.thread_cache_hit_rate``          ||| For each connection, a thread is needed.  If this value is low,\
                                                        it indicates that either you have unexpected traffic loads or \
                                                        need to allocate more resources to the thread cache.   
|||``mysql.derived.tmp_disk_table_percentage``      ||| When MySQL needs to create a temp table (for instance due to \
                                                        a join), how many of the tables created need to be written to \
                                                        disk?  A high percentage could indicate that either your \
                                                        database operations are creating temporary tables that are \
                                                        large or you need to increase the space allocated for in \
                                                        memory temp tables.