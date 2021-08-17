import redis

from flask import Flask, render_template, request, flash

app = Flask(__name__)

r = redis.Redis()
app.secret_key = 'secret_key'
last_id = 0


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        global last_id
        name = request.form["full_name"]
        post = request.form["data"]
        print(name, post)
        last = r.get("last_id")
        if last is None:
            last_id = 1
        else:
            last_id = int(last)
            last_id += 1

        r.set(f"news:name:{last_id}", name)
        r.set(f"news:post:{last_id}", post)
        r.set("last_id", last_id)
        r.lpush("post_id", last_id)
        flash("Successfully submitted the post", category="success")

    return render_template("home.html")


@app.route("/all")
def all_posts():
    post_ids = r.lrange("post_id", 0, -1)

    posts = {}

    for post_id in post_ids:
        name_byte = r.get(f"news:name:{post_id.decode('utf-8')}")
        name = name_byte.decode('utf-8')

        post_byte = r.get(f"news:post:{post_id.decode('utf-8')}")
        post_data = post_byte.decode('utf-8')

        posts[name] = post_data

    return render_template("all.html", posts=posts)


if __name__ == '__main__':
    app.run()
