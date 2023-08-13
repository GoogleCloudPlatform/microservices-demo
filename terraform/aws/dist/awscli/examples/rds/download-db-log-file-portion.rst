**To download a DB log file**

The following ``download-db-log-file-portion`` example downloads only the latest part of your log file, saving it to a local file named ``tail.txt``. ::

    aws rds download-db-log-file-portion \
        --db-instance-identifier test-instance \
        --log-file-name log.txt \
        --output text > tail.txt

To download the entire file, you need to include the ``--starting-token 0`` parameter. The following example saves the output to a local file named ``full.txt``. ::

    aws rds download-db-log-file-portion \
        --db-instance-identifier test-instance \
        --log-file-name log.txt \
        --starting-token 0 \
        --output text > full.txt

The saved file might contain blank lines.  They appear at the end of each part of the log file while being downloaded.  This generally doesn't cause any trouble in your log file analysis.
