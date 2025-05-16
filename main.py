import os
from fastapi import FastAPI, HTTPException, Query
from databases import Database
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
PORT = int(os.getenv("PORT", 5000))
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5008")  # Changed to default PostgreSQL port
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "admin")
PG_DATABASE = os.getenv("PG_DATABASE", "studentdb")

# PostgreSQL connection URL
DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

# Initialize app and database
app = FastAPI()
database = Database(DATABASE_URL)

# Enable CORS for frontend (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect/disconnect handlers
@app.on_event("startup")
async def startup():
    try:
        await database.connect()
        print("✅ Database connected")
    except Exception as e:
        print("❌ Error connecting to database:", e)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("🔌 Database disconnected")


# Routes
@app.get("/api/total-registrations")
async def total_registrations():
    try:
        query = "SELECT COUNT(*) as total FROM students"
        result = await database.fetch_one(query)
        return {"total": result["total"] if result else 0}
    except Exception as e:
        print("❌ Error in total_registrations:", e)
        raise HTTPException(status_code=500, detail="Database query failed")


@app.get("/api/registrations-by-programme")
async def registrations_by_programme(year: str = Query("all")):
    try:
        params = {}
        query = "SELECT study_programme, COUNT(*) as count FROM students"

        if year != "all":
            year_int = int(year)  # 🔥 convert string to int
            query += " WHERE academic_year = :year"
            params = {"year": year_int}

        query += " GROUP BY study_programme ORDER BY count DESC"
        result = await database.fetch_all(query=query, values=params)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Year must be an integer or 'all'")
    except Exception as e:
        print("❌ Error in registrations_by_programme:", e)
        raise HTTPException(status_code=500, detail="Database query failed")


@app.get("/api/registrations-by-year")
async def registrations_by_year(programme: str = Query("all")):
    try:
        params = {}
        query = "SELECT academic_year, COUNT(*) as count FROM students"

        if programme != "all":
            query += " WHERE study_programme = :programme"
            params = {"programme": programme}

        query += " GROUP BY academic_year ORDER BY academic_year"
        result = await database.fetch_all(query=query, values=params)
        return result
    except Exception as e:
        print("❌ Error in registrations_by_year:", e)
        raise HTTPException(status_code=500, detail="Database query failed")


@app.get("/api/registrations-by-school")
async def registrations_by_school():
    try:
        query = """
        SELECT secondary_school, COUNT(*) as count
        FROM students
        GROUP BY secondary_school
        ORDER BY count DESC
        """
        result = await database.fetch_all(query=query)
        return result
    except Exception as e:
        print("❌ Error in registrations_by_school:", e)
        raise HTTPException(status_code=500, detail="Database query failed")


@app.get("/api/top-schools")
async def top_schools():
    try:
        query = """
        SELECT secondary_school, COUNT(*) as count
        FROM students
        GROUP BY secondary_school
        ORDER BY count DESC
        LIMIT 10
        """
        result = await database.fetch_all(query=query)
        return result
    except Exception as e:
        print("❌ Error in top_schools:", e)
        raise HTTPException(status_code=500, detail="Database query failed")


# Run the server if this is the main file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
