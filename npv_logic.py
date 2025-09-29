def npv_dcf_pgr(revenue, ebitda, capex, pgr, wacc, cash_adv):
    years = len(revenue)
    cash_flows = []
    
    for t in range(1, years + 1):
        cf = (revenue[t-1] * ebitda[t-1] - capex[t-1])*(1 - 0.28)
        cash_flows.append(cf / (1 + wacc)**(t-cash_adv))
    
    # Terminal value
    terminal_value = (cash_flows[-1] * (1 + pgr)) / (wacc - pgr)
    
    npv = sum(cash_flows) + terminal_value
    
    return npv, terminal_value, cash_flows