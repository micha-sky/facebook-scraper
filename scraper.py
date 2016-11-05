import mechanize
import sys
from bs4 import BeautifulSoup
import json
from facepy import GraphAPI
import MySQLdb

login = str(sys.argv[1])
password = str(sys.argv[2])
target_id = str(sys.argv[3])
oauth_access_token = 'yourapitoken'

graph = GraphAPI(oauth_access_token)

url = "https://m.facebook.com/login.php"

# login to facebook
br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454101')]
br.open(url)
br.select_form(nr=0)
br.form['email'] = login
br.form['pass'] = password
br.submit()


# init db
def init_db():
    db = MySQLdb.connect("localhost", "user", "password", "database")
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS facebook (
        event_id int(20) NOT NULL,
        user_id int(20) NOT NULL,
        user_name CHAR(20),
        age INT,
        sex CHAR(1),
        city VARCHAR(50),
        hometown VARCHAR(50) )"""

    cursor.execute(sql)
    db.close()


init_db()


def get_user_info(user_id):
    fb_url = "https://www.facebook.com/{0}".format(user_id)
    print "Processing user id: {0}".format(user_id)
    # fb_url = "https://www.facebook.com/profile.php?id={0}&sk=about".format(user_id)

    br.open(fb_url)
    all_html = br.response().get_data()
    soup = BeautifulSoup(all_html, 'html.parser')
    info = soup.find(type="application/ld+json")
    if info is None:
        print 'Error fetching data for user'
    else:
        user_info = json.loads(info.get_text())
        return user_info


def get_user_info2(user_id):
    fb_url = "https://www.facebook.com/{0}".format(user_id)
    print "Processing user id: {0}".format(user_id)

    br.open(fb_url)
    html = br.response().read()
    soup = BeautifulSoup(html, 'html.parser')
    info = soup.find(type="application/ld+json")
    if info is None:
        print 'Error fetching data for user'
    else:
        user_info = json.loads(info.get_text())
        return user_info


def get_event_attendees(event_id):
    users = graph.get("{0}/attending?fields=link,id".format(event_id))['data']
    return users


attendees = get_event_attendees(target_id)
for attendee in attendees:
    print get_user_info2(attendee['id'])


def write_data(event_id, user):
    db = MySQLdb.connect("localhost", "user", "password", "database")
    cursor = db.cursor()

    name = user['name']
    city = user['city']

    try:
        cursor.execute("INSERT INTO facebook(event_id, user_id, user_name, ) VALUES (%s, %s, %s)",
                       (event_id, name, city))
        db.commit()
    except():
        db.rollback()
