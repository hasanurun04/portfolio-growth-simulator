from flask import Flask, request, jsonify, render_template
from decimal import Decimal, getcontext

getcontext().prec = 28

app = Flask(__name__, static_folder="static", template_folder="templates")

def calc_growth(initial_amount, default_profit, default_days, additional_periods):

    profit_schedule = []

    for _ in range(default_days):
        profit_schedule.append(default_profit)

    for p in additional_periods:
        for _ in range(p["days"]):
            profit_schedule.append(p["profit"])

    total_days = len(profit_schedule)
    portfolio_values = []
    daily_profits = []
    growth_percentages = []
    profit_rates = []
    labels = []

    current_amount = initial_amount
    portfolio_values.append(float(current_amount))
    daily_profits.append(0.0)
    growth_percentages.append(0.0)
    profit_rates.append(0.0)
    labels.append(0)

    for day_index, daily_profit_rate in enumerate(profit_schedule, start=1):
        multiplier = (Decimal(1) + (daily_profit_rate / Decimal(100)))
        previous = current_amount
        current_amount = (previous * multiplier).quantize(Decimal('0.00000001'))
        daily_profit = (current_amount - previous)
        portfolio_values.append(float(current_amount))
        daily_profits.append(float(daily_profit))
        growth_percentages.append(float(((current_amount / initial_amount) - 1) * 100))
        profit_rates.append(float(daily_profit_rate))
        labels.append(day_index)

    summary = {
        "initial": float(initial_amount),
        "final": float(current_amount),
        "total_profit": float(current_amount - initial_amount),
        "total_growth_percent": float(((current_amount / initial_amount) - 1) * 100),
        "total_days": total_days
    }

    return {
        "labels": labels,
        "portfolio_values": portfolio_values,
        "daily_profits": daily_profits,
        "growth_percentages": growth_percentages,
        "profit_rates": profit_rates,
        "summary": summary
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(force=True)
    try:
        initial = Decimal(str(data.get("initialAmount", 0)))
        default_profit = Decimal(str(data.get("defaultProfitPercentage", 0)))
        default_days = int(data.get("defaultDays", 0))
        additional = data.get("additionalPeriods", [])
        add_periods = []
        for p in additional:
            add_periods.append({"profit": Decimal(str(p.get("profit", 0))), "days": int(p.get("days", 0))})
    except Exception as e:
        return jsonify({"error": "Invalid input format", "detail": str(e)}), 400

    if initial <= 0 or default_days <= 0:
        return jsonify({"error": "initialAmount and defaultDays must be positive"}), 400

    result = calc_growth(initial, default_profit, default_days, add_periods)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
