def calculate_travel_fund_saving(total_saving, 
                                  travel_fund_goal, 
                                  saving_goal, 
                                  min_travel_saving):

    if total_saving <= saving_goal / 2:
        return 0
    elif total_saving < travel_fund_goal + saving_goal:
        return min(travel_fund_goal, max(min_travel_saving, total_saving - saving_goal))
    else:
        return travel_fund_goal


def savings_formula(total_saving, 
                      travel_fund_goal, 
                      saving_goal, 
                      min_travel_saving, 
                      rbc_saving, 
                      retirement_saving_pct):
   

    # Travel Saving
    travel_saving = calculate_travel_fund_saving(
        total_saving, 
        travel_fund_goal, 
        saving_goal, 
        min_travel_saving
    )

    # Remaining after fixed RBC and travel fund savings
    remaining = total_saving - travel_saving - rbc_saving

    # Retirement Saving
    retirement_saving = round(remaining * retirement_saving_pct, 2)

    # Medium-term Saving
    medium_term_saving = round(remaining * (1 - retirement_saving_pct), 2)

    return travel_saving, retirement_saving, medium_term_saving
