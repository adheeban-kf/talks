from fastapi import FastAPI, Depends, Request, Form, status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine 
import models 

# Create database tables based on SQLAlchemy models
models.Base.metadata.create_all(bind=engine)

# Initialize Jinja2 templates for rendering HTML pages
templates = Jinja2Templates(directory="templates")

# Create a FastAPI app instance
app = FastAPI()

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define a route for the home page
@app.get("/")
async def home(req: Request, db: Session = Depends(get_db)):
    # Query all Todo objects from the database
    todos = db.query(models.Todo).all()
    # Render the "base.html" template with the request and todo_list variables
    return templates.TemplateResponse("base.html", {"request": req, "todo_list": todos})

# Define a route for adding a new todo
@app.post("/add")
def add(req: Request, title: str = Form(...), db: Session = Depends(get_db)):
    # Create a new Todo object with the provided title
    new_todo = models.Todo(title=title)
    # Add the new_todo to the database
    db.add(new_todo)
    # Commit the transaction to save changes to the database
    db.commit()
    # Redirect the user back to the home page after adding the todo
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

# Define a route for updating the completion status of a todo
@app.get("/update/{todo_id}")
def update(req: Request, todo_id: int, db: Session = Depends(get_db)):
    # Query the Todo object by its ID
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    # Toggle the completion status of the todo
    todo.complete = not todo.complete
    # Commit the transaction to save changes to the database
    db.commit()
    # Redirect the user back to the home page after updating the todo
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

# Define a route for deleting a todo
@app.get("/delete/{todo_id}")
def delete(req: Request, todo_id: int, db: Session = Depends(get_db)):
    # Query the Todo object by its ID
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    # Delete the todo from the database
    db.delete(todo)
    # Commit the transaction to save changes to the database
    db.commit()
    # Redirect the user back to the home page after deleting the todo
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
