----------------------
Step 2b - if yes
----------------------

Objective: 
Extract the specified numerical data from the document. 

Revenue
Number of Employees
Profit before Taxes
Taxes on Profit

Provide the output in a format as shown below.

---

Detailed instructions


Use following markdown as template structure for the input.


Combined the structure with the data from the document.


Substitute the placeholders <year-1> wiht the earlier year from the source document. 
Substitute <year-2> with the following year. 

If you encounter a country such as "Domestic" or "home country" then
replace this with the country of the headquarters of the reporting company from the top or bottom of the document.


Render the result as an HTML table.
Dont show the HTML code - but show the table.



|            | revenue <year-1> | revenue <year-2> | employees <year-1> | employees <year-2> | profit-before-taxes <year-1> | profit-before-taxes <year-2> | taxes-on-profit <year-1> | taxes-on-profit <year-2> |
|------------|------------------|------------------|--------------------|--------------------|------------------------------|------------------------------|--------------------------|--------------------------|
| country 1  | <amount>         | <amount>         | <amount>           | <amount>           | <amount>                     | <amount>                     | <amount>                 | <amount>                 |
| country 2  | <amount>         | <amount>         | <amount>           | <amount>           | <amount>                     | <amount>                     | <amount>                 | <amount>                 |
| country 3  | <amount>         | <amount>         | <amount>           | <amount>           | <amount>                     | <amount>                     | <amount>                 | <amount>                 |



