Due to the file size limit on GitHub, please download the dataset at [here](https://figshare.com/s/1fcea61928e416533380).

And you need to import it into MongoDB. Run:
```
mongorestore --db=license --gzip data/package.bson.gz
```