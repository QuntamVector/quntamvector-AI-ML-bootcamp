# ============================================
# 🏦 PYTHON BANK ATM - STREAMLIT APPLICATION
# ============================================

import streamlit as st
import time

# --------------------------------------------
# PAGE CONFIG
# --------------------------------------------
st.set_page_config(
    page_title="Python Bank ATM",
    page_icon="🏧",
    layout="centered"
)

# --------------------------------------------
# SAMPLE DATABASE
# --------------------------------------------
accounts = {
    "123456": {"pin": "1234", "balance": 15000, "name": "Pritam"},
    "789615": {"pin": "5678", "balance": 30000, "name": "Manasa"},
    "354647": {"pin": "9012", "balance": 40000, "name": "Rohit"},
}

# --------------------------------------------
# SESSION STATE VARIABLES
# --------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "card_number" not in st.session_state:
    st.session_state.card_number = ""

if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []

# --------------------------------------------
# HEADER
# --------------------------------------------
st.markdown(
    """
    <h1 style='text-align:center;color:#00BFFF;'>
    🏧 PYTHON BANK ATM
    </h1>
    <hr>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------
# LOGIN SECTION
# --------------------------------------------
if not st.session_state.logged_in:

    st.subheader("🔐 Login to Your Account")

    card_number = st.text_input("Enter Card Number")

    pin = st.text_input("Enter ATM PIN", type="password")

    login_btn = st.button("Login")

    if login_btn:

        if card_number in accounts:

            account = accounts[card_number]

            if st.session_state.attempts >= 3:
                st.error("🚫 Card Blocked Due To Multiple Wrong Attempts")
                st.stop()

            if pin == account["pin"]:

                st.session_state.logged_in = True
                st.session_state.card_number = card_number
                st.session_state.attempts = 0

                st.success("✅ Login Successful")
                time.sleep(1)
                st.rerun()

            else:
                st.session_state.attempts += 1

                remaining = 3 - st.session_state.attempts

                if remaining > 0:
                    st.error(
                        f"❌ Wrong PIN. Remaining Attempts: {remaining}"
                    )
                else:
                    st.error(
                        "🚫 Card Blocked! Too Many Wrong Attempts"
                    )

        else:
            st.error("❌ Invalid Card Number")


# --------------------------------------------
# ATM DASHBOARD
# --------------------------------------------
else:

    card_number = st.session_state.card_number
    account = accounts[card_number]

    st.success(f"👋 Welcome {account['name']}")

    st.markdown("---")

    # ----------------------------------------
    # SIDEBAR
    # ----------------------------------------
    menu = st.sidebar.radio(
        "📌 Select Option",
        [
            "🏦 Account Details",
            "💰 Check Balance",
            "💸 Withdraw Money",
            "💵 Deposit Money",
            "📜 Transaction History",
            "🚪 Logout"
        ]
    )

    # ----------------------------------------
    # ACCOUNT DETAILS
    # ----------------------------------------
    if menu == "🏦 Account Details":

        st.subheader("🏦 Account Information")

        st.info(f"👤 Name : {account['name']}")
        st.info(f"💳 Card Number : {card_number}")
        st.info(f"💰 Balance : Rs {account['balance']}")

    # ----------------------------------------
    # CHECK BALANCE
    # ----------------------------------------
    elif menu == "💰 Check Balance":

        st.subheader("💰 Available Balance")

        st.success(
            f"Your Current Balance is Rs {account['balance']}"
        )

    # ----------------------------------------
    # WITHDRAW MONEY
    # ----------------------------------------
    elif menu == "💸 Withdraw Money":

        st.subheader("💸 Withdraw Cash")

        amount = st.number_input(
            "Enter Amount",
            min_value=0,
            step=100
        )

        withdraw_btn = st.button("Withdraw")

        if withdraw_btn:

            if amount <= 0:
                st.error("❌ Amount Must Be Greater Than 0")

            elif amount % 100 != 0:
                st.error("❌ Amount Must Be Multiple Of 100")

            elif amount > 10000:
                st.error("❌ Maximum Rs 10000 Per Transaction")

            elif amount > account["balance"]:
                st.error("❌ Insufficient Balance")

            else:

                account["balance"] -= amount

                st.session_state.transaction_history.append(
                    f"Withdrawn Rs {amount}"
                )

                st.success(
                    f"✅ Rs {amount} Withdrawn Successfully"
                )

                st.info(
                    f"💰 Remaining Balance : Rs {account['balance']}"
                )

    # ----------------------------------------
    # DEPOSIT MONEY
    # ----------------------------------------
    elif menu == "💵 Deposit Money":

        st.subheader("💵 Deposit Cash")

        deposit = st.number_input(
            "Enter Deposit Amount",
            min_value=0,
            step=100
        )

        deposit_btn = st.button("Deposit")

        if deposit_btn:

            if deposit <= 0:
                st.error("❌ Deposit Amount Must Be Greater Than 0")

            else:

                account["balance"] += deposit

                st.session_state.transaction_history.append(
                    f"Deposited Rs {deposit}"
                )

                st.success(
                    f"✅ Rs {deposit} Deposited Successfully"
                )

                st.info(
                    f"💰 Updated Balance : Rs {account['balance']}"
                )

    # ----------------------------------------
    # TRANSACTION HISTORY
    # ----------------------------------------
    elif menu == "📜 Transaction History":

        st.subheader("📜 Transaction History")

        if st.session_state.transaction_history:

            for txn in reversed(
                st.session_state.transaction_history
            ):
                st.write(f"✅ {txn}")

        else:
            st.warning("No Transactions Yet")

    # ----------------------------------------
    # LOGOUT
    # ----------------------------------------
    elif menu == "🚪 Logout":

        logout_btn = st.button("Logout")

        if logout_btn:

            st.session_state.logged_in = False
            st.session_state.card_number = ""

            st.success("✅ Logged Out Successfully")

            time.sleep(1)

            st.rerun()

# --------------------------------------------
# FOOTER
# --------------------------------------------
st.markdown("---")
st.caption("🏦 Secure Banking System Using Streamlit")