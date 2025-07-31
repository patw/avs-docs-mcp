from pymongo import MongoClient, DESCENDING
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    print("❌ MONGO_URI not found in .env file")
    sys.exit(1)

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client["sample_mflix"]
    movies_collection = db["movies"]
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Could not connect to MongoDB: {e}")
    sys.exit(1)

# Create the MCP server
mcp = FastMCP("Movie Database")

@mcp.tool
def find_movies(
    title: str = None,
    genre: str = None,
    actor: str = None,
    year: int = None,
    min_rating: float = None,
    limit: int = 10
):
    """
    Find movies based on search criteria.
    
    Args:
        title: Movie title to search for
        genre: Genre like "Comedy", "Drama", etc.
        actor: Actor name to search for
        year: Release year
        min_rating: Minimum IMDb rating (e.g., 7.5)
        limit: Maximum number of results (default: 10)
    
    Returns:
        List of movies matching the criteria
    """
    # Build the search query
    query = {}
    
    if title:
        # Case-insensitive partial match
        query["title"] = {"$regex": title, "$options": "i"}
    
    if genre:
        query["genres"] = genre
    
    if actor:
        # Case-insensitive partial match in cast array
        query["cast"] = {"$regex": actor, "$options": "i"}
    
    if year:
        query["year"] = year
    
    if min_rating:
        query["imdb.rating"] = {"$gte": min_rating}
    
    # Find movies and return only essential fields
    results = movies_collection.find(
        query,
        {
            "title": 1,
            "year": 1,
            "genres": 1,
            "cast": 1,
            "imdb.rating": 1,
            "plot": 1,
            "_id": 0
        }
    ).sort("imdb.rating", DESCENDING).limit(limit)
    
    return list(results)

@mcp.tool
def count_movies(
    genre: str = None,
    year: int = None,
    min_rating: float = None
):
    """
    Count how many movies match the criteria.
    
    Args:
        genre: Genre to filter by
        year: Release year to filter by
        min_rating: Minimum IMDb rating
    
    Returns:
        Number of movies matching the criteria
    """
    query = {}
    
    if genre:
        query["genres"] = genre
    
    if year:
        query["year"] = year
    
    if min_rating:
        query["imdb.rating"] = {"$gte": min_rating}
    
    return movies_collection.count_documents(query)

@mcp.tool
def get_top_movies(
    year: int = None,
    genre: str = None,
    limit: int = 5
):
    """
    Get the top-rated movies.
    
    Args:
        year: Filter by release year
        genre: Filter by genre
        limit: Number of movies to return (default: 5)
    
    Returns:
        List of top-rated movies
    """
    query = {}
    
    if year:
        query["year"] = year
    
    if genre:
        query["genres"] = genre
    
    # Must have an IMDb rating
    query["imdb.rating"] = {"$exists": True}
    
    results = movies_collection.find(
        query,
        {
            "title": 1,
            "year": 1,
            "imdb.rating": 1,
            "genres": 1,
            "_id": 0
        }
    ).sort("imdb.rating", DESCENDING).limit(limit)
    
    return list(results)

@mcp.tool
def get_movie_details(title: str):
    """
    Get detailed information about a specific movie.
    
    Args:
        title: Exact movie title
    
    Returns:
        Movie details or None if not found
    """
    movie = movies_collection.find_one(
        {"title": title},
        {"_id": 0}
    )
    return movie

if __name__ == "__main__":
    print("\n🎬 Movie Database Server is running!")
    print("\nExample queries you can ask:")
    print("- 'Find movies with Tom Hanks'")
    print("- 'How many Comedy movies are there?'")
    print("- 'What are the top 5 movies from 1994?'")
    print("- 'Show me details for The Shawshank Redemption'")
    
    mcp.run()
