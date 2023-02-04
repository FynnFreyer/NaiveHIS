# NaiveHIS

This project strives to implement a ***very*** simple Hospital Information System (HIS)

Development happens in the context of a university lecture about informational systems in healthcare (Informationssysteme im Gesundheitswesen), given by [Prof. Dr. Schaaf](https://www.htw-berlin.de/hochschule/personen/person/?eid=4298) at the HTW Berlin.

# Getting started

Here are basic commands to get you started.

    # clone the repo
    git clone https://github.com/FynnFreyer/NaiveHIS.git
    cd NaiveHIS

    # setup a venv and install the dependencies
    python -m venv venv
    source venv/bin/activate
    python -m pip install -r requirements.txt

    # project setup
    cd src
    
    # migrate the db
    python manage.py makemigrations
    python manage.py migrate

    # get static files
    mkdir static
    python manage.py collectstatic

    # create an admin account
    python manage.py createsuperuser

    # optionally load some play data
    #
    # python manage.py shell
    # 
    # >>> from init_data import init_data
    # >>> init_data()
    # >>> exit()
    
    # set up the env file
    touch .env
    echo SECRET_KEY=so_very_secret >> .env
    echo PROD=True >> .env
    echo HOST=my.domain.tld >> .env

    # run the project with gunicorn
    # (runs on 127.0.0.1:8000 and should be made accessible
    #  via reverse proxy under my.domain.tld)
    gunicorn NaiveHIS.wsgi
    


# Current State

This is basically what I handed in for another course, but it needs some modification to be even slightly usable.

# Roadmap

Before we start, there should be a discussion among project contributors about the requirements we're working to satisfy.
So we probably need to meet first and discuss what we need, and how we want to implement it.
It makes sense to include Prof. Dr. Schaaf in this conversation.
After having set some requirements, we need to consider what to keep, and what to throw away from the legacy code, and potential refactors in general.

Potential features I have in mind (not considering any actual requirements yet):

- GUI (can be cli-based, like e.g. vim)
- Networking -- Client/Server architecture
- ORM -- load and save objects to the database, don't fiddle with SQL
- support for HL7 (probably very difficult and very optional)

# Contributions

Contribution is only possible for other participants of the course.
Please contact me via E-Mail (posted in the discussion on Moodle), or the Moodle-Forum.

## Guidelines for Contributors

To have a somewhat cohesive development experience:

- Contributions should at least roughly conform to PEP8, therefore it is recommended to use a linter.
- Code should have proper type annotations.
- Code should be commented where necessary.
- Commits should have a descriptive commit message.
- The language to be used for comments and commit messages is English.
- Tests would be nice. As long as the code is well-structured and documented we might get away without them.

Nice, but optional, reading materials are [PEP8](https://peps.python.org/pep-0008/), and the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Workflow

You can either fork this repository, and send pull requests, or I can add you as contributor, and you work on this project directly.
Let's discuss specifics on Moodle.

# Old Documentation

Since this builds on a previous assignment, I'll append the existing documentation (for lack of a better word) here.

# Usage

Start `app.py` with the `--mem` flag to run DB in memory only or with `-v` to echo SQL transactions. 
On the first run, DB will automatically be populated with test data.

Test data can be edited in the `populate` function in `db.py`. 

# Dependencies

This project requires SQLAlchemy and pydicom to run. 
You can install these with the provided `requirements.txt` file or manually.

# "Documentation"

Start `app.py` with `-h` flag for usage or get help with `?` while running.

```
possible commands:

list <entity_type>              - list all entities you have access to  
create <entity_type>            - Create entities, e.g. 'create patient'  
show <entity_type> <identifier> - show details for entity; identifier must be the id  
assign <case_id>                - assign a doctor to a case  

possible entity_types:

case
<type>report                   - type ::= [ any | radiology | surgery | pathology ] 
patient

q to quit
```

# Test data

After initialization, you can log in to the application with the following `usernames:passwords:roles`

```
tom:test:ADMIN
ghouse:pass:ADMISSIONS,RADIOLOGIST
mbailey:pass:SURGEON,RADIOLOGIST
jdorian:pass:SURGEON,PATHOLOGIST
shansen:pass:RADIOLOGIST,PATHOLOGIST
```

# Test cases

The specified testing scenarios could be simulated with the following command inputs 
(specific answers to specific questions are irrelevant and not documented)

Commands must be performed with sufficient privilege (in some cases admin or admissions role)

## Radiologie ohne Befund
```
create patient (optional)
create case
assign <case_id>
create radiologyreport
```

## Chirurgie und Pathologie
```
create patient (optional)
create case
assign <case_id>
create surgeryreport
create pathologyreport
```

## Radiologie, Chirurgie, Pathologie
```
create patient (optional)
create case
assign <case_id>
create radiologyreport
create surgeryreport
create pathologyreport
```
