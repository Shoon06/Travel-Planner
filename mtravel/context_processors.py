def currency_processor(request):
    """Add currency formatting to all templates"""
    def format_mmk(amount):
        """Format amount as Myanmar Kyat"""
        try:
            # Format with commas for thousands
            amount = float(amount)
            return f"MMK {amount:,.0f}".replace(",", ",")
        except:
            return f"MMK {amount}"
    
    return {
        'format_mmk': format_mmk,
        'currency_symbol': 'MMK',
        'currency_name': 'Myanmar Kyat'
    }