# Flask-FileAlchemy

![](https://github.com/siddhantgoel/flask-filealchemy/workflows/flask-filealchemy/badge.svg) ![](https://badge.fury.io/py/flask-filealchemy.svg)

`Flask-FileAlchemy` is a [Flask] extension that lets you use Markdown or YAML
formatted plain-text files as the main data store for your apps.

## Installation

```bash
$ pip install flask-filealchemy
```

## Background

The constraints on which data-store to use for applications that only have to
run locally are quite relaxed as compared to the ones that have to serve
production traffic. For such applications, it's normally OK to sacrifice on
performance for ease of use.

One very strong use case here is generating static sites. While you can use
[Frozen-Flask] to "freeze" an entire Flask application to a set of HTML files,
your application still needs to read data from somewhere. This means you'll need
to set up a data store, which (locally) tends to be file based SQLite. While
that does the job extremely well, this also means executing SQL statements to
input data.

Depending on how many data models you have and what types they contain, this can
quickly get out of hand (imagine having to write an `INSERT` statement for a
blog post).

In addition, you can't version control your data. Well, technically you can, but
the diffs won't make any sense to a human.

Flask-FileAlchemy lets you use an alternative data store - plain text files.

Plain text files have the advantage of being much easier to handle for a human.
Plus, you can version control them so your application data and code are both
checked in together and share history.

Flask-FileAlchemy lets you enter your data in Markdown or YAML formatted plain
text files and loads them according to the [SQLAlchemy] models you've defined
using [Flask-SQLAlchemy] This data is then put into whatever data store you're
using (in-memory SQLite works best) and is then ready for your app to query
however it pleases.

This lets you retain the comfort of dynamic sites without compromising on the
simplicity of static sites.

## Usage

### Define data models

Define your data models using the standard (Flask-)SQLAlchemy API. As an
example, a `BlogPost` model can defined as follows.

```python
app = Flask(__name__)

# configure Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

db = SQLAlchemy()

db.init_app(app)

class BlogPost(db.Model):
   __tablename__ = 'blog_posts'

   slug = Column(String(255), primary_key=True)
   title = Column(String(255), nullable=False)
   content = Column(Text, nullable=False)
```

### Add some data

Next, create a `data/` directory somewhere on your disk (to keep things simple,
it's recommended to have this directory in the application root). For each model
you've defined, create a directory under this `data/` directory with the same
name as the `__tablename__` attribute.

We currently support three different ways to define data.

#### 1. Multiple YAML files

The first way is to have multiple YAML files inside the `data/<__tablename__>/`
directory, each file corresponding to one record.

In case of the "blog" example, we can define a new `BlogPost` record by creating
the file `data/blog_posts/first-post-ever.yml` with the following content.

```yaml
slug: first-post-ever
title: First post ever!
content: |
  This blog post talks about how it's the first post ever!
```

Adding more such files in the same directory would result in more records.

#### 2. Single YAML file

For "smaller" models which don't have more than 2-3 fields, Flask-FileAlchemy
supports reading from an `_all.yml` file. In such a case, instead of adding one
file for every row, simply add all the rows in the `_all.yml` file inside the
table directory.

For the "blog" example, this would look like the following.

```yaml
- slug: first-post-ever
  title: First post ever!
  content: This blog post talks about how it's the first post ever!

- slug: second-post-ever
  title: second post ever!
  content: This blog post talks about how it's the second post ever!
 ```

#### 3. Markdown/Frontmatter

It's also possible to load data from Jekyll-style Markdown files containing
Frontmatter metadata.

In case of the blog example, it's possible to create a new `BlogPost` record by
defining a `data/blog_posts/first-post-ever.md` file with the following
content.

```markdown
---
slug: first-post-ever
title: First post ever!
---

This blog post talks about how it's the first post ever!
```

Please note that when defining data using markdown, the name of the column
associated with the main markdown body **needs** to be `content`.

#### 4. Configure and load

Finally, configure `Flask-FileAlchemy` with your setup and ask it to load all
your data.

```python
# configure Flask-FileAlchemy
app.config['FILEALCHEMY_DATA_DIR'] = os.path.join(
   os.path.dirname(os.path.realpath(__file__)), 'data'
)
app.config['FILEALCHEMY_MODELS'] = (BlogPost,)

# load tables
FileAlchemy(app, db).load_tables()
```

`Flask-FileAlchemy` then reads your data from the given directory, and stores
them in the data store of your choice that you configured `Flask-FileAlchemy`
with (the preference being `sqlite:///:memory:`).

Please note that it's not possible to write to this database using `db.session`.
Well, technically it's allowed, but the changes your app makes will only be
reflected in the in-memory data store but won't be persisted to disk.

## Contributing

Contributions are most welcome!

Please make sure you have Python 3.9+ and [uv] installed.

1. Git clone the repository -
   `git clone https://github.com/siddhantgoel/flask-filealchemy`.

2. Install the packages required for development - `uv sync`.

3. That's basically it. You should now be able to run the test suite -
   `uv run pytest`.

[Flask-SQLAlchemy]: https://flask-sqlalchemy.palletsprojects.com/
[Flask]: https://flask.palletsprojects.com/
[Frozen-Flask]: https://pythonhosted.org/Frozen-Flask/
[SQLAlchemy]: https://www.sqlalchemy.org/
[uv]: https://docs.astral.sh/uv/
