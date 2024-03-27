"""
The database loan.db consists of 3 tables: 
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data
    
You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

"""


def question_1():    
    
    #Make use of a JOIN to find out the `AverageIncome` per `CustomerClass`

    qry = """SELECT  credit.CustomerClass, AVG(customers.Income) AS AverageIncome FROM customers
    JOIN credit
    ON customers.CustomerID = credit.CustomerID
    GROUP BY credit.CustomerClass;"""
    
    return qry






def question_2():    
    
    #Q2: Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'. 

    qry = """
    -- Update the table to include only the full names of the provinces instead of a mixture of the full names and the povince codes.
    UPDATE customers
    SET Region = CASE
         WHEN Region = 'WC' THEN 'WesternCape'
         WHEN Region = 'FS' THEN 'FreeState'
         WHEN Region = 'EC' THEN 'EasternCape'
         WHEN Region = 'NC' THEN 'NorthernCape'
         WHEN Region = 'G' THEN 'Gauteng'
         WHEN Region = 'GT' THEN 'Gauteng'
         WHEN Region = 'NL' THEN 'KwaZuluNatal'
         WHEN Region = 'Natal' THEN 'KwaZuluNatal'
         WHEN Region = 'MP' THEN 'Mpumalanga'
         WHEN Region = 'LP'  THEN 'Limpopo'
         WHEN Region = 'NW' THEN 'NorthWest'
         ELSE Region
         END;

    -- Count and return the rejected applications per province using a JOIN function between the loans and customers columns.
    SELECT customers.Region, COUNT(DISTINCT customers.CustomerID) AS RejectedApplications
    FROM customers
    LEFT JOIN loans
    ON customers.CustomerID = loans.CustomerID 
    WHERE loans.ApprovalStatus = 'Rejected'
    GROUP BY customers.Region;"""

    return qry






def question_3():    
    
    # Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
        # `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`
    # Do not return the new table

    qry = """CREATE TABLE financing(
    CustomerID INT,
    Income INT,
    LoanAmount INT,
    LoanTerm INT,
    InterestRate DECIMAL(4,2),
    ApprovalStatus VARCHAR(20),
    CreditScore INT);

    -- Populate the columns in the financing tables using instances from the customers, loans and credit tables.
    INSERT INTO financing (CustomerID, Income, LoanAmount, LoanTerm, InterestRate, ApprovalStatus, CreditScore)
    SELECT customers.CustomerID, Income, LoanAmount, LoanTerm, InterestRate, ApprovalStatus, CreditScore
    FROM customers
    JOIN loans ON customers.CustomerID = loans.CustomerID
    JOIN credit ON customers.CustomerID = credit.CustomerID;"""

    return qry





# Question 4 and 5 are linked

def question_4():

    # Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarizes Repayments per customer per month.
    # Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    # Repayments should only occur between 6am and 6pm London Time.
    # Hint: there should be 12x CustomerID = 1.
    # Null values to be filled with 0.

    qry = """
    CREATE TABLE timeline (
    CustomerID INT,
    MonthID INT,
    MonthName VARCHAR(20),
    NumberOfRepayments INT DEFAULT 0, 
    AmountTotal INT DEFAULT 0
    );
    
    INSERT INTO timeline (CustomerID, MonthName, MonthID)
    SELECT DISTINCT c.customerID, m.MonthName, m.MonthID
    FROM customers c
    CROSS JOIN months m;
    
    UPDATE  timeline  SET 
    --Populate the table to contain monthly repayment counts of repayments that adhere to the specified time range.
    -- The time zone is also changed from the one specified in the repayments table to the London time zone.
    NumberOfRepayments = COALESCE((
        SELECT COUNT(*) 
        FROM repayments r
        WHERE (timeline.CustomerID = r.CustomerID) 
        AND EXTRACT(HOUR FROM r.RepaymentDate AT TIME ZONE r.TimeZone AT TIME ZONE 'Europe/London') BETWEEN 6 AND 18
        AND EXTRACT(MONTH FROM r.RepaymentDate AT TIME ZONE r.TimeZone AT TIME ZONE 'Europe/London') = timeline.MonthID
    ),0),
    --Populate the table to contain the total monthly payment amounts per customer for repayments that adhere to the specified time range.
    AmountTotal = COALESCE((
            SELECT SUM(r.Amount)
            FROM repayments r
            WHERE timeline.CustomerID = r.CustomerID
            AND EXTRACT(HOUR FROM r.RepaymentDate AT TIME ZONE r.TimeZone AT TIME ZONE 'Europe/London') BETWEEN 6 AND 18
            AND EXTRACT(MONTH FROM r.RepaymentDate AT TIME ZONE r.TimeZone AT TIME ZONE 'Europe/London') = timeline.MonthID
    ), 0);

    -- Remove the MonthID column from the timeline table, the column was used during the construction of the table to match the payment dates with the month names.
    ALTER TABLE timeline
    DROP COLUMN MonthID;

    -- Return the timeline table:
    SELECT * FROM timeline
    ORDER BY CustomerID;
    """

    return qry




def question_5():

    # Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
        # CustomerID, JanuaryRepayments, JanuaryTotal,...,DecemberRepayments, DecemberTotal,...etc
    # MonthRepayments columns (e.g JanuaryRepayments) should be integers
    # Hint: there should be 1x CustomerID = 1

    qry = """
    SELECT 
        CustomerID,
        SUM(CASE WHEN MonthName = 'January' THEN NumberOfRepayments END) AS JanuaryRepayments,
        SUM(CASE WHEN MonthName = 'January' THEN AmountTotal END) AS JanuaryTotal,
        SUM(CASE WHEN MonthName = 'February' THEN NumberOfRepayments END) AS FebruaryRepayments,
        SUM(CASE WHEN MonthName = 'February' THEN AmountTotal END) AS FebruaryTotal,
        SUM(CASE WHEN MonthName = 'March' THEN NumberOfRepayments END) AS MarchRepayments,
        SUM(CASE WHEN MonthName = 'March' THEN AmountTotal END) AS MarchTotal,
        SUM(CASE WHEN MonthName = 'April' THEN NumberOfRepayments END) AS AprilRepayments,
        SUM(CASE WHEN MonthName = 'April' THEN AmountTotal END) AS AprilTotal,
        SUM(CASE WHEN MonthName = 'May' THEN NumberOfRepayments END) AS MayRepayments,
        SUM(CASE WHEN MonthName = 'May' THEN AmountTotal END) AS MayTotal,
        SUM(CASE WHEN MonthName = 'June' THEN NumberOfRepayments END) AS JuneRepayments,
        SUM(CASE WHEN MonthName = 'June' THEN AmountTotal END) AS JuneTotal,
        SUM(CASE WHEN MonthName = 'July' THEN NumberOfRepayments END) AS JulyRepayments,
        SUM(CASE WHEN MonthName = 'July' THEN AmountTotal END) AS JulyTotal,
        SUM(CASE WHEN MonthName = 'August' THEN NumberOfRepayments END) AS AugustRepayments,
        SUM(CASE WHEN MonthName = 'August' THEN AmountTotal END) AS AugustTotal,
        SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments END) AS SeptemberRepayments,
        SUM(CASE WHEN MonthName = 'September' THEN AmountTotal END) AS SeptemberTotal,
        SUM(CASE WHEN MonthName = 'October' THEN NumberOfRepayments END) AS OctoberRepayments,
        SUM(CASE WHEN MonthName = 'October' THEN AmountTotal END) AS OctoberTotal,
        SUM(CASE WHEN MonthName = 'November' THEN NumberOfRepayments END) AS NovemberRepayments,
        SUM(CASE WHEN MonthName = 'November' THEN AmountTotal END) AS NovemberTotal,
        SUM(CASE WHEN MonthName = 'December' THEN NumberOfRepayments END) AS DecemberRepayments,
        SUM(CASE WHEN MonthName = 'December' THEN AmountTotal END) AS DecemberTotal
    FROM timeline
    GROUP BY customerID"""

    return qry





#QUESTION 6 and 7 are linked

def question_6():

    # The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    # Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    # relation to the corresponding CustomerID.

    # Utilize a window function to correct this mistake in a new `CorrectedAge` column.
    # Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender` 
    # Also return a result set for this table
    # Null values can be input manually

    qry = """
    CREATE TABLE corrected_customers (
        CustomerID INT,
        Age INT,
        CorrectedAge INT,
        Gender VARCHAR(8));

        --Populate the corrected_customer table columns using the customers table and a offset value for the CorrectedAge column.
    INSERT INTO corrected_customers(CustomerID, Age, CorrectedAge, Gender)
    SELECT 
        CustomerID, 
        Age,
        LEAD(Age,-2) OVER (ORDER BY CustomerID),
        Gender
    FROM customers;
    
    SELECT * FROM corrected_customers;
    """

    return qry


def question_7():

    # Create a column called 'AgeCategory' that categorizes customers by age 
    # Age categories should be as follows:
        # Teen: x < 20
        # Young Adult: 20 <= x < 30
        # Adult: 30 <= x < 60
        # Pensioner: x >= 60
    # Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    # The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6 
    # Customers with no repayments should be included as 0 in the result.

    qry = """
    -- Add the AgeCategory column to the corrected_customers table. 
    ALTER TABLE corrected_customers
    ADD COLUMN AgeCategory VARCHAR(20);
    
    -- Populate the AgeCategory column based on corrected age ranges
    UPDATE corrected_customers
    SET AgeCategory = CASE
        WHEN CorrectedAge < 20 THEN 'Teen'
        WHEN CorrectedAge >= 20 AND CorrectedAge < 30 THEN 'Young Adult'
        WHEN CorrectedAge >= 30 AND CorrectedAge < 60 THEN 'Adult'
        WHEN CorrectedAge >= 60 THEN 'Pensioner'
        ELSE NULL
        END;
    
    -- Add the Rank column to store the ranking based on the total number of repayments made per age group
    ALTER TABLE corrected_customers
    ADD COLUMN Rank INT;
    
    -- Update the 'Rank' column using a window function
    WITH RepaymentCounts AS (
        SELECT 
            cc.CustomerID,
            cc.AgeCategory,
            COALESCE(COUNT(r.CustomerID), 0) AS RepaymentCount,
            DENSE_RANK() OVER (PARTITION BY cc.AgeCategory ORDER BY COALESCE(COUNT(r.CustomerID), 0) DESC) AS Rank
        FROM corrected_customers cc
        -- Use a left join because there are customers in the customers table which are not present in the repayments table.
        LEFT JOIN repayments r ON cc.CustomerID = r.CustomerID
        GROUP BY cc.CustomerID, cc.AgeCategory
    )
    UPDATE corrected_customers AS c1
    SET Rank = COALESCE((SELECT RepaymentCounts.Rank FROM RepaymentCounts WHERE RepaymentCounts.CustomerID = c1.CustomerID AND RepaymentCounts.AgeCategory = c1.AgeCategory), 0);
    
    -- Update the rank to 0 for customers who have not made any payments.
    UPDATE corrected_customers AS c2
    SET Rank = 0
    WHERE c2.CustomerID NOT IN (SELECT CustomerID FROM repayments);
    
    
    SELECT * FROM corrected_customers;"""

    return qry
