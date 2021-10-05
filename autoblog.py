import sqlite3
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "issuetracker.settings")  # nopep8
django.setup()  # nopep8
from blog.models import Post, PrivatePost  # nopep8

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()
for i in range(20, 40):
    db = 'privatepost'  # 'privatepost' or 'post'
    author_id = 1
    conn.execute(f"""
        INSERT INTO blog_{db} (id, title, date_posted, author_id, image, content)
        VALUES ({i}, 'auto {db} post {i}', datetime('now', 'localtime'), {author_id}, '', 'auto generated text {db} post body {i}');
        """)
    conn.commit()
    PrivatePost.objects.filter(id=i).get().tags.add(
        f"tag{i}", "auto-gen-private")
    # print(f"{i} is done")

# cur.execute("select id, title, author_id from blog_post where author_id=8")
# records = cur.fetchall()
# print(records)
# print(len(records))
conn.commit()
conn.close()


# blog_post id has to be unique number
# .headers on will show column names in sqlite3
# .schema blog_post will show key requirements for each column
# use cursor.fetchall() and cursor.rowcount
# select col1, col2 from table where col1='text';
# if tag already exists reuse the tag, otherwise create a new one
# delete from blog_post where id=n
