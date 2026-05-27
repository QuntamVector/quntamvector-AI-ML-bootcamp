import streamlit as st
from datetime import datetime, date

st.title("🚆 Railway Ticket Booking System")

# Seat availability
seats = {
    "Mumbai-Delhi": 45,
    "Delhi-Bangalore": 12,
    "Chennai-Hyderabad": 3
}

# Base prices
prices = {
    "Mumbai-Delhi": 1200,
    "Delhi-Bangalore": 1800,
    "Chennai-Hyderabad": 1500
}

# User Inputs
source = st.selectbox("Select Source City", ["Mumbai", "Delhi", "Chennai"])
destination = st.selectbox("Select Destination City", ["Delhi", "Bangalore", "Hyderabad"])
travel_date = st.date_input("Select Travel Date", min_value=date.today())
age = st.number_input("Enter Passenger Age", min_value=1, max_value=120)

if st.button("Check Fare & Availability"):

    route = f"{source}-{destination}"

    if route not in seats:
        st.error("❌ Route not available.")
    else:
        base_price = prices[route]
        total_price = base_price

        # Passenger category
        discount = 0
        passenger_type = "Adult"

        if age >= 60:
            discount = base_price * 0.40
            passenger_type = "Senior Citizen"
        elif age < 12:
            discount = base_price * 0.50
            passenger_type = "Child"

        total_price -= discount

        # Weekend surcharge
        weekend_charge = 0
        day_name = travel_date.strftime("%A")

        if travel_date.weekday() >= 5:
            weekend_charge = total_price * 0.10
            total_price += weekend_charge

        # Tatkal surcharge
        tatkal_charge = 0
        days_left = (travel_date - date.today()).days

        if 0 <= days_left <= 2:
            tatkal_charge = total_price * 0.30
            total_price += tatkal_charge

        st.subheader("🎫 Ticket Summary")

        st.write(f"*Journey:* {source} → {destination}")
        st.write(f"*Date:* {day_name}")
        st.write(f"*Passenger:* {passenger_type}")
        st.write(f"*Base Price:* ₹{base_price:.2f}")

        if discount > 0:
            st.write(f"*Discount:* -₹{discount:.2f}")

        if weekend_charge > 0:
            st.write(f"*Weekend Surcharge:* +₹{weekend_charge:.2f}")

        if tatkal_charge > 0:
            st.write(f"*Tatkal Charge:* +₹{tatkal_charge:.2f}")

        st.success(f"💰 Total Fare: ₹{total_price:.2f}")

        # Seat Availability
        available = seats[route]

        if available < 5:
            st.warning(f"⚠️ Only {available} seats left! Book fast!")
        else:
            st.info(f"Seats Available: {available}")

        # Payment Section
        st.subheader("💳 Payment")

        amount_paid = st.number_input(
            "Enter Payment Amount",
            min_value=0.0,
            step=1.0,
            key="payment"
        )

        if st.button("Make Payment"):

            if amount_paid == total_price:
                st.success("✅ Payment Successful. Exact amount received.")

            elif amount_paid > total_price:
                change = amount_paid - total_price
                st.success(
                    f"✅ Payment Successful. Return change: ₹{change:.2f}"
                )

            else:
                shortage = total_price - amount_paid
                st.error(
                    f"❌ Insufficient payment. Need ₹{shortage:.2f} more."
                )