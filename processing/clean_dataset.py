import pandas as pd
from datetime import datetime as dt


def epoch_to_date(unix_epoch):
    return dt.fromtimestamp(unix_epoch)


df = pd.read_csv('dataset/movie/ratings.bak', index_col=False)
df['date'] = df.timestamp.apply(epoch_to_date)
df.drop(columns=["timestamp"], inplace=True)
print(df.head(10))
df.to_csv("dataset/movie/ratings.csv", index=False)

"""
The data type of "date" field is String (type 2), we need to convert it to Date

mongo shell command:
> db.ratings.find({'date' : { $type : 2 }}).forEach(function(x) {
    x.date = new ISODate(x.date);
    db.ratings.save(x);
})

verify:
> db.ratings.find({'date' : { $type : 2 }}).count()
> 0
"""

