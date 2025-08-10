TRUST_TYPES = [
    "None",
    "Discretionary Trust",
    "Life Interest Trust",
    "Property Protection Trust",
]

def make_trust_clause(trust_type: str, trustees: str, beneficiaries: str, age_of_access: str, special: str) -> str:
    """
    Return a block of wording for the chosen trust type.
    NOTE: This is template wording. You must ensure final legal suitability.
    """
    trust_type = (trust_type or "None").strip()
    t = trustees.strip() or "the Trustees named in this Will"
    b = beneficiaries.strip() or "the Beneficiaries named in this Will"
    age = (age_of_access or "18").strip()

    if trust_type == "Discretionary Trust":
        return f"""
I give my Residuary Estate to {t} to hold upon discretionary trusts for the benefit of {b} (the "Discretionary Beneficiaries").

1. Discretion: The Trustees may at their absolute discretion apply income and/or capital for any one or more of the Discretionary Beneficiaries in such shares and at such times as they think fit.
2. Accumulation: Income not applied may be accumulated and added to capital during the trust period.
3. Default Beneficiaries: Subject to the above, the trust fund shall be held for {b} equally at the end of the trust period.
4. Letter of Wishes: The Trustees shall have regard to any Letter of Wishes I may leave.
""".strip()

    if trust_type == "Life Interest Trust":
        return f"""
I give my interest in the Trust Fund to {t} on trust to pay or apply the income thereof to or for the benefit of {b} (the "Life Tenant") for life, with power to advance capital for the Life Tenant's benefit at the Trustees' discretion. Subject thereto, on the Life Tenant's death the Trust Fund shall be held for the remaindermen as my Trustees shall appoint or, failing such appointment, equally between my issue contingent upon attaining age {age}.
""".strip()

    if trust_type == "Property Protection Trust":
        return f"""
I give my share and interest in my main residence to {t} to hold upon the following trusts:

1. Right of Occupation: {b} may occupy the property for life or until vacated, subject to reasonable conditions as to insurance, repairs and outgoings.
2. Power to Sell and Reinvest: The Trustees may sell, purchase or invest in an alternative residence for occupation on the same terms.
3. Remainder: On termination of the right of occupation, the Trust Fund shall be held for my residuary beneficiaries equally or as my Trustees shall appoint.
""".strip()

    # No trust selected
    return ""
