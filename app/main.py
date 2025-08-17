from fastapi import FastAPI, HTTPException
from typing import Any, Dict, List
import os

try:
    import pytds
except Exception as import_error:  # pragma: no cover
    pytds = None  # type: ignore


app = FastAPI(title="User Dashboard API", version="1.0.0")


def str_to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    return normalized in {"1", "true", "t", "yes", "y"}


def get_db_connection():
    host = os.getenv("DB_HOST")
    port_str = os.getenv("DB_PORT", "1433")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    encrypt = str_to_bool(os.getenv("DB_ENCRYPT", "false"))
    trust_server_cert = str_to_bool(os.getenv("DB_TRUST_SERVER_CERT", "false"))

    if pytds is None:
        raise HTTPException(status_code=500, detail="Database driver not installed. Ensure 'python-tds' is installed.")

    if not host or not database or not user or not password:
        raise HTTPException(
            status_code=500,
            detail="Database configuration missing. Set DB_HOST, DB_NAME, DB_USER, DB_PASSWORD (and optionally DB_PORT, DB_ENCRYPT, DB_TRUST_SERVER_CERT).",
        )

    try:
        port = int(port_str)
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid DB_PORT value: {port_str}")

    try:
        conn = pytds.connect(
            server=host,
            database=database,
            user=user,
            password=password,
            port=port,
            as_dict=True,
            encrypt=encrypt,
            trustservercert=trust_server_cert,
        )
        return conn
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to connect to database: {exc}") from exc


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/user-dashboard/{employee_id}")
def get_user_dashboard(employee_id: int) -> Dict[str, List[Dict[str, Any]]]:
    conn = get_db_connection()
    # Ensure connection is closed after use
    try:
        with conn:
            cursor = conn.cursor()
            try:
                # Execute the stored procedure: [Letshelp].[sp_GetUserDashboard] @Param1 = employee_id
                cursor.callproc("Letshelp.sp_GetUserDashboard", (employee_id,))
                rows = cursor.fetchall()
                # rows are list[dict] when as_dict=True; FastAPI can serialize datetimes and decimals
                return {"data": rows}
            except Exception as exec_exc:
                raise HTTPException(status_code=500, detail=f"Stored procedure execution failed: {exec_exc}") from exec_exc
    finally:
        try:
            conn.close()
        except Exception:
            pass