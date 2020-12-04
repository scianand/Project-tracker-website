from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

#initialise app
app = Flask(__name__)

# user = postgres
# password = postgres
# database = project_tracker
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:postgres@localhost/project_tracker'
app.config['SECRET_KEY'] = '\xb3\xbbF\xf0\xa1\xea\xf0_\xe8\xf4'

db = SQLAlchemy(app)

class Project(db.Model):
    __tablename__ = 'projects'

    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=50))
    
    # This relation will help if we want to delete project. 
    # If we want to delete project the tasks associated with the project will be automatically deleted.
    task = db.relationship("Task", cascade="all, delete-orphan")

class Task(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    description = db.Column(db.String(length=50))

    # Foreign key relationship for SQLAlchemy. 
    # backref will help to access the project associated with the particluar task.
    project = db.relationship("Project", backref='project')

@app.route("/")
def show_projects():
    return render_template("index.html", projects=Project.query.all())

@app.route("/project/<project_id>")
def show_tasks(project_id):
    return render_template("project-tasks.html", project = Project.query.filter_by(project_id=project_id).first(),
    tasks = Task.query.filter_by(project_id=project_id).all())

@app.route("/add/project", methods =['POST'])
def add_project():
    # Add project
    if not request.form['project-title']:
        flash("Enter the title for your new project", "red")
    else:
        new_project = Project(title=request.form['project-title'])
        db.session.add(new_project)
        db.session.commit()
        flash("Project added successfully", "green")
    return redirect(url_for('show_projects'))

@app.route("/add/task/<project_id>", methods=['POST'])
def add_task(project_id):
    # Add task
    if not request.form['task-description']:
        flash("Enter the task", "red")
    else:
        new_task = Task(description=request.form['task-description'], project_id=project_id)
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully", "green")
    return redirect(url_for('show_tasks', project_id=project_id))

@app.route("/delete/task/<task_id>", methods=['POST'])
def delete_task(task_id):
    task_to_be_deleted = Task.query.filter_by(task_id=task_id).first()
    print(task_to_be_deleted)
    original_project_id = task_to_be_deleted.project.project_id
    db.session.delete(task_to_be_deleted)
    db.session.commit()
    return redirect(url_for('show_tasks', project_id=original_project_id))


@app.route("/delete/project/<project_id>", methods=['POST'])
def delete_project(project_id):
    project_to_be_deleted = Project.query.filter_by(project_id=project_id).first()
    db.session.delete(project_to_be_deleted)
    db.session.commit()
    return redirect(url_for('show_projects'))

app.run(debug=True, host="127.0.0.1", port=3000)