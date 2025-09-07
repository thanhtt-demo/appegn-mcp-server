import uvicorn
from typing import List, Dict, Any, Optional, Union
import httpx
import os
import math
from fastmcp import FastMCP
from fastapi import FastAPI
from fastmcp.server.openapi import RouteMap, MCPType
from mcp.types import Prompt, PromptMessage, TextContent

app = FastAPI(
    title="api",
    description="api + mcp")

# 1. Generate MCP server from your API
mcp = FastMCP.from_fastapi(app=app, name="MCP")

# 2. Create the MCP's ASGI app
mcp_app = mcp.http_app(path='/mcp')

# 3. Mount it back into your FastAPI app
app = FastAPI(title="API", lifespan=mcp_app.lifespan)
app.mount("/llm", mcp_app)

# ======================= CALCULATOR TOOLS =======================

@mcp.tool(name="sum_numbers", description="Calculate the sum of multiple numbers")
async def sum_numbers(numbers: List[float]) -> float:
    """
    Calculates the sum of all numbers in a given list.
    
    Args:
        numbers: A list of numbers to be added together.
    
    Returns:
        The sum of the numbers as a float.
    """
    if not numbers:
        raise ValueError("The list of numbers cannot be empty.")
    return sum(numbers)


@mcp.tool(name="subtract", description="Calculate the difference between two numbers (a - b)")
async def subtract(a: float, b: float) -> float:
    """
    Subtracts the second number from the first number (a - b).
    
    Args:
        a: The number to subtract from (minuend).
        b: The number to subtract (subtrahend).
    
    Returns:
        The difference between a and b.
    """
    return a - b


@mcp.tool(name="multiply_numbers", description="Calculate the product of multiple numbers")
async def multiply_numbers(numbers: List[float]) -> float:
    """
    Calculates the product of all numbers in a given list.
    
    Args:
        numbers: A list of numbers to be multiplied together.
    
    Returns:
        The product of the numbers as a float.
    """
    if not numbers:
        raise ValueError("The list of numbers to multiply cannot be empty.")
    return math.prod(numbers)


@mcp.tool(name="divide", description="Divide one number by another (dividend / divisor)")
async def divide(dividend: float, divisor: float) -> float:
    """
    Divides the first number by the second number. Includes a check for division by zero.
    
    Args:
        dividend: The number to be divided.
        divisor: The number to divide by. Cannot be zero.
    
    Returns:
        The quotient as a float.
    """
    if divisor == 0:
        raise ValueError("Cannot divide by zero.")
    return dividend / divisor


@mcp.tool(name="power", description="Calculate the power of a number (base^exponent)")
async def power(base: float, exponent: float) -> float:
    """
    Calculates base raised to the power of exponent.
    
    Args:
        base: The base number.
        exponent: The exponent.
    
    Returns:
        The result of base^exponent.
    """
    return base ** exponent


@mcp.tool(name="square_root", description="Calculate the square root of a number")
async def square_root(number: float) -> float:
    """
    Calculates the square root of a number.
    
    Args:
        number: The number to calculate square root for. Must be non-negative.
    
    Returns:
        The square root of the number.
    """
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number.")
    return math.sqrt(number)


@mcp.tool(name="percentage", description="Calculate percentage of a number")
async def percentage(number: float, percent: float) -> float:
    """
    Calculates what percentage of a number equals.
    
    Args:
        number: The base number.
        percent: The percentage (e.g., 25 for 25%).
    
    Returns:
        The percentage value.
    """
    return (number * percent) / 100


@mcp.tool(name="average", description="Calculate the average of multiple numbers")
async def average(numbers: List[float]) -> float:
    """
    Calculates the arithmetic mean of all numbers in a given list.
    
    Args:
        numbers: A list of numbers to calculate average for.
    
    Returns:
        The average of the numbers as a float.
    """
    if not numbers:
        raise ValueError("The list of numbers cannot be empty.")
    return sum(numbers) / len(numbers)


@mcp.tool(name="factorial", description="Calculate the factorial of a non-negative integer")
async def factorial(n: int) -> int:
    """
    Calculates the factorial of a non-negative integer.
    
    Args:
        n: A non-negative integer.
    
    Returns:
        The factorial of n.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if not isinstance(n, int):
        raise ValueError("Factorial is only defined for integers.")
    return math.factorial(n)


@mcp.tool(name="gcd", description="Calculate the greatest common divisor of two integers")
async def gcd(a: int, b: int) -> int:
    """
    Calculates the greatest common divisor (GCD) of two integers.
    
    Args:
        a: First integer.
        b: Second integer.
    
    Returns:
        The GCD of a and b.
    """
    return math.gcd(a, b)


@mcp.tool(name="lcm", description="Calculate the least common multiple of two integers")
async def lcm(a: int, b: int) -> int:
    """
    Calculates the least common multiple (LCM) of two integers.
    
    Args:
        a: First integer.
        b: Second integer.
    
    Returns:
        The LCM of a and b.
    """
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)

# ======================= FINISH CONVERSATION TOOL =======================
@mcp.tool(name="finish_conversation", description="Use this tool to provide the final answer to the user and end the conversation. This should be called only when all necessary information has been gathered from other agents.")
def finish_conversation(final_answer: str):
    """
    Provides the final, comprehensive and complete response to send to the user.
    This should be called only when all necessary information has been gathered from other agents.
    
    Args:
        final_answer: Final, comprehensive and complete response to send to user.
    
    Returns:
        The final answer string.
    """
    return final_answer

# ======================= DBT PROMPTS =======================

@mcp.prompt(name="generate_dbt_sql_prompt", description="Generate a prompt for creating DBT SQL model based on the template format.")
async def generate_dbt_sql_prompt(
    table_name: str,
    description: str,
    source_tables: str,
    business_logic: str = ""
) -> List[PromptMessage]:
    """
    
    Args:
        table_name: Name of the target table/model
        description: Business description of the table
        source_tables: List of source tables (comma-separated)
        business_logic: Additional business logic requirements
    
    Returns:
        A formatted prompt for LLM to generate DBT SQL
    """
    
    template_path = os.path.join(os.path.dirname(__file__), "template", "type-append", "egn_cmn_cdp_bal_rpt_byday.sql")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        template_content = "Template file not found. Please check the template directory."
    
    prompt = f"""
Bạn là chuyên gia DBT và SQL. Hãy tạo ra một file SQL DBT model với các yêu cầu sau:

**Yêu cầu:**
- Tên bảng/model: {table_name}
- Mô tả: {description}
- Bảng nguồn: {source_tables}
- Logic nghiệp vụ bổ sung: {business_logic if business_logic else "Không có yêu cầu đặc biệt"}

**Template tham khảo:**
```sql
{template_content}
```

**Hướng dẫn:**
1. Sử dụng cấu trúc config tương tự như template với materialized='incremental'
2. Sử dụng incremental_strategy='insert_overwrite' và partition_by=['data_date']
3. Thêm các cột kỹ thuật: tf_sourcing_at, tf_etl_at, data_date
4. Sử dụng source() macro để tham chiếu đến bảng nguồn
5. Áp dụng các điều kiện filter phù hợp
6. Thực hiện JOIN nếu cần thiết
7. Đảm bảo cú pháp SQL đúng chuẩn DBT

Hãy tạo ra file SQL hoàn chỉnh theo format trên.
"""
    
    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt)
        )
    ]

@mcp.prompt(name="generate_dbt_schema_prompt", description="Generate a prompt for creating DBT schema.yml file based on the template format.")
async def generate_dbt_schema_prompt(
    model_name: str,
    description: str,
    table_type: str = "append",
    partition_strategy: str = "sysdate_1",
    dagster_group: str = "cmn_engine",
    columns_info: str = ""
) -> List[PromptMessage]:
    """
    Args:
        model_name: Name of the DBT model
        description: Description of the model
        table_type: Type of table (append, upsert, scd)
        partition_strategy: Partitioning strategy (t24, way4, sysdate_1)
        dagster_group: Dagster group name
        columns_info: Information about columns (comma-separated: name:type:description)
    
    Returns:
        A formatted prompt for LLM to generate DBT schema.yml
    """
    
    # Read the template schema file
    template_path = os.path.join(os.path.dirname(__file__), "template", "type-append", "schema.yml")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        template_content = "Template file not found. Please check the template directory."
    
    prompt = f"""
Bạn là chuyên gia DBT và Data Engineering. Hãy tạo ra một file schema.yml cho DBT model với các yêu cầu sau:

**Yêu cầu:**
- Tên model: {model_name}
- Mô tả: {description}
- Kiểu bảng: {table_type}
- Chiến lược partition: {partition_strategy}
- Dagster group: {dagster_group}
- Thông tin cột: {columns_info if columns_info else "Cần định nghĩa dựa trên SQL model"}

**Template tham khảo:**
```yaml
{template_content}
```

**Hướng dẫn:**
1. Sử dụng cấu trúc config với alias, schema và meta như template
2. Thiết lập table_type, partition và max_retries phù hợp
3. Cấu hình dagster group và depends nếu cần
4. Thiết lập spark configuration cho execution và test
5. Định nghĩa tất cả columns với name, description và data_type
6. Đảm bảo các cột kỹ thuật: tf_sourcing_at, tf_etl_at, data_date được khai báo
7. Sử dụng các data type phù hợp: string, int, decimal, date, timestamp
8. Viết description tiếng Việt rõ ràng cho từng cột

Hãy tạo ra file schema.yml hoàn chỉnh theo format trên.
"""
    
    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt)
        )
    ]


@mcp.prompt(name="generate_dbt_test_prompt", description="Generate a prompt for creating DBT test configuration based on the template format.")
async def generate_dbt_test_prompt(
    model_name: str,
    description: str,
    test_requirements: str = "",
    test_columns: str = "",
    test_type: str = "basic"
) -> List[PromptMessage]:
    """
    Args:
        model_name: Name of the DBT model to test
        description: Description of the model
        test_requirements: Specific test requirements (business rules, validations)
        test_columns: Column names to test (comma-separated)
        test_type: Type of test (basic, advanced, custom)
    
    Returns:
        A formatted prompt for LLM to generate DBT test configuration
    """
    
    # Read the template test file
    template_path = os.path.join(os.path.dirname(__file__), "template", "type-append", "dbt_test_example.yml")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        template_content = "Template file not found. Please check the template directory."
    
    prompt = f"""
Bạn là chuyên gia DBT và Data Quality. Hãy tạo ra file test configuration cho DBT model với các yêu cầu sau:

**Yêu cầu:**
- Tên model: {model_name}
- Mô tả: {description}
- Yêu cầu test: {test_requirements if test_requirements else "Test cơ bản cho data quality"}
- Các cột cần test: {test_columns if test_columns else "Tất cả cột quan trọng"}
- Loại test: {test_type}

**Template tham khảo:**
```yaml
{template_content}
```

**Các loại test có sẵn:**
1. **Built-in tests:**
   - `unique`: Kiểm tra tính duy nhất
   - `not_null`: Kiểm tra không null
   - `accepted_values`: Kiểm tra giá trị trong danh sách cho phép
   - `relationships`: Kiểm tra foreign key

2. **DBT Utils tests:**
   - `dbt_utils.expression_is_true`: Test business logic với expression tùy chỉnh
   - `dbt_utils.unique_combination_of_columns`: Test unique trên nhiều cột

3. **DBT Expectations tests:**
   - `dbt_expectations.expect_column_values_to_be_unique`: Test unique nâng cao
   - `dbt_expectations.expect_column_values_to_be_between`: Test giá trị trong khoảng
   - `dbt_expectations.expect_column_values_to_match_regex`: Test format dữ liệu

**Hướng dẫn:**
1. Thiết lập test ở cấp model (model tests) cho business logic
2. Thiết lập test ở cấp column (column tests) cho data quality
3. Sử dụng `row_condition` để test chỉ trên dữ liệu mới: `"data_date = date('{{{{ var('datadate') }}}}')"`  
4. Phân loại test theo tags:
   - `[required]`: Test bắt buộc, fail sẽ dừng job
   - `[optional]`: Test tùy chọn, fail không ảnh hưởng job
5. Thêm `meta.description` để mô tả test case rõ ràng
6. Cấu hình spark resources phù hợp cho test
7. Set `test.include: true` để enable test execution

**Ví dụ test patterns:**
- Test unique: `dbt_expectations.expect_column_values_to_be_unique`
- Test business rule: `dbt_utils.expression_is_true`
- Test data range: `dbt_expectations.expect_column_values_to_be_between`
- Test not null: `not_null`

Hãy tạo ra file test configuration hoàn chỉnh theo format trên với các test case phù hợp.
"""
    
    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt)
        )
    ]

@app.get("/")
def health():
    return {"status": "ok", "tools": [
        "sum_numbers", "subtract", "multiply_numbers", "divide", 
        "power", "square_root", "percentage", "average", 
        "factorial", "gcd", "lcm", "finish_conversation"
    ]}

@app.get("/calculator/tools")
def list_calculator_tools():
    return {
        "calculator_tools": [
            {"name": "sum_numbers", "description": "Calculate the sum of multiple numbers"},
            {"name": "subtract", "description": "Calculate the difference between two numbers (a - b)"},
            {"name": "multiply_numbers", "description": "Calculate the product of multiple numbers"},
            {"name": "divide", "description": "Divide one number by another (dividend / divisor)"},
            {"name": "power", "description": "Calculate the power of a number (base^exponent)"},
            {"name": "square_root", "description": "Calculate the square root of a number"},
            {"name": "percentage", "description": "Calculate percentage of a number"},
            {"name": "average", "description": "Calculate the average of multiple numbers"},
            {"name": "factorial", "description": "Calculate the factorial of a non-negative integer"},
            {"name": "gcd", "description": "Calculate the greatest common divisor of two integers"},
            {"name": "lcm", "description": "Calculate the least common multiple of two integers"}
        ]
    }

if __name__ == "__main__":
    # Start an HTTP server on port 8000
  # mcp.run(transport="http", host="0.0.0.0", port=8001)
  # mcp.run()
  uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
