import pyodbc
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Mapping of logical company entities to their Skyline Company Codes (IFS IDs)
COMPANIES = {
    "Bay Bayou Florida RV Resort": ["135"],
    "Sunkissed Village RV Resort": ["140", "142"],
    "Park City Mobile Homes, Inc.": ["28", "205", "24", "121", "26"],
    "The Bluffs MH & RV Resort": ["147"],
    "Jennings Realty, Inc.": ["1"],
    "Barbara Descendant's Trust": ["110"],
    "Home Sites / Ellis": ["38"],
    "Home Sites / Galaxy": ["33", "144", "145", "146"],
    "Tax Certificate Entities": ["150", "160", "180", "190"],
    "Lakeview Mobile Home Park": ["PLVMH", "19"],
    "Madison Community Resort": ["143"],
}

class SkylineIntegration:
    """
    Seamless integration with SS&C Skyline via ODBC.
    Provides read access to General Ledger data and CSV-based write access
    (the recommended method for posting to Skyline's GL to ensure validation).
    """

    def __init__(self, dsn: str = "SkylineDB", user: str = "", password: str = ""):
        """
        Initialize the connection to Skyline via ODBC.
        
        Args:
            dsn: The ODBC Data Source Name (or full connection string).
                 For Pervasive SQL, it might look like:
                 'Driver={Pervasive ODBC Interface};ServerName=YOUR_SERVER;dbq=SKYLINE_DATA_FOLDER;'
            user: Database username
            password: Database password
        """
        self.dsn = dsn
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        """Establish the ODBC connection."""
        if self.conn is None:
            # Check if dsn is a full connection string or just a DSN name
            if "Driver=" in self.dsn or "DSN=" in self.dsn:
                conn_str = self.dsn
            else:
                conn_str = f"DSN={self.dsn};Uid={self.user};Pwd={self.password};"
            
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()

    def close(self):
        """Close the ODBC connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_gl_transactions(self, company_code: str, start_date: str) -> List[Dict[str, Any]]:
        """
        Read transactions from the General Ledger Detail (GLDET).
        
        Args:
            company_code: The Skyline company code (e.g., '001')
            start_date: Start date string (YYYY-MM-DD)
            
        Returns:
            List of transaction dictionaries.
        """
        self.connect()
        query = """
            SELECT CO_CODE, GL_ACCT, POST_DATE, AMOUNT, DESC 
            FROM GLDET 
            WHERE POST_DATE >= ? AND CO_CODE = ?
        """
        self.cursor.execute(query, (start_date, company_code))
        
        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def get_chart_of_accounts(self) -> List[Dict[str, Any]]:
        """
        Read the Chart of Accounts (CHART table).
        """
        self.connect()
        query = "SELECT GL_ACCT, ACCT_DESC, ACCT_TYPE FROM CHART"
        self.cursor.execute(query)
        
        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def get_account_balances(self) -> List[Dict[str, Any]]:
        """
        Read account balances from the General Ledger Master (GLMAST).
        """
        self.connect()
        query = "SELECT GL_ACCT, CURR_BAL, BUDGET, DEPT FROM GLMAST"
        self.cursor.execute(query)
        
        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def generate_income_statement(self, company_codes: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate an Income Statement (Revenue, Expenses, Net Income) for one or more
        Skyline company codes over a specific date range.
        
        Args:
            company_codes: List of company codes/IFS IDs (e.g. ['135'])
            start_date: Start date string (YYYY-MM-DD or YYMMDD)
            end_date: End date string (YYYY-MM-DD or YYMMDD)
            
        Returns:
            Dictionary containing total revenue, total expenses, net income, and account breakdown.
        """
        self.connect()
        placeholders = ",".join("?" for _ in company_codes)
        
        # Query joining GLDET and CHART to accurately aggregate by account type
        query = f"""
            SELECT 
                c.ACCT_TYPE,
                g.GL_ACCT,
                c.ACCT_DESC,
                SUM(g.AMOUNT) as TOTAL_AMOUNT
            FROM GLDET g
            LEFT JOIN CHART c ON g.GL_ACCT = c.GL_ACCT
            WHERE g.CO_CODE IN ({placeholders})
              AND g.POST_DATE >= ? AND g.POST_DATE <= ?
            GROUP BY c.ACCT_TYPE, g.GL_ACCT, c.ACCT_DESC
        """
        
        params = list(company_codes) + [start_date, end_date]
        self.cursor.execute(query, params)
        
        revenue = 0.0
        expenses = 0.0
        breakdown = []
        
        for acct_type, gl_acct, acct_desc, total_amount in self.cursor.fetchall():
            amount = float(total_amount or 0.0)
            breakdown.append({
                "account": gl_acct,
                "description": acct_desc or "Unknown",
                "type": acct_type,
                "amount": amount
            })
            
            # Type 08 is Revenue (credits are usually negative in GL, so invert)
            if acct_type == '08' or (acct_type is None and gl_acct.startswith('3')):
                revenue -= amount
            # Type 09 is Expense (debits are positive)
            elif acct_type == '09' or (acct_type is None and gl_acct[0] in '456789'):
                expenses += amount

        return {
            "company_codes": company_codes,
            "period": (start_date, end_date),
            "revenue": revenue,
            "expenses": expenses,
            "net_income": revenue - expenses,
            "accounts": breakdown
        }

    def write_gl_import_csv(self, entries: List[Dict[str, Any]], output_filepath: str):
        """
        Write journal entries to the Skyline standard CSV import format.
        Direct SQL inserts into GLDET are discouraged because it bypasses
        Skyline's built-in validation (balancing checks, fiscal periods).
        
        Format per row:
        1. Record Type: 'GLDET' (Hardcoded)
        2. Company Code: (e.g., '001')
        3. Post Date: (e.g., '2023/10/20')
        4. Month: 'YYYY/MM'
        5. GL Account Number: (e.g., '1010-00')
        6. Transaction Date: 'YYYY/MM/DD'
        7. Description: (Up to 30 chars)
        8. Batch ID: (e.g., '1')
        9. Amount: Positive for Debit, Negative for Credit
        10. Status: 'C' (Hardcoded for "Current")
        
        Args:
            entries: List of dictionaries representing journal entries.
                     Required keys: company_code, post_date, gl_account, 
                                    description, amount
            output_filepath: Path to save the generated CSV.
        """
        with open(output_filepath, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for entry in entries:
                post_date_obj = datetime.strptime(entry['post_date'], '%Y-%m-%d')
                post_date_str = post_date_obj.strftime('%Y/%m/%d')
                month_str = post_date_obj.strftime('%Y/%m')
                
                row = [
                    'GLDET',                               # 1. Record Type
                    entry['company_code'],                 # 2. Company Code
                    post_date_str,                         # 3. Post Date
                    month_str,                             # 4. Month
                    entry['gl_account'],                   # 5. GL Account Number
                    post_date_str,                         # 6. Transaction Date
                    entry['description'][:30],             # 7. Description
                    entry.get('batch_id', '1'),            # 8. Batch ID
                    f"{float(entry['amount']):.2f}",       # 9. Amount
                    'C'                                    # 10. Status
                ]
                writer.writerow(row)

# Example usage:
if __name__ == "__main__":
    # NOTE: You will need to install pyodbc: `pip install pyodbc`
    # Ensure the "Pervasive ODBC Interface" driver is installed on this machine 
    # if connecting directly to a local/network Skyline database.
    pass
