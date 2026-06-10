from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

# ==========================
# DASHBOARD PAGE
# ==========================
@app.route("/")
def dashboard():

    df = pd.read_csv(
        "outputs/final_customer_scorecard.csv"
    )

    total_customers = len(df)

    high_risk = len(
        df[df["risk_level"] == "High Risk"]
    )

    enterprise = len(
        df[df["enterprise_customer"] == True]
    )

    offers_sent = len(
        df[df["recommended_offer"] != "No Offer Needed"]
    )

    top_risk = df[
        df["risk_level"] == "High Risk"
    ].head(10)

    return render_template(
        "dashboard.html",
        total_customers=total_customers,
        high_risk=high_risk,
        enterprise=enterprise,
        offers_sent=offers_sent,
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

        df = pd.read_csv(
            "outputs/final_customer_scorecard.csv"
        )

        # Search multiple customer IDs
        matched_rows = []

        for cid in id_list:

            temp = df[
                df["msisdn"].str.contains(
                    cid,
                    case=False,
                    na=False
                )
            ]

            matched_rows.append(temp)

        if len(matched_rows) > 0:

            result = pd.concat(
                matched_rows,
                ignore_index=True
            ).drop_duplicates()

        else:

            result = pd.DataFrame()

        if len(result) > 0:

            customers = result.to_dict("records")

            # ==========================
            # REVENUE COMPARISON CHART
            # ==========================
            customer_names = result["msisdn"]
            revenues = result["total_revenue"]

            plt.figure(figsize=(10, 5))

            plt.bar(
                customer_names,
                revenues
            )

            plt.title(
                "Customer Revenue Comparison"
            )

            plt.xlabel("Customer ID")
            plt.ylabel("Total Revenue")

            plt.xticks(rotation=90)

            plt.tight_layout()

            plt.savefig(
                "static/customer_comparison.png"
            )

            plt.close()

            # ==========================
            # EMAIL PREVIEW
            # ==========================
            if len(result) == 1:

                customer_row = result.iloc[0]

                email_preview = customer_row[
                    "email_text"
                ]

    return render_template(
        "customer.html",
        customers=customers,
        email_preview=email_preview
    )

# ==========================
# ENTERPRISE PAGE
# ==========================
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
        customers=enterprise_df.to_dict(
            "records"
        )
    )


# ==========================
# OUTREACH PAGE
# ==========================
@app.route("/outreach")
def outreach():

    df = pd.read_csv(
        "outputs/final_customer_scorecard.csv"
    )

    outreach_df = df[
        df["customer_segment"]
        == "Outreach Customer"
    ]

    return render_template(
        "outreach.html",
        customers=outreach_df.to_dict(
            "records"
        )
    )


# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    app.run(debug=True)