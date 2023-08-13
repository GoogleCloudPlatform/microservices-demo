**To describe dimension keys**

This example requests the names of all wait events. The data is summarized by event name, and the aggregate values of those events over the specified time period.

Command::

  aws pi describe-dimension-keys --service-type RDS --identifier db-LKCGOBK26374TPTDFXOIWVCPPM --start-time 1527026400 --end-time 1527080400 --metric db.load.avg --group-by '{"Group":"db.wait_event"}'

Output::

  {
      "AlignedEndTime": 1.5270804E9,
      "AlignedStartTime": 1.5270264E9,
      "Keys": [
          {
              "Dimensions": {"db.wait_event.name": "wait/synch/mutex/innodb/aurora_lock_thread_slot_futex"},
              "Total": 0.05906906851195666
          },
          {
              "Dimensions": {"db.wait_event.name": "wait/io/aurora_redo_log_flush"},
              "Total": 0.015824722186149193
          },
          {
              "Dimensions": {"db.wait_event.name": "CPU"},
              "Total": 0.008014396230265477
          },
          {
              "Dimensions": {"db.wait_event.name": "wait/io/aurora_respond_to_client"},
              "Total": 0.0036361612526204477
          },
          {
              "Dimensions": {"db.wait_event.name": "wait/io/table/sql/handler"},
              "Total": 0.0019108398419382965
          },
          {
              "Dimensions": {"db.wait_event.name": "wait/synch/cond/mysys/my_thread_var::suspend"},
              "Total": 8.533847837782684E-4
          },
          {
              "Dimensions": {"db.wait_event.name": "wait/io/file/csv/data"},
              "Total": 6.864181956477376E-4
          },
          {
              "Dimensions": {"db.wait_event.name": "Unknown"},
              "Total": 3.895887056379051E-4
          },
          {
              "Dimensions": {"db.wait_event.name": "wait/synch/mutex/sql/FILE_AS_TABLE::LOCK_shim_lists"},
              "Total": 3.710368625122906E-5
          },
          {
              "Dimensions": {"db.wait_event.name": "wait/lock/table/sql/handler"},
              "Total": 0
          }
      ]
  }
