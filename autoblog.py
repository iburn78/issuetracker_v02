import sqlite3

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()
#conn.execute("""
#    INSERT INTO blog_post (id, title, date_posted, author_id, image, content) 
#    VALUES (7, 'auto post 2', datetime('now', 'localtime'), 8, '', 'auto generated text body');
#    """)
cur.execute("select id, title, author_id from blog_post where author_id=8")
records = cur.fetchall()
print(records)
print(len(records))
conn.commit()
conn.close()



# blog_post id has to be unique number
# .headers on will show column names in sqlite3
# .schema blog_post will show key requirements for each column
# use cursor.fetchall() and cursor.rowcount
# select col1, col2 from table where col1='text';
# if tag already exists reuse the tag, otherwise create a new one
# delete from blog_post where id=n


