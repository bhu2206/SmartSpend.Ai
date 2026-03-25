import streamlit as st
import pandas as pd
from model import predict_expense

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="SmartSpend AI", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.stMetric {
    background-color: #1e1e1e;
    padding: 10px;
    border-radius: 10px;
}
[data-testid="stMetricValue"] {
    color: #00FFAA !important;
    font-size: 28px;
    font-weight: bold;
}
[data-testid="stMetricLabel"] {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- LOGIN / REGISTER ----------
def login_register():
    st.title("🔐 SmartSpend AI")

    menu = st.radio("Choose Option", ["Login", "Register"])

    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number").replace("-", "").strip()
    account = st.text_input("Account Number").strip()
    dob = st.date_input("Date of Birth")

    # ---------------- REGISTER ----------------
    if menu == "Register":
       if st.button("Register"):

        if not name or not phone or not account:
            st.error("❌ Please fill all fields properly!")
            return

        try:
            users = pd.read_csv("users.csv")
        except:
            users = pd.DataFrame(columns=["Name", "Phone", "Account", "DOB"])

        new_user = pd.DataFrame([[name, str(phone), str(account), dob]],
                                columns=["Name", "Phone", "Account", "DOB"])

        users = pd.concat([users, new_user], ignore_index=True)
        users.to_csv("users.csv", index=False)

        st.success("✅ Registered Successfully!")
    # ---------------- LOGIN ----------------
    if menu == "Login":
        if st.button("Login"):
            try:
                users = pd.read_csv("users.csv")

                # 🔥 FORCE STRING MATCH
                users["Phone"] = users["Phone"].astype(str)
                users["Account"] = users["Account"].astype(str)

                phone_input = str(phone)
                account_input = str(account)

                match = users[
                    (users["Phone"] == phone_input) &
                    (users["Account"] == account_input)
                ]

                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user = match.iloc[0].to_dict()
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    option = st.sidebar.selectbox(
                    "Choose",
    ["👤 Profile", "➕ Add Expense", "📊 Dashboard", "🔮 Prediction"]
)
                    st.error("❌ Invalid credentials")
                    st.sidebar.write(f"👤 Welcome, {st.session_state.user['Name']}")
            except Exception as e:
                st.error(f"Error: {e}")
                st.write(users)
                phone = st.text_input("Phone Number").replace("-", "").strip()
# ---------- LOAD DATA ----------
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except:
        df = pd.DataFrame(columns=["Date", "Category", "Amount"])
    return df

# =========================================================
# 🔐 MAIN CONTROL
# =========================================================
if not st.session_state.logged_in:
    login_register()   # ✅ FIXED HERE

else:
    st.title("💸 SmartSpend AI")

    df = load_data()

    # ---------- SIDEBAR ----------
    st.sidebar.title("📂 Navigation")

    option = st.sidebar.selectbox(
        "Choose",
        ["➕ Add Expense", "📊 Dashboard", "🔮 Prediction"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        st.subheader("👤 User Profile")
        user = st.session_state.user

        col1, col2 = st.columns(2)

        col1.metric("👤 Name", user["Name"])
        col2.metric("📱 Phone", user["Phone"])

        col1.metric("🏦 Account", user["Account"])
        col2.metric("🎂 DOB", user["DOB"])
    # =========================================================
    # ➕ ADD EXPENSE
    # =========================================================
    if option == "➕ Add Expense":

        st.subheader("➕ Add Expense")

        date = st.date_input("Select Date")
        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Rent", "Bills", "Other"]
        )
        amount = st.number_input("Amount", min_value=0)

        if st.button("Add Expense"):
            new_data = pd.DataFrame([[date, category, amount]],
                                    columns=["Date", "Category", "Amount"])

            new_data.to_csv("data.csv", mode='a', header=False, index=False)
            st.success("✅ Expense added successfully!")

    # =========================================================
    # 📊 DASHBOARD
    # =========================================================
    elif option == "📊 Dashboard":

        st.subheader("📊 Dashboard")

        if df.empty:
            st.warning("No data available. Add expenses first!")
        else:
            col1, col2 = st.columns(2)

            total = df["Amount"].sum()
            avg = df["Amount"].mean()

            col1.metric("💰 Total Spending", f"₹{total}")
            col2.metric("📈 Average Spending", f"₹{avg:.2f}")

            st.divider()

            st.subheader("📋 All Expenses")
            st.write(df)

            category_sum = df.groupby("Category")["Amount"].sum()

            st.subheader("📊 Spending by Category")
            st.bar_chart(category_sum)

            st.subheader("🧩 Expense Distribution")
            st.pyplot(category_sum.plot.pie(autopct='%1.1f%%').figure)

            st.divider()

            max_category = category_sum.idxmax()
            st.info(f"💡 You spend most on **{max_category}**")

            # 🚨 Alerts
            if avg > 300:
                st.warning("⚠️ Your average spending is high!")

            if max_category == "Shopping":
                st.warning("🛍️ Shopping expenses are dominating!")

            # 💸 Budget Feature
            budget = st.number_input("Set Monthly Budget (₹)", min_value=0)

            if budget > 0:
                if total > budget:
                    st.error("🚨 Budget exceeded!")
                elif total > 0.8 * budget:
                    st.warning("⚠️ Close to budget limit!")
                else:
                    st.success("✅ Within budget")

            # 📅 Monthly Trend
            df["Date"] = pd.to_datetime(df["Date"])
            monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()

            st.subheader("📅 Monthly Spending Trend")
            st.line_chart(monthly)

            # 📥 Download
            st.download_button(
                label="📥 Download Report",
                data=df.to_csv(index=False),
                file_name="expense_report.csv",
                mime="text/csv"
            )

    # =========================================================
    # 🔮 PREDICTION
    # =========================================================
    elif option == "🔮 Prediction":

        st.subheader("🔮 Expense Prediction")

        pred = predict_expense()

        if pred is None:
            st.warning("Add at least 5 expenses for prediction!")
        else:
            st.metric("📅 Predicted Expense (Next Week)", f"₹{pred:.2f}")

            if pred > df["Amount"].mean():
                st.warning("⚠️ Spending may increase next week!")
            else:
                st.success("✅ Spending looks stable!")
