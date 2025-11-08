from modules.cashflow_unbooked.transaction_form import record_saving_transaction

def record_deposit_for_review(reviewed_data: dict):
    """
    Prepares the cashflow deposit data based on the reviewed income data 
    and records it into the session state for immediate review.
    
    Args:
        reviewed_data: A dictionary containing the processed income data.
    """
    
    # 1. Extract dynamic data from the reviewed income
    transaction_date = reviewed_data['date']
    amount = reviewed_data['amount']
    
    # 2. Define static/default values for the deposit transaction
    account_name = "RBC Chequing"
    transaction_type = "Deposit"
    purpose = "Income"
    source_notes = None 
    
    # 3. Call the external function to record the transaction to session state
    # Note: transfer_to_account is implicitly None if not passed, but 
    # we follow the original function's required parameters if any.
    record_saving_transaction(
        transaction_date, 
        account_name, 
        transaction_type, # which is "Deposit"
        amount, 
        purpose, 
        source_notes
    )