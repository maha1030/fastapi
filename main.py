from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session

app = FastAPI()

# Database URL
DATABASE_URL = "sqlite:///./test.db"

# Engine create (DB connection)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}
)

# Session 
SessionLocal = sessionmaker(bind=engine)

# Base
Base = declarative_base()

# Table
class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    completed = Column(Boolean, default=False)
    
# Table create
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.post("/todos")
def create_todo(title: str, db: Session = Depends(get_db)):
    todo = Todo(title=title, completed="False")
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return {
        "message":"Todo Created",
        "data":todo
    }
    
@app.get("/todos")
def get_todos(db:Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return {
        "Total" : len(todos),
        "data" : todos
    }
    
@app.get("/todos/{todo_id}")
def get_todo(todo_id:int, db:Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo Not Found")
    return todo

@app.put("/todos/{todo_id}")
def update_todo(todo_id:int, title:str, db:Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo Not Found") 
    
    todo.title=title
    db.commit()
    db.refresh(todo)
    return {
        "message":"Todo Updated",
        "data": todo
    }
    
# @app.put("/todos/{todo_id}")
# def update_todo(todo_id:int, title:str|None=None,completed:bool|None=None, db:Session=Depends(get_db)):
#     todo = db.query(Todo).filter(Todo.id==todo_id).first()
#     if not todo:
#         raise HTTPException(status_code=404, detail="Todo Not Found") 
    
#     if title is not None:
#         todo.title=title
        
#     if completed is not None:
#         todo.completed = completed
        
#     db.commit()
#     db.refresh(todo)
    
#     return {
#         "message":"Todo Updated",
#         "data": todo
#     }

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int, db:Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo Not Found")
    db.delete(todo)
    db.commit()
    return {
        "message":"TODO Deleted"
    }