import os
import subprocess
import sys

def copy_customer_table():
    source_db = os.getenv('SOURCE_DB')
    target_db = os.getenv('TARGET_DB')
    if not source_db or not target_db:
        print('Error: SOURCE_DB and TARGET_DB environment variables must be set.', file=sys.stderr)
        sys.exit(1)
    # Use pg_dump to dump only the customer table schema and data
    dump_cmd = ['pg_dump', '--no-owner', '--no-acl', '--format=plain', '--data-only', '--table=customer', source_db]
    # Pipe dump into psql targeting the target database
    psql_cmd = ['psql', target_db]
    try:
        print('Starting dump from source database...')
        dump_process = subprocess.Popen(dump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        psql_process = subprocess.Popen(psql_cmd, stdin=dump_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dump_process.stdout.close()  # Allow dump_process to receive a SIGPIPE if psql exits.
        out, err = psql_process.communicate()
        if psql_process.returncode != 0:
            print('Error during import to target DB:', err.decode(), file=sys.stderr)
            sys.exit(1)
        print('Copy completed successfully.')
    except FileNotFoundError as e:
        print('Error: pg_dump or psql not found. Ensure PostgreSQL client tools are installed.', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    copy_customer_table()
