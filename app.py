# app.py

import streamlit as st
import pandas as pd
from backend import run_full_pipeline


# ---------------------------------------------------
# Streamlit page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Liftoff VX Block Audit – AI Assistant",
    layout="wide",
)


# ---------------------------------------------------
# Sidebar – Inputs
# ---------------------------------------------------
st.sidebar.title("Run VX Block Audit")

st.sidebar.markdown(
    """
Enter publisher app IDs (Vungle app IDs), optional exclusions,  
and where the AI summary email should be sent.
"""
)

# Publisher app IDs (comma or newline separated)
default_app_ids = (
    "632cc7810ca02c6344d51822\n"
    "632cc70d35cc2d93ebf3b2d5\n"
    "5b2abc08c4867b46785c2206\n"
    "650363ddd38855ef54aae568"
)

app_ids_text = st.sidebar.text_area(
    "Publisher app IDs (one per line or comma-separated)",
    value=default_app_ids,
    height=120,
)

# Exclusions (block_values to ignore)
exclusions_text = st.sidebar.text_area(
    "Optional exclusions (domains / market IDs to ignore)",
    value="",
    placeholder="e.g. dreamgames.com, king.com",
    height=80,
)

# Email settings
st.sidebar.subheader("Email delivery")

recipient_email = st.sidebar.text_input(
    "Recipient email",
    value="ssai@liftoff.io",
    placeholder="recipient@example.com",
)

sender_email = st.sidebar.text_input(
    "Sender Gmail address",
    value="ssai@liftoff.io",
    placeholder="your_gmail@gmail.com",
)

gmail_app_password = st.sidebar.text_input(
    "Gmail App Password (16-char)",
    value="",
    type="password",
    help="Create this in your Google Account › Security › App passwords.",
)

# Schedule (coming soon)
st.sidebar.subheader("Schedule (coming soon)")
schedule_option = st.sidebar.selectbox(
    "Run mode",
    ["Run now (no schedule)", "Daily (coming soon)", "Weekly (coming soon)"],
    index=0,
    help="Scheduling not implemented yet – only 'Run now' works.",
)

run_button = st.sidebar.button("Run analysis", type="primary")


# ---------------------------------------------------
# Helper – parse text inputs into lists
# ---------------------------------------------------
def parse_id_list(text: str):
    if not text:
        return []
    # Split on newlines and commas
    raw = []
    for line in text.splitlines():
        raw.extend(line.split(","))
    return [x.strip() for x in raw if x.strip()]


def parse_exclusions(text: str):
    if not text:
        return []
    raw = []
    for line in text.splitlines():
        raw.extend(line.split(","))
    return [x.strip() for x in raw if x.strip()]


# ---------------------------------------------------
# Main layout
# ---------------------------------------------------
st.title("Liftoff VX – Block / Unblock AI Audit")
st.markdown(
    """
Use this tool to analyse **publisher blocks vs DSP & network spend**,  
see what **similar apps are monetising**, and receive an **AI-written summary by email**.
"""
)

# Container for results
results_placeholder = st.empty()


# ---------------------------------------------------
# When user clicks "Run analysis"
# ---------------------------------------------------
if run_button:
    target_app_ids = parse_id_list(app_ids_text)
    excluded_block_values = parse_exclusions(exclusions_text)

    if not target_app_ids:
        st.error("Please enter at least one publisher app ID.")
    elif not recipient_email:
        st.error("Please enter a recipient email.")
    elif not sender_email or not gmail_app_password:
        st.error("Please enter sender Gmail and Gmail App Password.")
    else:
        with st.spinner("Running analysis, generating AI summary and sending email..."):
            try:
                result = run_full_pipeline(
                    target_app_ids=target_app_ids,
                    excluded_block_values=excluded_block_values,
                    recipient_email=recipient_email,
                    sender_email=sender_email,
                    gmail_app_password=gmail_app_password,
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
            else:
                st.success(f"Done! AI summary emailed to {recipient_email}.")

                # ---------------------------------------------------
                # Show AI summary (HTML)
                # ---------------------------------------------------
                st.subheader("AI Summary (preview)")
                st.markdown(
                    "This is the same HTML summary that was sent by email:"
                )

                # Use HTML container so it keeps the formatting & tables
                st.components.v1.html(
                    result["html_summary"],
                    height=600,
                    scrolling=True,
                )

                # ---------------------------------------------------
                # Show detailed tables in tabs
                # ---------------------------------------------------
                st.subheader("Detailed outputs")

                (
                    tab1,
                    tab2,
                    tab3,
                    tab4,
                    tab5,
                ) = st.tabs(
                    [
                        "L7D DSP spend (blocks)",
                        "L30D network spend (blocks)",
                        "Block summary per app",
                        "Competitor revenue matrix",
                        "Summary metrics",
                    ]
                )

                with tab1:
                    st.markdown(
                        """
**Blocks enriched with L7D DSP spend (app + domain)**  
Non-VX spend shows what other DSPs are spending where VX is blocked.
"""
                    )
                    st.dataframe(result["combined_blocks_with_spend"])

                with tab2:
                    st.markdown(
                        """
**Global advertiser network spend (L30D) for blocked advertisers**  
Helps size missed opportunity from global scale.
"""
                    )
                    st.dataframe(result["combined_blocks_with_global"])

                with tab3:
                    st.markdown(
                        """
**Block summary per app (our apps only)**  
Block aggressiveness vs similar apps, including z-scores and missed spend.
"""
                    )
                    st.dataframe(result["combined_summary_our"])

                with tab4:
                    st.markdown(
                        """
**Competitor revenue matrix (L7D)**  
Revenue similar apps earn from advertisers the target apps block.
"""
                    )
                    st.dataframe(result["combined_rev_matrix"])

                with tab5:
                    st.markdown(
                        """
**High-level summary metrics**  
Key roll-up metrics used by the AI summary.
"""
                    )
                    st.dataframe(result["summary_metrics"])

else:
    st.info("Fill in the sidebar and click **Run analysis** to start.")
