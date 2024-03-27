import pandas as pd
import numpy as np
import os

"""
To answer the following questions, make use of datasets: 
    'scheduled_loan_repayments.csv'
    'actual_loan_repayments.csv'
These files are located in the 'data' folder. 

All loans have a loan term of 2 years with an annual interest rate of 10%. Repayments are scheduled monthly.
A type 1 default will occur on a loan when a repayment is missed.
A type 2 default will occur on a loan when more than 15% of the expected total payments are unpaid for the year.

"""


def calculate_df_balances(df_scheduled,df_actual):
    """ 
        This is a utility function that creates a merged dataframe that will be used in the following questions. 
        This function will not be graded directly.

        Args:
            df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
            df_actual (DataFrame): Dataframe created from the 'actual_loan_repayments.csv' dataset
        
        Returns:
            DataFrame: A merged Dataframe 

            Columns after the merge should be: 
            ['RepaymentID', 'LoanID', 'Month', 'ActualRepayment', 'LoanAmount', 'ScheduledRepayment']

            Additional columns to be used in later questions should include: 
            ['UnscheduledPrincipal', 'LoanBalanceStart, 'LoanBalanceEnd'] 
            Note: 'LoanBalanceStart' for the first month of each loan should equal the 'LoanAmount'

            You may create other columns to assist you in your calculations. e.g:
            ['InterestPayment']

    """
    #merge the two dataframes together:
    df_merged = pd.merge(df_actual,df_scheduled)
    df_merged = df_merged.sort_values(['LoanID','Month']).reset_index().drop('index',axis=1) #Sort the columns using the loans and month columns.

    def calculate_columns(loan):
        r_pm = 0.1/12 #calculate the monly interest rate
        balance_start =[]
        interest_payment = []
        scheduled_principal =[]
        unscheduled_principal =[]
        
        for i, row in loan.iterrows():
            if  balance_start: #if the balance_start list is not empty this section of code will be executed.
                balance_start.append(balance_end[-1])
                balance_end.append(balance_start[-1]*(1+r_pm) - row['ActualRepayment'])
            else: #if the balance_start list is empty this section of code will be executed.
                balance_start = [row['LoanAmount']] #initialise the balance_start as the first element of the amount column.
                balance_end = [balance_start[-1]*(1+r_pm)-row['ActualRepayment']]
        
            interest_payment.append(balance_start[-1]*r_pm)
            scheduled_principal.append(row['ScheduledRepayment']-balance_start[-1]*r_pm)   
            unscheduled_principal.append(row['ActualRepayment']-row['ScheduledRepayment'] if (row['ActualRepayment']>row['ScheduledRepayment']) else 0.0)
        
        loan['LoanBalanceStart'] = [round(n, 2) for n in balance_start]
        loan['LoanBalanceEnd']=[round(n, 2) for n in balance_end]
        loan['InterestPayment']=[round(n, 2) for n in interest_payment]
        loan['ScheduledPrincipal']=[round(n, 2) for n in scheduled_principal]
        loan['UnscheduledPrincipal']=[round(n, 2) for n in unscheduled_principal]
        return loan

    df_balances = df_merged.groupby('LoanID').apply(calculate_columns, include_groups=False)
    df_balances= df_balances.reset_index()[['RepaymentID', 'LoanID', 'Month', 'ActualRepayment','LoanAmount', 'ScheduledRepayment',
                                         'LoanBalanceStart','LoanBalanceEnd', 'InterestPayment', 'ScheduledPrincipal','UnscheduledPrincipal']]

    return df_balances



#Do not edit these directories
root = os.getcwd()

if 'Task_2' in root:
    df_scheduled = pd.read_csv('data/scheduled_loan_repayments.csv')
    df_actual = pd.read_csv('data/actual_loan_repayments.csv')
else:
    df_scheduled = pd.read_csv('Task_2/data/scheduled_loan_repayments.csv')
    df_actual = pd.read_csv('Task_2/data/actual_loan_repayments.csv')

df_balances = calculate_df_balances(df_scheduled,df_actual)





def question_1(df_balances):
    """ 
        Calculate the percent of loans that defaulted as per the type 1 default definition 
        
        Args:
            df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        
        Returns:
            float: The percentage of defaulted loans (type 1)

    """
    #missed payments are denoted by a 0 in the ActualRepayment column.
    loans_missing_payments = len(df_balances[df_balances['ActualRepayment']==0]['LoanID'].unique())
    
    #Calculate the total amount of loans in the dataset:
    total_loans = len(df_balances['LoanID'].unique())
    
    default_rate_percent = loans_missing_payments/total_loans*100
    return default_rate_percent






def question_2(df_balances, df_scheduled=None):
    """ 
        Calculate the percent of loans that defaulted as per the type 2 default definition 
        
        Args:
            df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
            df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
        
        Returns:
            float: The percentage of defaulted loans (type 2)

    """
    #Note that only the df_balances input dataframes will be used.
    T2_margin = 12*0.15 #The number of missed payments which result in a T2 default if exceeded.

    #Calculate the number of missed payments per loan.
    missed_payments_per_loan = df_balances[df_balances['ActualRepayment']==0].groupby('LoanID').count()
    
    #Count the number of loans which has more missed payments than the allowable margin.
    T2_default_number = sum(missed_payments_per_loan['Month'] > T2_margin)
    
    #Calculate the total amount of loans in the dataset:
    total_loans = len(df_balances['LoanID'].unique())
    
    default_rate_percent = 100*T2_default_number/total_loans
    return default_rate_percent






def question_3(df_balances):
    """ 
        Calculate the anualized CPR (As a %) from the geometric mean SMM.
        SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
        CPR is calcualted as: 1 - (1- SMM_mean)^12  

        Args:
            df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

        Returns:
            float: The anualized CPR of the loan portfolio as a percent.
            
    """
    #Create a SMM column which conatins the Single Monthly Mortality Rate for every month of each loan.
    df_balances['SMM'] = df_balances['UnscheduledPrincipal']/df_balances['LoanBalanceStart']

    def geometric_mean(column):
        """" Calculate the geometric mean of a input column
        Args: 
            column (Pandas Series) : Any series containing numeric values.
        
        Returns:
            float: The geometric mean of the input series."""
        prod = 1
        for i in column:
            prod *= i
        return prod**(1/len(column))

    #Calculate the cpr_percent for the entire loan portfolio using the supplied equation [CPR = 1 - (1- SMM_mean)^12].
    cpr_percent = (1-(1-geometric_mean(df_balances['SMM']))**12)*100

    ##The Geometric mean used to calculate the mean of the SMM results in a value of 0 when the series contains one or more 0 value. For the CPR to have a 
    ##non-zero value when the geometric mean is used all the payments should contain a uncheduled payment. Since the series 
    ##contains many zeros due to unsheduled payments being scarce, arithmetic mean seams like a more appropriate solution. The following line of code
    ##can be uncommented to use the arithmetic mean which results in an annualized CPR percentage of 3.64%. However since the question specifically asks for 
    ## geometic mean the CPR value of 0 calculated using the geometric mean is returned by the function.
    # cpr_percent = (1-(1-df_balances['SMM'].mean())**12)*100
    
    return cpr_percent






def question_4(df_balances):
    """ 
        Calculate the predicted total loss for the second year in the loan term.
        Use the equation: probability_of_default * total_loan_balance * (1 - recovery_rate).
        The probability_of_default value must be taken from either your question_1 or question_2 answer. 
        Decide between the two answers based on which default definition you believe to be the more useful metric.
        Assume a recovery rate of 80% 
        
        Args:
            df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        
        Returns:
            float: The predicted total loss for the second year in the loan term.
            
    """
    #Type 1 default is chosen to use as the probability of defaults because it is a more conservative approach than the type 2 default. 
    #Thus the predicted total loss is more likely to be overestimated.
    probability_of_default = question_1(df_balances=df_balances)/100 # divide by 100 to get probability.
    recovery_rate = 0.8
    
    #The total loan balance is taken as the sum of all the outstanding loan balances at the end of the first year. 
    total_loan_balance = sum(df_balances[df_balances['Month']== 12]['LoanBalanceEnd'])

    #Use the supplied equation to calculate the predicted total loss for the second year of the loan:
    total_loss = round(probability_of_default*total_loan_balance*(1-recovery_rate),2)
    return total_loss