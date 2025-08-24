from typing import Any
import httpx
import os
from fastmcp import FastMCP

mcp = FastMCP("DBT Template Generator MCP Server", stateless_http=True)


@mcp.tool()
async def health_check() -> str:
    """Health check for monitoring MCP server status."""
    return "MCP Server is healthy and running"


@mcp.prompt()
async def generate_dbt_sql_prompt(
    table_name: str,
    description: str,
    source_tables: str,
    business_logic: str = ""
) -> str:
    """
    Generate a prompt for creating DBT SQL model based on the template format.
    
    Args:
        table_name: Name of the target table/model
        description: Business description of the table
        source_tables: List of source tables (comma-separated)
        business_logic: Additional business logic requirements
    
    Returns:
        A formatted prompt for LLM to generate DBT SQL
    """
    
    # Read the template SQL file
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
    
    return prompt


@mcp.prompt()
async def generate_dbt_schema_prompt(
    model_name: str,
    description: str,
    table_type: str = "append",
    partition_strategy: str = "sysdate_1",
    dagster_group: str = "cmn_engine",
    columns_info: str = ""
) -> str:
    """
    Generate a prompt for creating DBT schema.yml file based on the template format.
    
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
    
    return prompt


@mcp.prompt()
async def generate_dbt_test_prompt(
    model_name: str,
    description: str,
    test_requirements: str = "",
    test_columns: str = "",
    test_type: str = "basic"
) -> str:
    """
    Generate a prompt for creating DBT test configuration based on the template format.
    
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
    
    return prompt


# Basic prompt returning a string (converted to user message automatically)
@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Generates a user message asking for an explanation of a topic about dbt, appengine"""
    return f"Can you please explain the concept of '{topic}'?"


if __name__ == "__main__":
    # Start an HTTP server on port 8000
    mcp.run(transport="http", host="127.0.0.1", port=8000)
    # mcp.run()
