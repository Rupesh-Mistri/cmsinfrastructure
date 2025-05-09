import MySQLdb  # This is the mysqlclient module
from django.conf import settings
import sys
import os
import datetime
import subprocess

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    message = 'It works!\n'
    return [message.encode()]

def connect_to_mysql():
    print(type(settings.DATABASES['default']['HOST']))
    try:
        connection = MySQLdb.connect(
            host=str(settings.DATABASES['default']['HOST']),
            port=int(settings.DATABASES['default']['PORT']),
            user=str(settings.DATABASES['default']['USER']),
            passwd=str(settings.DATABASES['default']['PASSWORD']),
            db=str(settings.DATABASES['default']['NAME'])
        )
        
        return connection
    except MySQLdb.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_mysql_query(query):
    connection = connect_to_mysql()
    if not connection:
        return {"error": "Unable to connect to the database"}
    
    try:
        cursor = connection.cursor()
        
        # Handle `source` command
        if query.strip().lower().startswith('source'):
            file_path = query.strip().split(' ', 1)[1].strip()  # Extract the file path
            return execute_sql_file(file_path)
        
        # Execute regular SQL queries
        cursor.execute(query)
        if query.strip().lower().startswith(('insert', 'update', 'delete', 'alter', 'create', 'drop', 'truncate')):
            connection.commit()
            return {"message": f"Query executed successfully: {cursor.rowcount} rows affected."}
        elif query.strip().lower().startswith(('select', 'show', 'describe', 'explain')):
            result = cursor.fetchall()
            return {"data": result}
        else:
            return {"message": "Query executed successfully."}

    except MySQLdb.Error as e:
        return {"error": str(e)}

    finally:
        if connection.open:
            cursor.close()
            connection.close()

def execute_sql_file(file_path):
    connection = connect_to_mysql()
    if not connection:
        return {"error": "Unable to connect to the database"}

    try:
        cursor = connection.cursor()
        with open(file_path, 'r') as file:
            sql_commands = file.read().split(';')  # Split commands by semicolon

        for command in sql_commands:
            command = command.strip()
            if command:  # Skip empty commands
                try:
                    cursor.execute(command)
                except MySQLdb.Error as e:
                    print(f"Error executing command: {command}\nError: {e}")
                    return {"error": str(e)}

        connection.commit()
        return {"message": "SQL file executed successfully."}

    except FileNotFoundError:
        return {"error": f"File not found: {file_path}"}
    except Exception as e:
        return {"error": f"Error reading or executing the file: {e}"}

    finally:
        if connection.open:
            cursor.close()
            connection.close()




def backup_mysql_database():
    """
    Backs up the entire MySQL database using mysqldump and saves it with a timestamped name.
    
    :return: A dictionary containing the status or error message.
    """

    try:
        # Define database credentials
        db_user = str(settings.DATABASES['default']['USER'])           # Replace with your MySQL username
        db_password = str(settings.DATABASES['default']['PASSWORD']) # Replace with your MySQL password
        db_name = str(settings.DATABASES['default']['NAME'])     # Replace with your database name

        # Define the backup directory and filename
        
        backup_dir = os.path.join(os.getcwd(), "static", "mysqlbackup")
        os.makedirs(backup_dir, exist_ok=True)  # Ensure the directory exists

        timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
        if settings.LOCAL_ENV==True:     
            backup_file = os.path.join(backup_dir, f"local_backup_{timestamp}.sql")
        else:
            backup_file = os.path.join(backup_dir, f"live_backup_{timestamp}.sql")

        # Construct the mysqldump non interactive command
        dump_command = [
            "mysqldump",
            "-u", db_user,
            f"--password={db_password}",  # Pass the password inline
            db_name,
            "-r", backup_file    # Output file
        ]

        # # Construct the mysqldump interactive cmd
        # dump_command = [
        #     "mysqldump",
        #     "-u", db_user,
        #     f"-p{db_password}",  # No space after -p
        #     db_name,
        #     "-r", backup_file    # Output file
        # ]

        # Execute the mysqldump command
        subprocess.run(dump_command, check=True)

        return {"message": f"Backup saved to {backup_file}"}

    except subprocess.CalledProcessError as e:
        return {"error": f"mysqldump failed: {e}"}

    except Exception as ex:
        return {"error": f"Unexpected error: {ex}"}

# # Example Usage
# result = backup_mysql_database()

# if "error" in result:
#     print("Error:", result["error"])
# else:
#     print("Success:", result["message"])