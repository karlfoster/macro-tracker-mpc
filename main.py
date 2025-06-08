import sqlite3
import os
import argparse
from datetime import date
from mcp.server.fastmcp import FastMCP

# Parse command line arguments
parser = argparse.ArgumentParser(description='Macro Tracker MCP Server')

# Initialize FastMCP server
mcp = FastMCP("macro-tracker")

# Database path from command line argument
DB_PATH = os.path.expanduser("~/macro_tracker.db")

def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create foods table for food database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create daily_goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            target_calories REAL NOT NULL,
            target_protein REAL NOT NULL,
            target_carbs REAL NOT NULL,
            target_fat REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create daily_intake table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            food_name TEXT NOT NULL,
            portion_description TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL,
            meal_type TEXT DEFAULT 'other',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migrate old schema if needed
    cursor.execute("PRAGMA table_info(daily_intake)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'serving_size_g' in columns and 'portion_description' not in columns:
        # Add new column
        cursor.execute('ALTER TABLE daily_intake ADD COLUMN portion_description TEXT DEFAULT "unknown portion"')
        # Update existing records
        cursor.execute('UPDATE daily_intake SET portion_description = serving_size_g || "g" WHERE portion_description = "unknown portion"')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# ===== TOOLS =====

@mcp.tool()
async def set_daily_goals(target_calories: float, target_protein: float, 
                         target_carbs: float, target_fat: float, date_str: str = None) -> str:
    """Set daily macro goals.
    
    Args:
        target_calories: Target calories for the day
        target_protein: Target protein in grams
        target_carbs: Target carbohydrates in grams
        target_fat: Target fat in grams
        date_str: Date in YYYY-MM-DD format (optional, defaults to today)
    """
    try:
        if date_str is None:
            date_str = date.today().isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_goals 
            (date, target_calories, target_protein, target_carbs, target_fat)
            VALUES (?, ?, ?, ?, ?)
        ''', (date_str, target_calories, target_protein, target_carbs, target_fat))
        
        conn.commit()
        conn.close()
        
        return f"✅ Set daily goals for {date_str}:\n" \
               f"🎯 {target_calories} calories, {target_protein}g protein, " \
               f"{target_carbs}g carbs, {target_fat}g fat"
    except Exception as e:
        return f"❌ Error setting goals: {str(e)}"

@mcp.tool()
async def add_food_to_database(name: str, calories: float, protein: float, 
                              carbs: float, fat: float) -> str:
    """Add a new food to the reference database for future lookups.
    
    Args:
        name: Name of the food
        calories: Calories per 100g (for reference)
        protein: Protein in grams per 100g (for reference)
        carbs: Carbohydrates in grams per 100g (for reference)
        fat: Fat in grams per 100g (for reference)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO foods (name, calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, calories, protein, carbs, fat))
        
        conn.commit()
        conn.close()
        
        return f"✅ Added {name} to food database\n" \
               f"Reference values per 100g: {calories} cal, {protein}g protein, {carbs}g carbs, {fat}g fat"
    except sqlite3.IntegrityError:
        return f"❌ Food '{name}' already exists in database"
    except Exception as e:
        return f"❌ Error adding food: {str(e)}"

@mcp.tool()
async def lookup_food(name: str = None) -> str:
    """Look up foods in the database for macro reference.
    
    Args:
        name: Specific food name to look up (optional, if not provided returns all foods)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if name:
            cursor.execute('SELECT * FROM foods WHERE name LIKE ?', (f'%{name}%',))
            foods = cursor.fetchall()
            
            if not foods:
                conn.close()
                return f"❌ No foods found matching '{name}'"
        else:
            cursor.execute('SELECT * FROM foods ORDER BY name')
            foods = cursor.fetchall()
        
        conn.close()
        
        if not foods:
            return "📝 No foods in database yet. Use add_food_to_database to add some."
        
        result = "🍎 Food Database (per 100g)\n"
        result += "=" * 30 + "\n"
        
        for food in foods:
            _, name, calories, protein, carbs, fat, _ = food
            result += f"• {name}: {calories}cal, {protein}g protein, {carbs}g carbs, {fat}g fat\n"
        
        return result
    except Exception as e:
        return f"❌ Error looking up foods: {str(e)}"

@mcp.tool()
async def log_food_intake(food_name: str, calories: float, protein: float, 
                         carbs: float, fat: float, portion_description: str,
                         meal_type: str = "other", date_str: str = None) -> str:
    """Log food intake with calculated macros.
    
    Args:
        food_name: Name of the food eaten
        calories: Total calories for this portion
        protein: Total protein in grams for this portion
        carbs: Total carbs in grams for this portion  
        fat: Total fat in grams for this portion
        portion_description: Description of portion (e.g. "200g", "1 cup", "1 medium apple")
        meal_type: Type of meal (breakfast, lunch, dinner, snack, other)
        date_str: Date in YYYY-MM-DD format (optional, defaults to today)
    """
    try:
        if date_str is None:
            date_str = date.today().isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Log the intake with calculated values
        cursor.execute('''
            INSERT INTO daily_intake 
            (date, food_name, portion_description, calories, protein, carbs, fat, meal_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date_str, food_name, portion_description, calories, protein, carbs, fat, meal_type))
        
        conn.commit()
        conn.close()
        
        return f"✅ Logged {portion_description} of {food_name} for {meal_type}\n" \
               f"Added: {calories:.0f} cal, {protein:.1f}g protein, " \
               f"{carbs:.1f}g carbs, {fat:.1f}g fat"
    except Exception as e:
        return f"❌ Error logging food: {str(e)}"

@mcp.tool()
async def get_database_info() -> str:
    """Get information about the database location and status."""
    try:
        file_exists = os.path.exists(DB_PATH)
        file_size = os.path.getsize(DB_PATH) if file_exists else 0
        
        result = f"📁 Database Information\n"
        result += "=" * 25 + "\n"
        result += f"Location: {DB_PATH}\n"
        result += f"Exists: {'✅ Yes' if file_exists else '❌ No'}\n"
        
        if file_exists:
            result += f"Size: {file_size} bytes\n"
            
            # Get some basic stats
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM foods")
            food_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM daily_intake")
            intake_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT date) FROM daily_goals")
            goal_days = cursor.fetchone()[0]
            
            conn.close()
            
            result += f"\n📊 Contents:\n"
            result += f"• {food_count} foods in database\n"
            result += f"• {intake_count} food entries logged\n"
            result += f"• {goal_days} days with goals set\n"
        
        return result
    except Exception as e:
        return f"❌ Error getting database info: {str(e)}"
    """Review daily macro values and progress.
    
    Args:
        date_str: Date in YYYY-MM-DD format (optional, defaults to today)
    """
    return await get_daily_summary(date_str)

@mcp.tool()
async def review_meals(date_str: str = None) -> str:
    """Review all meals for a specific day.
    
    Args:
        date_str: Date in YYYY-MM-DD format (optional, defaults to today)
    """
    try:
        if date_str is None:
            date_str = date.today().isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT meal_type, food_name, portion_description, calories, protein, carbs, fat, created_at
            FROM daily_intake 
            WHERE date = ?
            ORDER BY meal_type, created_at
        ''', (date_str,))
        
        meals = cursor.fetchall()
        conn.close()
        
        if not meals:
            return f"🍽️ No meals logged for {date_str}"
        
        result = f"🍽️ Meals for {date_str}\n"
        result += "=" * 30 + "\n\n"
        
        current_meal_type = None
        for meal_type, food_name, portion_desc, calories, protein, carbs, fat, timestamp in meals:
            if meal_type != current_meal_type:
                current_meal_type = meal_type
                result += f"🍽️ {meal_type.upper()}\n"
                result += "-" * 15 + "\n"
            
            result += f"• {portion_desc} {food_name}\n"
            result += f"  {calories:.0f} cal | {protein:.1f}g protein | {carbs:.1f}g carbs | {fat:.1f}g fat\n\n"
        
        return result
    except Exception as e:
        return f"❌ Error reviewing meals: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')