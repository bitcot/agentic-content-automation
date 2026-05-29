from database import engine, Base
import models
from sqlalchemy.schema import CreateTable

for table in Base.metadata.sorted_tables:
    print(str(CreateTable(table).compile(engine)).strip() + ";\n")
