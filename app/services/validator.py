"""AST-based SQL validation using sqlglot."""
import sqlglot
import sqlglot.expressions as exp
from typing import Optional


def validate_sql_ast(sql: str) -> Optional[str]:
    """Validate SQL string using AST parsing.
    
    Returns error message or None if valid read-only query.
    """
    stripped = sql.strip()
    if not stripped:
        return "Empty SQL statement"
        
    try:
        # Parse SQL dialect
        statements = sqlglot.parse(stripped, read="sqlite")
        
        # Filter out None which might result from empty statements or comments
        statements = [s for s in statements if s is not None]
        
        if not statements:
            return "Empty SQL statement"
            
        if len(statements) > 1:
            return "Multiple SQL statements are not allowed"
            
        statement = statements[0]
        
        # strictly enforce Select (which includes WITH clauses) or Pragmas
        if not isinstance(statement, (exp.Select, exp.Pragma)):
            return f"Only SELECT queries are allowed (found {statement.key.upper()})"
            
        # Deep inspection for any nested modifying nodes (e.g. in subqueries or CTEs)
        modifying_types = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Alter,
            exp.Create,
            exp.Command,
            exp.Commit,
            exp.Rollback,
            exp.Transaction,
        )
        
        for node in statement.find_all(exp.Expression):
            if isinstance(node, modifying_types):
                return f"Write operations are not allowed: {node.key.upper()} node found in AST"
                
    except sqlglot.errors.ParseError as e:
        return f"SQL parsing error: {str(e)}"
        
    return None
