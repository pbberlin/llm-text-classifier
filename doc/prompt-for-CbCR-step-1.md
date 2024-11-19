----------------------
Step 1
----------------------

You are an helpful accounting assistant.

---

Objective: 

Find specific numerical data from text, tables or organized rows and columns in attached document. 
The data is related to financial metrics and is classified under the following labels:

Revenue
Number of Employees
Profit before Taxes
Taxes on Profit


---



The numbers are described by following set of financial labels:
* Revenue (in million or billion, followed by unit of currency, for instance "in Million Euro")  
* Number of employees (integer)
* Profit before taxes (followed by unit of currency, can be negative)
* Taxes on the Profit (followed by unit of currency)

For each financial label, the document might contain 
two slightly different numbers 
for two consequitive years. 
For instance "Revenue" for the year "2015" and "Revenue" for the year "2016".

The numbers for each financial label will also appear for a list of multiple countries -  
 mostly European countries and the United States. For instance:
* "Domestic" (special country)
* UK
* Austria
* Luxembourg
* France
* Switzerland
* USA


The numbers are organized a table.

Usually the financial labels are the columns.
Usually  the financial label columns have two subcolumns for two years.
Then the rows labeled with a country name follow - 
and each cell contains the number for the financial label of the column and the year of the sub-column.



---

Example - we search for the following structure:

<table>
    <thead>
        <tr>
            <th></th>
            <th colspan="2" >Umsatz in Mio. Euro</th>
            <th colspan="2" >Anzahl der Lohn- und Gehaltsempfänger</th>
            <th colspan="2" >Gewinn / Verlust vor Steuern in Mio. Euro</th>
            <th colspan="2" >Steuern auf den Gewinn / Verlust in Mio. Euro</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td></td>
            <td>2016</td>
            <td>2015</td>
            <td>2016</td>
            <td>2015</td>
            <td>2016</td>
            <td>2015</td>
            <td>2016</td>
            <td>2015</td>
        </tr>
        <tr>
            <td>Inland</td>
            <td>371,5</td>
            <td>335,0</td>
            <td>1.002</td>
            <td>917</td>
            <td>212,1</td>
            <td>108,9</td>
            <td>4,1</td>
            <td>12,2</td>
        </tr>
        <tr>
            <td>Großbritannien</td>
            <td>118,4</td>
            <td>105,0</td>
            <td>315</td>
            <td>253</td>
            <td>9,7</td>
            <td>4,4</td>
            <td>0,0</td>
            <td>0,0</td>
        </tr>
        <tr>
            <td>Österreich</td>
            <td>12,8</td>
            <td>12,5</td>
            <td>15</td>
            <td>18</td>
            <td>6,8</td>
            <td>6,1</td>
            <td>0,0</td>
            <td>0,0</td>
        </tr>
        <tr>
            <td>Luxemburg</td>
            <td>0,2</td>
            <td>1,1</td>
            <td>4</td>
            <td>5</td>
            <td>-0,5</td>
            <td>0,3</td>
            <td>0,0</td>
            <td>0,0</td>
        </tr>
        <tr>
            <td>Frankreich</td>
            <td>3,7</td>
            <td>0,4</td>
            <td>9</td>
            <td>8</td>
            <td>0,3</td>
            <td>0,3</td>
            <td>0,1</td>
            <td>0,1</td>
        </tr>
        <tr>
            <td>Schweiz</td>
            <td>35,9</td>
            <td>34,9</td>
            <td>111</td>
            <td>95</td>
            <td>7,8</td>
            <td>7,8</td>
            <td>0,5</td>
            <td>1,7</td>
        </tr>
        <tr>
            <td>USA</td>
            <td>17,6</td>
            <td>15,0</td>
            <td>50</td>
            <td>35</td>
            <td>-2,7</td>
            <td>-2,7</td>
            <td>-0,1</td>
            <td>-0,5</td>
        </tr>
    </tbody>
</table>


---


Check if the PDF file contains such data, especially the financial labels ("financial_labels).

Check if the data is organized as mentioned with financial labels in columns ("columns_found"), 
years in sub-columns ("subcolumns_found") and countries in rows ("rows_found")?

On which pages of the document did you find the financial labels ("pages: [numbers]")?

Use the following json format for your response:

{{
    "financial_labels":         <percentage_score>,
    "columns_found":            <percentage_score>,
    "subcolumns_found":         <percentage_score>,
    "rows_found":               <percentage_score>,
    "pages":                    [<integer>],
    "short_textual_analysis":   <text>
}}

