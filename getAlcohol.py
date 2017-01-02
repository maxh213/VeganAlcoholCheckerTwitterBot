import psycopg2
import secretConstants

connectionString = (
    'dbname=' + secretConstants.DATABASE_NAME + 
    ' user=' + secretConstants.DATABASE_USER + 
    ' host=' + secretConstants.DATABASE_HOST + 
    ' password=' + secretConstants.DATABASE_PASSWORD +
    ' port=' + secretConstants.DATABASE_PORT
)
conn = None
result = None

def getAlcoholByName(name):
    name = fixTypingErrors(name)
    name = "%" + name + "%"
    QUERY = (
        "SELECT barnivore_product_name, barnivore_status, barnivore_country " + 
        "FROM barnivore_product " +
        "WHERE lower(barnivore_product_name) like lower(%s)"
    )
        
    try:
        conn = psycopg2.connect(connectionString)
        cur = conn.cursor()
        cur.execute(QUERY, (name,))
        result = cur.fetchall()

    except psycopg2.DatabaseError as e:
        print('Error %s' % e)    

    finally:
        if conn:
            conn.close()

    return result

def get_random_alcohol_info_for_tweet():
    QUERY = (
        "SELECT barnivore_product_name, barnivore_status, barnivore_country " +
        "FROM barnivore_product " +
        "order by random() " +
        "limit 1"
    )
        
    try:
        conn = psycopg2.connect(connectionString)
        cur = conn.cursor()
        cur.execute(QUERY)
        result = cur.fetchall()

    except psycopg2.DatabaseError as e:
        print('Error %s' % e)    

    finally:
        if conn:
            conn.close()

    return result[0] #No need for this to be in an array cause only 1 tweet
    

def fixTypingErrors(name):
    name = name.lower() 
    if name == "guiness":
        name = "guinness"
    return name

#Uncomment for testing
#print(getAlcoholByName("Budweiser"))


