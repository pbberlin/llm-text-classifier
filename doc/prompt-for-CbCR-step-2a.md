----------------------
Step 2a - if yes
----------------------


Objective: 
Extract the specified numerical data from the document. 

Revenue
Number of Employees
Profit before Taxes
Taxes on Profit


---

Provide the output in a structured format as shown below.

Use the following JSON schema to express the extracted currency values.
Order the "data" elements by year ascending.

If you encounter a country such as "Domestic" or "home country" then
replace this with the country of the headquarters of the reporting company from the top or bottom of the document.

{{
    "country":         <string>,
    "data": [
        {
            "year":               <integer>,
            "revenue":            <currency:EUR>,
            "profit_before_tax":  <currency:EUR>,
            "tax_on_profit":      <currency:EUR>,
        },
        {
            "year":               <integer>,
            "revenue":            <currency:EUR>,
            "profit_before_tax":  <currency:EUR>,
            "tax_on_profit":      <currency:EUR>,
        }
    ]
}}



----------------------
Step 2b - if no
----------------------

By Country - Columns:   
Look for rows that describe the metrics 
and extract corresponding country values from the table columns.






