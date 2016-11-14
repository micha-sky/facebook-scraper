import mechanize
import sys
from bs4 import BeautifulSoup
import json
from facepy import GraphAPI
import MySQLdb
import requests

login = str(sys.argv[1])
password = str(sys.argv[2])
event_id = str(sys.argv[3])
oauth_access_token = 'apitoken'

graph = GraphAPI(oauth_access_token)

def init_db():
    db = MySQLdb.connect("localhost", "user", "password", "database")
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS `facebook_user` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `fbuid` VARCHAR(45) NOT NULL,
      `name` VARCHAR(100) NOT NULL,
      `scraped` TINYINT(1) NOT NULL DEFAULT 0,
      PRIMARY KEY (`id`))
      ENGINE = InnoDB;"""

    cursor.execute(sql)
    db.close()


# init_db()


def get_event_attendees(event_id):
    all_attendees = []
    attendees = graph.get("{0}/attending?fields=link,id,name".format(event_id))

    while True:
        try:
            for attendee in attendees['data']:
                all_attendees.append(attendee)

            attendees = requests.get(attendees['paging']['next']).json()

        except KeyError:
            # When there are no more pages (['paging']['next']), break from the
            # loop and end the script.
            break

    return all_attendees


def save_attendees_by_event(event_id):
    db = MySQLdb.connect("localhost", "user", "password", "database")
    cursor = db.cursor()
    attendees = get_event_attendees(event_id)
    for attendee in attendees:
        attendee_id = int(attendee['id'])
        attendee_name = str(attendee['name'].encode('utf-8'))
        try:
            cursor.execute("INSERT INTO facebook_user(fbuid, name, scraped) "
                           "VALUES (%s, %s, %s)",
                           (attendee_id, attendee_name, 0))
            db.commit()
        except():
            db.rollback()


save_attendees_by_event(event_id)
