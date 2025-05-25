from scipy.stats import norm

def probability_of_failure(beta):
    """
    Convert reliability index (beta) to probability of failure (Pf).
    
    Parameters:
        beta (float): Reliability index
    
    Returns:
        float: Probability of failure
    """
    return norm.cdf(-beta)

list = [4.1,11,8.9,8,7.1]
for beta in list:
    pf = probability_of_failure(beta)
    print(f"Probability of failure for beta = {beta}: {pf:.2e}")
