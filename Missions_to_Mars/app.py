from flask import Flask, render_template, redirect
import scrape_mars
import pymongo
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars_db
collection = db.mars_info

app = Flask(__name__)

@app.route('/')
def index():
    mars_current_info = collection.find_one()
    if mars_current_info:
        return render_template('index.html', info=mars_current_info)
    else:
        mars_current_info = scrape_mars.scrape()
        collection.insert(mars_current_info)
        return render_template('index.html', info=mars_current_info)

@app.route('/scrape')
def scraper():
    mars_current_info = collection.find_one()
    mars_new_info = scrape_mars.scrape()
    collection.replace_one({"mars_featured_image": mars_current_info['mars_featured_image']}, mars_new_info)
    collection.update({}, mars_new_info, upsert=True)
    return redirect('/', code=302)

if __name__ == '__main__':
    app.run(debug=True)
