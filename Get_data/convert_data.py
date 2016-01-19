from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import zipfile


def go():
    dbname = 'taxi'
    username = 'jgabor'

#     engine = create_engine('postgresql://%s@localhost/%s'%(username,dbname))
#     print 'ENGINE', engine.url

    # Connect to the database and create a "cursor" object that allows us
    # to issue SQL commands.
    con = None
    con = psycopg2.connect(database = dbname, user = username)
    cur = con.cursor()

    # Create new tables.  If the tables already exist, this won't work!
    create_tables(cur)

    # Define data directory and data files
    dir = "/Volumes/MYPASSPORT/Data/"

    nfiles = 12
    dat_filenames = \
        [('trip_data_'+str(i)+'.csv') for i in range(1,nfiles+1)]
    fare_filenames = \
        [('trip_fare_'+str(i)+'.csv') for i in range(1,nfiles+1)]

    # Loop over the files, processing each into SQL
    for dat_fbase, fare_fbase in zip(dat_filenames, fare_filenames):
        # First deal with 'trip_data' files
        file = dir + dat_fbase
        file_zipped = file + '.zip'
        zz = zipfile.ZipFile(file_zipped)
        fffile = zz.open(dat_fbase)

        # create a new TABLE with 1-line, just to get the column headers
#         taxi_data = pd.read_csv(fffile, nrows=100)
#         taxi_data.to_sql('taxi_data5', engine, if_exists='replace', index=False)

        ### SLOW WAY
#         for data in pd.read_csv(fffile, chunksize=1000000):
#             data.to_sql('taxi_data5', engine, if_exists='append', index=False)
#             print "."

        print "About to issue COPY command for", dat_fbase
        trip_tablename = 'taxi_trips'
        sql_command = "COPY "+trip_tablename+" FROM stdin CSV HEADER NULL '' "
        cur.copy_expert(sql_command, fffile)

#         cur.copy_from(fffile, 'taxi_trips', sep=',', null = '')
        con.commit()  # Commit the changes
        zz.close()
        print "Done reading", dat_fbase

        #---- Now deal with "trip_fare" files
        file = dir + fare_fbase
        file_zipped = file + '.zip'
        zz = zipfile.ZipFile(file_zipped)
        fffile = zz.open(fare_fbase)

        print "About to issue COPY command for", fare_fbase
        fare_tablename = 'taxi_fares'
        sql_command = "COPY "+fare_tablename+" FROM stdin CSV HEADER NULL '' "
        cur.copy_expert(sql_command, fffile)
        con.commit()
        zz.close()
        print "Done reading", fare_fbase

    con.close()
    print "Done!"
    test_data()


#         fare_data = pd.read_csv(zz.open(fare_fbase))  ##, nrows=100)
#         print "Done reading", fare_fbase
        
#         # insert data into database from Python
#         fare_data.to_sql('taxi_fare', engine, if_exists='append', index=False,
#                          chunksize=10000)
        

def test_data():
    """Issue some simple queries to test whether tables exist"""

    print "Testing 2 queries!"

    dbname = 'taxi'
    username = 'jgabor'

#     engine = create_engine('postgresql://%s@localhost/%s'%(username,dbname))
#     print 'ENGINE', engine.url

    # connect to the server to run a test SQL command
    con = None
    con = psycopg2.connect(database = dbname, user = username)

    # query:
    sql_query = "SELECT COUNT(trip_distance) "+\
        " FROM taxi_trips WHERE trip_distance > 10;"
    subdat = pd.read_sql_query(sql_query,con)
    print sql_query
    print subdat.head()

    sql_query = "SELECT COUNT(fare_amount) "+\
        " FROM taxi_fares WHERE fare_amount > 30;"
    subdat = pd.read_sql_query(sql_query,con)
    print sql_query
    print subdat.head()
    con.close()



def create_tables(cursor):
    """Create taxi tables within the SQL database

    cursor is a cursor object which connects to the database.
    """
    command1 = trip_data_schema()
    command2 = fare_data_schema()
    cursor.execute(command1)
    cursor.execute(command2)
    print "Created tables!"
    return


def trip_data_schema(tablename = 'taxi_trips'):
    """Define the schema for taxi trip data"""
    command_create = "CREATE TABLE " + tablename + """(
    medallion             varchar(40),
    hack_license          varchar(40),
    vendor_id             varchar(10),
    rate_code             int,
    store_and_fwd_flag    varchar(3),
    pickup_datetime       timestamp without time zone,
    dropoff_datetime      timestamp without time zone,
    passenger_count       int,
    trip_time_in_secs     int,
    trip_distance         real,
    pickup_longitude      real,
    pickup_latitude       real,
    dropoff_longitude     real,
    dropoff_latitude      real    
    );"""
    return command_create


def fare_data_schema(tablename = 'taxi_fares'):
    """ Define the schema for taxi fare data"""
    command_create = \
        "CREATE TABLE " + tablename + """(
medallion                varchar(40),
hack_license             varchar(40),
vendor_id                varchar(10),
pickup_datetime          timestamp without time zone,
payment_type             varchar(5),
fare_amount              real,
surcharge                 real,
mta_tax                  real,
tip_amount               real,
tolls_amount             real,
total_amount             real    
);"""
    return command_create

