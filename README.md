# Macro Tracker MCP Server

A Model Context Protocol (MCP) server for tracking daily macro nutrients (calories, protein, carbohydrates, and fat). This server allows you to set daily goals, maintain a food database, log meals, and review your nutritional progress through Claude Desktop or any MCP-compatible client.

## Features

- **Daily Goal Setting**: Set and track daily macro targets
- **Food Database**: Build a personal database of foods with their nutritional values
- **Meal Logging**: Log food intake with portion sizes and meal types
- **Progress Tracking**: Review daily meals and macro progress
- **Flexible Portions**: Support for various portion descriptions (grams, cups, pieces, etc.)

## Available Tools

1. **set_daily_goals** - Set daily macro targets (calories, protein, carbs, fat)
2. **add_food_to_database** - Add foods to your reference database
3. **lookup_food** - Search for foods in your database
4. **log_food_intake** - Log meals with calculated macros
5. **review_meals** - Review all meals for a specific day
6. **get_database_info** - Check database status and statistics

## Installation

### Prerequisites

- Python 3.10 or higher

### Setup

1. **Install uv** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   
   Restart your terminal after installation to ensure `uv` is available.

2. **Clone the repository**:
   ```bash
   git clone https://github.com/karlfoster/macro-tracker-mpc.git
   cd macro-tracker-mpc
   ```

3. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   uv venv
   
   # Activate virtual environment
   # macOS/Linux:
   source .venv/bin/activate
   
   # Windows:
   .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   uv sync
   ```

5. **Test the server** (optional):
   ```bash
   uv run main.py
   ```
   Press `Ctrl+C` to stop the test.

## Configuration

### Claude Desktop Setup

1. **Find your uv path**:
   ```bash
   # macOS/Linux
   which uv
   
   # Windows
   where uv
   ```

2. **Get your project's absolute path**:
   ```bash
   # In your macro-tracker-mcp directory
   pwd
   ```

3. **Open Claude Desktop configuration file**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

4. **Add the macro tracker server configuration**:
   ```json
   {
     "globalShortcut": "Ctrl+Space",
     "mcpServers": {
       "macro": {
         "command": "/path/to/your/uv",
         "args": [
           "--directory",
           "/absolute/path/to/macro-tracker-mcp",
           "run",
           "main.py"
         ]
       }
     }
   }
   ```
   
   **Replace**:
   - `/path/to/your/uv` with the output from `which uv` command
   - `/absolute/path/to/macro-tracker-mcp` with the output from `pwd` command

5. **Restart Claude Desktop** for changes to take effect.

### Database Location

By default, the database is stored at `~/macro_tracker.db`. You can specify a custom location using the `--db-path` argument:

```json
{
  "globalShortcut": "Ctrl+Space",
  "mcpServers": {
    "macro": {
      "command": "/path/to/your/uv",
      "args": [
        "--directory",
        "/absolute/path/to/macro-tracker-mcp",
        "run",
        "main.py",
        "--db-path",
        "/custom/path/to/database.db"
      ]
    }
  }
}
```

## Usage Examples

### Setting Daily Goals
```
Set my daily macro goals to 2000 calories, 150g protein, 200g carbs, and 65g fat
```

### Adding Foods to Database
```
Add chicken breast to my food database: 165 calories, 31g protein, 0g carbs, 3.6g fat per 100g
```

### Logging Meals
```
I ate 200g of chicken breast for lunch
```

### Reviewing Progress
```
Show me all my meals for today
```
```
What's my macro progress for yesterday?
```

### Looking Up Foods
```
Look up chicken in my food database
```

## Database Schema

The server creates three main tables:

### foods
Stores nutritional information per 100g for reference foods.
- `name` (TEXT): Food name
- `calories` (REAL): Calories per 100g
- `protein` (REAL): Protein in grams per 100g
- `carbs` (REAL): Carbohydrates in grams per 100g
- `fat` (REAL): Fat in grams per 100g

### daily_goals
Stores daily macro targets.
- `date` (TEXT): Date in YYYY-MM-DD format
- `target_calories` (REAL): Daily calorie goal
- `target_protein` (REAL): Daily protein goal in grams
- `target_carbs` (REAL): Daily carb goal in grams
- `target_fat` (REAL): Daily fat goal in grams

### daily_intake
Logs actual food consumption.
- `date` (TEXT): Date in YYYY-MM-DD format
- `food_name` (TEXT): Name of consumed food
- `portion_description` (TEXT): Portion size description
- `calories` (REAL): Total calories for portion
- `protein` (REAL): Total protein for portion
- `carbs` (REAL): Total carbs for portion
- `fat` (REAL): Total fat for portion
- `meal_type` (TEXT): breakfast, lunch, dinner, snack, or other

## Tips for Best Results

1. **Build Your Food Database**: Start by adding commonly eaten foods to your database for quick lookups
2. **Be Specific with Portions**: Use clear descriptions like "200g", "1 cup", "1 medium apple"
3. **Consistent Meal Types**: Use standard meal types (breakfast, lunch, dinner, snack) for better organization
4. **Daily Goal Setting**: Set realistic, consistent daily goals to track progress effectively

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. **Check the configuration file path and syntax**
2. **Verify the absolute paths** to both `uv` and your project directory
3. **Ensure Claude Desktop is restarted** after configuration changes
4. **Test the server manually**:
   ```bash
   cd /path/to/macro-tracker-mcp
   uv run main.py
   ```

### Database Issues

1. **Check database permissions** for the specified path
2. **Verify disk space** is available
3. **Use `get_database_info` tool** to check database status

### Common Error Messages

- **"Food already exists"**: The food name is already in your database
- **"No foods found"**: Your search didn't match any foods in the database
- **"No meals logged"**: No food intake recorded for the specified date

## Contributing

This is a personal macro tracking tool, but feel free to modify it for your needs:

- Add new nutritional metrics (fiber, sugar, sodium, etc.)
- Implement meal planning features
- Add data export/import functionality
- Create visualization tools

## License

This project is provided as-is for personal use. Modify and distribute as needed for your macro tracking requirements.