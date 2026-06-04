from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

# ==========================
# DASHBOARD PAGE
# ==========================
@app.route("/")
def dashboard():

    df = pd.read_csv("outputs/final_customer_scorecard.csv")

    total_customers = len(df)

    high_drop = len(df[df["bill_drop_label"] == "High Drop"])

    enterprise = len(df[df["enterprise_customer"] == True])

    emails_sent = len(df[df["email_sent"] == True])

    top_risk = df.sort_values(
        by="bill_drop",
        ascending=False
    ).head(10)

    return render_template(
        "dashboard.html",
        total_customers=total_customers,
        high_drop=high_drop,
        enterprise=enterprise,
        emails_sent=emails_sent,
        top_risk=top_risk.to_dict("records")
    )


# ==========================
# CUSTOMER DETAILS PAGE
# ==========================
@app.route("/customer", methods=["GET", "POST"])
def customer():

    customers = None
    email_preview = None

    if request.method == "POST":

        customer_ids = request.form["customer_ids"]

        id_list = [
            x.strip()
            for x in customer_ids.split(",")
        ]

        df = pd.read_csv("outputs/final_customer_scorecard.csv")

        result = df[df["customerID"].isin(id_list)]

        if len(result) > 0:

            customers = result.to_dict("records")

            # ==========================
            # COMPARISON CHART
            # ==========================
            customer_names = result["customerID"]
            predicted_bills = result["predicted_next_bill"]

            plt.figure(figsize=(8, 4))

            plt.bar(customer_names, predicted_bills)

            plt.title("Predicted Bill Comparison")
            plt.xlabel("Customer ID")
            plt.ylabel("Predicted Bill")
            plt.xticks(rotation=45)

            plt.tight_layout()

            plt.savefig("static/customer_comparison.png")
            plt.close()

            # ==========================
            # EMAIL PREVIEW
            # ==========================
            if len(result) == 1:

                customer = result.iloc[0]

                email_preview = f"""
Dear Customer,

We value your relationship with us.

Our system predicts a change in your upcoming bill.

Recommended Offer:
{customer['recommended_offer']}

Predicted Next Bill:
{customer['predicted_next_bill']}

Bill Drop:
{customer['bill_drop']}

Thank you for choosing our telecom services.

Telecom Customer Success Team
"""

    return render_template(
        "customer.html",
        customers=customers,
        email_preview=email_preview
    )
@app.route("/enterprise")
def enterprise():

    df = pd.read_csv(
        "outputs/final_customer_scorecard.csv"
    )

    enterprise_df = df[
        df["enterprise_customer"] == True
    ]

    return render_template(
        "enterprise.html",
        customers=enterprise_df.to_dict("records")
    )


@app.route("/outreach")
def outreach():

    df = pd.read_csv(
        "outputs/final_customer_scorecard.csv"
    )

    outreach_df = df[
        df["customer_segment"] == "Outreach Customer"
    ]

    return render_template(
        "outreach.html",
        customers=outreach_df.to_dict("records")
    )



if __name__ == "__main__":
    app.run(debug=True)